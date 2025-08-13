import fs from "fs";
import path from "path";
import EngineeringPostClient from "./EngineeringPostClient";

interface EngineeringPostPageProps {
  params: {
    slug: string;
  };
}

const posts = {
  "running-in-parallel": {
    title: "Running in Parallel",
    author: "Loïc Muhirwa",
    authorUrl: "https://www.linkedin.com/in/loïc-muhirwa-b3a940242/",
    content: {
      simple: "/content-test/engineering/post1/body_simple.md",
      detailed: "/content-test/engineering/post1/body.md",
    },
  },

  "ml-strategy-for-business-leaders": {
    title:
      "Is Your ML Strategy Grounded in Reality? A Strategic Framework for Business Leaders",
    author: "Loïc Muhirwa",
    authorUrl: "https://www.linkedin.com/in/loïc-muhirwa-b3a940242/",
    content: {
      simple: "/content-test/engineering/post2/body_simple.md",
      detailed: "/content-test/engineering/post2/body.md",
    },
  },
};

export async function generateStaticParams() {
  // Instead of reading from filesystem, we'll use the known posts
  return Object.keys(posts).map((slug) => ({
    slug,
  }));
}

export default function EngineeringPostPage({
  params,
}: EngineeringPostPageProps) {
  const post = posts[params.slug as keyof typeof posts];

  if (!post) {
    return <div>Post not found</div>;
  }

  return <EngineeringPostClient post={post} slug={params.slug} />;
}
