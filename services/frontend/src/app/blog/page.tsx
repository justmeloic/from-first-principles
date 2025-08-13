import Image from "next/image";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import BlogThumbnail from "@/components/Content/BlogThumbnail";

const articles = [
  {
    title: "The Order of Operations",
    slug: "order-of-operations",
    image:
      "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/thumbnail-N7Iuw8wVIKVgYOtdMha1A8TXa1xkFi.png",
    page: "blog",
  },
  {
    title: "Abstraction",
    slug: "abstraction",
    image:
      "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/thumbnail-dcH7BZKXdfP1oY3MsKTlfQ6X3K52mc.png",
    page: "blog",
  },
  {
    title: "Financial Literacy Matters",
    slug: "financial-literacy",
    image:
      "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/thumbnail-1NC6lantvSmJJPILYBUPh2ibRvebRb.png",
    page: "blog",
  },
];

export default function BlogPage() {
  return (
    <main className="min-h-screen pt-20 pb-16">
      <div className="mt-12 container">
        <h1 className="text-4xl font-open-sans md:text-5xl tracking-[2px] mb-4">
          Blog
        </h1>

        <p className="text-lg text-muted-foreground mb-16">
          These first three articles should be a primer for all content on this
          website. This is because the{" "}
          <Link href="/blog/order-of-operations">
            {" "}
            <em className="text-accent hover:underline cursor-pointer">
              {" "}
              order of operations
            </em>{" "}
          </Link>{" "}
          matters.
        </p>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-0">
          {articles.map((article) => (
            <BlogThumbnail key={article.slug} article={article} />
          ))}
        </div>
      </div>
    </main>
  );
}
