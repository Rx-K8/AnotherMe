"""MuseTalkProvider の単体テスト (CI互換: GPU不要、MuseTalk import モック)"""

import os
import sys
from collections.abc import Generator
from pathlib import Path
from types import ModuleType
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from app.lipsync.abc import LipsyncProvider, LipsyncResult

_MODULE = "app.lipsync.musetalk_provider"


# ---------------------------------------------------------------------------
# MuseTalk モジュールのスタブ群（CI環境にMuseTalkが無い場合に備える）
# ---------------------------------------------------------------------------
def _build_musetalk_stubs() -> dict[str, ModuleType]:
    """musetalk.* 名前空間のスタブモジュールを生成する"""
    stubs: dict[str, ModuleType] = {}

    # musetalk
    musetalk = ModuleType("musetalk")
    stubs["musetalk"] = musetalk

    # musetalk.utils
    musetalk_utils = ModuleType("musetalk.utils")
    stubs["musetalk.utils"] = musetalk_utils

    # musetalk.utils.utils
    utils_utils = ModuleType("musetalk.utils.utils")
    mock_models = (MagicMock(), MagicMock(), MagicMock())
    utils_utils.load_all_model = MagicMock(return_value=mock_models)  # type: ignore[attr-defined]
    utils_utils.get_file_type = MagicMock(return_value="video")  # type: ignore[attr-defined]
    utils_utils.get_video_fps = MagicMock(return_value=25)  # type: ignore[attr-defined]
    utils_utils.datagen = MagicMock(return_value=iter([]))  # type: ignore[attr-defined]
    stubs["musetalk.utils.utils"] = utils_utils

    # musetalk.utils.preprocessing
    preprocessing = ModuleType("musetalk.utils.preprocessing")
    preprocessing.get_landmark_and_bbox = MagicMock(return_value=([], []))  # type: ignore[attr-defined]
    preprocessing.read_imgs = MagicMock(return_value=[])  # type: ignore[attr-defined]
    preprocessing.coord_placeholder = (-1, -1, -1, -1)  # type: ignore[attr-defined]
    preprocessing.get_bbox_range = MagicMock(return_value="")  # type: ignore[attr-defined]
    stubs["musetalk.utils.preprocessing"] = preprocessing

    # musetalk.utils.blending
    blending = ModuleType("musetalk.utils.blending")
    blending.get_image = MagicMock()  # type: ignore[attr-defined]
    stubs["musetalk.utils.blending"] = blending

    # musetalk.utils.face_parsing
    face_parsing = ModuleType("musetalk.utils.face_parsing")
    face_parsing.FaceParsing = MagicMock()  # type: ignore[attr-defined]
    stubs["musetalk.utils.face_parsing"] = face_parsing

    # musetalk.utils.audio_processor
    audio_processor = ModuleType("musetalk.utils.audio_processor")
    audio_processor.AudioProcessor = MagicMock()  # type: ignore[attr-defined]
    stubs["musetalk.utils.audio_processor"] = audio_processor

    return stubs


def _build_torch_mock() -> MagicMock:
    """load_models() 用の torch モックを生成する

    CI 環境に CUDA が無いため、torch.device / torch.tensor 等を
    MagicMock で差し替える。
    """
    mock_torch = MagicMock()
    mock_torch.device = MagicMock
    mock_torch.float16 = "float16"
    mock_torch.float32 = "float32"
    ctx = MagicMock(__enter__=MagicMock(), __exit__=MagicMock())
    mock_torch.no_grad = MagicMock(return_value=ctx)
    mock_torch.tensor = MagicMock()
    return mock_torch


def _build_whisper_mock() -> MagicMock:
    """load_models() 用の WhisperModel モックを生成する

    CI 環境にモデルファイルが無いため、from_pretrained をモックする。
    """
    mock_cls = MagicMock()
    mock_cls.from_pretrained.return_value = MagicMock()
    return mock_cls


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture()
def musetalk_stubs() -> dict[str, ModuleType]:
    return _build_musetalk_stubs()


@pytest.fixture()
def _patch_musetalk_imports(
    musetalk_stubs: dict[str, ModuleType],
    tmp_path: Path,
) -> Generator[None, None, None]:
    """MuseTalk スタブ + torch/WhisperModel モックを注入する

    musetalk.* — sys.modules に直接注入（パッケージが存在しないため）
    torch, WhisperModel — モジュールレベル参照を patch で差し替え
    """
    # musetalk スタブを sys.modules に注入
    originals: dict[str, Any] = {}
    for name, mod in musetalk_stubs.items():
        originals[name] = sys.modules.get(name)
        sys.modules[name] = mod

    mock_torch = _build_torch_mock()
    mock_whisper = _build_whisper_mock()

    with (
        patch(f"{_MODULE}.torch", mock_torch),
        patch(f"{_MODULE}.WhisperModel", mock_whisper),
        patch(f"{_MODULE}._DEFAULT_MODEL_DIR", tmp_path),
        patch(f"{_MODULE}.MuseTalkProvider._check_model_files", return_value=[]),
    ):
        yield

    for name in musetalk_stubs:
        if originals[name] is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = originals[name]


# ---------------------------------------------------------------------------
# テストクラス
# ---------------------------------------------------------------------------
class TestMuseTalkProviderInit:
    """__init__ のパラメータ検証"""

    @pytest.mark.unit
    def test_init_default_values(self) -> None:
        from app.lipsync.musetalk_provider import MuseTalkProvider

        provider = MuseTalkProvider()
        assert provider._device == "cuda:0"
        assert provider._use_float16 is True
        assert provider._batch_size == 8
        assert provider._loaded is False

    @pytest.mark.unit
    def test_init_custom_values(self) -> None:
        from app.lipsync.musetalk_provider import MuseTalkProvider

        provider = MuseTalkProvider(
            device="cuda:1",
            model_dir="/custom/path",
            use_float16=False,
            batch_size=4,
        )
        assert provider._device == "cuda:1"
        assert provider._model_dir == Path("/custom/path")
        assert provider._use_float16 is False
        assert provider._batch_size == 4

    @pytest.mark.unit
    def test_model_dir_defaults_to_submodules(self) -> None:
        from app.lipsync.musetalk_provider import MuseTalkProvider

        provider = MuseTalkProvider()
        expected = Path(__file__).resolve().parents[2] / "submodules" / "MuseTalk"
        assert provider._model_dir == expected

    @pytest.mark.unit
    def test_is_subclass_of_lipsync_provider(self) -> None:
        from app.lipsync.musetalk_provider import MuseTalkProvider

        assert issubclass(MuseTalkProvider, LipsyncProvider)


class TestMuseTalkProviderIsReady:
    """is_ready() の状態テスト"""

    @pytest.mark.unit
    async def test_is_ready_false_before_load(self) -> None:
        from app.lipsync.musetalk_provider import MuseTalkProvider

        provider = MuseTalkProvider()
        assert await provider.is_ready() is False

    @pytest.mark.unit
    @pytest.mark.usefixtures("_patch_musetalk_imports")
    async def test_is_ready_true_after_load(self) -> None:
        from app.lipsync.musetalk_provider import MuseTalkProvider

        provider = MuseTalkProvider()
        provider.load_models()
        assert await provider.is_ready() is True


class TestMuseTalkProviderSysPath:
    """_setup_sys_path のテスト"""

    @pytest.mark.unit
    def test_setup_sys_path_adds_model_dir(self) -> None:
        from app.lipsync.musetalk_provider import MuseTalkProvider

        provider = MuseTalkProvider(model_dir="/fake/musetalk")
        original_path = sys.path.copy()

        try:
            provider._setup_sys_path()
            assert "/fake/musetalk" in sys.path
        finally:
            sys.path[:] = original_path

    @pytest.mark.unit
    def test_setup_sys_path_idempotent(self) -> None:
        from app.lipsync.musetalk_provider import MuseTalkProvider

        provider = MuseTalkProvider(model_dir="/fake/musetalk2")
        original_path = sys.path.copy()

        try:
            provider._setup_sys_path()
            provider._setup_sys_path()
            count = sys.path.count("/fake/musetalk2")
            assert count == 1
        finally:
            sys.path[:] = original_path


class TestMuseTalkProviderChdirMusetalk:
    """_chdir_musetalk() コンテキストマネージャーのテスト"""

    @pytest.mark.unit
    def test_chdir_changes_to_model_dir(self, tmp_path: Path) -> None:
        from app.lipsync.musetalk_provider import MuseTalkProvider

        provider = MuseTalkProvider(model_dir=str(tmp_path))
        original_cwd = os.getcwd()

        with provider._chdir_musetalk():
            assert os.getcwd() == str(tmp_path)

        assert os.getcwd() == original_cwd

    @pytest.mark.unit
    def test_chdir_restores_on_exception(self, tmp_path: Path) -> None:
        from app.lipsync.musetalk_provider import MuseTalkProvider

        provider = MuseTalkProvider(model_dir=str(tmp_path))
        original_cwd = os.getcwd()

        with pytest.raises(RuntimeError, match="test error"):
            with provider._chdir_musetalk():
                assert os.getcwd() == str(tmp_path)
                msg = "test error"
                raise RuntimeError(msg)

        assert os.getcwd() == original_cwd


class TestMuseTalkProviderLoadModels:
    """load_models() のテスト（MuseTalk import をモック）"""

    @pytest.mark.unit
    @pytest.mark.usefixtures("_patch_musetalk_imports")
    def test_load_models_sets_loaded_flag(self) -> None:
        from app.lipsync.musetalk_provider import MuseTalkProvider

        provider = MuseTalkProvider()
        assert provider._loaded is False
        provider.load_models()
        assert provider._loaded is True

    @pytest.mark.unit
    @pytest.mark.usefixtures("_patch_musetalk_imports")
    def test_load_models_sets_internal_attributes(self) -> None:
        from app.lipsync.musetalk_provider import MuseTalkProvider

        provider = MuseTalkProvider()
        provider.load_models()

        assert provider._vae is not None
        assert provider._unet is not None
        assert provider._pe is not None
        assert provider._audio_processor is not None
        assert provider._whisper is not None
        assert provider._timesteps is not None

    @pytest.mark.unit
    @pytest.mark.usefixtures("_patch_musetalk_imports")
    def test_load_models_idempotent(self) -> None:
        """load_models() を2回呼んでも問題ない"""
        from app.lipsync.musetalk_provider import MuseTalkProvider

        provider = MuseTalkProvider()
        provider.load_models()
        provider.load_models()
        assert provider._loaded is True


class TestMuseTalkProviderGenerate:
    """generate() のテスト"""

    @pytest.mark.unit
    async def test_generate_raises_when_not_loaded(self) -> None:
        from app.lipsync.musetalk_provider import MuseTalkProvider

        provider = MuseTalkProvider()
        with pytest.raises(RuntimeError, match="load_models"):
            await provider.generate(
                audio_path="/tmp/test.wav",
                video_path="/tmp/test.mp4",
            )

    @pytest.mark.unit
    @pytest.mark.usefixtures("_patch_musetalk_imports")
    async def test_generate_calls_inference_sync_in_executor(self) -> None:
        from app.lipsync.musetalk_provider import MuseTalkProvider

        provider = MuseTalkProvider()
        provider.load_models()

        fake_result = LipsyncResult(
            video_bytes=b"\x00\x00\x00\x1c\x66\x74\x79\x70",
            duration_seconds=2.5,
        )

        with patch.object(
            provider, "_inference_sync", return_value=fake_result
        ) as mock_sync:
            result = await provider.generate(
                audio_path="/tmp/test.wav",
                video_path="/tmp/test.mp4",
                bbox_shift=5,
                extra_margin=15,
                parsing_mode="face",
            )

            mock_sync.assert_called_once_with(
                "/tmp/test.wav", "/tmp/test.mp4", 5, 15, "face"
            )
            assert result is fake_result

    @pytest.mark.unit
    @pytest.mark.usefixtures("_patch_musetalk_imports")
    async def test_generate_returns_lipsync_result(self) -> None:
        from app.lipsync.musetalk_provider import MuseTalkProvider

        provider = MuseTalkProvider()
        provider.load_models()

        fake_result = LipsyncResult(
            video_bytes=b"fakevideo",
            duration_seconds=1.0,
        )

        with patch.object(provider, "_inference_sync", return_value=fake_result):
            result = await provider.generate(
                audio_path="/tmp/test.wav",
                video_path="/tmp/test.mp4",
            )

            assert isinstance(result, LipsyncResult)
            assert result.video_bytes == b"fakevideo"
            assert result.duration_seconds == 1.0

    @pytest.mark.unit
    @pytest.mark.usefixtures("_patch_musetalk_imports")
    async def test_generate_default_parameters(self) -> None:
        from app.lipsync.musetalk_provider import MuseTalkProvider

        provider = MuseTalkProvider()
        provider.load_models()

        fake_result = LipsyncResult(video_bytes=b"data", duration_seconds=0.5)

        with patch.object(
            provider, "_inference_sync", return_value=fake_result
        ) as mock_sync:
            await provider.generate(
                audio_path="/tmp/a.wav",
                video_path="/tmp/v.mp4",
            )

            mock_sync.assert_called_once_with("/tmp/a.wav", "/tmp/v.mp4", 0, 10, "jaw")


class TestMuseTalkProviderInferenceSync:
    """_inference_sync() の内部ロジックテスト（重い処理はすべてモック）"""

    @pytest.mark.unit
    @pytest.mark.usefixtures("_patch_musetalk_imports")
    def test_inference_sync_returns_lipsync_result(self, tmp_path: Path) -> None:
        from app.lipsync.musetalk_provider import MuseTalkProvider

        provider = MuseTalkProvider()
        provider.load_models()

        # _run_pipeline をモックして MP4 バイト列を返す
        fake_bytes = b"\x00\x00\x00\x1c\x66\x74\x79\x70\x69\x73\x6f\x6d"
        with patch.object(provider, "_run_pipeline", return_value=(fake_bytes, 2.0)):
            result = provider._inference_sync(
                str(tmp_path / "test.wav"),
                str(tmp_path / "test.mp4"),
                0,
                10,
                "jaw",
            )

        assert isinstance(result, LipsyncResult)
        assert result.video_bytes == fake_bytes
        assert result.duration_seconds == 2.0


class TestMuseTalkProviderFactoryIntegration:
    """factory.py との統合テスト"""

    @pytest.mark.integration
    def test_factory_creates_musetalk_provider(self) -> None:
        from app.lipsync.factory import create_provider
        from app.lipsync.musetalk_provider import MuseTalkProvider

        with patch("app.lipsync.factory.settings") as mock_settings:
            mock_settings.gpu_device = "cuda:0"
            provider = create_provider("musetalk")

        assert isinstance(provider, MuseTalkProvider)

    @pytest.mark.integration
    def test_factory_still_creates_mock_provider(self) -> None:
        from app.lipsync.factory import create_provider
        from app.lipsync.mock import MockLipsyncProvider

        provider = create_provider("mock")
        assert isinstance(provider, MockLipsyncProvider)

    @pytest.mark.integration
    def test_factory_unknown_provider_raises(self) -> None:
        from app.lipsync.factory import create_provider

        with pytest.raises(ValueError, match="不明なプロバイダー名"):
            create_provider("nonexistent")


class TestMuseTalkProviderConfig:
    """config.py に追加された設定値のテスト"""

    @pytest.mark.unit
    def test_settings_has_provider_name(self) -> None:
        from app.core.config import Settings

        s = Settings()
        assert hasattr(s, "provider_name")
        assert s.provider_name == "musetalk"

    @pytest.mark.unit
    def test_settings_has_use_float16(self) -> None:
        from app.core.config import Settings

        s = Settings()
        assert hasattr(s, "use_float16")
        assert s.use_float16 is True

    @pytest.mark.unit
    def test_settings_has_batch_size(self) -> None:
        from app.core.config import Settings

        s = Settings()
        assert hasattr(s, "batch_size")
        assert s.batch_size == 8


# ---------------------------------------------------------------------------
# モデルファイル存在チェック
# ---------------------------------------------------------------------------
class TestMuseTalkProviderModelCheck:
    """_check_model_files / load_models のモデル存在チェックテスト"""

    @pytest.mark.unit
    def test_check_model_files_all_missing(self, tmp_path: Path) -> None:
        from app.lipsync.musetalk_provider import MuseTalkProvider

        provider = MuseTalkProvider(model_dir=str(tmp_path))
        missing = provider._check_model_files()
        assert len(missing) == len(MuseTalkProvider._REQUIRED_MODEL_FILES)

    @pytest.mark.unit
    def test_check_model_files_all_present(self, tmp_path: Path) -> None:
        from app.lipsync.musetalk_provider import MuseTalkProvider

        models_dir = tmp_path / "models"
        for f in MuseTalkProvider._REQUIRED_MODEL_FILES:
            path = models_dir / f
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"dummy")

        provider = MuseTalkProvider(model_dir=str(tmp_path))
        assert provider._check_model_files() == []

    @pytest.mark.unit
    def test_load_models_raises_when_files_missing(self, tmp_path: Path) -> None:
        from app.lipsync.musetalk_provider import MuseTalkProvider

        provider = MuseTalkProvider(model_dir=str(tmp_path))
        with pytest.raises(FileNotFoundError, match="download_weights.sh"):
            provider.load_models()


# ---------------------------------------------------------------------------
# GPU テスト (CI除外)
# ---------------------------------------------------------------------------
class TestMuseTalkProviderGPU:
    """GPU環境でのみ実行するテスト"""

    @pytest.mark.gpu
    def test_load_models_on_gpu(self) -> None:
        from app.lipsync.musetalk_provider import MuseTalkProvider

        provider = MuseTalkProvider(device="cuda:0")
        provider.load_models()
        assert provider._loaded is True

    @pytest.mark.gpu
    async def test_generate_with_real_data(self, tmp_path: Path) -> None:
        from app.lipsync.musetalk_provider import MuseTalkProvider

        provider = MuseTalkProvider(device="cuda:0")
        provider.load_models()

        # 実際のテストデータが必要
        audio_path = str(tmp_path / "test.wav")
        video_path = str(tmp_path / "test.mp4")
        result = await provider.generate(
            audio_path=audio_path,
            video_path=video_path,
        )
        assert isinstance(result, LipsyncResult)
        assert len(result.video_bytes) > 0
        assert result.duration_seconds > 0
