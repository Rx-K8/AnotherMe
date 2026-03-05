import { act, renderHook } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

vi.mock("@/api/lipsyncApi", () => ({
  generateLipsync: vi.fn(),
}))

import { generateLipsync } from "@/api/lipsyncApi"
import { useLipsync } from "./useLipsync"

// Valid base64 test data
const AUDIO_B64 = btoa("test-audio-data")
const VIDEO_B64 = btoa("test-video-data")
const VIDEO_B64_2 = btoa("test-video-data-2")

describe("useLipsync", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(URL, "createObjectURL").mockReturnValue("blob:mock-url")
    vi.spyOn(URL, "revokeObjectURL").mockImplementation(() => {})
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it("returns initial state", () => {
    const { result } = renderHook(() => useLipsync())
    expect(result.current.isGenerating).toBe(false)
    expect(result.current.videoUrl).toBeNull()
    expect(result.current.error).toBeNull()
  })

  it("generates video and sets videoUrl from base64 response", async () => {
    vi.mocked(generateLipsync).mockResolvedValueOnce({
      video_data: VIDEO_B64,
      duration_seconds: 3.0,
      processing_time_ms: 2000,
    })

    const { result } = renderHook(() => useLipsync())
    const videoFile = new File(["video"], "ref.mp4", { type: "video/mp4" })

    await act(async () => {
      await result.current.generate(AUDIO_B64, videoFile)
    })

    expect(generateLipsync).toHaveBeenCalledWith({
      audio: expect.any(Blob),
      video: videoFile,
    })
    expect(URL.createObjectURL).toHaveBeenCalledOnce()
    expect(result.current.videoUrl).toBe("blob:mock-url")
    expect(result.current.isGenerating).toBe(false)
    expect(result.current.error).toBeNull()
  })

  it("accepts optional lipsync params", async () => {
    vi.mocked(generateLipsync).mockResolvedValueOnce({
      video_data: VIDEO_B64,
      duration_seconds: 1,
      processing_time_ms: 100,
    })

    const { result } = renderHook(() => useLipsync())
    const videoFile = new File(["video"], "ref.mp4", { type: "video/mp4" })

    await act(async () => {
      await result.current.generate(AUDIO_B64, videoFile, {
        bbox_shift: 5,
        extra_margin: 20,
        parsing_mode: "face",
      })
    })

    expect(generateLipsync).toHaveBeenCalledWith({
      audio: expect.any(Blob),
      video: videoFile,
      bbox_shift: 5,
      extra_margin: 20,
      parsing_mode: "face",
    })
  })

  it("revokes previous videoUrl when generating new video", async () => {
    vi.mocked(generateLipsync)
      .mockResolvedValueOnce({
        video_data: VIDEO_B64,
        duration_seconds: 1,
        processing_time_ms: 100,
      })
      .mockResolvedValueOnce({
        video_data: VIDEO_B64_2,
        duration_seconds: 2,
        processing_time_ms: 200,
      })

    const { result } = renderHook(() => useLipsync())
    const videoFile = new File(["video"], "ref.mp4", { type: "video/mp4" })

    await act(async () => {
      await result.current.generate(AUDIO_B64, videoFile)
    })
    expect(result.current.videoUrl).toBe("blob:mock-url")

    await act(async () => {
      await result.current.generate(AUDIO_B64, videoFile)
    })

    expect(URL.revokeObjectURL).toHaveBeenCalledWith("blob:mock-url")
  })

  it("clearVideo revokes url and resets state", async () => {
    vi.mocked(generateLipsync).mockResolvedValueOnce({
      video_data: VIDEO_B64,
      duration_seconds: 1,
      processing_time_ms: 100,
    })

    const { result } = renderHook(() => useLipsync())
    const videoFile = new File(["video"], "ref.mp4", { type: "video/mp4" })

    await act(async () => {
      await result.current.generate(AUDIO_B64, videoFile)
    })
    expect(result.current.videoUrl).toBe("blob:mock-url")

    act(() => {
      result.current.clearVideo()
    })

    expect(URL.revokeObjectURL).toHaveBeenCalledWith("blob:mock-url")
    expect(result.current.videoUrl).toBeNull()
  })

  it("sets error on API failure", async () => {
    vi.mocked(generateLipsync).mockRejectedValueOnce(new Error("GPU error"))

    const { result } = renderHook(() => useLipsync())
    const videoFile = new File(["video"], "ref.mp4", { type: "video/mp4" })

    await act(async () => {
      await result.current.generate(AUDIO_B64, videoFile)
    })

    expect(result.current.error).toBe("GPU error")
    expect(result.current.videoUrl).toBeNull()
    expect(result.current.isGenerating).toBe(false)
  })
})
