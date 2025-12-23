"use client";

import { useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface MarkdownViewerProps {
  content: string;
  isStreaming?: boolean;
}

export function MarkdownViewer({ content, isStreaming = false }: MarkdownViewerProps) {
  const cursorRef = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    if (isStreaming && cursorRef.current) {
      cursorRef.current.scrollIntoView({
        behavior: "smooth",
        block: "nearest",
        inline: "nearest"
      });
    }
  }, [content, isStreaming]);

  return (
    <div 
      className="prose prose-slate max-w-none prose-pre:bg-slate-900 prose-pre:text-slate-50 prose-headings:text-slate-800 prose-a:text-sky-600 relative"
    >
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {content}
      </ReactMarkdown>
      {isStreaming && content && (
        <span
          ref={cursorRef}
          className="inline-block w-0.5 h-5 ml-0.5 align-middle"
          style={{
            backgroundColor: "var(--color-primary)",
            animation: "var(--animate-cursor-blink)"
          }}
        />
      )}
    </div>
  );
}

