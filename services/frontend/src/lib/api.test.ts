/**
 * Tests for API utilities
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key];
    }),
    clear: vi.fn(() => {
      store = {};
    }),
  };
})();

Object.defineProperty(global, "localStorage", { value: localStorageMock });

// Import after mocking
import {
    hasExistingSession,
    startNewSession,
} from "./api";

describe("Session Management", () => {
  beforeEach(() => {
    localStorageMock.clear();
    vi.clearAllMocks();
  });

  describe("hasExistingSession", () => {
    it("returns false when no session exists", () => {
      expect(hasExistingSession()).toBe(false);
    });

    it("returns true when session exists", () => {
      localStorageMock.setItem("agentChatSessionId", "test-session-123");
      expect(hasExistingSession()).toBe(true);
    });
  });

  describe("startNewSession", () => {
    it("clears all session-related localStorage items", () => {
      // Set up initial state
      localStorageMock.setItem("agentChatSessionId", "old-session");
      localStorageMock.setItem("agentChatHistory", "[]");
      localStorageMock.setItem("agentChatReferences", "[]");
      localStorageMock.setItem("agentIsFirstPrompt", "true");

      startNewSession();

      expect(localStorageMock.removeItem).toHaveBeenCalledWith(
        "agentChatSessionId"
      );
      expect(localStorageMock.removeItem).toHaveBeenCalledWith(
        "agentChatHistory"
      );
      expect(localStorageMock.removeItem).toHaveBeenCalledWith(
        "agentChatReferences"
      );
      expect(localStorageMock.removeItem).toHaveBeenCalledWith(
        "agentIsFirstPrompt"
      );
    });
  });
});

describe("sendMessage", () => {
  beforeEach(() => {
    localStorageMock.clear();
    vi.clearAllMocks();
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("constructs FormData with message text", async () => {
    const { sendMessage } = await import("./api");

    const mockResponse = {
      ok: true,
      json: vi.fn().mockResolvedValue({ response: "Hello" }),
      headers: new Headers({ "x-session-id": "new-session" }),
    };
    (global.fetch as any).mockResolvedValue(mockResponse);

    await sendMessage("Hello world");

    expect(global.fetch).toHaveBeenCalledTimes(1);
    const [url, options] = (global.fetch as any).mock.calls[0];
    expect(url).toContain("/api/v1/root_agent/");
    expect(options.method).toBe("POST");
    expect(options.body).toBeInstanceOf(FormData);
  });

  it("includes model in FormData when provided", async () => {
    const { sendMessage } = await import("./api");

    const mockResponse = {
      ok: true,
      json: vi.fn().mockResolvedValue({ response: "Hello" }),
      headers: new Headers({ "x-session-id": "session" }),
    };
    (global.fetch as any).mockResolvedValue(mockResponse);

    await sendMessage("Hello", undefined, { model: "gpt-4" });

    const [, options] = (global.fetch as any).mock.calls[0];
    const formData = options.body as FormData;
    expect(formData.get("model")).toBe("gpt-4");
  });

  it("throws error on non-ok response", async () => {
    const { sendMessage } = await import("./api");

    const mockResponse = {
      ok: false,
      status: 500,
    };
    (global.fetch as any).mockResolvedValue(mockResponse);

    await expect(sendMessage("Hello")).rejects.toThrow("HTTP error! status: 500");
  });

  it("stores new session ID from response headers", async () => {
    const { sendMessage } = await import("./api");

    const mockResponse = {
      ok: true,
      json: vi.fn().mockResolvedValue({ response: "Hello" }),
      headers: new Headers({ "x-session-id": "new-session-456" }),
    };
    (global.fetch as any).mockResolvedValue(mockResponse);

    await sendMessage("Hello");

    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      "agentChatSessionId",
      "new-session-456"
    );
  });

  it("clears chat data when session ID changes", async () => {
    const { sendMessage } = await import("./api");

    // Set existing session
    localStorageMock.setItem("agentChatSessionId", "old-session-123");

    const mockResponse = {
      ok: true,
      json: vi.fn().mockResolvedValue({ response: "Hello" }),
      headers: new Headers({ "x-session-id": "new-session-456" }),
    };
    (global.fetch as any).mockResolvedValue(mockResponse);

    await sendMessage("Hello");

    expect(localStorageMock.removeItem).toHaveBeenCalledWith("agentChatHistory");
    expect(localStorageMock.removeItem).toHaveBeenCalledWith("agentChatReferences");
  });
});

describe("SSE Parsing Logic", () => {
  // Test SSE parsing helper logic in isolation
  it("parses SSE data from line format", () => {
    const line = 'data: {"type":"token","content":"Hello"}';

    if (line.startsWith("data: ")) {
      const data = JSON.parse(line.slice(6));
      expect(data.type).toBe("token");
      expect(data.content).toBe("Hello");
    }
  });

  it("handles SSE buffer splitting correctly", () => {
    const buffer = 'data: {"type":"token"}\n\ndata: {"type":"done"}';
    const lines = buffer.split("\n\n");

    expect(lines).toHaveLength(2);
    expect(lines[0]).toBe('data: {"type":"token"}');
    expect(lines[1]).toBe('data: {"type":"done"}');
  });

  it("keeps partial message in buffer", () => {
    const buffer = 'data: {"type":"token"}\n\ndata: {"type":"par';
    const lines = buffer.split("\n\n");
    const remaining = lines.pop();

    expect(remaining).toBe('data: {"type":"par');
    expect(lines).toHaveLength(1);
  });
});
