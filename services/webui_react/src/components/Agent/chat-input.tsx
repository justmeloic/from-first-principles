"use client";

import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";
import { Mic, Plus, SendHorizontal, Square } from "lucide-react";
import { useEffect, useRef, useState } from "react";

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
}

export function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [isFocused, setIsFocused] = useState(false);
  const [message, setMessage] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { toast } = useToast();

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = `${Math.max(48, textarea.scrollHeight)}px`;
    }
  }, [message]);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (message.trim() && !isLoading) {
      const userMessage = message;
      setMessage("");
      onSend(userMessage);
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      if (message.trim() && !isLoading) {
        handleSubmit(event as any);
      }
    }
  };

  const startRecording = async () => {
    try {
      console.log("Requesting microphone permission...");
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setIsRecording(true);
      console.log("Recording started");
      toast({
        title: "Recording started",
        description: "Speak now. Click the stop button when you're done.",
      });
    } catch (error) {
      console.error("Error starting recording:", error);
      toast({
        title: "Recording failed",
        description: "Please make sure you've granted microphone permissions.",
        variant: "destructive",
      });
    }
  };

  const stopRecording = () => {
    setIsRecording(false);
    console.log("Recording stopped");
    toast({
      title: "Recording stopped",
      description: "Your audio has been processed.",
    });
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="relative w-full max-w-[70%] mx-auto mb-6"
    >
      <div
        className={cn(
          "relative flex flex-col w-full min-h-28 rounded-3xl border bg-white dark:bg-black dark:border-gray-600 transition-shadow duration-300 ease-in-out",
          isFocused
            ? "shadow-[0_1px_6px_1px_rgba(32,33,36,0.12),0_1px_8px_2px_rgba(32,33,36,0.12),0_1px_12px_3px_rgba(32,33,36,0.2)] dark:shadow-[0_4px_8px_0_rgba(0,0,0,0.4)]"
            : "shadow-none"
        )}
      >
        {/* Top section with textarea input */}
        <textarea
          ref={textareaRef}
          placeholder="Ask anything"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          className="min-h-12 w-full rounded-t-3xl bg-transparent px-4 py-3 text-sm dark:text-gray-200 outline-none placeholder:text-muted-foreground dark:placeholder:text-gray-500 resize-none overflow-hidden"
          rows={1}
          disabled={isLoading}
        />

        {/* Bottom section with buttons */}
        <div className="flex justify-between items-center mt-auto mb-4 px-2">
          {/* File upload button */}
          <div className="flex items-center">
            <button
              type="button"
              className={cn(
                "flex h-8 w-8 cursor-pointer items-center justify-center rounded-full transition-colors",
                "hover:bg-gradient-to-r from-blue-500/20 to-pink-500/20 focus:bg-gray-100 dark:focus:bg-gray-700 focus:outline-none"
              )}
            >
              <Plus className="h-5 w-5 text-gray-600 dark:text-gray-300" />
              <span className="sr-only">Upload files</span>
            </button>
          </div>

          {/* Right side buttons */}
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={isRecording ? stopRecording : startRecording}
              className={cn(
                "flex h-8 w-8 items-center justify-center rounded-full transition-colors",
                isRecording
                  ? "bg-red-500 hover:bg-red-600"
                  : "text-gray-600 dark:text-gray-300 hover:bg-gradient-to-r from-blue-500/20 to-pink-500/20",
                "focus:outline-none"
              )}
            >
              {isRecording ? (
                <Square className="h-4 w-4 text-white" />
              ) : (
                <Mic className="h-5 w-5 text-gray-600 dark:text-gray-300" />
              )}
              <span className="sr-only">
                {isRecording ? "Stop recording" : "Start recording"}
              </span>
            </button>
            {message.trim() && !isLoading ? (
              <button
                type="submit"
                className={cn(
                  "flex h-7 w-7 items-center justify-center rounded-full transition-colors",
                  "bg-blue-100 hover:bg-blue-200 focus:bg-blue-200 dark:bg-gray-700 dark:hover:bg-gray-600 dark:focus:bg-gray-600 focus:outline-none"
                )}
              >
                <SendHorizontal className="h-4 w-4 text-gray-800 dark:text-gray-300" />
                <span className="sr-only">Send message</span>
              </button>
            ) : null}
          </div>
        </div>
      </div>
    </form>
  );
}
