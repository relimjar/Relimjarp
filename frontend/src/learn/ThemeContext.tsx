import AsyncStorage from "@react-native-async-storage/async-storage";
import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { darkPalette, LearnPalette, LearnThemeMode, lightPalette } from "@/src/learn/theme";

const STORAGE_KEY = "learn_theme_mode_v1";

type Ctx = {
  mode: LearnThemeMode;
  colors: LearnPalette;
  setMode: (m: LearnThemeMode) => void;
  toggle: () => void;
  ready: boolean;
};

const LearnThemeContext = createContext<Ctx | undefined>(undefined);

export function LearnThemeProvider({ children }: { children: React.ReactNode }) {
  const [mode, setModeState] = useState<LearnThemeMode>("dark");
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const raw = await AsyncStorage.getItem(STORAGE_KEY);
        if (!mounted) return;
        if (raw === "light" || raw === "dark") setModeState(raw);
      } catch {
        /* fallthrough */
      } finally {
        if (mounted) setReady(true);
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  const setMode = useCallback((m: LearnThemeMode) => {
    setModeState(m);
    AsyncStorage.setItem(STORAGE_KEY, m).catch(() => undefined);
  }, []);

  const toggle = useCallback(() => {
    setModeState((prev) => {
      const next: LearnThemeMode = prev === "dark" ? "light" : "dark";
      AsyncStorage.setItem(STORAGE_KEY, next).catch(() => undefined);
      return next;
    });
  }, []);

  const colors = mode === "dark" ? darkPalette : lightPalette;
  const value = useMemo<Ctx>(() => ({ mode, colors, setMode, toggle, ready }), [mode, colors, setMode, toggle, ready]);

  return <LearnThemeContext.Provider value={value}>{children}</LearnThemeContext.Provider>;
}

export function useLearnTheme(): Ctx {
  const ctx = useContext(LearnThemeContext);
  if (!ctx) {
    // Safe fallback for isolated tests / hot reload edge cases — return dark palette.
    return {
      mode: "dark",
      colors: darkPalette,
      setMode: () => undefined,
      toggle: () => undefined,
      ready: true,
    };
  }
  return ctx;
}
