interface AvatarDisplayProps {
  videoUrl: string | null
  isGenerating: boolean
}

export function AvatarDisplay({ videoUrl, isGenerating }: AvatarDisplayProps) {
  return (
    <div className="bg-gray-900 flex-1 flex flex-col items-center justify-center relative">
      {videoUrl ? (
        // biome-ignore lint/a11y/useMediaCaption: リップシンク動画にキャプションは不要
        <video
          data-testid="avatar-video"
          src={videoUrl}
          autoPlay
          className="max-h-full max-w-full object-contain"
        />
      ) : (
        !isGenerating && <p className="text-gray-400">ここにアバターを配置</p>
      )}
      {isGenerating && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-black/60 text-white px-4 py-2 rounded-full text-sm">
          動画生成中...
        </div>
      )}
    </div>
  )
}
