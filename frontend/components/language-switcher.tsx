"use client";

import { useLanguage } from "@/context/language-context";
import { Globe } from "lucide-react";

export function LanguageSwitcher() {
  const { locale, setLocale } = useLanguage();

  return (
    <button
      onClick={() => setLocale(locale === "en" ? "zh" : "en")}
      className="flex items-center gap-2 px-3 py-1.5 rounded-full backdrop-blur-sm transition-all text-sm font-medium shadow-sm hover:shadow-md bg-card border border-border text-muted-foreground hover:bg-[rgba(255,255,255,0.8)] hover:text-foreground"
    >
      <Globe className="w-4 h-4" />
      <span>{locale === "en" ? "English" : "中文"}</span>
    </button>
  );
}
