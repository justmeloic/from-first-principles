/**
 * Copyright 2025 Loïc Muhirwa
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

"use client";

import { File, FileText, Image, Paperclip, X } from "lucide-react";
import { useCallback, useRef, useState } from "react";

interface FileAttachment {
  file: File;
  id: string;
}

interface FileAttachmentProps {
  onFilesChange: (files: File[]) => void;
  maxFiles?: number;
  maxFileSize?: number; // in bytes
}

const SUPPORTED_TYPES = {
  "image/png": "image",
  "image/jpeg": "image",
  "image/jpg": "image",
  "image/gif": "image",
  "image/webp": "image",
  "text/plain": "text",
  "text/markdown": "text",
  "text/csv": "data",
  "application/csv": "data",
  "application/json": "data",
  "application/pdf": "document",
  "text/html": "code",
  "text/css": "code",
  "text/javascript": "code",
  "application/javascript": "code",
};

const getFileIcon = (file: File) => {
  const type = file.type;
  if (type.startsWith("image/")) {
    return <Image className="w-4 h-4" />;
  } else if (
    type.includes("text") ||
    type.includes("json") ||
    type.includes("csv")
  ) {
    return <FileText className="w-4 h-4" />;
  }
  return <File className="w-4 h-4" />;
};

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
};

export function FileAttachment({
  onFilesChange,
  maxFiles = 5,
  maxFileSize = 10 * 1024 * 1024, // 10MB
}: FileAttachmentProps) {
  const [attachments, setAttachments] = useState<FileAttachment[]>([]);
  const [error, setError] = useState<string>("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = useCallback(
    (file: File): string | null => {
      // Check file size
      if (file.size > maxFileSize) {
        return `File "${file.name}" is too large (${formatFileSize(
          file.size
        )}). Max size: ${formatFileSize(maxFileSize)}.`;
      }

      // Check file type
      if (!Object.keys(SUPPORTED_TYPES).includes(file.type)) {
        return `File type "${file.type}" is not supported for "${file.name}".`;
      }

      return null;
    },
    [maxFileSize]
  );

  const addFiles = useCallback(
    (files: File[]) => {
      if (attachments.length + files.length > maxFiles) {
        setError(`Cannot add more files. Maximum ${maxFiles} files allowed.`);
        return;
      }

      const newAttachments: FileAttachment[] = [];
      const errors: string[] = [];

      files.forEach((file) => {
        const validationError = validateFile(file);
        if (validationError) {
          errors.push(validationError);
        } else {
          newAttachments.push({
            file,
            id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          });
        }
      });

      if (errors.length > 0) {
        setError(errors[0]); // Show first error
        return;
      }

      setError("");
      const updatedAttachments = [...attachments, ...newAttachments];
      setAttachments(updatedAttachments);
      onFilesChange(updatedAttachments.map((a) => a.file));
    },
    [attachments, maxFiles, validateFile, onFilesChange]
  );

  const removeFile = useCallback(
    (id: string) => {
      const updatedAttachments = attachments.filter((att) => att.id !== id);
      setAttachments(updatedAttachments);
      onFilesChange(updatedAttachments.map((a) => a.file));
      setError("");
    },
    [attachments, onFilesChange]
  );

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = Array.from(e.target.files || []);
      if (files.length > 0) {
        addFiles(files);
      }
      // Reset input
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    },
    [addFiles]
  );

  const triggerFileSelect = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  return (
    <div className="space-y-2">
      {/* File attachments display */}
      {attachments.length > 0 && (
        <div className="flex flex-wrap gap-2 p-2 bg-gray-50 dark:bg-gray-800 rounded-lg">
          {attachments.map((attachment) => (
            <div
              key={attachment.id}
              className="flex items-center gap-2 px-3 py-2 bg-white dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600"
            >
              {getFileIcon(attachment.file)}
              <span className="text-sm text-gray-700 dark:text-gray-300 max-w-[200px] truncate">
                {attachment.file.name}
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {formatFileSize(attachment.file.size)}
              </span>
              <button
                onClick={() => removeFile(attachment.id)}
                className="ml-1 p-1 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-full transition-colors"
                title="Remove file"
              >
                <X className="w-3 h-3 text-gray-500 dark:text-gray-400" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Error display */}
      {error && (
        <div className="text-sm text-red-600 dark:text-red-400 px-2 py-1 bg-red-50 dark:bg-red-900/20 rounded border border-red-200 dark:border-red-800">
          {error}
        </div>
      )}

      {/* File input and trigger button */}
      <div className="flex items-center gap-2">
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleFileSelect}
          multiple
          accept={Object.keys(SUPPORTED_TYPES).join(",")}
          className="hidden"
        />
        <button
          onClick={triggerFileSelect}
          disabled={attachments.length >= maxFiles}
          className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          title={
            attachments.length >= maxFiles
              ? `Maximum ${maxFiles} files allowed`
              : "Attach files"
          }
        >
          <Paperclip className="w-5 h-5 text-gray-600 dark:text-gray-400" />
        </button>
        {attachments.length > 0 && (
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {attachments.length}/{maxFiles} files
          </span>
        )}
      </div>
    </div>
  );
}
