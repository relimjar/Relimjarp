import { Ionicons } from "@expo/vector-icons";
import { useRouter } from "expo-router";
import React, { useMemo, useState } from "react";
import { Pressable, ScrollView, StyleSheet, Text, TextInput, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { lessons } from "@/src/learn/data";
import { useLearnTheme } from "@/src/learn/ThemeContext";
import { learnRadius, LearnPalette } from "@/src/learn/theme";

export default function VocabLessons() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const [q, setQ] = useState("");
  const { colors } = useLearnTheme();
  const s = useMemo(() => makeStyles(colors), [colors]);

  const filtered = useMemo(() => {
    const x = q.trim().toLowerCase();
    if (!x) return lessons;
    return lessons.filter(
      (l) => l.title.toLowerCase().includes(x) || l.description.toLowerCase().includes(x),
    );
  }, [q]);

  return (
    <View style={{ flex: 1, backgroundColor: colors.bg }}>
      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          paddingTop: insets.top + 12,
          paddingBottom: 40,
          paddingHorizontal: 18,
        }}
      >
        <View style={s.searchRow}>
          <View style={s.searchPill}>
            <Ionicons name="search" size={18} color="#7A7A85" />
            <TextInput
              value={q}
              onChangeText={setQ}
              placeholder="Search video lessons"
              placeholderTextColor="#7A7A85"
              style={s.searchInput}
            />
          </View>
          <Pressable style={s.filterBtn}>
            <Ionicons name="options-outline" size={20} color="#FFFFFF" />
          </Pressable>
        </View>

        <Text style={s.section}>Lessons for you</Text>

        <View style={{ gap: 14 }}>
          {filtered.map((l) => (
            <View key={l.id} style={s.lessonCard}>
              <Text style={s.lessonTitle}>{l.title}</Text>
              <Text style={s.lessonDesc}>{l.description}</Text>
              <View style={s.metaRow}>
                <View style={s.metaItem}>
                  <Ionicons name="time-outline" size={16} color="#0B0B0F" />
                  <Text style={s.metaText}>{l.minutes} min</Text>
                </View>
                <View style={s.metaItem}>
                  <Ionicons name="stats-chart" size={16} color="#0B0B0F" />
                  <Text style={s.metaText}>{l.level}</Text>
                </View>
              </View>
              <Pressable
                style={({ pressed }) => [s.startBtn, pressed && { opacity: 0.9 }]}
                onPress={() => router.push("/learn/(tabs)")}
              >
                <Ionicons name="play" size={16} color="#FFFFFF" />
                <Text style={s.startText}>Start lesson</Text>
              </Pressable>
            </View>
          ))}
        </View>
      </ScrollView>
    </View>
  );
}

const makeStyles = (c: LearnPalette) =>
  StyleSheet.create({
    searchRow: {
      flexDirection: "row",
      gap: 10,
      marginBottom: 22,
      alignItems: "center",
    },
    searchPill: {
      flex: 1,
      backgroundColor: c.mode === "dark" ? c.cardLight : "#FFFFFF",
      borderRadius: learnRadius.chip,
      paddingHorizontal: 18,
      height: 48,
      flexDirection: "row",
      alignItems: "center",
      gap: 10,
      borderWidth: c.mode === "light" ? 1 : 0,
      borderColor: c.border,
    },
    searchInput: { flex: 1, color: c.onLight, fontSize: 15, padding: 0 },
    filterBtn: {
      width: 48,
      height: 48,
      borderRadius: 24,
      backgroundColor: c.purple,
      alignItems: "center",
      justifyContent: "center",
    },
    section: { color: c.text, fontSize: 22, fontWeight: "800", marginBottom: 16 },
    lessonCard: {
      backgroundColor: c.mode === "dark" ? c.cardLight : "#FFFFFF",
      borderRadius: 24,
      padding: 18,
      borderWidth: c.mode === "light" ? 1 : 0,
      borderColor: c.border,
    },
    lessonTitle: {
      color: c.onLight,
      fontSize: 20,
      fontWeight: "800",
      lineHeight: 26,
      marginBottom: 10,
    },
    lessonDesc: { color: "#3E3E48", fontSize: 14, lineHeight: 20, marginBottom: 12 },
    metaRow: { flexDirection: "row", gap: 20, marginBottom: 14 },
    metaItem: { flexDirection: "row", alignItems: "center", gap: 5 },
    metaText: { color: "#0B0B0F", fontSize: 13, fontWeight: "600" },
    startBtn: {
      backgroundColor: c.onLight,
      borderRadius: learnRadius.chip,
      paddingVertical: 14,
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "center",
      gap: 8,
    },
    startText: { color: "#FFFFFF", fontSize: 15, fontWeight: "700" },
  });
