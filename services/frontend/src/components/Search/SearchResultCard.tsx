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
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SearchResult } from "@/types";
import { ExternalLink } from "lucide-react";
import Link from "next/link";

interface SearchResultCardProps {
  result: SearchResult;
}

export function SearchResultCard({ result }: SearchResultCardProps) {
  const formatDate = (dateString: string) => {
    if (!dateString) return "";
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return dateString;
    }
  };

  const truncateContent = (content: string, maxLength: number = 300) => {
    if (content.length <= maxLength) return content;
    return content.substring(0, maxLength) + "...";
  };

  // Construct the proper local URL path
  const getLocalUrl = () => {
    // If the URL is already a full URL, extract the path
    if (result.url.startsWith("http")) {
      try {
        const url = new URL(result.url);
        return url.pathname;
      } catch {
        // Fallback to constructing from category and slug
        return `/${result.category}/${result.slug}`;
      }
    }

    // If it's already a path, use it
    if (result.url.startsWith("/")) {
      return result.url;
    }

    // Construct from category and slug
    return `/${result.category}/${result.slug}`;
  };

  return (
    <Link href={getLocalUrl()} className="block">
      <Card className="group shadow-md hover:shadow-2xl hover:shadow-accent/20 transition-all duration-300 cursor-pointer border border-gray-200 dark:border-gray-700 hover:border-accent/30 bg-white dark:bg-gray-950 rounded-3xl hover:-translate-y-1">
        <CardHeader className="pb-4">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              <CardTitle className="text-xl font-bold text-gray-900 dark:text-white group-hover:text-accent transition-colors duration-200 leading-tight">
                {result.title}
              </CardTitle>
              <div className="flex items-center gap-3 mt-2">
                <Badge className="text-xs font-medium bg-accent text-accent-foreground hover:bg-accent/90 border-0 shadow-sm rounded-full">
                  {result.category}
                </Badge>
                {result.publish_date && (
                  <span className="text-xs text-gray-500 dark:text-gray-400 font-medium">
                    {formatDate(result.publish_date)}
                  </span>
                )}
              </div>
            </div>
            <div className="flex flex-col items-end gap-1">
              <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                <span className="font-medium">
                  Relevance: {(result.score * 100).toFixed(0)}%
                </span>
              </div>
              <div className="w-12 h-1 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-accent transition-all duration-300"
                  style={{ width: `${result.score * 100}%` }}
                />
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="space-y-4">
            {result.excerpt && (
              <p className="text-sm text-gray-600 dark:text-gray-300 font-medium leading-relaxed border-l-2 border-accent/30 pl-3">
                {result.excerpt}
              </p>
            )}
            <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed line-clamp-3">
              {truncateContent(result.content, 280)}
            </p>
            {result.tags && result.tags.length > 0 && (
              <div className="flex flex-wrap gap-2 pt-2 border-t border-gray-100 dark:border-gray-800">
                {result.tags.slice(0, 5).map((tag, index) => (
                  <Badge
                    key={index}
                    variant="secondary"
                    className="text-xs bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-accent/10 hover:text-accent transition-colors duration-200 rounded-full"
                  >
                    {tag}
                  </Badge>
                ))}
                {result.tags.length > 5 && (
                  <Badge
                    variant="secondary"
                    className="text-xs bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 rounded-full"
                  >
                    +{result.tags.length - 5} more
                  </Badge>
                )}
              </div>
            )}

            {/* Read More Button */}
            <div className="flex justify-end pt-3">
              <Button
                variant="ghost"
                size="sm"
                className="text-accent rounded-2xl hover:text-accent hover:bg-accent/10 transition-colors duration-200"
              >
                Read More
                <ExternalLink className="ml-2 h-3 w-3" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
