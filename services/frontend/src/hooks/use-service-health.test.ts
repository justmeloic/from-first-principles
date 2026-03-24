/**
 * Tests for useServiceHealth hook
 */
import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { useServiceHealth } from "./use-service-health";

// Helper to flush promises
const flushPromises = () => new Promise((resolve) => setTimeout(resolve, 0));

describe("useServiceHealth", () => {
  afterEach(() => {
    vi.clearAllMocks();
    vi.useRealTimers();
  });

  it("starts with 'checking' status", () => {
    const healthCheck = vi.fn().mockResolvedValue(undefined);
    const { result } = renderHook(() => useServiceHealth(healthCheck));

    expect(result.current.status).toBe("checking");
  });

  it("sets status to 'available' when health check succeeds", async () => {
    const healthCheck = vi.fn().mockResolvedValue(undefined);
    const { result } = renderHook(() => useServiceHealth(healthCheck));

    await waitFor(() => {
      expect(result.current.status).toBe("available");
    });
  });

  it("sets status to 'unavailable' when health check fails", async () => {
    const healthCheck = vi.fn().mockRejectedValue(new Error("Service down"));
    const { result } = renderHook(() => useServiceHealth(healthCheck));

    await waitFor(() => {
      expect(result.current.status).toBe("unavailable");
    });
  });

  it("calls health check immediately on mount", () => {
    const healthCheck = vi.fn().mockResolvedValue(undefined);
    renderHook(() => useServiceHealth(healthCheck));

    expect(healthCheck).toHaveBeenCalledTimes(1);
  });

  it("calls health check at specified interval", async () => {
    vi.useFakeTimers();
    const healthCheck = vi.fn().mockResolvedValue(undefined);
    const interval = 5000; // 5 seconds

    renderHook(() => useServiceHealth(healthCheck, interval));

    // Initial call
    expect(healthCheck).toHaveBeenCalledTimes(1);

    // Advance timer by interval
    await act(async () => {
      vi.advanceTimersByTime(interval);
    });

    expect(healthCheck).toHaveBeenCalledTimes(2);

    // Advance again
    await act(async () => {
      vi.advanceTimersByTime(interval);
    });

    expect(healthCheck).toHaveBeenCalledTimes(3);
  });

  it("uses default interval of 120 seconds", async () => {
    vi.useFakeTimers();
    const healthCheck = vi.fn().mockResolvedValue(undefined);

    renderHook(() => useServiceHealth(healthCheck));

    expect(healthCheck).toHaveBeenCalledTimes(1);

    // Advance by less than default interval
    await act(async () => {
      vi.advanceTimersByTime(60000); // 60 seconds
    });

    expect(healthCheck).toHaveBeenCalledTimes(1);

    // Advance to complete the default interval
    await act(async () => {
      vi.advanceTimersByTime(60000); // Another 60 seconds = 120 total
    });

    expect(healthCheck).toHaveBeenCalledTimes(2);
  });

  it("provides a retry function that triggers immediate health check", async () => {
    const healthCheck = vi.fn().mockResolvedValue(undefined);
    const { result } = renderHook(() => useServiceHealth(healthCheck));

    // Wait for initial check
    await waitFor(() => {
      expect(result.current.status).toBe("available");
    });

    expect(healthCheck).toHaveBeenCalledTimes(1);

    // Call retry
    await act(async () => {
      await result.current.retry();
    });

    expect(healthCheck).toHaveBeenCalledTimes(2);
  });

  it("cleans up interval on unmount", async () => {
    vi.useFakeTimers();
    const healthCheck = vi.fn().mockResolvedValue(undefined);
    const interval = 5000;

    const { unmount } = renderHook(() =>
      useServiceHealth(healthCheck, interval)
    );

    expect(healthCheck).toHaveBeenCalledTimes(1);

    unmount();

    // Advance timer - should not trigger more calls
    await act(async () => {
      vi.advanceTimersByTime(interval * 3);
    });

    // Still only the initial call
    expect(healthCheck).toHaveBeenCalledTimes(1);
  });

  it("updates status when service recovers after retry", async () => {
    const healthCheck = vi
      .fn()
      .mockRejectedValueOnce(new Error("Down"))
      .mockResolvedValueOnce(undefined);

    const { result } = renderHook(() => useServiceHealth(healthCheck, 120000));

    // Initial check fails
    await waitFor(() => {
      expect(result.current.status).toBe("unavailable");
    });

    // Manual retry triggers recovery
    await act(async () => {
      await result.current.retry();
    });

    // Service recovered
    await waitFor(() => {
      expect(result.current.status).toBe("available");
    });
  });
});
