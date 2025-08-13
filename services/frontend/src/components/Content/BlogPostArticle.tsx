"use client";

import React, { Dispatch, SetStateAction } from "react";
import { useTheme } from "@/providers/theme-provider";
import MarkdownRenderer from "./MarkdownRenderer";
import Link from "next/link";

interface BlogPostArticleProps {
  post: {
    title: string;
    author: string;
    authorUrl?: string; // Add optional author URL
    content: {
      simple: string;
      detailed: string;
    };
  };
  isSimplified: boolean;
  setIsSimplified: Dispatch<SetStateAction<boolean>>;
  markdownContent: string; // Add markdownContent prop
  children?: React.ReactNode; // Make children prop optional
}

const BlogPostArticle: React.FC<BlogPostArticleProps> = ({
  post,
  isSimplified,
  setIsSimplified,
  markdownContent, // Destructure markdownContent prop
  children, // Destructure children prop
}) => {
  const { theme } = useTheme();

  return (
    <article
      className={`
            relative rounded-[2rem] p-6 md:p-16 mt-1 mb-11 duration-500
            ${
              theme === "dark"
                ? "bg-zinc-900 shadow-none"
                : "bg-white shadow-custom"
            }
            mt-12
          `}
    >
      {/* Simplify toggle */}
      <div className="absolute right-8 top-18 flex items-center mt-1 mb-15 md: mb-15">
        <span className="mr-5 text-[12px] text-gray-400 dark:text-gray-50">
          {isSimplified ? "Simplify" : "Simplify"}
        </span>
        <button
          onClick={() => setIsSimplified(!isSimplified)}
          className="relative inline-block w-[40px] h-[24px]"
        >
          <div
            className={`absolute inset-0 rounded-full cursor-pointer transition-colors duration-300 ${
              theme === "dark" ? "bg-accent" : "bg-gray-300"
            }`}
          >
            <div
              className={`absolute rounded-full w-[19px] h-[18px] transition-transform duration-300 left-[2.4px] top-[2.7px] bg-white ${
                isSimplified ? "translate-x-[16px]" : "translate-x-[1px]"
              }`}
            />
          </div>
        </button>
      </div>
      {/* Article header */}
      <header className="text-center mt-12 mb-16 max-w-3xl mx-0 md:mx-auto">
        <h1 className="font-[400] text-2xl md:text-5xl font-serif mb-5 leading-tight text-zinc-900 dark:text-white">
          {post.title}
        </h1>
        <p className="mt-2 text-zinc-400  italic dark:text-zinc-500">
          {post.authorUrl ? (
            <Link
              href={post.authorUrl}
              className="hover:text-accent transition-colors"
            >
              {post.author}
            </Link>
          ) : (
            post.author
          )}
        </p>
        <hr className="mt-9 border-gray-200 dark:border-zinc-700  mx-auto" />
      </header>
      {/* Article content */}
      <div className="prose prose-lg dark:prose-invert mx-1 md:mx-auto max-w-3xl mb-3">
        <div className="text-[16px] font-light ">
          <MarkdownRenderer content={markdownContent} />
        </div>
      </div>
      {children} {/* Render children */}
    </article>
  );
};

export default BlogPostArticle;
