"""MuseTalk を利用したリップシンクプロバイダー

MuseTalk は submodules/MuseTalk に配置されており、
pyproject.toml が存在しないため sys.path 方式で import する。
GPU 推論はすべて _inference_sync() で同期的に行い、
generate() から run_in_executor で呼び出す。
"""

from __future__ import annotations

import asyncio
import copy
import glob
import logging
import os
import re
import sys
import tempfile
from argparse import Namespace
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import cv2
import imageio
import numpy as np
import torch
from transformers import WhisperModel

from app.lipsync.abc import LipsyncProvider, LipsyncResult

logger = logging.getLogger(__name__)

# デフォルトの MuseTalk サブモジュールパス
_DEFAULT_MODEL_DIR = Path(__file__).resolve().parents[2] / "submodules" / "MuseTalk"


class MuseTalkProvider(LipsyncProvider):
    """MuseTalk による高品質リップシンク動画生成プロバイダー

    load_models() を呼ぶまでは推論不可。
    MuseTalk 関連の import は load_models() 内で動的に行い、
    CI 環境（GPU/MuseTalk 未インストール）でも import エラーにならない。
    """

    def __init__(
        self,
        device: str = "cuda:0",
        model_dir: str | None = None,
        use_float16: bool = True,
        batch_size: int = 8,
    ) -> None:
        self._device = device
        self._model_dir = (
            Path(model_dir) if model_dir is not None else _DEFAULT_MODEL_DIR
        )
        self._use_float16 = use_float16
        self._batch_size = batch_size
        self._loaded = False

        # load_models() で初期化される内部状態
        self._vae: Any = None
        self._unet: Any = None
        self._pe: Any = None
        self._audio_processor: Any = None
        self._whisper: Any = None
        self._timesteps: Any = None
        self._weight_dtype: Any = None

        # MuseTalk のユーティリティ関数（動的 import 後に設定）
        self._get_file_type: Any = None
        self._get_video_fps: Any = None
        self._datagen: Any = None
        self._get_landmark_and_bbox: Any = None
        self._read_imgs: Any = None
        self._coord_placeholder: Any = None
        self._get_bbox_range: Any = None
        self._get_image: Any = None
        self._FaceParsing: Any = None

    def _setup_sys_path(self) -> None:
        """submodules/MuseTalk を sys.path に追加する（冪等）"""
        model_dir_str = str(self._model_dir)
        if model_dir_str not in sys.path:
            sys.path.insert(0, model_dir_str)

    @contextmanager
    def _chdir_musetalk(self) -> Iterator[None]:
        """CWD を MuseTalk ルートに一時変更する

        MuseTalk の preprocessing.py や face_parsing が
        相対パス（./musetalk/utils/dwpose/... 等）で
        モデルを参照するため、import 時・実行時に CWD が
        MuseTalk ルートである必要がある。
        """
        prev_cwd = os.getcwd()
        os.chdir(self._model_dir)
        try:
            yield
        finally:
            os.chdir(prev_cwd)

    # load_models() でチェックする必須モデルファイル（models/ からの相対パス）
    _REQUIRED_MODEL_FILES: tuple[str, ...] = (
        "musetalkV15/unet.pth",
        "musetalkV15/musetalk.json",
        "sd-vae/config.json",
        "sd-vae/diffusion_pytorch_model.bin",
        "whisper/config.json",
        "whisper/pytorch_model.bin",
        "dwpose/dw-ll_ucoco_384.pth",
        "face-parse-bisent/79999_iter.pth",
        "face-parse-bisent/resnet18-5c106cde.pth",
    )

    def _check_model_files(self) -> list[str]:
        """不足しているモデルファイルの相対パスリストを返す"""
        models_dir = self._model_dir / "models"
        return [f for f in self._REQUIRED_MODEL_FILES if not (models_dir / f).exists()]

    def load_models(self) -> None:
        """全モデルをロードする（同期メソッド）

        MuseTalk の import をここで動的に行うため、
        CI 環境でもクラスの import 自体は成功する。
        preprocessing.py がモジュールレベルで相対パスを使って
        init_model() を呼ぶため、CWD を MuseTalk ルートに変更する。

        Raises:
            FileNotFoundError: 必須モデルファイルが不足している場合
        """
        if self._loaded:
            return

        missing = self._check_model_files()
        if missing:
            msg = (
                "以下のモデルファイルが見つかりません:\n"
                + "\n".join(f"  - {f}" for f in missing)
                + "\n\nダウンロードスクリプトを実行してください:\n"
                "  cd lipsync-server && bash download_weights.sh"
            )
            raise FileNotFoundError(msg)

        self._setup_sys_path()

        # MuseTalk モジュールは pyproject.toml に含まれず、
        # sys.path 追加 + CWD 変更が前提のため動的 import が必須。
        # load_all_model() 内部で os.path.join("models", vae_type) と
        # 相対パスがハードコードされているため、CWD を維持する。
        with self._chdir_musetalk():
            from musetalk.utils.audio_processor import AudioProcessor
            from musetalk.utils.blending import get_image
            from musetalk.utils.face_parsing import FaceParsing
            from musetalk.utils.preprocessing import (
                coord_placeholder,
                get_bbox_range,
                get_landmark_and_bbox,
                read_imgs,
            )
            from musetalk.utils.utils import (
                datagen,
                get_file_type,
                get_video_fps,
                load_all_model,
            )

            device = torch.device(self._device)

            vae, unet, pe = load_all_model(device=device)

        # ユーティリティ関数を保持
        self._get_file_type = get_file_type
        self._get_video_fps = get_video_fps
        self._datagen = datagen
        self._get_landmark_and_bbox = get_landmark_and_bbox
        self._read_imgs = read_imgs
        self._coord_placeholder = coord_placeholder
        self._get_bbox_range = get_bbox_range
        self._get_image = get_image
        self._FaceParsing = FaceParsing

        if self._use_float16:
            pe = pe.half()
            vae.vae = vae.vae.half()
            unet.model = unet.model.half()
            self._weight_dtype = torch.float16
        else:
            self._weight_dtype = torch.float32

        pe = pe.to(device)
        vae.vae = vae.vae.to(device)
        unet.model = unet.model.to(device)

        self._vae = vae
        self._unet = unet
        self._pe = pe
        self._timesteps = torch.tensor([0], device=device)

        models_dir = str(self._model_dir / "models")
        whisper_path = os.path.join(models_dir, "whisper")
        self._audio_processor = AudioProcessor(feature_extractor_path=whisper_path)
        whisper = WhisperModel.from_pretrained(whisper_path)
        whisper = whisper.to(device=device, dtype=self._weight_dtype).eval()
        whisper.requires_grad_(False)
        self._whisper = whisper

        self._loaded = True
        logger.info("MuseTalk models loaded on %s", self._device)

    def _run_pipeline(
        self,
        audio_path: str,
        video_path: str,
        bbox_shift: int,
        extra_margin: int,
        parsing_mode: str,
    ) -> tuple[bytes, float]:
        """MuseTalk 推論パイプラインを実行する

        Returns:
            (動画バイト列, 秒数) のタプル
        """
        # moviepy.editor は ffmpeg 依存の重い初期化を含むため関数内 import
        from moviepy.editor import AudioFileClip, VideoFileClip

        device = torch.device(self._device)

        args = Namespace(
            result_dir="",
            fps=25,
            batch_size=self._batch_size,
            output_vid_name="",
            use_saved_coord=False,
            audio_padding_length_left=2,
            audio_padding_length_right=2,
            version="v15",
            extra_margin=extra_margin,
            parsing_mode=parsing_mode,
            left_cheek_width=90,
            right_cheek_width=90,
        )

        with tempfile.TemporaryDirectory(prefix="musetalk_") as work_dir:
            temp_dir = os.path.join(work_dir, "v15")
            os.makedirs(temp_dir, exist_ok=True)

            input_basename = os.path.basename(video_path).split(".")[0]
            audio_basename = os.path.basename(audio_path).split(".")[0]
            output_basename = f"{input_basename}_{audio_basename}"

            result_img_save_path = os.path.join(temp_dir, output_basename)
            os.makedirs(result_img_save_path, exist_ok=True)

            output_vid_path = os.path.join(temp_dir, f"{output_basename}.mp4")

            # --- フレーム抽出 ---
            if self._get_file_type(video_path) == "video":
                save_dir_full = os.path.join(temp_dir, input_basename)
                os.makedirs(save_dir_full, exist_ok=True)
                reader = imageio.get_reader(video_path)
                for i, im in enumerate(reader):  # type: ignore[arg-type, var-annotated]
                    imageio.imwrite(f"{save_dir_full}/{i:08d}.png", im)
                input_img_list = sorted(
                    glob.glob(os.path.join(save_dir_full, "*.[jpJP][pnPN]*[gG]"))
                )
                fps = self._get_video_fps(video_path)
            else:
                input_img_list = glob.glob(
                    os.path.join(video_path, "*.[jpJP][pnPN]*[gG]")
                )
                input_img_list = sorted(
                    input_img_list,
                    key=lambda x: int(os.path.splitext(os.path.basename(x))[0]),
                )
                fps = args.fps

            # --- 音声特徴抽出 ---
            whisper_input_features, librosa_length = (
                self._audio_processor.get_audio_feature(audio_path)
            )
            whisper_chunks = self._audio_processor.get_whisper_chunk(
                whisper_input_features,
                device,
                self._weight_dtype,
                self._whisper,
                librosa_length,
                fps=fps,
                audio_padding_length_left=args.audio_padding_length_left,
                audio_padding_length_right=args.audio_padding_length_right,
            )

            # --- 前処理 ---
            try:
                coord_list, frame_list = self._get_landmark_and_bbox(
                    input_img_list, bbox_shift
                )
            except ZeroDivisionError:
                raise ValueError(
                    "入力画像/動画から顔を検出できませんでした。"
                    "顔が明瞭に写っているファイルを使用してください。"
                ) from None

            # FaceParsing.model_init() が ./models/face-parse-bisent/ を参照するため
            # CWD を MuseTalk ルートに変更する
            with self._chdir_musetalk():
                fp = self._FaceParsing(
                    left_cheek_width=args.left_cheek_width,
                    right_cheek_width=args.right_cheek_width,
                )

            input_latent_list = []
            for bbox, frame in zip(coord_list, frame_list, strict=False):
                if bbox == self._coord_placeholder:
                    continue
                x1, y1, x2, y2 = bbox
                y2 = y2 + args.extra_margin
                y2 = min(y2, frame.shape[0])
                crop_frame = frame[y1:y2, x1:x2]
                crop_frame = cv2.resize(
                    crop_frame, (256, 256), interpolation=cv2.INTER_LANCZOS4
                )
                latents = self._vae.get_latents_for_unet(crop_frame)
                input_latent_list.append(latents)

            # サイクル化（スムージング用）
            frame_list_cycle = frame_list + frame_list[::-1]
            coord_list_cycle = coord_list + coord_list[::-1]
            input_latent_list_cycle = input_latent_list + input_latent_list[::-1]

            # --- 推論 ---
            gen = self._datagen(
                whisper_chunks=whisper_chunks,
                vae_encode_latents=input_latent_list_cycle,
                batch_size=args.batch_size,
                delay_frame=0,
                device=device,
            )

            res_frame_list: list[Any] = []
            for whisper_batch, latent_batch in gen:
                audio_feature_batch = self._pe(whisper_batch)
                latent_batch = latent_batch.to(dtype=self._weight_dtype)
                pred_latents = self._unet.model(
                    latent_batch,
                    self._timesteps,
                    encoder_hidden_states=audio_feature_batch,
                ).sample
                recon = self._vae.decode_latents(pred_latents)
                for res_frame in recon:
                    res_frame_list.append(res_frame)

            # --- ブレンディング + 書き出し ---
            last_frame = frame_list[-1] if frame_list else None
            for i, res_frame in enumerate(res_frame_list):
                bbox = coord_list_cycle[i % len(coord_list_cycle)]
                ori_frame = copy.deepcopy(frame_list_cycle[i % len(frame_list_cycle)])
                x1, y1, x2, y2 = bbox
                y2 = y2 + args.extra_margin
                frame_ref = last_frame if last_frame is not None else ori_frame
                y2 = min(y2, frame_ref.shape[0])
                try:
                    res_frame = cv2.resize(
                        res_frame.astype(np.uint8), (x2 - x1, y2 - y1)
                    )
                except Exception:
                    continue

                combine_frame = self._get_image(
                    ori_frame,
                    res_frame,
                    [x1, y1, x2, y2],
                    mode=args.parsing_mode,
                    fp=fp,
                )
                cv2.imwrite(
                    f"{result_img_save_path}/{str(i).zfill(8)}.png",
                    combine_frame,
                )

            # --- 動画生成 ---
            pattern = re.compile(r"\d{8}\.png")
            files = sorted(
                [f for f in os.listdir(result_img_save_path) if pattern.match(f)],
                key=lambda x: int(x.split(".")[0]),
            )

            images: list[Any] = [
                imageio.imread(os.path.join(result_img_save_path, f))  # type: ignore[no-untyped-call]
                for f in files
            ]

            temp_video_path = os.path.join(work_dir, "temp.mp4")
            imageio.mimwrite(  # type: ignore[call-overload]
                temp_video_path,
                images,
                "FFMPEG",
                fps=25,
                codec="libx264",
                pixelformat="yuv420p",
            )

            # --- 音声合成 ---
            video_clip = VideoFileClip(temp_video_path)
            audio_clip = AudioFileClip(audio_path)
            video_clip = video_clip.set_audio(audio_clip)
            video_clip.write_videofile(
                output_vid_path, codec="libx264", audio_codec="aac", fps=25
            )
            video_clip.close()
            audio_clip.close()

            duration = len(images) / 25.0

            with open(output_vid_path, "rb") as f:
                video_bytes = f.read()

        return video_bytes, duration

    def _inference_sync(
        self,
        audio_path: str,
        video_path: str,
        bbox_shift: int,
        extra_margin: int,
        parsing_mode: str,
    ) -> LipsyncResult:
        """同期推論（run_in_executor から呼ばれる）"""
        with torch.no_grad():
            video_bytes, duration = self._run_pipeline(
                audio_path, video_path, bbox_shift, extra_margin, parsing_mode
            )

        return LipsyncResult(
            video_bytes=video_bytes,
            duration_seconds=duration,
        )

    async def generate(
        self,
        audio_path: str,
        video_path: str,
        bbox_shift: int = 0,
        extra_margin: int = 10,
        parsing_mode: str = "jaw",
    ) -> LipsyncResult:
        if not self._loaded:
            msg = "モデル未ロード: 先に load_models() を呼び出してください"
            raise RuntimeError(msg)

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            self._inference_sync,
            audio_path,
            video_path,
            bbox_shift,
            extra_margin,
            parsing_mode,
        )

    async def is_ready(self) -> bool:
        return self._loaded
