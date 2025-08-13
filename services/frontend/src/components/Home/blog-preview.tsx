"use client";

import Image from "next/image";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { useTheme } from "@/providers/theme-provider";

interface BlogPost {
  title: string;
  subtitle: string;
  excerpt: string;
  image: string;
  slug: string;
  category: string;
  imagePosition?: "left" | "right";
}

function BlogPostPreview({ post }: { post: BlogPost }) {
  const { theme } = useTheme();

  const addQuotes = (text: string) => {
    return `"${text}"`;
  };

  return (
    <div
      className={`grid md:grid-cols-[1fr_2fr] gap-4 md:gap-8 items-stretch ${
        post.imagePosition === "right" ? "md:grid-cols-[2fr_1fr]" : ""
      } transition-colors duration-500`}
    >
      {post.imagePosition === "right" && (
        <div
          className={`p-4 md:p-8 rounded-3xl h-full flex flex-col justify-between ${
            theme === "dark"
              ? "bg-zinc-900"
              : "bg-white shadow-custom dark:shadow-none"
          } transition-colors duration-500`}
        >
          <div className="space-y-3 md:space-y-6">
            <h3 className="text-accent font-open-sans tracking-[4px] md:tracking-[6px] text-sm md:text-base uppercase mb-4 md:mb-8 wow fadeInUp">
              {post.category}
            </h3>
            <h2
              className={`text-xl md:text-3xl font-open-sans tracking-[1.2px] font-[70] ${
                theme === "dark" ? "text-gray-200" : "text-gray-800"
              } transition-colors duration-500`}
            >
              {addQuotes(post.subtitle)}
            </h2>
            <p
              className={`hidden sm:block text-sm md:text-base text-muted-foreground ${
                theme === "dark" ? "text-gray-400" : "text-gray-500"
              } transition-colors duration-500`}
            >
              {post.excerpt}
            </p>
            <Button
              variant="ghost"
              className={`text-sm md:text-base rounded-full hover:bg-accent hover:text-white transition-colors px-4 md:px-6 py-1 md:py-2 ${
                theme === "dark"
                  ? "bg-zinc-800 text-gray-300"
                  : "bg-gray-100 text-gray-700"
              } border-none`}
              asChild
            >
              <Link href={`/blog/${post.slug}`}>Read more</Link>
            </Button>
          </div>
        </div>
      )}
      <div
        className={`${
          post.imagePosition === "right" ? "order-last" : ""
        } h-full hidden sm:block`}
      >
        <div className="relative h-full rounded-3xl overflow-hidden group shadow-custom dark:shadow-none">
          <Link href={`/blog/${post.slug}`}>
            <Image
              src={post.image || "/placeholder.svg"}
              alt={post.title}
              fill
              className="object-cover transition-transform group-hover:scale-105"
            />
          </Link>
        </div>
      </div>
      {post.imagePosition !== "right" && (
        <div
          className={`p-4 md:p-8 rounded-3xl h-full flex flex-col justify-between ${
            theme === "dark"
              ? "bg-zinc-900"
              : "bg-white shadow-custom dark:shadow-none"
          } transition-colors duration-500`}
        >
          <div className="space-y-3 md:space-y-6">
            <h3 className="text-accent font-open-sans tracking-[4px] md:tracking-[6px] text-sm md:text-base uppercase mb-4 md:mb-8 wow fadeInUp">
              {post.category}
            </h3>
            <h2
              className={`text-xl md:text-3xl font-open-sans tracking-[1.2px] font-[70] ${
                theme === "dark" ? "text-gray-200" : "text-gray-800"
              } transition-colors duration-500`}
            >
              {addQuotes(post.subtitle)}
            </h2>
            <p
              className={`hidden sm:block text-sm md:text-base text-muted-foreground ${
                theme === "dark" ? "text-gray-400" : "text-gray-500"
              } transition-colors duration-500`}
            >
              {post.excerpt}
            </p>
            <Button
              variant="ghost"
              className={`text-sm md:text-base rounded-full hover:bg-accent hover:text-white transition-colors px-4 md:px-6 py-1 md:py-2 ${
                theme === "dark"
                  ? "bg-zinc-800 text-gray-300"
                  : "bg-gray-100 text-gray-700"
              } border-none`}
              asChild
            >
              <Link href={`/blog/${post.slug}`}>Read more</Link>
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

export function BlogPreviews() {
  const { theme } = useTheme();
  const posts: BlogPost[] = [
    {
      title: "The Order of Operations",
      category: "THE ORDER OF OPERATIONS",
      subtitle:
        "In some cases, reordering might save time; in others, it's the difference between success and failure.",
      excerpt:
        "When striving to achieve a goal, many of us instinctively create a list of steps or tasks...",
      image:
        "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/thumbnail-N7Iuw8wVIKVgYOtdMha1A8TXa1xkFi.png",
      slug: "order-of-operations",
      imagePosition: "right",
    },
    {
      title: "Abstraction",
      category: "ABSTRACTION",
      subtitle:
        "In other words, abstraction is the bedrock of human cognition.",
      excerpt:
        "Abstraction, the process of simplifying complex information by focusing on essential features while ignoring irrelevant details...",
      image:
        "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/thumbnail-dcH7BZKXdfP1oY3MsKTlfQ6X3K52mc.png",
      slug: "abstraction",
    },
    {
      title: "Financial Literacy",
      category: "FINANCIAL LITERACY",
      subtitle:
        "...therefore, within the context of a capitalistic society, financial literacy matters by definition",
      excerpt:
        'What does it mean for something "to matter"? This seemingly simple question...',
      image:
        "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/thumbnail-1NC6lantvSmJJPILYBUPh2ibRvebRb.png",
      slug: "financial-literacy",
      imagePosition: "right",
    },
  ];

  return (
    <section
      id="blog-previews"
      className={`py-12 md:py-24 ${
        theme === "dark" ? "bg-black" : "bg-light-mode-white"
      }`}
    >
      <div className="container">
        <div className="space-y-12 md:space-y-24">
          {posts.map((post, index) => (
            <div key={index} className="max-w-[1150px] mx-auto">
              <BlogPostPreview post={post} />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
