"use client";

import ResumeClient from "./ResumeClient";

interface ResumePageProps {
  params?: {
    slug?: string;
  };
}

// Resume data
const resume = {
  title: "Loïc Muhirwa — AI Applied Scientist & Engineer",
  author: "Loïc Muhirwa",
  authorUrl: "https://www.linkedin.com/in/loïc-muhirwa-b3a940242/",
  content: {
    simple: "/content-test/resume/body_simple.md",
    detailed: "/content-test/resume/body.md",
  },
};

export default function ResumePage({ params }: ResumePageProps) {
  return <ResumeClient resume={resume} />;
}
