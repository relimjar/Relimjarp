import { Stack } from "expo-router";
import React from "react";
import { StatusBar } from "expo-status-bar";
import { View } from "react-native";

import { lessonColors } from "@/src/lessons/theme";

export default function LessonsLayout() {
  return (
    <View style={{ flex: 1, backgroundColor: lessonColors.bg }}>
      <StatusBar style="dark" />
      <Stack
        screenOptions={{
          headerShown: false,
          contentStyle: { backgroundColor: lessonColors.bg },
        }}
      >
        <Stack.Screen name="lesson/[id]" options={{ presentation: "fullScreenModal", animation: "slide_from_bottom" }} />
      </Stack>
    </View>
  );
}
