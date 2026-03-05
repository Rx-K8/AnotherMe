import { Button } from "@/components/ui/button"

interface LipsyncSettingsProps {
  videoFile: File | null
  setVideoFile: (file: File | null) => void
  lipsyncEnabled: boolean
  setLipsyncEnabled: (enabled: boolean) => void
  bboxShift: number
  setBboxShift: (value: number) => void
  extraMargin: number
  setExtraMargin: (value: number) => void
  parsingMode: "jaw" | "face"
  setParsingMode: (mode: "jaw" | "face") => void
}

export function LipsyncSettings({
  videoFile,
  setVideoFile,
  lipsyncEnabled,
  setLipsyncEnabled,
  bboxShift,
  setBboxShift,
  extraMargin,
  setExtraMargin,
  parsingMode,
  setParsingMode,
}: LipsyncSettingsProps) {
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (!file.name.match(/\.(mp4|mov|jpg|jpeg|png)$/i)) {
      alert("MP4/MOV/JPG/PNGファイルを選択してください")
      e.target.value = ""
      return
    }

    setVideoFile(file)
  }

  const handleRemoveFile = () => {
    setVideoFile(null)
    setLipsyncEnabled(false)
  }

  const handleToggleLipsync = () => {
    if (!videoFile) {
      alert("参照動画/画像ファイルを設定してください")
      return
    }
    setLipsyncEnabled(!lipsyncEnabled)
  }

  return (
    <div className="flex flex-col gap-3 p-4 bg-gray-50 border-t border-b">
      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="lipsync-enabled"
          checked={lipsyncEnabled}
          onChange={handleToggleLipsync}
          className="h-4 w-4"
        />
        <label htmlFor="lipsync-enabled" className="text-sm font-medium">
          リップシンクを有効化
        </label>
      </div>

      <div className="flex flex-col gap-2">
        <label htmlFor="video-file-input" className="text-sm font-medium">
          参照動画/画像ファイル
        </label>
        {videoFile ? (
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-700 flex-1">{videoFile.name}</span>
            <Button variant="outline" size="sm" onClick={handleRemoveFile}>
              削除
            </Button>
          </div>
        ) : (
          <input
            id="video-file-input"
            type="file"
            accept=".mp4,.mov,.jpg,.jpeg,.png"
            onChange={handleFileChange}
            className="text-sm"
          />
        )}
      </div>

      <div className="flex flex-col gap-2">
        <label htmlFor="parsing-mode" className="text-sm font-medium">
          顔パースモード
        </label>
        <select
          id="parsing-mode"
          value={parsingMode}
          onChange={(e) => setParsingMode(e.target.value as "jaw" | "face")}
          className="text-sm border rounded px-2 py-1"
        >
          <option value="jaw">Jaw（顎）</option>
          <option value="face">Face（顔全体）</option>
        </select>
      </div>

      <div className="flex flex-col gap-2">
        <label htmlFor="bbox-shift" className="text-sm font-medium">
          バウンディングボックスシフト: {bboxShift}
        </label>
        <input
          id="bbox-shift"
          type="range"
          min="-20"
          max="20"
          step="1"
          value={bboxShift}
          onChange={(e) => setBboxShift(Number.parseInt(e.target.value, 10))}
          className="w-full"
        />
      </div>

      <div className="flex flex-col gap-2">
        <label htmlFor="extra-margin" className="text-sm font-medium">
          追加マージン: {extraMargin}
        </label>
        <input
          id="extra-margin"
          type="range"
          min="0"
          max="50"
          step="1"
          value={extraMargin}
          onChange={(e) => setExtraMargin(Number.parseInt(e.target.value, 10))}
          className="w-full"
        />
      </div>
    </div>
  )
}
