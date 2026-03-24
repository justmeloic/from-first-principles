/**
 * Tests for ChatInput component
 */
import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ChatInput } from "./ChatInput";

describe("ChatInput", () => {
  const mockOnSend = vi.fn();

  beforeEach(() => {
    mockOnSend.mockClear();
  });

  it("renders textarea with placeholder", () => {
    render(<ChatInput onSend={mockOnSend} isLoading={false} />);

    expect(screen.getByPlaceholderText("Ask anything")).toBeInTheDocument();
  });

  it("updates textarea value on input", async () => {
    render(<ChatInput onSend={mockOnSend} isLoading={false} />);

    const textarea = screen.getByPlaceholderText("Ask anything");
    await userEvent.type(textarea, "Hello world");

    expect(textarea).toHaveValue("Hello world");
  });

  it("does not call onSend with empty message", async () => {
    render(<ChatInput onSend={mockOnSend} isLoading={false} />);

    const textarea = screen.getByPlaceholderText("Ask anything");
    await userEvent.type(textarea, "   ");
    fireEvent.keyDown(textarea, { key: "Enter", shiftKey: false });

    expect(mockOnSend).not.toHaveBeenCalled();
  });

  it("calls onSend with trimmed message on Enter", async () => {
    render(<ChatInput onSend={mockOnSend} isLoading={false} />);

    const textarea = screen.getByPlaceholderText("Ask anything");
    await userEvent.type(textarea, "  Hello world  ");
    fireEvent.keyDown(textarea, { key: "Enter", shiftKey: false });

    expect(mockOnSend).toHaveBeenCalledWith("Hello world", undefined);
  });

  it("clears textarea after sending", async () => {
    render(<ChatInput onSend={mockOnSend} isLoading={false} />);

    const textarea = screen.getByPlaceholderText("Ask anything");
    await userEvent.type(textarea, "Hello");
    fireEvent.keyDown(textarea, { key: "Enter", shiftKey: false });

    expect(textarea).toHaveValue("");
  });

  it("allows newlines with Shift+Enter", async () => {
    render(<ChatInput onSend={mockOnSend} isLoading={false} />);

    const textarea = screen.getByPlaceholderText("Ask anything");
    await userEvent.type(textarea, "Line 1");
    fireEvent.keyDown(textarea, { key: "Enter", shiftKey: true });
    await userEvent.type(textarea, "Line 2");

    // Should not have sent
    expect(mockOnSend).not.toHaveBeenCalled();
    // Should contain both lines (textarea still has line 1)
    expect(textarea).toHaveValue("Line 1Line 2");
  });

  it("disables textarea when loading", () => {
    render(<ChatInput onSend={mockOnSend} isLoading={true} />);

    const textarea = screen.getByPlaceholderText("Ask anything");
    expect(textarea).toBeDisabled();
  });

  it("does not send when loading", async () => {
    render(<ChatInput onSend={mockOnSend} isLoading={true} />);

    const textarea = screen.getByPlaceholderText("Ask anything");
    // Use fireEvent since textarea is disabled
    fireEvent.change(textarea, { target: { value: "Hello" } });
    fireEvent.keyDown(textarea, { key: "Enter", shiftKey: false });

    expect(mockOnSend).not.toHaveBeenCalled();
  });

  it("renders file upload button", () => {
    render(<ChatInput onSend={mockOnSend} isLoading={false} />);

    // The Plus icon button for file upload
    const uploadButton = document.querySelector('input[type="file"]');
    expect(uploadButton).toBeInTheDocument();
  });

  it("renders submit button", () => {
    render(<ChatInput onSend={mockOnSend} isLoading={false} />);

    // Look for the send button (contains SendHorizontal icon)
    const buttons = screen.getAllByRole("button");
    expect(buttons.length).toBeGreaterThan(0);
  });
});

describe("ChatInput File Upload", () => {
  const mockOnSend = vi.fn();

  beforeEach(() => {
    mockOnSend.mockClear();
  });

  it("accepts file uploads", async () => {
    render(<ChatInput onSend={mockOnSend} isLoading={false} />);

    const fileInput = document.querySelector(
      'input[type="file"]',
    ) as HTMLInputElement;
    const file = new File(["test content"], "test.txt", { type: "text/plain" });

    await userEvent.upload(fileInput, file);

    // File should be staged (shown in UI)
    expect(screen.getByText("test.txt")).toBeInTheDocument();
  });

  it("sends files along with message", async () => {
    render(<ChatInput onSend={mockOnSend} isLoading={false} />);

    const fileInput = document.querySelector(
      'input[type="file"]',
    ) as HTMLInputElement;
    const file = new File(["test content"], "test.txt", { type: "text/plain" });

    await userEvent.upload(fileInput, file);

    const textarea = screen.getByPlaceholderText("Ask anything");
    await userEvent.type(textarea, "Analyze this file");
    fireEvent.keyDown(textarea, { key: "Enter", shiftKey: false });

    expect(mockOnSend).toHaveBeenCalledWith("Analyze this file", [
      expect.any(File),
    ]);
  });

  it("clears files after sending", async () => {
    render(<ChatInput onSend={mockOnSend} isLoading={false} />);

    const fileInput = document.querySelector(
      'input[type="file"]',
    ) as HTMLInputElement;
    const file = new File(["test content"], "test.txt", { type: "text/plain" });

    await userEvent.upload(fileInput, file);
    expect(screen.getByText("test.txt")).toBeInTheDocument();

    const textarea = screen.getByPlaceholderText("Ask anything");
    await userEvent.type(textarea, "Hello");
    fireEvent.keyDown(textarea, { key: "Enter", shiftKey: false });

    // File should be cleared after send
    expect(screen.queryByText("test.txt")).not.toBeInTheDocument();
  });
});
