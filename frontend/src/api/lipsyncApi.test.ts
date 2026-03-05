import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { generateLipsync } from "./lipsyncApi"

const MOCK_BASE_URL = "http://localhost:8002"

describe("generateLipsync", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn())
    vi.stubEnv("VITE_LIPSYNC_API_BASE_URL", MOCK_BASE_URL)
  })

  afterEach(() => {
    vi.restoreAllMocks()
    vi.unstubAllEnvs()
  })

  it("sends FormData with audio, video and default params", async () => {
    const mockResponse = {
      video_data: "base64video",
      duration_seconds: 2.5,
      processing_time_ms: 1200,
    }
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify(mockResponse), { status: 200 }),
    )

    const audioBlob = new Blob(["audio"], { type: "audio/wav" })
    const videoFile = new File(["video"], "ref.mp4", { type: "video/mp4" })

    const result = await generateLipsync({
      audio: audioBlob,
      video: videoFile,
    })

    expect(fetch).toHaveBeenCalledOnce()
    const [url, options] = vi.mocked(fetch).mock.calls[0]
    expect(url).toBe(`${MOCK_BASE_URL}/api/lipsync/generate`)
    expect(options?.method).toBe("POST")

    const body = options?.body as FormData
    expect(body.get("audio_file")).toBeInstanceOf(Blob)
    expect(body.get("video_file")).toBeInstanceOf(File)
    expect(body.get("bbox_shift")).toBe("0")
    expect(body.get("extra_margin")).toBe("10")
    expect(body.get("parsing_mode")).toBe("jaw")

    expect(result).toEqual(mockResponse)
  })

  it("sends custom params when provided", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          video_data: "x",
          duration_seconds: 1,
          processing_time_ms: 100,
        }),
        { status: 200 },
      ),
    )

    const audioBlob = new Blob(["audio"], { type: "audio/wav" })
    const videoFile = new File(["video"], "ref.mp4", { type: "video/mp4" })

    await generateLipsync({
      audio: audioBlob,
      video: videoFile,
      bbox_shift: 5,
      extra_margin: 20,
      parsing_mode: "face",
    })

    const body = vi.mocked(fetch).mock.calls[0][1]?.body as FormData
    expect(body.get("bbox_shift")).toBe("5")
    expect(body.get("extra_margin")).toBe("20")
    expect(body.get("parsing_mode")).toBe("face")
  })

  it("throws on API error response", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ error: "Invalid file", detail: "bad format" }), {
        status: 400,
      }),
    )

    const audioBlob = new Blob(["audio"], { type: "audio/wav" })
    const videoFile = new File(["video"], "ref.mp4", { type: "video/mp4" })

    await expect(
      generateLipsync({ audio: audioBlob, video: videoFile }),
    ).rejects.toThrow("Invalid file: bad format")
  })

  it("throws with error only when detail is missing", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ error: "Server error" }), { status: 500 }),
    )

    const audioBlob = new Blob(["audio"], { type: "audio/wav" })
    const videoFile = new File(["video"], "ref.mp4", { type: "video/mp4" })

    await expect(
      generateLipsync({ audio: audioBlob, video: videoFile }),
    ).rejects.toThrow("Server error")
  })
})
