import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import React from "react";
import { View } from "react-native";

import { LearnThemeProvider, useLearnTheme } from "@/src/learn/ThemeContext";

function Shell() {
  const { colors, mode } = useLearnTheme();
  return (
    <View style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar style={mode === "dark" ? "light" : "dark"} />
      <Stack
        screenOptions={{
          headerShown: false,
          contentStyle: { backgroundColor: colors.bg },
          animation: "fade",
        }}
      />
    </View>
  );
}

export default function LearnLayout() {
  return (
    <LearnThemeProvider>
      <Shell />
    </LearnThemeProvider>
  );
}
