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

import { cn } from "@/lib/utils";

interface ServiceUnavailableProps {
  serviceName: string;
  className?: string;
}

export function ServiceUnavailable({
  serviceName,
  className,
}: ServiceUnavailableProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center min-h-[60vh] px-4 text-center",
        className,
      )}
    >
      <h2 className="text-3xl font-open-sans font-[10] tracking-[2px] text-zinc-500 dark:text-white mb-2">
        {serviceName} is temporarily unavailable
      </h2>

      <p className="text-gray-500 dark:text-gray-400 max-w-sm mb-6">
        In the meantime, you can still browse our content.
      </p>

      <div className="flex flex-wrap justify-center gap-4">
        <a
          href="/blog"
          className="text-sm text-accent hover:text-accent/80 underline underline-offset-4 transition-colors"
        >
          Browse articles
        </a>
        <a
          href="/engineering"
          className="text-sm text-accent hover:text-accent/80 underline underline-offset-4 transition-colors"
        >
          Engineering posts
        </a>
        <a
          href="/"
          className="text-sm text-accent hover:text-accent/80 underline underline-offset-4 transition-colors"
        >
          Homepage
        </a>
      </div>
    </div>
  );
}
