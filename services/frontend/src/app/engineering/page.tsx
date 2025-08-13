import Link from "next/link";
import BlogThumbnail from "@/components/Content/BlogThumbnail";

const articles = [
  {
    title: "Running in Parallel",
    slug: "running-in-parallel",
    image:
      "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/thumbnail-FA334FGq38I43AGGr9joI9p6vD2WAt.png",
    page: "engineering",
  },

  {
    title:
      "Is Your ML Strategy Grounded in Reality? A Strategic Framework for Business Leaders",
    slug: "ml-strategy-for-business-leaders",
    image: "/content-test/engineering/post2/thumbnail.png",
    page: "engineering",
  },
];

export default function EngineeringPage() {
  return (
    <main className="min-h-screen pt-20 pb-16">
      <div className="mt-12 container">
        <h1 className="text-4xl font-open-sans md:text-5xl tracking-[2px] mb-4">
          Engineering
        </h1>
        <p className="text-lg text-muted-foreground mb-16 text-justify">
          In one of my favorite books on the subject,{" "}
          <Link href="https://abseil.io/resources/swe-book">
            {/* Removed the <a> tag, styling directly on Link */}
            <em className="text-accent hover:underline cursor-pointer">
              Software Engineering at Google
            </em>
          </Link>
          , the authors state that{" "}
          <em>Software engineering is programming integrated over time.</em>{" "}
          This quote perfectly encapsulates the crucial distinction between
          simply writing code and the broader discipline of software
          engineering. Because of this temporal element, we must go beyond the
          immediate act of coding and consider a multitude of factors related to
          the future maintenance, scalability, and evolution of the code. These
          factors include <em>effective collaboration</em>,{" "}
          <em>clear communication</em>, <em>thorough documentation</em>,
          <em>robust testing</em>, <em>architectural design</em>,{" "}
          <em>version control</em>, <em>dependency management</em>, and{" "}
          <em>continuous integration and deployment</em>. —{" "}
          <Link href="https://www.linkedin.com/in/lo%C3%AFc-muhirwa-b3a940242/">
            {" "}
            <em className="text-accent hover:underline cursor-pointer">
              {" "}
              Loïc Muhirwa{" "}
            </em>{" "}
          </Link>
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
