import React from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";

import { lessonColors, lessonFonts, lessonRadius } from "@/src/lessons/theme";

// Chunky "3D" push button with a darker bottom edge — the signature
// interactive element of the Lessons app.
export function ChunkyButton({
  label,
  onPress,
  color = lessonColors.green,
  edge,
  textColor = lessonColors.onGreen,
  disabled,
  testID,
  height = 52,
}: {
  label: string;
  onPress: () => void;
  color?: string;
  edge?: string;
  textColor?: string;
  disabled?: boolean;
  testID?: string;
  height?: number;
}) {
  const [pressed, setPressed] = React.useState(false);
  const edgeColor = edge || shade(color);
  return (
    <Pressable
      testID={testID}
      disabled={disabled}
      onPressIn={() => setPressed(true)}
      onPressOut={() => setPressed(false)}
      onPress={onPress}
      style={{ opacity: disabled ? 0.5 : 1 }}
    >
      <View style={[styles.edge, { backgroundColor: edgeColor, borderRadius: lessonRadius.md }]}>
        <View
          style={[
            styles.face,
            {
              backgroundColor: color,
              height,
              borderRadius: lessonRadius.md,
              transform: [{ translateY: pressed ? 4 : 0 }],
            },
          ]}
        >
          <Text style={[styles.label, { color: textColor }]}>{label}</Text>
        </View>
      </View>
    </Pressable>
  );
}

function shade(hex: string): string {
  // darken ~18% for the 3D edge
  const h = hex.replace("#", "");
  const n = parseInt(h.length === 3 ? h.split("").map((c) => c + c).join("") : h, 16);
  const r = Math.max(0, ((n >> 16) & 255) - 42);
  const g = Math.max(0, ((n >> 8) & 255) - 42);
  const b = Math.max(0, (n & 255) - 42);
  return `rgb(${r},${g},${b})`;
}

const styles = StyleSheet.create({
  edge: { paddingBottom: 4 },
  face: { alignItems: "center", justifyContent: "center", paddingHorizontal: 20 },
  label: { fontFamily: lessonFonts.black, fontSize: 16, letterSpacing: 0.5, textTransform: "uppercase" },
});
