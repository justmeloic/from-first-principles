/**
 * Copyright 2025 Loïc Muhirwa
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

"use client";

import { cn } from "@/lib/utils";
import { Filter, Loader2, Search as SearchIcon } from "lucide-react";
import { useState } from "react";

interface SearchBarProps {
  query: string;
  onQueryChange: (query: string) => void;
  onSearch: () => void;
  onClearSearch: () => void;
  onToggleFilters: () => void;
  isLoading: boolean;
  showFilters: boolean;
  hasResults?: boolean; // Add hasResults prop
}

export function SearchBar({
  query,
  onQueryChange,
  onSearch,
  onClearSearch,
  onToggleFilters,
  isLoading,
  showFilters,
  hasResults = false, // Default to false
}: SearchBarProps) {
  const [isFocused, setIsFocused] = useState(false);

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !isLoading) {
      onSearch();
    }
  };

  return (
    <div
      className={cn(
        "relative mx-auto transition-all duration-1000 ease-in-out",
        "w-full max-w-[95%]", // Mobile: keep current width
        hasResults
          ? "md:max-w-4xl" // Desktop with results: current full width
          : "md:max-w-2xl" // Desktop centered: narrower width
      )}
    >
      {/* Chat-like interface for all screen sizes */}
      <div
        className={cn(
          "relative flex w-full rounded-full border bg-white dark:bg-black dark:border-gray-600 transition-shadow duration-300 ease-in-out",
          "min-h-16",
          isFocused
            ? "shadow-[0_1px_6px_1px_rgba(32,33,36,0.12),0_1px_8px_2px_rgba(32,33,36,0.12),0_1px_12px_3px_rgba(32,33,36,0.2)] dark:shadow-custom-white-input"
            : "shadow-none"
        )}
      >
        {/* Search icon */}
        <div className="flex items-center pl-4">
          <SearchIcon className="h-5 w-5 text-gray-400" />
        </div>

        {/* Input */}
        <input
          type="text"
          placeholder="Search through our knowledge base..."
          value={query}
          onChange={(e) => onQueryChange(e.target.value)}
          onKeyPress={handleKeyPress}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          className="flex-1 bg-transparent px-3 py-4 text-base dark:text-gray-200 outline-none placeholder:text-muted-foreground dark:placeholder:text-gray-500"
          disabled={isLoading}
        />

        {/* Filter button - slides left when search button appears */}
        <div
          className={cn(
            "transition-all duration-300 ease-in-out flex items-end pb-3",
            query.trim() && !isLoading
              ? "transform -translate-x-12" // Slide left when search button appears
              : "transform translate-x-0"
          )}
        >
          <button
            onClick={onToggleFilters}
            className={cn(
              "flex items-center justify-center h-10 w-10 rounded-full mr-3 transition-all duration-200",
              showFilters
                ? "bg-accent text-white shadow-md"
                : "bg-gray-100 dark:bg-dark-mode-gray-secondary-bg text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700"
            )}
          >
            <Filter className="h-5 w-5" />
          </button>
        </div>

        {/* Send/Search button - positioned like in chat */}
        <div
          className={cn(
            "absolute right-3 top-1/2 -translate-y-1/2 transition-all duration-500 ease-in-out",
            query.trim() && !isLoading
              ? "opacity-100 scale-100"
              : "opacity-0 scale-90 pointer-events-none"
          )}
        >
          <button
            onClick={onSearch}
            disabled={!query.trim() || isLoading}
            className={cn(
              "group flex items-center justify-center rounded-full",
              "h-10 w-10",
              "transition-all duration-200 ease-in-out",
              "bg-accent hover:bg-accent/80 dark:bg-accent dark:hover:bg-accent/80",
              "hover:scale-110 active:scale-95",
              "text-white focus:outline-none",
              "shadow-md hover:shadow-lg",
              "transform-gpu"
            )}
          >
            {isLoading ? (
              <Loader2 className="h-5 w-5 text-white animate-spin" />
            ) : (
              <SearchIcon className="h-5 w-5 text-white group-hover:translate-x-0.5 transition-transform duration-150 ease-in-out" />
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
