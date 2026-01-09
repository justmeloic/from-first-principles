"use client";

import BlogPostArticle from "@/components/Content/BlogPostArticle";
import { Button } from "@/components/ui/button";
import { useTheme } from "@/providers/theme-provider";
import Link from "next/link";
import { useEffect, useState } from "react";

export default function ResumeClient({ resume }: { resume: any }) {
  const [isSimplified, setIsSimplified] = useState(false);
  const { theme } = useTheme();
  const [markdownContent, setMarkdownContent] = useState("");

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  useEffect(() => {
    const fetchMarkdown = async () => {
      const contentUrl = isSimplified
        ? resume.content.simple
        : resume.content.detailed;
      const response = await fetch(contentUrl);
      const text = await response.text();
      setMarkdownContent(text);
    };

    fetchMarkdown();
  }, [isSimplified, resume.content]);

  return (
    <main
      className={`min-h-screen pt-24 ${
        theme === "dark" ? "bg-black" : "bg-light-mode-white"
      }`}
    >
      <div className="container max-w-4xl mx-auto px-6">
        <div className="relative mt-12 pt-1">
          <div className="absolute left-0 -top-2 z-10">
            <Link href="/">
              <Button
                variant="secondary"
                size="sm"
                className="gap-0 w-[65px] rounded-full bg-gray-200 text-zinc-500 dark:text-zinc-400 dark:bg-zinc-900 hover:bg-[#C6A760] hover:text-white dark:hover:bg-[#C6A760] dark:hover:text-white"
              >
                Back
              </Button>
            </Link>
          </div>
          <BlogPostArticle
            post={resume}
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
