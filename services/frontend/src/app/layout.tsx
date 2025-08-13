import { AgentFloatingButton } from "@/components/Agent/floating-button";
import { Footer } from "@/components/Layout/footer";
import { NavBar } from "@/components/Layout/nav-bar";
import { ThemeProvider } from "@/providers/theme-provider";
import type { Metadata } from "next";
import { Toaster } from "sonner";
import "../styles/globals.css";

export const metadata: Metadata = {
  title: "From First Principles",
  description:
    "Knowledge empowers individuals and enhances lives, and we're committed to providing a platform for lifelong learning.",
  icons: {
    icon: "/images/tab-logo.png",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@200;300;400;600;700&display=swap"
          rel="stylesheet"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <ThemeProvider defaultTheme="light" enableSystem>
          <div className="min-h-screen bg-light-mode-white dark:bg-black transition-colors duration-0 ">
            <NavBar />
            {children}
            <Footer />
            <AgentFloatingButton />
          </div>
        </ThemeProvider>
        <Toaster position="top-center" richColors />
      </body>
    </html>
  );
}
