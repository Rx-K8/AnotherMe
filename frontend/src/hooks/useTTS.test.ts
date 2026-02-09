import { act, renderHook } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

vi.mock("@/api/ttsApi", () => ({
  voiceClone: vi.fn(),
}))

import { voiceClone } from "@/api/ttsApi"
import { useTTS } from "./useTTS"

describe("useTTS", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it("returns initial state", () => {
    const { result } = renderHook(() => useTTS())
    expect(result.current.isGenerating).toBe(false)
    expect(result.current.error).toBeNull()
  })

  it("generateAudio returns base64 audio data", async () => {
    vi.mocked(voiceClone).mockResolvedValueOnce({
      audio_data: "base64audiodata",
    })

    const { result } = renderHook(() => useTTS())

    let audioData: string | undefined
    await act(async () => {
      audioData = await result.current.generateAudio("hello", {
        audioFile: new File(["audio"], "ref.wav", { type: "audio/wav" }),
        refText: "reference text",
        speed: 1.0,
      })
    })

    expect(audioData).toBe("base64audiodata")
    expect(voiceClone).toHaveBeenCalledWith({
      audio_file: expect.any(File),
      input: "hello",
      ref_text: "reference text",
      speed: 1.0,
    })
    expect(result.current.isGenerating).toBe(false)
    expect(result.current.error).toBeNull()
  })

  it("sets isGenerating during API call", async () => {
    let resolvePromise: ((v: { audio_data: string }) => void) | undefined
    vi.mocked(voiceClone).mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          resolvePromise = resolve
        }),
    )

    const { result } = renderHook(() => useTTS())

    let promise: Promise<string> | undefined
    act(() => {
      promise = result.current.generateAudio("hello", {
        audioFile: new File(["audio"], "ref.wav"),
        refText: "ref",
      })
    })

    expect(result.current.isGenerating).toBe(true)

    await act(async () => {
      resolvePromise?.({ audio_data: "data" })
      await promise
    })

    expect(result.current.isGenerating).toBe(false)
  })

  it("sets error on failure", async () => {
    vi.mocked(voiceClone).mockRejectedValueOnce(new Error("API failed"))

    const { result } = renderHook(() => useTTS())

    await act(async () => {
      await expect(
        result.current.generateAudio("hello", {
          audioFile: new File(["audio"], "ref.wav"),
          refText: "ref",
        }),
      ).rejects.toThrow("API failed")
    })

    expect(result.current.error).toBe("API failed")
    expect(result.current.isGenerating).toBe(false)
  })
})
