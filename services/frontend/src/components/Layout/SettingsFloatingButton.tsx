"use client";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useTheme } from "@/providers/theme-provider";
import { Moon, Settings, Sun } from "lucide-react";
import { useState } from "react";

export function SettingsFloatingButton() {
  const [isExpanded, setIsExpanded] = useState(false);
  const { theme, setTheme } = useTheme();

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  const handleThemeChange = (newTheme: "light" | "dark") => {
    setTheme(newTheme);
    setIsExpanded(false);
  };

  return (
    <div className="fixed bottom-6 left-6 z-30">
      {/* Theme Options - appear above the main button when expanded */}
      <div
        className={cn(
          "flex flex-col gap-2 mb-2 transition-all duration-300 ease-in-out",
          isExpanded
            ? "opacity-100 translate-y-0 pointer-events-auto"
            : "opacity-0 translate-y-4 pointer-events-none"
        )}
      >
        {/* Light Mode Button */}
        <Button
          size="sm"
          onClick={() => handleThemeChange("light")}
          className={cn(
            "h-10 w-10 rounded-full shadow-lg transition-all duration-200",
            theme === "light"
              ? "bg-accent hover:bg-accent/80 text-white"
              : "bg-white dark:bg-dark-mode-gray-secondary-bg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300"
          )}
          aria-label="Light Mode"
        >
          <Sun className="h-4 w-4" />
        </Button>

        {/* Dark Mode Button */}
        <Button
          size="sm"
          onClick={() => handleThemeChange("dark")}
          className={cn(
            "h-10 w-10 rounded-full shadow-lg transition-all duration-200",
            theme === "dark"
              ? "bg-accent hover:bg-accent/80 text-white"
              : "bg-white dark:bg-dark-mode-gray-secondary-bg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300"
          )}
          aria-label="Dark Mode"
        >
          <Moon className="h-4 w-4" />
        </Button>
      </div>

      {/* Main Settings Button */}
      <Button
        size="lg"
        onClick={toggleExpanded}
        className={cn(
          "h-12 w-12 rounded-full shadow-lg hover:shadow-xl transition-all duration-300 border-0 p-0",
          isExpanded
            ? "bg-accent hover:bg-accent/80 text-white rotate-45"
            : "bg-white dark:bg-dark-mode-gray-secondary-bg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300"
        )}
        aria-label="Settings"
      >
        <Settings className="h-5 w-5" />
      </Button>

      {/* Backdrop to close when clicking outside */}
      {isExpanded && (
        <div
          className="fixed inset-0 -z-10"
          onClick={() => setIsExpanded(false)}
        />
      )}
    </div>
  );
}
