"use client";

import { cn } from "@/lib/utils";
import { Plus, SendHorizontal } from "lucide-react";
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
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

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
    if (message.trim() && !isLoading) {
      const userMessage = message.trim();
      const files = uploadedFiles.map((uf) => uf.file);
      setMessage("");
      setUploadedFiles([]); // Clear files after sending
      onSend(userMessage, files.length > 0 ? files : undefined);
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
            {/* Send button */}
            <div
              className={cn(
                "transition-all duration-300 ease-in-out",
                message.trim() && !isLoading
                  ? "opacity-100 scale-100"
                  : "opacity-0 scale-90 pointer-events-none"
              )}
            >
              <button
                type="submit"
                disabled={!message.trim() || isLoading}
                className={cn(
                  "group flex items-center justify-center rounded-full",
                  "h-8 w-8",
                  "transition-all duration-200 ease-in-out",
                  "bg-accent hover:bg-accent/80 dark:bg-accent dark:hover:bg-accent/80",
                  "hover:scale-110 active:scale-95",
                  "text-white focus:outline-none",
                  "shadow-md hover:shadow-lg",
                  "ring-0 focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2",
                  "transform-gpu"
                )}
              >
                <SendHorizontal
                  className={cn(
                    "text-white transition-transform duration-150 ease-in-out",
                    "h-4 w-4",
                    "group-hover:translate-x-0.5"
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
              className="flex items-center bg-accent/80 rounded-3xl px-3 py-1 text-sm"
            >
              <span className="mr-2 truncate max-w-32 text-white">
                {file.name}
              </span>
              <span className="text-xs text-white/70 mr-2">
                ({(file.size / 1024).toFixed(1)}KB)
              </span>
              <button
                type="button"
                onClick={() => handleRemoveFile(id)}
                className="text-white/80 hover:text-white ml-auto text-lg leading-none"
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
