import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it, vi } from "vitest"
import { LipsyncSettings } from "./LipsyncSettings"

const defaultProps = {
  videoFile: null as File | null,
  setVideoFile: vi.fn(),
  lipsyncEnabled: false,
  setLipsyncEnabled: vi.fn(),
  bboxShift: 0,
  setBboxShift: vi.fn(),
  extraMargin: 10,
  setExtraMargin: vi.fn(),
  parsingMode: "jaw" as const,
  setParsingMode: vi.fn(),
}

describe("LipsyncSettings", () => {
  it("renders lipsync toggle", () => {
    render(<LipsyncSettings {...defaultProps} />)
    expect(screen.getByLabelText("リップシンクを有効化")).toBeInTheDocument()
  })

  it("renders video file upload input when no file selected", () => {
    render(<LipsyncSettings {...defaultProps} />)
    expect(screen.getByLabelText("参照動画/画像ファイル")).toBeInTheDocument()
  })

  it("shows file name and remove button when file is selected", () => {
    const file = new File(["video"], "avatar.mp4", { type: "video/mp4" })
    render(<LipsyncSettings {...defaultProps} videoFile={file} />)
    expect(screen.getByText("avatar.mp4")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "削除" })).toBeInTheDocument()
  })

  it("calls setVideoFile(null) and disables lipsync when remove clicked", async () => {
    const user = userEvent.setup()
    const setVideoFile = vi.fn()
    const setLipsyncEnabled = vi.fn()
    const file = new File(["video"], "avatar.mp4", { type: "video/mp4" })

    render(
      <LipsyncSettings
        {...defaultProps}
        videoFile={file}
        setVideoFile={setVideoFile}
        setLipsyncEnabled={setLipsyncEnabled}
      />,
    )

    await user.click(screen.getByRole("button", { name: "削除" }))
    expect(setVideoFile).toHaveBeenCalledWith(null)
    expect(setLipsyncEnabled).toHaveBeenCalledWith(false)
  })

  it("renders parsing mode selector", () => {
    render(<LipsyncSettings {...defaultProps} />)
    expect(screen.getByLabelText("顔パースモード")).toBeInTheDocument()
  })

  it("renders bbox_shift slider", () => {
    render(<LipsyncSettings {...defaultProps} />)
    expect(screen.getByLabelText(/バウンディングボックスシフト/)).toBeInTheDocument()
  })

  it("renders extra_margin slider", () => {
    render(<LipsyncSettings {...defaultProps} />)
    expect(screen.getByLabelText(/追加マージン/)).toBeInTheDocument()
  })
})
