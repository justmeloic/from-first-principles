"use client";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useToast } from "@/hooks/use-toast";
import { Copy, MoreHorizontal, Pause, Volume2 } from "lucide-react";
import { useState } from "react";

interface MessageActionsProps {
  message: string;
}

export function MessageActions({ message }: MessageActionsProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioRef, setAudioRef] = useState<SpeechSynthesisUtterance | null>(
    null
  );
  const { toast } = useToast();

  const handleCopy = () => {
    navigator.clipboard
      .writeText(message)
      .then(() => {
        toast({
          title: "Copied to clipboard",
          description: "The message has been copied.",
          duration: 1500,
          className:
            "bottom-0 left-0 fixed mb-4 ml-4 bg-blue-50 dark:bg-gray-800/80 rounded-full shadow-[0_3px_3px_-1px_rgba(5,0.7,.7,0.4)] text-gray-600 dark:text-gray-300",
        });
      })
      .catch((err) => {
        console.error("Failed to copy text: ", err);
        toast({
          title: "Copy failed",
          description: "Failed to copy the message. Please try again.",
          variant: "destructive",
          duration: 1500,
          className:
            "bottom-0 left-0 fixed mb-4 ml-4 bg-blue-50 dark:bg-gray-800/80 rounded-full shadow-[0_3px_3px_-1px_rgba(5,0.7,.7,0.4)] text-red-600 dark:text-red-300",
        });
      });
  };

  const handlePlay = () => {
    if (audioRef) {
      window.speechSynthesis.resume();
    } else {
      const utterance = new SpeechSynthesisUtterance(message);
      setAudioRef(utterance);
      utterance.onend = () => {
        setIsPlaying(false);
        setAudioRef(null);
      };
      window.speechSynthesis.speak(utterance);
    }
    setIsPlaying(true);
    toast({
      title: "Audio playing",
      description: "The message is being read aloud.",
      duration: 1500,
      className:
        "bottom-0 left-0 fixed mb-4 ml-4 bg-blue-50 dark:bg-gray-800/80 rounded-full shadow-[0_3px_3px_-1px_rgba(5,0.7,.7,0.4)] text-gray-600 dark:text-gray-300",
    });
  };

  const handlePause = () => {
    if (audioRef) {
      window.speechSynthesis.pause();
      setIsPlaying(false);
      toast({
        title: "Audio paused",
        description: "The audio has been paused.",
        duration: 1500,
        className:
          "bottom-0 left-0 fixed mb-4 ml-4 bg-blue-50 dark:bg-gray-800/80 rounded-full shadow-[0_3px_3px_-1px_rgba(5,0.7,.7,0.4)] text-gray-600 dark:text-gray-300",
      });
    }
  };

  return (
    <div className="flex items-center gap-2 mt-2">
      <button
        onClick={handleCopy}
        className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full transition-colors"
      >
        <Copy className="h-4 w-4 text-gray-600 dark:text-gray-300" />
      </button>
      {isPlaying ? (
        <button
          onClick={handlePause}
          className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full transition-colors"
        >
          <Pause className="h-4 w-4 text-gray-600 dark:text-gray-300" />
        </button>
      ) : (
        <button
          onClick={handlePlay}
          className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full transition-colors"
        >
          <Volume2 className="h-4 w-4 text-gray-600 dark:text-gray-300" />
        </button>
      )}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <button className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full transition-colors">
            <MoreHorizontal className="h-4 w-4 text-gray-600 dark:text-gray-300" />
          </button>
        </DropdownMenuTrigger>
        <DropdownMenuContent>
          <DropdownMenuItem onClick={handleCopy}>
            <Copy className="mr-2 h-4 w-4" />
            <span>Copy</span>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
