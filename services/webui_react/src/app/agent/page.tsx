"use client";

import { ChatInput } from "@/components/Agent/chat-input";
import { MessageActions } from "@/components/Agent/message-actions";
import { ReferencesPanel } from "@/components/Agent/references-panel";
import { Avatar, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Toaster } from "@/components/ui/toaster";
import { useToast } from "@/hooks/use-toast";
import { useTheme } from "@/providers/theme-provider";
import { useCallback, useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

// Types
interface ChatMessage {
  role: "user" | "bot";
  content: string;
}

interface Reference {
  title: string;
  link?: string;
  description?: string;
}

// Mock API function - replace with your actual API
const sendMessage = async (
  message: string,
  options?: { signal?: AbortSignal; model?: string }
): Promise<{ response: string; references?: { [key: string]: Reference } }> => {
  // Simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 1000));

  if (options?.signal?.aborted) {
    throw new Error("Request aborted");
  }

  // Mock response - replace with actual API call
  return {
    response: `Thank you for your message: "${message}". This is a mock response from the AI agent. The selected model is ${
      options?.model || "default"
    }.`,
    references: {
      "1": {
        title: "Sample Reference",
        link: "https://example.com",
        description: "This is a sample reference",
      },
    },
  };
};

// Typewriter hook
const useTypewriter = (text: string, speed: number = 100) => {
  const [displayText, setDisplayText] = useState("");
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    if (text.length === 0) return;

    setDisplayText("");
    setIsComplete(false);
    let index = 0;

    const timer = setInterval(() => {
      if (index < text.length) {
        setDisplayText(text.slice(0, index + 1));
        index++;
      } else {
        setIsComplete(true);
        clearInterval(timer);
      }
    }, speed);

    return () => clearInterval(timer);
  }, [text, speed]);

  return { displayText, isComplete };
};

export default function AgentPage() {
  const { toast } = useToast();
  const { theme } = useTheme();
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [references, setReferences] = useState<{ [key: string]: Reference }>(
    {}
  );
  const [isFirstPrompt, setIsFirstPrompt] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingText, setLoadingText] = useState("Thinking...");
  const [isReferencesHidden, setIsReferencesHidden] = useState(false);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Typewriter animation for greeting
  const greetingText = "Hello! I'm an AI Agent";
  const subtitleText =
    "I can help you navigate our content, dive deeper into topics, and discover insights from our knowledge base!";

  const { displayText: displayGreeting, isComplete: greetingComplete } =
    useTypewriter(greetingText, 80);
  const { displayText: displaySubtitle, isComplete: subtitleComplete } =
    useTypewriter(greetingComplete ? subtitleText : "", 30);

  // Persist and restore chat state
  useEffect(() => {
    const storedChatHistory = localStorage.getItem("agentChatHistory");
    const storedReferences = localStorage.getItem("agentChatReferences");
    const storedIsFirstPrompt = localStorage.getItem("agentIsFirstPrompt");

    if (storedChatHistory) {
      try {
        const parsedHistory = JSON.parse(storedChatHistory);
        setChatHistory(parsedHistory);
        if (parsedHistory.length > 0) {
          setIsFirstPrompt(false);
        }
      } catch (error) {
        console.error("Error parsing stored chat history:", error);
      }
    }

    if (storedReferences) {
      try {
        const parsedReferences = JSON.parse(storedReferences);
        setReferences(parsedReferences);
      } catch (error) {
        console.error("Error parsing stored references:", error);
      }
    }

    if (storedIsFirstPrompt !== null) {
      try {
        const parsedIsFirstPrompt = JSON.parse(storedIsFirstPrompt);
        setIsFirstPrompt(parsedIsFirstPrompt);
      } catch (error) {
        console.error("Error parsing stored isFirstPrompt:", error);
      }
    }

    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  // Save chat history to localStorage
  useEffect(() => {
    if (chatHistory.length > 0) {
      localStorage.setItem("agentChatHistory", JSON.stringify(chatHistory));
    } else {
      localStorage.removeItem("agentChatHistory");
    }
  }, [chatHistory]);

  // Save references to localStorage
  useEffect(() => {
    if (Object.keys(references).length > 0) {
      localStorage.setItem("agentChatReferences", JSON.stringify(references));
    } else {
      localStorage.removeItem("agentChatReferences");
    }
  }, [references]);

  // Save isFirstPrompt to localStorage
  useEffect(() => {
    localStorage.setItem("agentIsFirstPrompt", JSON.stringify(isFirstPrompt));
  }, [isFirstPrompt]);

  const scrollToBottom = useCallback(() => {
    if (chatContainerRef.current) {
      const scrollHeight = chatContainerRef.current.scrollHeight;
      const height = chatContainerRef.current.clientHeight;
      const maxScrollTop = scrollHeight - height;
      chatContainerRef.current.scrollTop = maxScrollTop > 0 ? maxScrollTop : 0;
    }
  }, []);

  // Function to handle citation clicks
  const handleCitationClick = useCallback(
    (citationNumber: string) => {
      const reference = references[citationNumber];
      if (reference && reference.link) {
        window.open(reference.link, "_blank");
      }
    },
    [references]
  );

  // Component to render message content
  const MessageContent = ({ content }: { content: string }) => {
    return (
      <div className="prose prose-sm max-w-none dark:prose-invert">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
      </div>
    );
  };

  useEffect(() => {
    if (isLoading) {
      const intervalId = setInterval(() => {
        setLoadingText((prevText) => {
          if (prevText === "Thinking...") {
            return "Processing your request...";
          } else if (prevText === "Processing your request...") {
            return "Finding the best answer...";
          }
          return "Thinking...";
        });
      }, 2000);

      return () => clearInterval(intervalId);
    }
  }, [isLoading]);

  const handleSend = useCallback(
    async (userMessage: string) => {
      if (isLoading) return;

      if (isFirstPrompt) {
        setIsFirstPrompt(false);
      }

      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      abortControllerRef.current = new AbortController();

      setIsLoading(true);
      setLoadingText("Thinking...");
      setChatHistory((prev) => [
        ...prev,
        { role: "user", content: userMessage },
        { role: "bot", content: "Thinking..." },
      ]);
      setTimeout(scrollToBottom, 0);

      try {
        const response = await sendMessage(userMessage, {
          signal: abortControllerRef.current.signal,
        });

        if (abortControllerRef.current.signal.aborted) {
          return;
        }

        if (
          response.references &&
          Object.keys(response.references).length > 0
        ) {
          setReferences(response.references);
        }

        setChatHistory((prev) => {
          const newHistory = [...prev];
          if (
            newHistory.length > 0 &&
            newHistory[newHistory.length - 1].role === "bot"
          ) {
            newHistory[newHistory.length - 1] = {
              role: "bot",
              content: response.response,
            };
          } else {
            newHistory.push({ role: "bot", content: response.response });
          }
          return newHistory;
        });
        setTimeout(scrollToBottom, 100);
      } catch (error: any) {
        if (
          error.name === "AbortError" ||
          abortControllerRef.current?.signal.aborted
        ) {
          return;
        }

        console.error("Error sending message:", error);
        setChatHistory((prev) =>
          prev.slice(0, -1).concat({
            role: "bot",
            content: "Sorry, I encountered an error. Please try again.",
          })
        );
        toast({
          title: "Error",
          description: "Failed to send message. Please try again.",
          variant: "destructive",
        });
      } finally {
        if (!abortControllerRef.current?.signal.aborted) {
          setIsLoading(false);
        }
      }
    },
    [scrollToBottom, isFirstPrompt, isLoading, toast]
  );

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory, scrollToBottom]);

  const clearChat = () => {
    setChatHistory([]);
    setReferences({});
    setIsFirstPrompt(true);
    setIsLoading(false);
    setLoadingText("Thinking...");
    setIsReferencesHidden(false);
    localStorage.removeItem("agentChatHistory");
    localStorage.removeItem("agentChatReferences");
    localStorage.removeItem("agentIsFirstPrompt");
    toast({
      title: "Chat Cleared",
      description: "Started a new conversation.",
      duration: 1500,
      className:
        "rounded-full data-[state=closed]:animate-out data-[state=closed]:slide-out-to-right data-[state=closed]:duration-300",
    });
  };

  const toggleReferencesVisibility = () => {
    setIsReferencesHidden((prev) => !prev);
  };

  return (
    <div className="min-h-screen pt-20 bg-light-mode-white dark:bg-black">
      <div className="flex flex-col h-[calc(100vh-5rem)]">
        <div className="flex items-center justify-between p-4  border-gray-200 dark:border-gray-700">
          <Button
            onClick={clearChat}
            variant="outline"
            size="sm"
            className="rounded-full text-gray-400 dark:text-gray-300 hover:text-white dark:hover:text-white"
          >
            Clear Chat
          </Button>
        </div>

        <div className="flex flex-1 overflow-hidden">
          <main
            className={`flex-1 flex flex-col items-center w-full relative overflow-hidden transition-all duration-700 ease-in-out ${
              Object.keys(references).length > 0 && !isReferencesHidden
                ? "mr-[28rem]"
                : ""
            }`}
          >
            <div
              ref={chatContainerRef}
              className="flex-1 w-full max-w-[800px] mx-auto px-4 pb-4 overflow-y-auto"
              style={{
                height: "calc(100vh - 14rem)",
                maxHeight: "calc(100vh - 14rem)",
              }}
            >
              {isFirstPrompt && chatHistory.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full space-y-6">
                  <h1 className="text-5xl md:text-6xl font-open-sans font-[10] tracking-[2px] text-center">
                    <span
                      className={`${
                        theme === "dark" ? "text-white" : "text-zinc-500"
                      }`}
                    >
                      {displayGreeting}
                    </span>
                  </h1>
                  {greetingComplete && (
                    <p
                      className={`text-xl font-open-sans font-[10] tracking-[1px] text-center max-w-md ${
                        theme === "dark" ? "text-zinc-400" : "text-zinc-600"
                      }`}
                    >
                      {displaySubtitle}
                    </p>
                  )}
                </div>
              ) : (
                <div className="w-full space-y-4 py-4">
                  {chatHistory.map((message, index) => (
                    <div
                      key={index}
                      className={`flex flex-col ${
                        message.role === "user" ? "items-end" : "items-start"
                      }`}
                    >
                      <div className="flex items-start gap-3 max-w-[85%] md:max-w-[80%]">
                        {message.role === "bot" && (
                          <Avatar className="w-8 h-8 shrink-0">
                            <AvatarImage
                              src="/placeholder-logo.png"
                              alt="AI Agent"
                            />
                          </Avatar>
                        )}
                        <div
                          className={`inline-block p-4 ${
                            message.role === "user"
                              ? "bg-accent text-white rounded-3xl rounded-tr-none"
                              : "bg-gray-100 dark:bg-black text-gray-900 dark:text-gray-300 rounded-3xl rounded-tl-none"
                          }`}
                          style={
                            message.role === "user"
                              ? {
                                  boxShadow:
                                    "0 8px 16px 0 rgba(0, 0, 0, 0.120), 0 4px 8px 0 rgba(0, 0, 0, 0.15)",
                                  filter:
                                    "drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2))",
                                }
                              : {}
                          }
                        >
                          {message.role === "bot" &&
                          message.content === loadingText ? (
                            <div className="flex items-center space-x-2">
                              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current"></div>
                              <span>{loadingText}</span>
                            </div>
                          ) : (
                            <MessageContent content={message.content} />
                          )}
                        </div>
                      </div>
                      {message.role === "bot" &&
                        index === chatHistory.length - 1 &&
                        !isLoading && (
                          <div className="ml-11 mt-2">
                            <MessageActions message={message.content} />
                          </div>
                        )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="w-full max-w-[800px] mx-auto p-4 border-gray-200 dark:border-gray-700">
              <ChatInput onSend={handleSend} isLoading={isLoading} />
            </div>
          </main>

          {Object.keys(references).length > 0 && (
            <>
              {isReferencesHidden && (
                <button
                  onClick={toggleReferencesVisibility}
                  className="fixed right-4 top-40 z-20 p-3 bg-accent hover:bg-accent/80 dark:bg-gray-700 rounded-full dark:hover:bg-gray-600 transition-all duration-300 shadow-lg"
                  aria-label="Show references"
                >
                  <svg
                    className="w-5 h-5 text-white dark:text-gray-300"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M15 19l-7-7 7-7"
                    />
                  </svg>
                </button>
              )}

              <div
                className={`fixed right-0 w-[28rem] bg-white dark:bg-zinc-900 overflow-y-auto rounded-[2rem] m-2 mr-4 mt-20 min-h-[200px] max-h-[calc(100vh-10rem)] transition-transform duration-700 ease-in-out shadow-custom dark:shadow-none ${
                  isReferencesHidden ? "translate-x-[120%]" : "translate-x-0"
                }`}
              >
                <ReferencesPanel
                  references={references}
                  isHidden={isReferencesHidden}
                  onToggleVisibility={toggleReferencesVisibility}
                />
              </div>
            </>
          )}
        </div>
      </div>
      <Toaster />
    </div>
  );
}
