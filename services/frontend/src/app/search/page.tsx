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
    setQuery("");
    setResults([]);
    setTotalResults(0);
    setSearchTime(0);
  };

  const resetFilters = () => {
    setSearchType("semantic");
    setLimit(10);
    setCategoryFilter(undefined);
    setSimilarityThreshold(0.5);
    setCaseSensitive(false);
  };

  const toggleFilters = () => {
    setShowFilters(!showFilters);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-black">
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
    </div>
  );
}
