"use client";

import React, { createContext, useContext, useState } from "react";
import Cookies from "js-cookie";
import { translations, Locale, Translation } from "@/lib/translations";

interface LanguageContextType {
  locale: Locale;
  t: Translation;
  setLocale: (locale: Locale) => void;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const getInitialLocale = (): Locale => {
    const savedLocale = Cookies.get("NEXT_LOCALE") as Locale;
    if (savedLocale && (savedLocale === "en" || savedLocale === "zh")) {
      return savedLocale;
    }
    if (typeof navigator !== "undefined") {
      return navigator.language.startsWith("zh") ? "zh" : "en";
    }
    return "en";
  };

  const [locale, setLocaleState] = useState<Locale>(getInitialLocale);

  const setLocale = (newLocale: Locale) => {
    setLocaleState(newLocale);
    Cookies.set("NEXT_LOCALE", newLocale, { expires: 365 });
  };

  const value = {
    locale,
    t: translations[locale],
    setLocale,
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error("useLanguage must be used within a LanguageProvider");
  }
  return context;
}

