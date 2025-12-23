"use client";

import { useState } from "react";
import { ArrowRight, Search } from "lucide-react";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/context/language-context";

interface HeroInputProps {
  onAnalyze: (url: string) => void;
  isLoading: boolean;
}

export function HeroInput({ onAnalyze, isLoading }: HeroInputProps) {
  const [url, setUrl] = useState("");
  const [isValid, setIsValid] = useState(true);
  const { t } = useLanguage();

  const validateUrl = (value: string) => {
    if (!value) return true;
    try {
      const parsed = new URL(value);
      return parsed.hostname === "github.com";
    } catch {
      return false;
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setUrl(value);
    setIsValid(validateUrl(value));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim() && isValid) {
      onAnalyze(url.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto relative group">
      <div 
        className={cn(
          "absolute -inset-0.5 rounded-xl opacity-30 group-hover:opacity-60 transition duration-500 blur bg-linear-to-r from-tool-pulse to-secondary",
          isLoading && "animate-pulse opacity-70"
        )}
      />
      <div 
        className={cn(
          "relative flex items-center rounded-xl shadow-xl overflow-hidden bg-card transition-colors",
          !isValid && "ring-2 ring-red-500"
        )}
      >
        <div className="pl-4 text-muted-foreground">
          <Search className="w-5 h-5" />
        </div>
        <input
          type="text"
          value={url}
          onChange={handleChange}
          placeholder={t.hero.placeholder}
          disabled={isLoading}
          className="w-full px-4 py-4 bg-transparent border-none outline-none font-medium text-foreground placeholder:text-muted-foreground/50"
        />
        <button
          type="submit"
          disabled={!url.trim() || isLoading || !isValid}
          className="m-2 p-2 rounded-lg transition-colors disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary-hover disabled:hover:bg-primary"
        >
          <ArrowRight className={cn("w-5 h-5", isLoading && "animate-spin")} />
        </button>
      </div>
      {!isValid && url && (
        <p className="absolute -bottom-6 left-0 text-xs text-red-500 ml-1">
          Please enter a valid GitHub URL
        </p>
      )}
    </form>
  );
}
