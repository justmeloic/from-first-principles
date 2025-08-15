"use client";

import { useTheme } from "@/providers/theme-provider";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react"; // Add this import

export function NavBar() {
  const pathname = usePathname();
  const isHomePage = pathname === "/";
  const { theme } = useTheme();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
      setIsMobileMenuOpen(false); // Close mobile menu after clicking
    }
  };

  const NavLinks = () => (
    <>
      <Link
        href="/"
        className={` md:text-[13px] text-[20px] transition-colors md:hover:text-accent hover:text-accent ${
          theme === "dark" ? "text-gray-300" : "text-gray-800"
        } md:py-0 py-6`}
        onClick={() => setIsMobileMenuOpen(false)}
      >
        Home
      </Link>
      <Link
        href="/blog"
        className={` md:text-[13px] text-[20px] transition-colors md:hover:text-accent hover:text-accent ${
          theme === "dark" ? "text-gray-300" : "text-gray-800"
        } md:py-0 py-6`}
        onClick={() => setIsMobileMenuOpen(false)}
      >
        Blog
      </Link>
      <Link
        href="/engineering"
        className={`md:text-[13px] text-[20px] transition-colors md:hover:text-accent hover:text-accent ${
          theme === "dark" ? "text-gray-300" : "text-gray-800"
        } md:py-0 py-6`}
        onClick={() => setIsMobileMenuOpen(false)}
      >
        Engineering
      </Link>

      <Link
        href="/agent"
        className={`md:text-[13px] text-[20px] transition-colors md:hover:text-accent hover:text-accent ${
          theme === "dark" ? "text-gray-300" : "text-gray-800"
        } md:py-0 py-6`}
        onClick={() => setIsMobileMenuOpen(false)}
      >
        Agent
      </Link>
      <Link
        href="/search"
        className={`md:text-[13px] text-[20px] transition-colors md:hover:text-accent hover:text-accent ${
          theme === "dark" ? "text-gray-300" : "text-gray-800"
        } md:py-0 py-6`}
        onClick={() => setIsMobileMenuOpen(false)}
      >
        Search
      </Link>
      {isHomePage ? (
        <button
          onClick={() => {
            scrollToSection("contact");
            setIsMobileMenuOpen(false);
          }}
          className={`md:text-[13px] text-[20px] transition-colors md:hover:text-accent hover:text-accent ${
            theme === "dark" ? "text-gray-300" : "text-gray-800"
          } md:py-0 py-6`}
        >
          Contact
        </button>
      ) : (
        <Link
          href="/#contact"
          className={` md:text-[13px] text-[20px] transition-colors md:hover:text-accent hover:text-accent ${
            theme === "dark" ? "text-gray-300" : "text-gray-800"
          } md:py-0 py-6`}
          onClick={() => setIsMobileMenuOpen(false)}
        >
          Contact
        </Link>
      )}
      {isHomePage ? (
        <button
          onClick={() => {
            scrollToSection("newsletter");
            setIsMobileMenuOpen(false);
          }}
          className={` md:text-[13px] text-[20px] transition-colors md:hover:text-accent hover:text-accent ${
            theme === "dark" ? "text-gray-300" : "text-gray-800"
          } md:py-0 py-6`}
        >
          Newsletter
        </button>
      ) : (
        <Link
          href="/#newsletter"
          className={` md:text-[13px] text-[20px] transition-colors md:hover:text-accent hover:text-accent ${
            theme === "dark" ? "text-gray-300" : "text-gray-800"
          } md:py-0 py-6`}
          onClick={() => setIsMobileMenuOpen(false)}
        >
          Newsletter
        </Link>
      )}
    </>
  );

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 shadow-xl dark:shadow-custom-white ${
        theme === "dark" ? "bg-black" : "bg-light-mode-white"
      } transition-colors duration-0`}
    >
      <div className="container flex h-20 items-center justify-between">
        <div className="w-36"></div>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center justify-center gap-12">
          <NavLinks />
        </div>

        {/* Mobile Menu Button */}
        <button
          className="md:hidden p-2"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          aria-label="Toggle mobile menu"
        >
          <div
            className={`w-6 h-0.5 bg-current mb-1.5 transition-all ${
              isMobileMenuOpen ? "rotate-45 translate-y-2" : ""
            }`}
          ></div>
          <div
            className={`w-6 h-0.5 bg-current mb-1.5 transition-all ${
              isMobileMenuOpen ? "opacity-0" : ""
            }`}
          ></div>
          <div
            className={`w-6 h-0.5 bg-current transition-all ${
              isMobileMenuOpen ? "-rotate-45 -translate-y-2" : ""
            }`}
          ></div>
        </button>

        <div className="w-36 flex justify-end">
          {/* Theme toggle removed - now handled by SettingsFloatingButton */}
        </div>
      </div>

      {/* Mobile Navigation Panel */}
      <div
        className={`md:hidden fixed inset-0 top-20 z-40 transition-transform duration-300 ease-in-out ${
          isMobileMenuOpen ? "translate-x-0" : "translate-x-full"
        } ${theme === "dark" ? "bg-black" : "bg-light-mode-white"}`}
      >
        <div className="flex flex-col items-center justify-center w-full h-full gap-0">
          <NavLinks />
        </div>
      </div>
    </nav>
  );
}
