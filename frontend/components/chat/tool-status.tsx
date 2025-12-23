"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Terminal, Loader2 } from "lucide-react";
import { useLanguage } from "@/context/language-context";
import type { ToolCallEvent } from "@/types/api";

interface ToolStatusProps {
  currentTool: ToolCallEvent | null;
}

export function ToolStatus({ currentTool }: ToolStatusProps) {
  const { t } = useLanguage();

  return (
    <AnimatePresence>
      {currentTool && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          className="flex items-center gap-2 px-4 py-2 rounded-full w-fit mb-4 mx-auto"
          style={{
            backgroundColor: "var(--color-tool-bg)",
            borderWidth: "1px",
            borderStyle: "solid",
            borderColor: "var(--color-tool-border)"
          }}
        >
          <div className="relative">
            <Terminal className="w-4 h-4" style={{ color: "var(--color-tool-icon)" }} />
            <span className="absolute -top-1 -right-1 flex h-2 w-2">
              <span 
                className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
                style={{ backgroundColor: "var(--color-tool-pulse)" }}
              />
              <span 
                className="relative inline-flex rounded-full h-2 w-2"
                style={{ backgroundColor: "var(--color-primary)" }}
              />
            </span>
          </div>
          <span className="text-sm font-medium" style={{ color: "var(--color-tool-text)" }}>
            {currentTool.message.startsWith("IsAnalyzingFile") ? t.status.reading :
             currentTool.message.startsWith("IsListingDirectory") ? t.status.scanning :
             currentTool.message.startsWith("IsGettingRepoStructure") ? t.status.scanning :
             currentTool.message}
            {currentTool.message.includes(" ") ? ` (${currentTool.message.split(" ").slice(1).join(" ")})` : ""}
          </span>
          <Loader2 className="w-3 h-3 animate-spin ml-1" style={{ color: "var(--color-muted-foreground)" }} />
        </motion.div>
      )}
    </AnimatePresence>
  );
}

