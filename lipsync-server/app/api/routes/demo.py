"""デモUIページのルート定義"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["Demo"])

DEMO_HTML = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AnotherMe Lipsync Demo</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
                         'Helvetica Neue', Arial, sans-serif;
            max-width: 640px;
            margin: 0 auto;
            padding: 2rem;
            background: #f5f5f5;
        }
        h1 { color: #333; margin-bottom: 1.5rem; }
        .form-group { margin-bottom: 1.25rem; }
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 600;
            color: #444;
        }
        input[type="file"] {
            width: 100%;
            padding: 0.5rem;
            border: 2px dashed #ddd;
            border-radius: 6px;
            background: #fff;
            cursor: pointer;
        }
        input[type="number"] {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 1rem;
        }
        select {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 1rem;
            background: #fff;
        }
        button {
            width: 100%;
            padding: 1rem;
            background: #4a90d9;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }
        button:hover { background: #357abd; }
        button:disabled { background: #ccc; cursor: not-allowed; }
        .result {
            margin-top: 1.5rem;
            padding: 1rem;
            background: #fff;
            border-radius: 6px;
            border: 1px solid #ddd;
            display: none;
        }
        .result.show { display: block; }
        .result h3 { margin: 0 0 1rem 0; color: #333; }
        video { width: 100%; border-radius: 6px; }
        .meta {
            margin-top: 0.75rem;
            font-size: 0.85rem;
            color: #666;
        }
        .download-btn {
            width: 100%;
            padding: 0.75rem;
            background: #28a745;
            margin-top: 0.75rem;
        }
        .download-btn:hover { background: #218838; }
        .error {
            color: #dc3545;
            padding: 1rem;
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 6px;
            margin-top: 1rem;
            display: none;
        }
        .error.show { display: block; }
        .loading {
            text-align: center;
            color: #666;
            padding: 1rem;
            display: none;
        }
        .loading.show { display: block; }
    </style>
</head>
<body>
    <h1>AnotherMe Lipsync Demo</h1>

    <form id="lipsyncForm">
        <div class="form-group">
            <label for="audioFile">音声ファイル (WAV/MP3)</label>
            <input type="file" id="audioFile" accept=".wav,.mp3" required>
        </div>

        <div class="form-group">
            <label for="videoFile">動画/画像ファイル (MP4/MOV/JPG/PNG)</label>
            <input type="file" id="videoFile" accept=".mp4,.mov,.jpg,.png" required>
        </div>

        <div class="form-group">
            <label for="bboxShift">BBox Shift</label>
            <input type="number" id="bboxShift" value="0" min="-50" max="50">
        </div>

        <div class="form-group">
            <label for="extraMargin">Extra Margin</label>
            <input type="number" id="extraMargin" value="10" min="0" max="40">
        </div>

        <div class="form-group">
            <label for="parsingMode">Parsing Mode</label>
            <select id="parsingMode">
                <option value="jaw" selected>jaw</option>
                <option value="face">face</option>
            </select>
        </div>

        <button type="submit" id="submitBtn">生成</button>
    </form>

    <div class="loading" id="loading">生成中... (数分かかる場合があります)</div>
    <div class="error" id="error"></div>

    <div class="result" id="result">
        <h3>生成結果</h3>
        <video id="videoPlayer" controls></video>
        <div class="meta" id="meta"></div>
        <button class="download-btn" id="downloadBtn">ダウンロード</button>
    </div>

    <script>
        const form = document.getElementById('lipsyncForm');
        const submitBtn = document.getElementById('submitBtn');
        const loading = document.getElementById('loading');
        const errorDiv = document.getElementById('error');
        const resultDiv = document.getElementById('result');
        const videoPlayer = document.getElementById('videoPlayer');
        const metaDiv = document.getElementById('meta');
        const downloadBtn = document.getElementById('downloadBtn');

        let videoBlob = null;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const audioFile = document.getElementById('audioFile').files[0];
            const videoFile = document.getElementById('videoFile').files[0];
            if (!audioFile || !videoFile) {
                showError('ファイルを選択してください');
                return;
            }

            submitBtn.disabled = true;
            loading.classList.add('show');
            errorDiv.classList.remove('show');
            resultDiv.classList.remove('show');

            try {
                const formData = new FormData();
                formData.append('audio_file', audioFile);
                formData.append('video_file', videoFile);
                formData.append('bbox_shift',
                    document.getElementById('bboxShift').value);
                formData.append('extra_margin',
                    document.getElementById('extraMargin').value);
                formData.append('parsing_mode',
                    document.getElementById('parsingMode').value);

                const response = await fetch('/api/lipsync/generate', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    const err = await response.json();
                    throw new Error(err.detail || err.error || 'エラーが発生しました');
                }

                const data = await response.json();
                const bin = atob(data.video_data);
                const bytes = new Uint8Array(bin.length);
                for (let i = 0; i < bin.length; i++) {
                    bytes[i] = bin.charCodeAt(i);
                }
                videoBlob = new Blob([bytes], { type: 'video/mp4' });

                videoPlayer.src = URL.createObjectURL(videoBlob);
                metaDiv.textContent =
                    `Duration: ${data.duration_seconds.toFixed(1)}s` +
                    ` | Processing: ${(data.processing_time_ms / 1000).toFixed(1)}s`;
                resultDiv.classList.add('show');
            } catch (err) {
                showError(err.message);
            } finally {
                submitBtn.disabled = false;
                loading.classList.remove('show');
            }
        });

        downloadBtn.addEventListener('click', () => {
            if (!videoBlob) return;
            const url = URL.createObjectURL(videoBlob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'lipsync_output.mp4';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        });

        function showError(msg) {
            errorDiv.textContent = msg;
            errorDiv.classList.add('show');
        }
    </script>
</body>
</html>
"""


@router.get(
    "/demo",
    response_class=HTMLResponse,
    summary="デモUIページ",
    description="リップシンク生成を試すためのデモUIページを表示します。",
)
async def demo_page() -> HTMLResponse:
    return HTMLResponse(content=DEMO_HTML)
