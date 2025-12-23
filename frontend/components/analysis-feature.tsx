"use client";

import { useAnalysis } from "@/hooks/use-analysis";
import { HeroInput } from "@/components/hero-input";
import { useLanguage } from "@/context/language-context";
import { motion } from "framer-motion";
import dynamic from "next/dynamic";

const AnalysisView = dynamic(
  () => import("@/components/chat/analysis-view").then((mod) => mod.AnalysisView),
  {
    loading: () => <p className="text-center p-4 text-muted-foreground">Loading analysis view...</p>,
    ssr: false,
  }
);

export function AnalysisFeature() {
  const { analyze, output, toolCalls, isAnalyzing, error } = useAnalysis();
  const { t } = useLanguage();

  return (
    <div className="flex-1 flex flex-col items-center max-w-4xl mx-auto w-full">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-12"
      >
        <h1 
          className="text-4xl md:text-6xl font-extrabold text-transparent bg-clip-text mb-6 tracking-tight bg-linear-to-r from-foreground via-card-foreground to-foreground"
        >
          {t.hero.title}
        </h1>
        <p className="text-lg md:text-xl max-w-2xl mx-auto font-light text-muted-foreground">
          {t.hero.subtitle}
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="w-full"
      >
        <HeroInput onAnalyze={analyze} isLoading={isAnalyzing} />
      </motion.div>

      <AnalysisView output={output} toolCalls={toolCalls} isAnalyzing={isAnalyzing} error={error} />
    </div>
  );
}

