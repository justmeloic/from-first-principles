"use client";

import { HeroSection } from "@/components/Home/hero-section";
import { BlogPreviews } from "@/components/Home/blog-preview";
import { ContactForm } from "@/components/Home/contact-form";

export default function Home() {
  return (
    <main className="bg-light-mode-white dark:bg-black">
      <HeroSection />
      <BlogPreviews />
      <ContactForm />
    </main>
  );
}
