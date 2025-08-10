"use client";

import { Button } from "@/components/ui/button";
import { MessageSquare } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

export function AgentFloatingButton() {
  const pathname = usePathname();

  // Don't show the button on the agent page itself
  if (pathname === "/agent" || pathname?.startsWith("/agent")) {
    return null;
  }

  return (
    <Link href="/agent">
      <Button
        size="lg"
        className="fixed bottom-6 right-6 z-30 h-12 w-12 rounded-full shadow-lg hover:shadow-xl transition-all duration-300 bg-accent hover:bg-accent/80 text-white border-0 p-0 animate-bounce hover:animate-none"
        aria-label="Open AI Agent Chat"
      >
        <MessageSquare className="h-5 w-5" />
      </Button>
    </Link>
  );
}
