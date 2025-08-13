"use client";

import BlogPostArticle from "@/components/Content/BlogPostArticle";
import { Button } from "@/components/ui/button";
import { useTheme } from "@/providers/theme-provider";
import Link from "next/link";
import { useEffect, useState } from "react";

export default function EngineeringPostClient({
  post,
  slug,
}: {
  post: any;
  slug: string;
}) {
  const [isSimplified, setIsSimplified] = useState(false);
  const { theme } = useTheme();
  const [markdownContent, setMarkdownContent] = useState("");

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  useEffect(() => {
    const fetchMarkdown = async () => {
      const contentUrl = isSimplified
        ? post.content.simple
        : post.content.detailed;
      const response = await fetch(contentUrl);
      const text = await response.text();
      setMarkdownContent(text);
    };

    fetchMarkdown();
  }, [isSimplified, post.content]);

  return (
    <main
      className={`min-h-screen pt-24 ${
        theme === "dark" ? "bg-black" : "bg-light-mode-white"
      }`}
    >
      <div className="container max-w-4xl mx-auto px-6">
        <div className="relative mt-12 pt-1">
          <div className="absolute left-0 -top-2 z-10">
            <Link href="/engineering">
              <Button
                variant="secondary"
                size="sm"
                className="gap-0 w-[65px] rounded-full bg-gray-200 text-zinc-500 dark:text-zinc-400 dark:bg-zinc-900 hover:bg-accent hover:text-white dark:hover:bg-accent dark:hover:text-white"
              >
                Back
              </Button>
            </Link>
          </div>
          <BlogPostArticle
            post={post}
            isSimplified={isSimplified}
            setIsSimplified={setIsSimplified}
            markdownContent={markdownContent}
          >
            {/* Optional additional content can go here */}
          </BlogPostArticle>
        </div>
      </div>
    </main>
  );
}
