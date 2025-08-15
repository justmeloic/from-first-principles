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

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { SearchResult } from "@/types";
import { SearchResultCard } from "./SearchResultCard";

interface SearchResultsProps {
  results: SearchResult[];
  totalResults: number;
  searchTime: number;
  searchType: string;
  categoryFilter?: string;
  isLoading: boolean;
}

export function SearchResults({
  results,
  totalResults,
  searchTime,
  searchType,
  categoryFilter,
  isLoading,
}: SearchResultsProps) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-3 w-1/2" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-3 w-full mb-2" />
              <Skeleton className="h-3 w-full mb-2" />
              <Skeleton className="h-3 w-2/3" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (results.length === 0 && totalResults === 0) {
    return null;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-600 dark:text-gray-300">
          {totalResults > 0 && (
            <>
              Found {totalResults} result{totalResults !== 1 ? "s" : ""} in{" "}
              {searchTime.toFixed(1)}ms
            </>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="text-xs">
            {searchType}
          </Badge>
          {categoryFilter && (
            <Badge variant="outline" className="text-xs">
              {categoryFilter}
            </Badge>
          )}
        </div>
      </div>

      <div className="space-y-4">
        {results.map((result, index) => (
          <SearchResultCard key={`${result.slug}-${index}`} result={result} />
        ))}
      </div>
    </div>
  );
}
