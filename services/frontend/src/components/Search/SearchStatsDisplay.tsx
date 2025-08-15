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

import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { SearchStats } from "@/types";

interface SearchStatsDisplayProps {
  stats: SearchStats | null;
  isLoading: boolean;
}

export function SearchStatsDisplay({
  stats,
  isLoading,
}: SearchStatsDisplayProps) {
  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <Skeleton className="h-4 w-32" />
            <Skeleton className="h-4 w-24" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!stats) {
    return null;
  }

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-300">
          <span>
            Database: {stats.total_chunks} chunks across{" "}
            {Object.values(stats.categories).reduce(
              (sum, cat) => sum + cat.posts,
              0
            )}{" "}
            posts
          </span>
          <span>Categories: {Object.keys(stats.categories).join(", ")}</span>
        </div>
      </CardContent>
    </Card>
  );
}
