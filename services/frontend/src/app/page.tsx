"use client";

import { BlogPreviews } from "@/components/Home/BlogPreview";
import { ContactForm } from "@/components/Home/ContactForm";
import { HeroSection } from "@/components/Home/HeroSection";

export default function Home() {
  return (
    <main className="bg-light-mode-white dark:bg-black">
      <HeroSection />
      <BlogPreviews />
      <ContactForm />
    </main>
  );
}
