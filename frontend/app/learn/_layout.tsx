import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import React from "react";
import { View } from "react-native";

import { learnColors } from "@/src/learn/theme";

export default function LearnLayout() {
  return (
    <View style={{ flex: 1, backgroundColor: learnColors.bg }}>
      <StatusBar style="light" />
      <Stack
        screenOptions={{
          headerShown: false,
          contentStyle: { backgroundColor: learnColors.bg },
          animation: "fade",
        }}
      />
    </View>
  );
}
