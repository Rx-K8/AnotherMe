import { act, renderHook } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

vi.mock("@/api/chatApi", () => ({
  createChatCompletion: vi.fn(),
}))
vi.mock("@/api/ttsApi", () => ({
  voiceClone: vi.fn(),
}))
vi.mock("@/api/lipsyncApi", () => ({
  generateLipsync: vi.fn(),
}))

import { createChatCompletion } from "@/api/chatApi"
import { generateLipsync } from "@/api/lipsyncApi"
import { voiceClone } from "@/api/ttsApi"
import { useChat } from "./useChat"

const AUDIO_B64 = btoa("test-audio")
const VIDEO_B64 = btoa("test-video")

describe("useChat", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(URL, "createObjectURL").mockReturnValue("blob:mock-url")
    vi.spyOn(URL, "revokeObjectURL").mockImplementation(() => {})
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it("sends message and receives AI response", async () => {
    vi.mocked(createChatCompletion).mockResolvedValueOnce({
      id: "resp-1",
      choices: [
        { index: 0, message: { role: "assistant", content: "Hi there!", id: "" } },
      ],
    })

    const { result } = renderHook(() => useChat())

    act(() => {
      result.current.setInputText("Hello")
    })

    await act(async () => {
      await result.current.sendMessage()
    })

    expect(result.current.messages).toHaveLength(2)
    expect(result.current.messages[0].role).toBe("user")
    expect(result.current.messages[1].role).toBe("assistant")
    expect(result.current.messages[1].content).toBe("Hi there!")
  })

  it("triggers TTS only when tts enabled and lipsync disabled", async () => {
    vi.mocked(createChatCompletion).mockResolvedValueOnce({
      id: "resp-1",
      choices: [
        { index: 0, message: { role: "assistant", content: "Hello!", id: "" } },
      ],
    })
    vi.mocked(voiceClone).mockResolvedValueOnce({ audio_data: AUDIO_B64 })

    const ttsAudioFile = new File(["audio"], "ref.wav")

    const { result } = renderHook(() =>
      useChat({
        ttsConfig: {
          audioFile: ttsAudioFile,
          refText: "reference",
          speed: 1.0,
          enabled: true,
        },
        lipsyncConfig: {
          videoFile: null,
          enabled: false,
          bboxShift: 0,
          extraMargin: 10,
          parsingMode: "jaw",
        },
      }),
    )

    act(() => {
      result.current.setInputText("Hi")
    })

    await act(async () => {
      await result.current.sendMessage()
    })

    expect(voiceClone).toHaveBeenCalledOnce()
    expect(generateLipsync).not.toHaveBeenCalled()
  })

  it("triggers TTS then Lipsync pipeline when both enabled", async () => {
    vi.mocked(createChatCompletion).mockResolvedValueOnce({
      id: "resp-1",
      choices: [
        { index: 0, message: { role: "assistant", content: "Hello!", id: "" } },
      ],
    })
    vi.mocked(voiceClone).mockResolvedValueOnce({ audio_data: AUDIO_B64 })
    vi.mocked(generateLipsync).mockResolvedValueOnce({
      video_data: VIDEO_B64,
      duration_seconds: 2.0,
      processing_time_ms: 1500,
    })

    const ttsAudioFile = new File(["audio"], "ref.wav")
    const lipsyncVideoFile = new File(["video"], "ref.mp4")

    const { result } = renderHook(() =>
      useChat({
        ttsConfig: {
          audioFile: ttsAudioFile,
          refText: "reference",
          speed: 1.0,
          enabled: true,
        },
        lipsyncConfig: {
          videoFile: lipsyncVideoFile,
          enabled: true,
          bboxShift: 0,
          extraMargin: 10,
          parsingMode: "jaw",
        },
      }),
    )

    act(() => {
      result.current.setInputText("Hi")
    })

    await act(async () => {
      await result.current.sendMessage()
    })

    expect(voiceClone).toHaveBeenCalledOnce()
    expect(generateLipsync).toHaveBeenCalledOnce()
    expect(generateLipsync).toHaveBeenCalledWith({
      audio: expect.any(Blob),
      video: lipsyncVideoFile,
      bbox_shift: 0,
      extra_margin: 10,
      parsing_mode: "jaw",
    })
    expect(result.current.videoUrl).toBe("blob:mock-url")
  })

  it("does not trigger TTS or Lipsync when both disabled", async () => {
    vi.mocked(createChatCompletion).mockResolvedValueOnce({
      id: "resp-1",
      choices: [{ index: 0, message: { role: "assistant", content: "Hi!", id: "" } }],
    })

    const { result } = renderHook(() => useChat())

    act(() => {
      result.current.setInputText("Hello")
    })

    await act(async () => {
      await result.current.sendMessage()
    })

    expect(voiceClone).not.toHaveBeenCalled()
    expect(generateLipsync).not.toHaveBeenCalled()
  })

  it("exposes lipsync state (videoUrl, isGeneratingVideo)", () => {
    const { result } = renderHook(() => useChat())
    expect(result.current.videoUrl).toBeNull()
    expect(result.current.isGeneratingVideo).toBe(false)
  })
})
