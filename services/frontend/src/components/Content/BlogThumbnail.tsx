import Image from "next/image";
import Link from "next/link";
import { Button } from "@/components/ui/button";

interface BlogThumbnailProps {
  article: {
    title: string;
    slug: string;
    image: string;
    page: string;
  };
}

const BlogThumbnail: React.FC<BlogThumbnailProps> = ({ article }) => {
  return (
    <div
      key={article.slug}
      className="group cursor-pointer flex flex-col items-center"
    >
      <Link href={`/${article.page}/${article.slug}`} className="block">
        <div className="relative w-full sm:w-[250px] h-[250px] aspect-square mb-3 rounded-3xl overflow-hidden bg-muted shadow-custom dark:shadow-none flex items-center justify-center">
          <Image
            src={article.image || "/placeholder.svg"}
            alt={article.title}
            fill
            className="object-cover transition-transform group-hover:scale-105"
          />
        </div>
      </Link>
      <h2 className="text-xl mb-2 font-open-sans tracking-[0.7px] text-center">
        {article.title}
      </h2>
      <Button
        variant="ghost"
        asChild
        className="rounded-full mb-10 hover:bg-accent hover:text-white transition-colors px-4 py-2 bg-[#ebebeb] text-black border-none"
      >
        <Link href={`/${article.page}/${article.slug}`}>Read more</Link>
      </Button>
    </div>
  );
};

export default BlogThumbnail;
