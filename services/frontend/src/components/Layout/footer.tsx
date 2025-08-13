"use client";

import { useState, useRef, useEffect } from "react";
import { Github, Linkedin } from "lucide-react";
import { useTheme } from "@/providers/theme-provider";
import type React from "react";
import { toast } from "sonner"; // Import toast from sonner

const toastStyles = {
  success: (theme: string) => ({
    backgroundColor: theme === "dark" ? "#C6A760" : "#C6A760",
    color: theme === "dark" ? "#fff" : "#fff",
    fontSize: "1rem",
    fontWeight: "bold",
    width: "300px",
    height: "100px",
    boxShadow: "-10px 10px 15px 5px rgba(1, 0.1, 0.1, 0.2)",
    position: "fixed",
    top: "50%",
    left: "50%",
    transform: "translate(-50%, -50%)",
    borderRadius: "25px",
    animation: "toastTranslate 6s forwards",
    marginTop: "250px",
    marginBottom: "50px",
  }),
  error: (theme: string) => ({
    backgroundColor: theme === "dark" ? "#333" : "#f56565",
    color: theme === "dark" ? "#fff" : "#fff",
    fontSize: "1rem",
    fontWeight: "bold",
    width: "300px",
    height: "100px",
    boxShadow: "-10px 10px 15px 5px rgba(1, 0.1, 0.1, 0.2)",
    position: "fixed",
    top: "50%",
    left: "50%",
    transform: "translate(-50%, -50%)",
    borderRadius: "25px",
    animation: "toastTranslate 3s forwards",
    marginTop: "250px",
    marginBottom: "50px",
  }),
};

export function Footer() {
  const { theme } = useTheme();
  const [email, setEmail] = useState("");
  const formRef = useRef<HTMLFormElement>(null);

  useEffect(() => {
    const styleSheet = document.styleSheets[0];
    styleSheet.insertRule(
      `@keyframes toastTranslate {
        0% { transform: translate(-50%, -50%); opacity: 1; }
        100% { transform: translate(-50%, -150%); opacity: 0; }
      }`,
      styleSheet.cssRules.length
    );
  }, []);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const formspreeEndpoint = process.env.NEXT_PUBLIC_FORMSPREE_ENDPOINT;

    if (!formspreeEndpoint) {
      console.error("Formspree endpoint is not defined!");
      toast.error("Form submission is not configured correctly.", {
        style: toastStyles.error(theme),
      });
      return;
    }

    try {
      const response = await fetch(formspreeEndpoint, {
        method: "POST",
        body: formData,
        headers: {
          Accept: "application/json",
        },
      });

      const data = await response.json();

      if (response.ok) {
        formRef.current?.reset();
        setEmail("");
        toast.success("Thank you for signing up!", {
          duration: 3000,
          style: toastStyles.success(theme),
        });
      } else {
        console.error("Formspree error:", data);
        toast.error(data.error || "Failed to sign up. Please try again.", {
          style: toastStyles.error(theme),
        });
      }
    } catch (error) {
      console.error("Error submitting form:", error);
      toast.error("Failed to sign up. Please try again.", {
        style: toastStyles.error(theme),
      });
    }
  }

  const handleEmailChange = (event) => {
    setEmail(event.target.value);
  };

  return (
    <footer className="py-24 bg-black text-white">
      <div className="container max-w-2xl mx-auto px-6">
        {/* Top Divider */}
        <div className="w-full h-px bg-zinc-800 mb-24" />

        {/* Main Content */}
        <div className="space-y-24">
          {/* About Section */}
          <div className="text-center space-y-4">
            <h2
              className={`text-2xl font-open-sans font-[20] text-white tracking-[1px]`}
            >
              From First Principles
            </h2>
            <p className={` max-w-[300px] mx-auto text-zinc-400`}>
              Information is a privilege, and we believe in sharing it widely.
              Join us in building "From First Principles" into a valuable
              resource for everyone.
            </p>
          </div>

          {/* Newsletter Section */}
          <div id="newsletter" className="text-center space-y-8">
            <h4
              className={`text-2xl font-open-sans font-[20] tracking-[2px] text-white`}
            >
              Newsletter
            </h4>
            <form
              ref={formRef}
              onSubmit={handleSubmit}
              className="max-w-md mx-auto space-y-8"
            >
              <div className="relative">
                <input
                  type="email"
                  name="email"
                  placeholder="Your Email Address"
                  required
                  className={`
                    rounded-full w-full bg-transparent border-b-2 pb-2 text-center outline-none text-lg bg-black
                    placeholder:text-zinc-500 transition-colors
                    border-zinc-800 text-white focus:border-zinc-600
                  `}
                />
              </div>
              <button
                type="submit"
                className={`
                  w-full max-w-xs h-14 rounded-full text-lg font-medium transition-all duration-300
                  bg-white text-black hover:bg-zinc-200
                `}
              >
                Sign Up
              </button>
            </form>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="mt-24 space-y-8">
          {/* Bottom Divider */}
          <div className="w-full h-px bg-zinc-800" />

          {/* Copyright and Social Links */}
          <div className="text-center space-y-6">
            <p className={`text-sm text-zinc-500`}>
              Copyright © 2025 Naturalingo Inc
            </p>
            <div className="flex justify-center gap-4">
              <a
                href="https://www.linkedin.com/in/loïc-muhirwa-b3a940242/"
                target="_blank"
                rel="noopener noreferrer"
                className={`
            p-2 rounded-full transition-colors
            bg-white text-black hover:bg-zinc-200
          `}
              >
                <Linkedin
                  className="h-5 w-5"
                  strokeWidth={0} // Remove the stroke
                  fill="currentColor" // Fill with the current text color
                />
              </a>
              <a
                href="https://github.com/justmeloic/from-first-principles"
                target="_blank"
                rel="noopener noreferrer"
                className={`
            p-2 rounded-full transition-colors
            bg-white text-black hover:bg-zinc-200
          `}
              >
                <Github
                  className="h-5 w-5"
                  strokeWidth={0} // Remove the stroke
                  fill="currentColor" // Fill with the current text color
                />
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
