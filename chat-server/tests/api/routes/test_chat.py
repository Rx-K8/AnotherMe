import json

from httpx import AsyncClient


class TestChatCompletionNonStreaming:
    async def test_success(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/chat/completions",
            json={
                "messages": [{"role": "user", "content": "こんにちは"}],
                "stream": False,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["object"] == "chat.completion"
        assert len(data["choices"]) == 1
        assert data["choices"][0]["message"]["role"] == "assistant"
        assert len(data["choices"][0]["message"]["content"]) > 0

    async def test_with_temperature(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/chat/completions",
            json={
                "messages": [{"role": "user", "content": "テスト"}],
                "temperature": 0.5,
            },
        )
        assert response.status_code == 200

    async def test_with_max_new_tokens(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/chat/completions",
            json={
                "messages": [{"role": "user", "content": "テスト"}],
                "max_new_tokens": 100,
            },
        )
        assert response.status_code == 200

    async def test_multiple_messages(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/chat/completions",
            json={
                "messages": [
                    {"role": "system", "content": "あなたはAIアシスタントです。"},
                    {"role": "user", "content": "こんにちは"},
                    {"role": "assistant", "content": "こんにちは！"},
                    {"role": "user", "content": "元気ですか？"},
                ],
            },
        )
        assert response.status_code == 200


class TestChatCompletionStreaming:
    async def test_streaming_response(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/chat/completions",
            json={
                "messages": [{"role": "user", "content": "テスト"}],
                "stream": True,
            },
        )
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")

    async def test_streaming_sse_format(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/chat/completions",
            json={
                "messages": [{"role": "user", "content": "テスト"}],
                "stream": True,
            },
        )
        text = response.text
        lines = [line for line in text.split("\n") if line.startswith("data:")]
        assert len(lines) >= 2  # 少なくとも1チャンク + [DONE]
        assert lines[-1] == "data: [DONE]"

    async def test_streaming_chunk_structure(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/chat/completions",
            json={
                "messages": [{"role": "user", "content": "テスト"}],
                "stream": True,
            },
        )
        text = response.text
        data_lines = [
            line[6:] for line in text.split("\n") if line.startswith("data:") and line.strip() != "data: [DONE]"
        ]
        assert len(data_lines) > 0
        first_chunk = json.loads(data_lines[0])
        assert first_chunk["object"] == "chat.completion.chunk"
        assert "choices" in first_chunk


class TestChatCompletionValidation:
    async def test_reject_empty_messages(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/chat/completions",
            json={"messages": []},
        )
        assert response.status_code == 422

    async def test_reject_empty_content(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/chat/completions",
            json={"messages": [{"role": "user", "content": ""}]},
        )
        assert response.status_code == 422

    async def test_reject_temperature_out_of_range(
        self, client: AsyncClient
    ) -> None:
        response = await client.post(
            "/api/chat/completions",
            json={
                "messages": [{"role": "user", "content": "テスト"}],
                "temperature": 2.0,
            },
        )
        assert response.status_code == 422

    async def test_reject_invalid_role(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/chat/completions",
            json={"messages": [{"role": "invalid", "content": "テスト"}]},
        )
        assert response.status_code == 422
