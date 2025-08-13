import BlogPostClient from "./BlogPostClient";

interface BlogPostPageProps {
  params: {
    slug: string;
  };
}

// This would normally come from a database or CMS
const posts = {
  "financial-literacy": {
    title: "In a Capitalist World, Financial Literacy Is Not Optional",
    author: "Loïc Muhirwa",
    authorUrl: "https://www.linkedin.com/in/loïc-muhirwa-b3a940242/",
    content: {
      simple: "/content-test/blog/post3/body_simple.md",
      detailed: "/content-test/blog/post3/body.md",
    },
  },
  abstraction: {
    title: "Abstraction is the Bedrock of Human Cognition",
    author: "Loïc Muhirwa",
    authorUrl: "https://www.linkedin.com/in/loïc-muhirwa-b3a940242/",
    content: {
      simple: "/content-test/blog/post2/body_simple.md",
      detailed: "/content-test/blog/post2/body.md",
    },
  },
  "order-of-operations": {
    title: "The Importance of the Order of Operations in Achieving Goals",
    author: "Loïc Muhirwa",
    authorUrl: "https://www.linkedin.com/in/loïc-muhirwa-b3a940242/",
    content: {
      simple: "/content-test/blog/post1/body_simple.md",
      detailed: "/content-test/blog/post1/body.md",
    },
  },
};

export async function generateStaticParams() {
  // Instead of reading from filesystem, we'll use the known posts
  return Object.keys(posts).map((slug) => ({
    slug,
  }));
}

export default function BlogPostPage({ params }: BlogPostPageProps) {
  const post = posts[params.slug as keyof typeof posts];

  if (!post) {
    return <div>Post not found</div>;
  }

  return <BlogPostClient post={post} slug={params.slug} />;
}
