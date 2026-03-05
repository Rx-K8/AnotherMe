import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { AvatarDisplay } from "./AvatarDisplay"

describe("AvatarDisplay", () => {
  it("shows placeholder when no video and not generating", () => {
    render(<AvatarDisplay videoUrl={null} isGenerating={false} />)
    expect(screen.getByText("ここにアバターを配置")).toBeInTheDocument()
  })

  it("shows loading indicator when generating", () => {
    render(<AvatarDisplay videoUrl={null} isGenerating={true} />)
    expect(screen.getByText("動画生成中...")).toBeInTheDocument()
    expect(screen.queryByText("ここにアバターを配置")).not.toBeInTheDocument()
  })

  it("renders video element when videoUrl is provided", () => {
    render(<AvatarDisplay videoUrl="blob:mock-url" isGenerating={false} />)
    const video = screen.getByTestId("avatar-video") as HTMLVideoElement
    expect(video).toBeInTheDocument()
    expect(video.src).toBe("blob:mock-url")
    expect(video).toHaveAttribute("autoPlay")
    expect(screen.queryByText("ここにアバターを配置")).not.toBeInTheDocument()
  })

  it("shows video even while generating new one", () => {
    render(<AvatarDisplay videoUrl="blob:mock-url" isGenerating={true} />)
    expect(screen.getByTestId("avatar-video")).toBeInTheDocument()
    expect(screen.getByText("動画生成中...")).toBeInTheDocument()
  })
})
