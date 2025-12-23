import { useState, useRef, useCallback } from "react";
import { useLanguage } from "@/context/language-context";
import type { ToolCallEvent } from "@/types/api";
import { parseSSEResponse } from "@/lib/sse-parser";

interface UseAnalysisReturn {
  analyze: (repoUrl: string) => Promise<void>;
  output: string;
  toolCalls: ToolCallEvent[];
  isAnalyzing: boolean;
  error: string | null;
  stop: () => void;
}

export function useAnalysis(): UseAnalysisReturn {
  const [output, setOutput] = useState("");
  const [toolCalls, setToolCalls] = useState<ToolCallEvent[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const { locale } = useLanguage();

  const stop = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setIsAnalyzing(false);
    }
  }, []);

  const analyze = useCallback(async (repoUrl: string) => {
    // Abort any existing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    setOutput("");
    setToolCalls([]);
    setError(null);
    setIsAnalyzing(true);

    const controller = new AbortController();
    abortControllerRef.current = controller;

    let keepAliveInterval: NodeJS.Timeout | null = null;

    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ repo_url: repoUrl, language: locale }),
        signal: controller.signal,
        keepalive: true,
      });

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`);
      }

      let lastActivityTime = Date.now();

      keepAliveInterval = setInterval(() => {
        const timeSinceLastActivity = Date.now() - lastActivityTime;
        if (timeSinceLastActivity > 30000) {
          console.warn("No activity for 30s, connection may be stale");
        }
      }, 10000);

      await parseSSEResponse(response, (event) => {
        lastActivityTime = Date.now();
        switch (event.type) {
          case "start":
            break;
          case "token":
            if (event.data.content) {
              setOutput((prev) => prev + event.data.content);
            }
            break;
          case "tool_call":
            if (event.data.message && event.data.tool) {
              const newToolCall: ToolCallEvent = {
                message: event.data.message,
                tool: event.data.tool,
                timestamp: event.timestamp,
              };
              setToolCalls((prev) => [...prev, newToolCall]);
            }
            break;
          case "tool_result":
            break;
          case "complete":
            setIsAnalyzing(false);
            break;
          case "error":
            setError(event.data.error || "Unknown error");
            setIsAnalyzing(false);
            break;
        }
      }, controller.signal);

    } catch (err) {
      if (err instanceof Error) {
        if (err.name === "AbortError") {
          console.log("Analysis aborted");
        } else {
          setError(err.message || "An unexpected error occurred");
        }
      } else {
        setError("An unexpected error occurred");
      }
      setIsAnalyzing(false);
    } finally {
      if (keepAliveInterval) {
        clearInterval(keepAliveInterval);
      }
      abortControllerRef.current = null;
    }
  }, [locale]);

  return { analyze, output, toolCalls, isAnalyzing, error, stop };
}

