/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_USE_MOCK_API: string
  readonly VITE_CHAT_API_BASE_URL: string
  readonly VITE_TTS_API_BASE_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
