/**
 * Tests for toast reducer logic
 */
import { describe, expect, it } from "vitest";
import { reducer } from "./use-toast";

// Test the reducer in isolation since it's the core logic
describe("Toast Reducer", () => {
  const createToast = (id: string, title?: string) => ({
    id,
    title,
    open: true,
    onOpenChange: () => {},
  });

  describe("ADD_TOAST", () => {
    it("adds a toast to empty state", () => {
      const initialState = { toasts: [] };
      const newToast = createToast("1", "Hello");

      const result = reducer(initialState, {
        type: "ADD_TOAST",
        toast: newToast,
      });

      expect(result.toasts).toHaveLength(1);
      expect(result.toasts[0].id).toBe("1");
      expect(result.toasts[0].title).toBe("Hello");
    });

    it("adds new toast at the beginning", () => {
      const initialState = { toasts: [createToast("1", "First")] };
      const newToast = createToast("2", "Second");

      const result = reducer(initialState, {
        type: "ADD_TOAST",
        toast: newToast,
      });

      expect(result.toasts).toHaveLength(1); // TOAST_LIMIT is 1
      expect(result.toasts[0].id).toBe("2"); // New toast replaces old
    });

    it("respects TOAST_LIMIT of 1", () => {
      const initialState = { toasts: [createToast("1")] };
      const newToast = createToast("2");

      const result = reducer(initialState, {
        type: "ADD_TOAST",
        toast: newToast,
      });

      expect(result.toasts).toHaveLength(1);
      expect(result.toasts[0].id).toBe("2");
    });
  });

  describe("UPDATE_TOAST", () => {
    it("updates an existing toast", () => {
      const initialState = {
        toasts: [createToast("1", "Original")],
      };

      const result = reducer(initialState, {
        type: "UPDATE_TOAST",
        toast: { id: "1", title: "Updated" },
      });

      expect(result.toasts[0].title).toBe("Updated");
      expect(result.toasts[0].id).toBe("1");
    });

    it("does not affect other toasts", () => {
      // This test would matter if TOAST_LIMIT was > 1
      const initialState = {
        toasts: [createToast("1", "First")],
      };

      const result = reducer(initialState, {
        type: "UPDATE_TOAST",
        toast: { id: "999", title: "Nonexistent" },
      });

      expect(result.toasts[0].title).toBe("First");
    });

    it("preserves other properties when updating", () => {
      const initialState = {
        toasts: [
          {
            ...createToast("1", "Title"),
            description: "Description",
          },
        ],
      };

      const result = reducer(initialState, {
        type: "UPDATE_TOAST",
        toast: { id: "1", title: "New Title" },
      });

      expect(result.toasts[0].title).toBe("New Title");
      expect(result.toasts[0].description).toBe("Description");
    });
  });

  describe("DISMISS_TOAST", () => {
    it("sets open to false for specific toast", () => {
      const initialState = {
        toasts: [{ ...createToast("1"), open: true }],
      };

      const result = reducer(initialState, {
        type: "DISMISS_TOAST",
        toastId: "1",
      });

      expect(result.toasts[0].open).toBe(false);
    });

    it("dismisses all toasts when no id provided", () => {
      const initialState = {
        toasts: [{ ...createToast("1"), open: true }],
      };

      const result = reducer(initialState, {
        type: "DISMISS_TOAST",
        toastId: undefined,
      });

      expect(result.toasts[0].open).toBe(false);
    });
  });

  describe("REMOVE_TOAST", () => {
    it("removes specific toast by id", () => {
      const initialState = {
        toasts: [createToast("1", "Toast 1")],
      };

      const result = reducer(initialState, {
        type: "REMOVE_TOAST",
        toastId: "1",
      });

      expect(result.toasts).toHaveLength(0);
    });

    it("removes all toasts when no id provided", () => {
      const initialState = {
        toasts: [createToast("1")],
      };

      const result = reducer(initialState, {
        type: "REMOVE_TOAST",
        toastId: undefined,
      });

      expect(result.toasts).toHaveLength(0);
    });

    it("does not affect state if toast id not found", () => {
      const initialState = {
        toasts: [createToast("1")],
      };

      const result = reducer(initialState, {
        type: "REMOVE_TOAST",
        toastId: "999",
      });

      expect(result.toasts).toHaveLength(1);
      expect(result.toasts[0].id).toBe("1");
    });
  });

  describe("State Immutability", () => {
    it("returns a new state object on ADD_TOAST", () => {
      const initialState = { toasts: [] };

      const result = reducer(initialState, {
        type: "ADD_TOAST",
        toast: createToast("1"),
      });

      expect(result).not.toBe(initialState);
      expect(result.toasts).not.toBe(initialState.toasts);
    });

    it("returns a new state object on UPDATE_TOAST", () => {
      const initialState = { toasts: [createToast("1")] };

      const result = reducer(initialState, {
        type: "UPDATE_TOAST",
        toast: { id: "1", title: "Updated" },
      });

      expect(result).not.toBe(initialState);
    });
  });
});
