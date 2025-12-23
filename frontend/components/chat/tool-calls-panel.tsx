"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, Terminal, Clock } from "lucide-react";
import type { ToolCallEvent } from "@/types/api";

interface ToolCallsPanelProps {
  toolCalls: ToolCallEvent[];
}

export function ToolCallsPanel({ toolCalls }: ToolCallsPanelProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  if (toolCalls.length === 0) return null;

  return (
    <div className="mb-6 border rounded-lg overflow-hidden" style={{ 
      borderColor: "var(--color-tool-border)",
      backgroundColor: "var(--color-card)"
    }}>
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 flex items-center justify-between transition-colors"
        style={{ 
          backgroundColor: "var(--color-tool-bg)"
        }}
      >
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4" style={{ color: "var(--color-tool-icon)" }} />
          <span className="text-sm font-medium" style={{ color: "var(--color-tool-text)" }}>
            Tool Calls ({toolCalls.length})
          </span>
        </div>
        <motion.div
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <ChevronDown className="w-4 h-4" style={{ color: "var(--color-muted-foreground)" }} />
        </motion.div>
      </button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="p-4 space-y-2 max-h-64 overflow-y-auto">
              {toolCalls.map((call, index) => (
                <motion.div
                  key={`${call.timestamp}-${index}`}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="flex items-start gap-3 p-3 rounded-lg"
                  style={{ backgroundColor: "var(--color-muted)" }}
                >
                  <div className="mt-0.5">
                    <Terminal className="w-3.5 h-3.5" style={{ color: "var(--color-tool-icon)" }} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-mono break-words" style={{ color: "var(--color-foreground)" }}>
                      {call.message}
                    </p>
                    <div className="flex items-center gap-1.5 mt-1">
                      <Clock className="w-3 h-3" style={{ color: "var(--color-muted-foreground)" }} />
                      <span className="text-xs" style={{ color: "var(--color-muted-foreground)" }}>
                        {new Date(call.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

