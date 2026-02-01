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
    <title>AnotherMe TTS Demo</title>
    <style>
        * {
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
                         'Helvetica Neue', Arial, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            padding: 2rem;
            background: #f5f5f5;
        }
        h1 {
            color: #333;
            margin-bottom: 1.5rem;
        }
        .form-group {
            margin-bottom: 1.25rem;
        }
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 600;
            color: #444;
        }
        input[type="text"],
        textarea {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 1rem;
        }
        textarea {
            resize: vertical;
            min-height: 80px;
        }
        input[type="file"] {
            width: 100%;
            padding: 0.5rem;
            border: 2px dashed #ddd;
            border-radius: 6px;
            background: #fff;
            cursor: pointer;
        }
        input[type="range"] {
            width: 100%;
        }
        .speed-display {
            text-align: center;
            color: #666;
            font-size: 0.9rem;
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
        button:hover {
            background: #357abd;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .result {
            margin-top: 1.5rem;
            padding: 1rem;
            background: #fff;
            border-radius: 6px;
            border: 1px solid #ddd;
            display: none;
        }
        .result.show {
            display: block;
        }
        .result h3 {
            margin: 0 0 1rem 0;
            color: #333;
        }
        audio {
            width: 100%;
            margin-bottom: 0.75rem;
        }
        .download-btn {
            width: 100%;
            padding: 0.75rem;
            background: #28a745;
            margin-top: 0.5rem;
        }
        .download-btn:hover {
            background: #218838;
        }
        .error {
            color: #dc3545;
            padding: 1rem;
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 6px;
            margin-top: 1rem;
            display: none;
        }
        .error.show {
            display: block;
        }
        .loading {
            text-align: center;
            color: #666;
            padding: 1rem;
            display: none;
        }
        .loading.show {
            display: block;
        }
    </style>
</head>
<body>
    <h1>AnotherMe TTS Demo</h1>

    <form id="ttsForm">
        <div class="form-group">
            <label for="audioFile">参照音声ファイル (WAV/MP3)</label>
            <input type="file" id="audioFile" accept=".wav,.mp3" required>
        </div>

        <div class="form-group">
            <label for="refText">参照音声のテキスト</label>
            <input type="text" id="refText" placeholder="参照音声で話している内容" required>
        </div>

        <div class="form-group">
            <label for="inputText">合成するテキスト</label>
            <textarea id="inputText" placeholder="音声合成したいテキストを入力" required></textarea>
        </div>

        <div class="form-group">
            <label for="speed">速度: <span id="speedValue">1.0</span>x</label>
            <input type="range" id="speed" min="0.5" max="2.0" step="0.1" value="1.0">
        </div>

        <button type="submit" id="submitBtn">音声を生成</button>
    </form>

    <div class="loading" id="loading">生成中...</div>

    <div class="error" id="error"></div>

    <div class="result" id="result">
        <h3>生成結果</h3>
        <audio id="audioPlayer" controls></audio>
        <button class="download-btn" id="downloadBtn">ダウンロード</button>
    </div>

    <script>
        const form = document.getElementById('ttsForm');
        const speedInput = document.getElementById('speed');
        const speedValue = document.getElementById('speedValue');
        const submitBtn = document.getElementById('submitBtn');
        const loading = document.getElementById('loading');
        const errorDiv = document.getElementById('error');
        const resultDiv = document.getElementById('result');
        const audioPlayer = document.getElementById('audioPlayer');
        const downloadBtn = document.getElementById('downloadBtn');

        let audioBlob = null;

        speedInput.addEventListener('input', () => {
            speedValue.textContent = speedInput.value;
        });

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const audioFile = document.getElementById('audioFile').files[0];
            const refText = document.getElementById('refText').value;
            const inputText = document.getElementById('inputText').value;
            const speed = speedInput.value;

            if (!audioFile) {
                showError('参照音声ファイルを選択してください');
                return;
            }

            submitBtn.disabled = true;
            loading.classList.add('show');
            errorDiv.classList.remove('show');
            resultDiv.classList.remove('show');

            try {
                const formData = new FormData();
                formData.append('audio_file', audioFile);
                formData.append('ref_text', refText);
                formData.append('input', inputText);
                formData.append('speed', speed);

                const response = await fetch('/api/tts/voice-clone', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'エラーが発生しました');
                }

                const data = await response.json();
                const audioData = data.audio_data;

                const binaryString = atob(audioData);
                const bytes = new Uint8Array(binaryString.length);
                for (let i = 0; i < binaryString.length; i++) {
                    bytes[i] = binaryString.charCodeAt(i);
                }
                audioBlob = new Blob([bytes], { type: 'audio/wav' });

                const audioUrl = URL.createObjectURL(audioBlob);
                audioPlayer.src = audioUrl;
                resultDiv.classList.add('show');
                audioPlayer.play();

            } catch (err) {
                showError(err.message);
            } finally {
                submitBtn.disabled = false;
                loading.classList.remove('show');
            }
        });

        downloadBtn.addEventListener('click', () => {
            if (!audioBlob) return;

            const url = URL.createObjectURL(audioBlob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'generated_audio.wav';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        });

        function showError(message) {
            errorDiv.textContent = message;
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
    description="音声合成を試すためのデモUIページを表示します。",
)
async def demo_page() -> HTMLResponse:
    """デモUIページを返す"""
    return HTMLResponse(content=DEMO_HTML)
