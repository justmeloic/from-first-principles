"use client";

import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";
import { Mic, Plus, SendHorizontal, Square } from "lucide-react";
import { useEffect, useRef, useState } from "react";

interface UploadedFile {
  id: string;
  file: File;
}

interface ChatInputProps {
  onSend: (message: string, files?: File[]) => void;
  isLoading: boolean;
}

export function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [isFocused, setIsFocused] = useState(false);
  const [message, setMessage] = useState("");
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      // Set maximum height to 150px (about 6-7 lines) before scrolling
      textarea.style.height = `${Math.min(
        Math.max(48, textarea.scrollHeight),
        150
      )}px`;
    }
  }, [message]);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if ((message.trim() || uploadedFiles.length > 0) && !isLoading) {
      const userMessage = message.trim() || ""; // Allow empty message if files are present
      const files = uploadedFiles.map((uf) => uf.file);
      setMessage("");
      setUploadedFiles([]); // Clear files after sending
      onSend(userMessage, files.length > 0 ? files : undefined);
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      if ((message.trim() || uploadedFiles.length > 0) && !isLoading) {
        handleSubmit(event as any);
      }
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files) {
      const newFiles = Array.from(files).map((file) => ({
        id: Math.random().toString(36).substr(2, 9),
        file,
      }));
      setUploadedFiles((prev) => [...prev, ...newFiles]);
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleRemoveFile = (fileId: string) => {
    setUploadedFiles((prev) => prev.filter((f) => f.id !== fileId));
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
      className="relative w-full max-w-[95%] md:max-w-[70%] mx-auto mb-6"
    >
      <div
        className={cn(
          "relative flex flex-col w-full rounded-full md:rounded-3xl border bg-white dark:bg-black dark:border-zinc-800 transition-shadow duration-300 ease-in-out",
          "min-h-16 md:min-h-28", // Reduced height on mobile
          isFocused
            ? "shadow-[0_1px_6px_1px_rgba(32,33,36,0.12),0_1px_8px_2px_rgba(32,33,36,0.12),0_1px_12px_3px_rgba(32,33,36,0.2)] dark:shadow-custom-white-input"
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
          className="min-h-8 md:min-h-12 w-full rounded-t-3xl bg-transparent px-4 pt-4 pb-2 md:py-3 text-base md:text-sm dark:text-gray-200 outline-none placeholder:text-muted-foreground dark:placeholder:text-gray-500 resize-none overflow-y-auto max-h-[150px]"
          rows={1}
          disabled={isLoading}
        />

        {/* Bottom section with buttons */}
        <div className="flex justify-between items-center mt-auto mb-2 md:mb-2 px-2">
          {/* File upload button - hidden on mobile */}
          <div className="hidden md:flex items-center">
            <input
              ref={fileInputRef}
              type="file"
              multiple
              onChange={handleFileUpload}
              className="hidden"
              id="chat-file-upload"
            />
            <label
              htmlFor="chat-file-upload"
              className={cn(
                "flex h-8 w-8 cursor-pointer items-center justify-center rounded-full transition-colors",
                "hover:bg-accent/20 focus:bg-gray-100 dark:focus:bg-gray-700 focus:outline-none"
              )}
            >
              <Plus className="h-5 w-5 text-gray-600 dark:text-gray-300" />
              <span className="sr-only">Upload files</span>
            </label>
          </div>

          {/* Right side buttons */}
          <div className="flex items-center ml-auto relative">
            {/* Microphone button - slides left when send button appears */}
            <button
              type="button"
              onClick={isRecording ? stopRecording : startRecording}
              className={cn(
                "hidden md:flex h-8 w-8 items-center justify-center rounded-full",
                "transition-all duration-1000 ease-in-out",
                isRecording
                  ? "bg-red-500 hover:bg-red-600"
                  : "text-gray-600 dark:text-gray-300 hover:bg-accent/20",
                "focus:outline-none",
                // Slide the mic button to the left when send button is visible
                (message.trim() || uploadedFiles.length > 0) && !isLoading
                  ? "transform -translate-x-9" // Move left by button width + gap
                  : "transform translate-x-0"
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

            {/* Send button - appears in the mic's original position on desktop, positioned higher on mobile */}
            <div
              className={cn(
                "absolute transition-all duration-1000 ease-in-out",
                // Desktop positioning (in mic's original position)
                "md:right-0",
                // Mobile positioning (higher up and to the right)
                "right-1 -top-11 md:top-0",
                (message.trim() || uploadedFiles.length > 0) && !isLoading
                  ? "opacity-100 scale-100"
                  : "opacity-0 scale-90 pointer-events-none"
              )}
            >
              <button
                type="submit"
                disabled={
                  !(message.trim() || uploadedFiles.length > 0) || isLoading
                }
                className={cn(
                  "group flex items-center justify-center rounded-full",
                  // Mobile: larger button, Desktop: smaller button
                  "h-10 w-10 md:h-7 md:w-7",
                  "transition-all duration-200 ease-in-out",
                  "bg-accent hover:bg-accent/80 dark:bg-accent dark:hover:bg-accent/80",
                  "hover:scale-110 active:scale-95",
                  "text-white focus:outline-none",
                  "shadow-md hover:shadow-lg",
                  "ring-0 focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2",
                  "transform-gpu" // Enables hardware acceleration
                )}
              >
                <SendHorizontal
                  className={cn(
                    "text-white transition-transform duration-150 ease-in-out",
                    // Mobile: larger icon, Desktop: smaller icon
                    "h-5 w-5 md:h-4 md:w-4",
                    "group-hover:translate-x-0.5" // Subtle forward movement on hover
                  )}
                />
                <span className="sr-only">Send message</span>
              </button>
            </div>
          </div>
        </div>
      </div>
      {uploadedFiles.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-2">
          {uploadedFiles.map(({ id, file }) => (
            <div
              key={id}
              className="flex items-center bg-gray-100 dark:bg-gray-800 rounded-lg px-3 py-2 text-sm"
            >
              <span className="mr-2 truncate max-w-32">{file.name}</span>
              <span className="text-xs text-gray-500 mr-2">
                ({(file.size / 1024).toFixed(1)}KB)
              </span>
              <button
                type="button"
                onClick={() => handleRemoveFile(id)}
                className="text-red-500 hover:text-red-700 ml-auto text-lg leading-none"
                aria-label="Remove file"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}
    </form>
  );
}
