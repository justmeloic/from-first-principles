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

import { SearchBar } from "@/components/Search/SearchBar";
import { SearchFilters } from "@/components/Search/SearchFilters";
import { SearchResults } from "@/components/Search/SearchResults";
import { Button } from "@/components/ui/button";
import { Toaster } from "@/components/ui/toaster";
import { useToast } from "@/hooks/use-toast";
import { getSearchStats, searchContent } from "@/lib/api";
import { cn } from "@/lib/utils";
import {
  SearchQuery,
  SearchResponse,
  SearchResult,
  SearchStats,
} from "@/types";
import { useCallback, useEffect, useRef, useState } from "react";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchStats, setSearchStats] = useState<SearchStats | null>(null);
  const [isStatsLoading, setIsStatsLoading] = useState(true);
  const [showFilters, setShowFilters] = useState(false);
  const [isClearing, setIsClearing] = useState(false);

  // Search parameters
  const [searchType, setSearchType] = useState<
    "semantic" | "keyword" | "hybrid"
  >("semantic");
  const [limit, setLimit] = useState(10);
  const [categoryFilter, setCategoryFilter] = useState<
    "blog" | "engineering" | undefined
  >(undefined);
  const [similarityThreshold, setSimilarityThreshold] = useState(0.5);
  const [caseSensitive, setCaseSensitive] = useState(false);

  // Metadata
  const [totalResults, setTotalResults] = useState(0);
  const [searchTime, setSearchTime] = useState(0);

  const abortController = useRef<AbortController | null>(null);
  const { toast } = useToast();

  // Persist and restore search state
  useEffect(() => {
    const storedQuery = localStorage.getItem("searchQuery");
    const storedResults = localStorage.getItem("searchResults");
    const storedTotalResults = localStorage.getItem("searchTotalResults");
    const storedSearchTime = localStorage.getItem("searchTime");
    const storedSearchType = localStorage.getItem("searchType");
    const storedLimit = localStorage.getItem("searchLimit");
    const storedCategoryFilter = localStorage.getItem("searchCategoryFilter");
    const storedSimilarityThreshold = localStorage.getItem(
      "searchSimilarityThreshold"
    );
    const storedCaseSensitive = localStorage.getItem("searchCaseSensitive");
    const storedShowFilters = localStorage.getItem("searchShowFilters");

    if (storedQuery) {
      setQuery(storedQuery);
    }

    if (storedResults) {
      try {
        const parsedResults = JSON.parse(storedResults);
        setResults(parsedResults);
      } catch (error) {
        console.error("Error parsing stored search results:", error);
      }
    }

    if (storedTotalResults) {
      setTotalResults(parseInt(storedTotalResults, 10) || 0);
    }

    if (storedSearchTime) {
      setSearchTime(parseFloat(storedSearchTime) || 0);
    }

    if (storedSearchType) {
      setSearchType(storedSearchType as "semantic" | "keyword" | "hybrid");
    }

    if (storedLimit) {
      setLimit(parseInt(storedLimit, 10) || 10);
    }

    if (storedCategoryFilter && storedCategoryFilter !== "undefined") {
      setCategoryFilter(storedCategoryFilter as "blog" | "engineering");
    }

    if (storedSimilarityThreshold) {
      setSimilarityThreshold(parseFloat(storedSimilarityThreshold) || 0.5);
    }

    if (storedCaseSensitive) {
      setCaseSensitive(storedCaseSensitive === "true");
    }

    if (storedShowFilters) {
      setShowFilters(storedShowFilters === "true");
    }

    return () => {
      if (abortController.current) {
        abortController.current.abort();
      }
    };
  }, []);

  // Load search stats on component mount
  useEffect(() => {
    const loadStats = async () => {
      try {
        const stats = await getSearchStats();
        setSearchStats(stats);
      } catch (error) {
        console.error("Failed to load search stats:", error);
        toast({
          title: "Warning",
          description: "Failed to load search statistics",
          variant: "destructive",
        });
      } finally {
        setIsStatsLoading(false);
      }
    };

    loadStats();
  }, [toast]);

  // Save search state to localStorage
  useEffect(() => {
    localStorage.setItem("searchQuery", query);
  }, [query]);

  useEffect(() => {
    if (results.length > 0) {
      localStorage.setItem("searchResults", JSON.stringify(results));
    } else {
      localStorage.removeItem("searchResults");
    }
  }, [results]);

  useEffect(() => {
    localStorage.setItem("searchTotalResults", totalResults.toString());
  }, [totalResults]);

  useEffect(() => {
    localStorage.setItem("searchTime", searchTime.toString());
  }, [searchTime]);

  useEffect(() => {
    localStorage.setItem("searchType", searchType);
  }, [searchType]);

  useEffect(() => {
    localStorage.setItem("searchLimit", limit.toString());
  }, [limit]);

  useEffect(() => {
    localStorage.setItem("searchCategoryFilter", categoryFilter || "undefined");
  }, [categoryFilter]);

  useEffect(() => {
    localStorage.setItem(
      "searchSimilarityThreshold",
      similarityThreshold.toString()
    );
  }, [similarityThreshold]);

  useEffect(() => {
    localStorage.setItem("searchCaseSensitive", caseSensitive.toString());
  }, [caseSensitive]);

  useEffect(() => {
    localStorage.setItem("searchShowFilters", showFilters.toString());
  }, [showFilters]);

  const handleSearch = useCallback(async () => {
    if (!query.trim()) {
      toast({
        title: "Invalid Query",
        description: "Please enter a search query",
        variant: "destructive",
      });
      return;
    }

    // Cancel any existing request
    if (abortController.current) {
      abortController.current.abort();
    }

    abortController.current = new AbortController();
    setIsLoading(true);

    try {
      const searchQuery: SearchQuery = {
        query: query.trim(),
        search_type: searchType,
        limit,
        ...(categoryFilter && { category_filter: categoryFilter }),
        similarity_threshold: similarityThreshold,
        case_sensitive: caseSensitive,
      };

      const response: SearchResponse = await searchContent(searchQuery, {
        signal: abortController.current.signal,
      });

      setResults(response.results);
      setTotalResults(response.total_results);
      setSearchTime(response.search_time_ms);

      if (response.results.length === 0) {
        toast({
          title: "No Results",
          description:
            "No content found matching your search query. Try adjusting your search terms or filters.",
        });
      }
    } catch (error) {
      if ((error as Error).name === "AbortError") {
        return; // Request was cancelled, don't show error
      }

      console.error("Search failed:", error);
      toast({
        title: "Search Failed",
        description: "An error occurred while searching. Please try again.",
        variant: "destructive",
      });
      setResults([]);
      setTotalResults(0);
      setSearchTime(0);
    } finally {
      setIsLoading(false);
    }
  }, [
    query,
    searchType,
    limit,
    categoryFilter,
    similarityThreshold,
    caseSensitive,
    toast,
  ]);

  const clearSearch = () => {
    setIsClearing(true);
    setQuery("");
    setResults([]);
    setTotalResults(0);
    setSearchTime(0);
    setShowFilters(false);
    // Clear localStorage when manually clearing search
    localStorage.removeItem("searchQuery");
    localStorage.removeItem("searchResults");
    localStorage.removeItem("searchTotalResults");
    localStorage.removeItem("searchTime");
    localStorage.setItem("searchShowFilters", "false");

    // Stop spinning after a short delay
    setTimeout(() => {
      setIsClearing(false);
      toast({
        title: "Search Cleared",
        description: "Search results and query have been cleared.",
        duration: 1500,
        className: "rounded-xl",
      });
    }, 600);
  };

  const resetFilters = () => {
    setSearchType("semantic");
    setLimit(10);
    setCategoryFilter(undefined);
    setSimilarityThreshold(0.5);
    setCaseSensitive(false);
    // Update filter-related localStorage when resetting
    localStorage.setItem("searchType", "semantic");
    localStorage.setItem("searchLimit", "10");
    localStorage.setItem("searchCategoryFilter", "undefined");
    localStorage.setItem("searchSimilarityThreshold", "0.5");
    localStorage.setItem("searchCaseSensitive", "false");
  };

  const toggleFilters = () => {
    setShowFilters(!showFilters);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-black">
      {/* Clear Search Button - fixed position in top left corner */}
      {(results.length > 0 || query.trim()) && (
        <div className="fixed top-24 left-4 z-10">
          <Button
            onClick={clearSearch}
            size="sm"
            className="rounded-full w-10 h-10 p-0 bg-white dark:bg-dark-mode-gray-secondary-bg text-accent dark:text-white/30 hover:text-white dark:hover:text-white hover:bg-accent dark:hover:bg-accent/50 flex items-center justify-center shadow-md hover:shadow-lg transition-all duration-200 border-0"
            title="Reset Search"
            disabled={isClearing}
          >
            <svg
              className={`w-5 h-5 transition-transform duration-600 ease-in-out ${
                isClearing ? "animate-spin" : ""
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
          </Button>
        </div>
      )}

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Dynamic layout based on whether we have results */}
          <div
            className={cn(
              "transition-all duration-1000 ease-in-out transform-gpu",
              results.length > 0 || isLoading
                ? "mt-28" // Slightly lower position when results are shown
                : "mt-32 md:mt-48" // Centered position when no results
            )}
          >
            {/* Search Bar Container with centering */}
            <div
              className={cn(
                "transition-all duration-1000 ease-in-out transform-gpu",
                results.length === 0 && !isLoading
                  ? "flex items-center justify-center min-h-[40vh]" // Center vertically when no results
                  : "" // Normal flow when results exist
              )}
            >
              <div className="w-full space-y-6">
                {/* Search Stats
                <SearchStatsDisplay
                  stats={searchStats}
                  isLoading={isStatsLoading}
                />*/}

                {/* Search Bar */}
                <SearchBar
                  query={query}
                  onQueryChange={setQuery}
                  onSearch={handleSearch}
                  onClearSearch={clearSearch}
                  onToggleFilters={toggleFilters}
                  isLoading={isLoading}
                  showFilters={showFilters}
                  hasResults={results.length > 0}
                />

                {/* Search Filters */}
                <SearchFilters
                  showFilters={showFilters}
                  searchType={searchType}
                  onSearchTypeChange={setSearchType}
                  categoryFilter={categoryFilter}
                  onCategoryFilterChange={setCategoryFilter}
                  limit={limit}
                  onLimitChange={setLimit}
                  similarityThreshold={similarityThreshold}
                  onSimilarityThresholdChange={setSimilarityThreshold}
                  caseSensitive={caseSensitive}
                  onCaseSensitiveChange={setCaseSensitive}
                  onResetFilters={resetFilters}
                />
              </div>
            </div>

            {/* Search Results */}
            <div
              className={cn(
                "transition-all duration-1000 ease-in-out transform-gpu",
                results.length > 0 || isLoading ? "mt-6" : "mt-0"
              )}
            >
              <SearchResults
                results={results}
                totalResults={totalResults}
                searchTime={searchTime}
                searchType={searchType}
                categoryFilter={categoryFilter}
                isLoading={isLoading}
              />
            </div>
          </div>
        </div>
      </div>
      <Toaster />
    </div>
  );
}
