import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"

interface TTSSettingsProps {
  audioFile: File | null
  setAudioFile: (file: File | null) => void
  refText: string
  setRefText: (text: string) => void
  speed: number
  setSpeed: (speed: number) => void
  ttsEnabled: boolean
  setTtsEnabled: (enabled: boolean) => void
}

export function TTSSettings({
  audioFile,
  setAudioFile,
  refText,
  setRefText,
  speed,
  setSpeed,
  ttsEnabled,
  setTtsEnabled,
}: TTSSettingsProps) {
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (!file.name.match(/\.(wav|mp3)$/i)) {
      alert("WAVまたはMP3ファイルを選択してください")
      e.target.value = ""
      return
    }

    setAudioFile(file)
  }

  const handleRemoveFile = () => {
    setAudioFile(null)
    setTtsEnabled(false)
  }

  const handleToggleTTS = () => {
    if (!audioFile || !refText.trim()) {
      alert("参照音声ファイルとテキスト書き起こしを設定してください")
      return
    }
    setTtsEnabled(!ttsEnabled)
  }

  return (
    <div className="flex flex-col gap-3 p-4 bg-gray-50 border-t border-b">
      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="tts-enabled"
          checked={ttsEnabled}
          onChange={handleToggleTTS}
          className="h-4 w-4"
        />
        <label htmlFor="tts-enabled" className="text-sm font-medium">
          TTS（音声合成）を有効化
        </label>
      </div>

      {!audioFile && !refText && (
        <div className="text-sm text-gray-600 bg-blue-50 p-2 rounded">
          TTSを使用するには、参照音声ファイルとその書き起こしテキストを設定してください
        </div>
      )}

      <div className="flex flex-col gap-2">
        <label className="text-sm font-medium">参照音声ファイル</label>
        {audioFile ? (
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-700 flex-1">{audioFile.name}</span>
            <Button variant="outline" size="sm" onClick={handleRemoveFile}>
              削除
            </Button>
          </div>
        ) : (
          <input
            type="file"
            accept=".wav,.mp3"
            onChange={handleFileChange}
            className="text-sm"
          />
        )}
      </div>

      <div className="flex flex-col gap-2">
        <label className="text-sm font-medium">参照音声の書き起こし</label>
        <Textarea
          placeholder="参照音声のテキスト書き起こしを入力してください"
          value={refText}
          onChange={(e) => setRefText(e.target.value)}
          className="min-h-[60px]"
        />
      </div>

      <div className="flex flex-col gap-2">
        <label className="text-sm font-medium">再生速度: {speed.toFixed(1)}x</label>
        <input
          type="range"
          min="0.5"
          max="2.0"
          step="0.1"
          value={speed}
          onChange={(e) => setSpeed(parseFloat(e.target.value))}
          className="w-full"
        />
      </div>
    </div>
  )
}
