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
import { Slider } from "@/components/ui/slider";
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
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium">
                Search Filters
              </CardTitle>
              <Button variant="ghost" size="sm" onClick={onResetFilters}>
                Reset
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Search Type */}
              <div className="space-y-2">
                <Label htmlFor="search-type" className="text-xs font-medium">
                  Search Type
                </Label>
                <Select value={searchType} onValueChange={onSearchTypeChange}>
                  <SelectTrigger id="search-type">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="semantic">Semantic</SelectItem>
                    <SelectItem value="keyword">Keyword</SelectItem>
                    <SelectItem value="hybrid">Hybrid</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Category Filter */}
              <div className="space-y-2">
                <Label htmlFor="category" className="text-xs font-medium">
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
                  <SelectTrigger id="category">
                    <SelectValue placeholder="All categories" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All categories</SelectItem>
                    <SelectItem value="blog">Blog</SelectItem>
                    <SelectItem value="engineering">Engineering</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Results Limit */}
              <div className="space-y-2">
                <Label htmlFor="limit" className="text-xs font-medium">
                  Results Limit
                </Label>
                <Select
                  value={limit.toString()}
                  onValueChange={(value) => onLimitChange(parseInt(value))}
                >
                  <SelectTrigger id="limit">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="5">5 results</SelectItem>
                    <SelectItem value="10">10 results</SelectItem>
                    <SelectItem value="20">20 results</SelectItem>
                    <SelectItem value="50">50 results</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Case Sensitive (Keyword Search) */}
              {searchType === "keyword" && (
                <div className="space-y-2">
                  <Label
                    htmlFor="case-sensitive"
                    className="text-xs font-medium"
                  >
                    Case Sensitive
                  </Label>
                  <div className="flex items-center space-x-2">
                    <Switch
                      id="case-sensitive"
                      checked={caseSensitive}
                      onCheckedChange={onCaseSensitiveChange}
                    />
                    <Label htmlFor="case-sensitive" className="text-xs">
                      {caseSensitive ? "Yes" : "No"}
                    </Label>
                  </div>
                </div>
              )}
            </div>

            {/* Similarity Threshold (Semantic Search) */}
            {(searchType === "semantic" || searchType === "hybrid") && (
              <div className="space-y-2">
                <Label className="text-xs font-medium">
                  Similarity Threshold: {similarityThreshold.toFixed(2)}
                </Label>
                <Slider
                  value={[similarityThreshold]}
                  onValueChange={(value) =>
                    onSimilarityThresholdChange(value[0])
                  }
                  max={1}
                  min={0}
                  step={0.05}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Less relevant</span>
                  <span>More relevant</span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </CollapsibleContent>
    </Collapsible>
  );
}
