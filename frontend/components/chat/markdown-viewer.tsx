"use client";

import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import mermaid from "mermaid";

interface MarkdownViewerProps {
  content: string;
  isStreaming?: boolean;
}

const Mermaid = ({ chart }: { chart: string }) => {
  const ref = useRef<HTMLDivElement>(null);
  const [svg, setSvg] = useState<string>("");

  useEffect(() => {
    mermaid.initialize({
      startOnLoad: true,
      theme: "default",
      securityLevel: "loose",
      fontFamily: "inherit",
    });
  }, []);

  useEffect(() => {
    let isMounted = true;
    if (ref.current && chart) {
      const renderChart = async () => {
        try {
          // Clean up the chart string to avoid syntax errors during streaming
          if (chart.includes("```")) return; 
          
          const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`;
          const { svg } = await mermaid.render(id, chart);
          if (isMounted) setSvg(svg);
        } catch {
          // Silent error during streaming as it's expected to fail until complete
        }
      };
      renderChart();
    }
    return () => {
      isMounted = false;
    };
  }, [chart]);

  return (
    <div className="mermaid-chart my-6 flex justify-center bg-white p-4 rounded-lg border border-slate-200 shadow-sm overflow-x-auto" ref={ref} dangerouslySetInnerHTML={{ __html: svg }} />
  );
};

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
      className="prose prose-slate max-w-none prose-pre:bg-transparent prose-pre:p-0 prose-headings:text-slate-800 prose-a:text-sky-600 relative"
    >
      <ReactMarkdown 
        remarkPlugins={[remarkGfm]}
        components={{
          code(props: React.ComponentProps<'code'> & { node?: unknown; inline?: boolean }) {
            const { inline, className, children, ...restProps } = props;
            const match = /language-(\w+)/.exec(className || "");
            const language = match ? match[1] : "";

            if (!inline && language === "mermaid") {
              return <Mermaid chart={String(children).replace(/\n$/, "")} />;
            }

            if (!inline && match) {
              return (
                <div className="rounded-md overflow-hidden my-4 shadow-sm">
                  <SyntaxHighlighter
                    style={oneDark}
                    language={language}
                    PreTag="div"
                  >
                    {String(children).replace(/\n$/, "")}
                  </SyntaxHighlighter>
                </div>
              );
            }

            return (
              <code className={className} {...restProps}>
                {children}
              </code>
            );
          },
        }}
      >
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

