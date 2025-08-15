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

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Collapsible, CollapsibleContent } from "@/components/ui/collapsible";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";

interface SearchFiltersProps {
  showFilters: boolean;
  searchType: "semantic" | "keyword" | "hybrid";
  onSearchTypeChange: (type: "semantic" | "keyword" | "hybrid") => void;
  categoryFilter: "blog" | "engineering" | undefined;
  onCategoryFilterChange: (
    category: "blog" | "engineering" | undefined
  ) => void;
  limit: number;
  onLimitChange: (limit: number) => void;
  similarityThreshold: number;
  onSimilarityThresholdChange: (threshold: number) => void;
  caseSensitive: boolean;
  onCaseSensitiveChange: (sensitive: boolean) => void;
  onResetFilters: () => void;
}

export function SearchFilters({
  showFilters,
  searchType,
  onSearchTypeChange,
  categoryFilter,
  onCategoryFilterChange,
  limit,
  onLimitChange,
  similarityThreshold,
  onSimilarityThresholdChange,
  caseSensitive,
  onCaseSensitiveChange,
  onResetFilters,
}: SearchFiltersProps) {
  return (
    <Collapsible open={showFilters}>
      <CollapsibleContent>
        <Card className="shadow-2xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-950 rounded-3xl">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium text-gray-900 dark:text-white">
                Search Filters
              </CardTitle>
              <Button
                variant="ghost"
                size="sm"
                onClick={onResetFilters}
                className="text-accent hover:text-accent hover:bg-accent/10 rounded-2xl"
              >
                Reset
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Search Type */}
              <div className="space-y-2">
                <Label
                  htmlFor="search-type"
                  className="text-xs font-medium text-gray-700 dark:text-gray-300"
                >
                  Search Type
                </Label>
                <Select value={searchType} onValueChange={onSearchTypeChange}>
                  <SelectTrigger
                    id="search-type"
                    className="rounded-2xl border border-gray-200 dark:border-gray-700"
                  >
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="rounded-2xl">
                    <SelectItem className="rounded-xl" value="semantic">
                      Semantic
                    </SelectItem>
                    <SelectItem className="rounded-xl" value="keyword">
                      Keyword
                    </SelectItem>
                    <SelectItem className="rounded-xl" value="hybrid">
                      Hybrid
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Category Filter */}
              <div className="space-y-2">
                <Label
                  htmlFor="category"
                  className="text-xs font-medium text-gray-700 dark:text-gray-300"
                >
                  Category
                </Label>
                <Select
                  value={categoryFilter || "all"}
                  onValueChange={(value) =>
                    onCategoryFilterChange(
                      value === "all"
                        ? undefined
                        : (value as "blog" | "engineering")
                    )
                  }
                >
                  <SelectTrigger
                    id="category"
                    className="rounded-2xl border border-gray-200 dark:border-gray-700"
                  >
                    <SelectValue placeholder="All categories" />
                  </SelectTrigger>
                  <SelectContent className="rounded-2xl">
                    <SelectItem className="rounded-xl" value="all">
                      All categories
                    </SelectItem>
                    <SelectItem className="rounded-xl" value="blog">
                      Blog
                    </SelectItem>
                    <SelectItem className="rounded-xl" value="engineering">
                      Engineering
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Results Limit */}
              <div className="space-y-2">
                <Label
                  htmlFor="limit"
                  className="text-xs font-medium text-gray-700 dark:text-gray-300"
                >
                  Results Limit
                </Label>
                <Select
                  value={limit.toString()}
                  onValueChange={(value) => onLimitChange(parseInt(value))}
                >
                  <SelectTrigger
                    id="limit"
                    className="rounded-2xl border border-gray-200 dark:border-gray-700"
                  >
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="rounded-2xl">
                    <SelectItem className="rounded-xl" value="5">
                      5 results
                    </SelectItem>
                    <SelectItem className="rounded-xl" value="10">
                      10 results
                    </SelectItem>
                    <SelectItem className="rounded-xl" value="20">
                      20 results
                    </SelectItem>
                    <SelectItem className="rounded-xl" value="50">
                      50 results
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Case Sensitive (Keyword Search) */}
              {searchType === "keyword" && (
                <div className="space-y-2">
                  <Label
                    htmlFor="case-sensitive"
                    className="text-xs font-medium text-gray-700 dark:text-gray-300"
                  >
                    Case Sensitive
                  </Label>
                  <div className="flex items-center space-x-2">
                    <Switch
                      id="case-sensitive"
                      checked={caseSensitive}
                      onCheckedChange={onCaseSensitiveChange}
                    />
                    <Label
                      htmlFor="case-sensitive"
                      className="text-xs text-gray-600 dark:text-gray-400"
                    >
                      {caseSensitive ? "Yes" : "No"}
                    </Label>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </CollapsibleContent>
    </Collapsible>
  );
}
