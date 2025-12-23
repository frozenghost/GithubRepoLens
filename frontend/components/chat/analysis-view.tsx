"use client";

import { motion } from "framer-motion";
import { MarkdownViewer } from "./markdown-viewer";
import { ToolCallsPanel } from "./tool-calls-panel";
import { useLanguage } from "@/context/language-context";
import type { ToolCallEvent } from "@/types/api";

interface AnalysisViewProps {
  output: string;
  toolCalls: ToolCallEvent[];
  isAnalyzing: boolean;
  error: string | null;
}

export function AnalysisView({ output, toolCalls, isAnalyzing, error }: AnalysisViewProps) {
  const { t } = useLanguage();

  if (!output && toolCalls.length === 0 && !error) return null;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="w-full max-w-4xl mx-auto mt-12 backdrop-blur-md rounded-2xl shadow-sm overflow-hidden bg-card border border-border"
    >
      <div 
        className="p-1 flex items-center justify-between px-4 py-2 bg-linear-to-r from-gradient-from to-gradient-to border-b border-border"
      >
        <div className="flex gap-2">
          <div className="w-3 h-3 rounded-full bg-window-dot" />
          <div className="w-3 h-3 rounded-full bg-window-dot" />
          <div className="w-3 h-3 rounded-full bg-window-dot" />
        </div>
        <span className="text-xs font-mono text-window-text">
          {t.report.title}
        </span>
      </div>

      <div className="p-8 min-h-[400px] max-h-[600px] overflow-y-auto relative">
        <ToolCallsPanel toolCalls={toolCalls} />
        
        {error ? (
          <div className="p-4 rounded-lg bg-error-bg text-error-text border border-error-border">
            <h3 className="font-bold">{t.status.error}</h3>
            <p>{error}</p>
          </div>
        ) : (
          <MarkdownViewer content={output} isStreaming={isAnalyzing} />
        )}
        
        {!output && !error && toolCalls.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center text-window-dot">
            {t.status.idle}
          </div>
        )}
      </div>
    </motion.div>
  );
}
