/**
 * Unit tests for utility functions
 */
import { describe, expect, it } from "vitest";
import { cn } from "./utils";

describe("cn utility", () => {
  it("merges class names correctly", () => {
    const result = cn("px-4", "py-2");
    expect(result).toBe("px-4 py-2");
  });

  it("handles conditional classes", () => {
    const isActive = true;
    const result = cn("base-class", isActive && "active");
    expect(result).toBe("base-class active");
  });

  it("handles falsy values", () => {
    const result = cn("base", false, null, undefined, "end");
    expect(result).toBe("base end");
  });

  it("merges conflicting Tailwind classes correctly", () => {
    // tailwind-merge should keep only the last conflicting class
    const result = cn("px-4", "px-8");
    expect(result).toBe("px-8");
  });

  it("handles arrays of classes", () => {
    const result = cn(["class1", "class2"], "class3");
    expect(result).toBe("class1 class2 class3");
  });

  it("handles empty input", () => {
    const result = cn();
    expect(result).toBe("");
  });
});
