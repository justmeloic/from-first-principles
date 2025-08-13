"use client";

import { useTheme } from "@/providers/theme-provider";
import { Button } from "@/components/ui/button";
import { Sun, Moon } from "lucide-react";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <div className="fixed top-4 right-2 z-50 flex items-center">
      <span className="mr-3 text-[10px] text-gray-400 dark:text-gray-50 hidden md:inline">
        {theme === "dark" ? "Dark Mode" : "Light Mode"}
      </span>
      {/* Desktop toggle */}
      <button
        onClick={() => setTheme(theme === "light" ? "dark" : "light")}
        className="mr-3 relative inline-block w-[40px] h-[24px] hidden md:inline-block"
      >
        <div
          className={`absolute inset-0 rounded-full cursor-pointer transition-colors duration-300 ${
            theme === "dark" ? "bg-accent" : "bg-gray-300"
          }`}
        >
          <div
            className={`absolute rounded-full w-[19px] h-[18px] transition-transform duration-300 left-[2.2px] top-[2.5px] bg-white ${
              theme === "dark" ? "translate-x-[16px]" : "translate-x-[1px]"
            }`}
          />
        </div>
      </button>
      {/* Mobile toggle */}
      <Button
        variant="ghost"
        size="icon"
        onClick={() => setTheme(theme === "light" ? "dark" : "light")}
        className="md:hidden h-12 w-12 p-2 rounded-full bg-transparent transition-colors [@media(hover:hover)]:hover:bg-accent [@media(hover:hover)]:dark:hover:text-black"
      >
        {theme === "dark" ? (
          <Sun className="h-10 w-10 fill-current  hover:text-accent [@media(hover:hover)]:dark:hover:text-white" />
        ) : (
          <Moon className="h-10 w-10 fill-current text-black dark:text-slate-200" />
        )}
      </Button>
    </div>
  );
}
