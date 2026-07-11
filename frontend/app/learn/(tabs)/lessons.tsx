import { Ionicons } from "@expo/vector-icons";
import { useRouter } from "expo-router";
import React, { useMemo, useState } from "react";
import { Pressable, ScrollView, StyleSheet, Text, TextInput, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { lessons } from "@/src/learn/data";
import { learnColors, learnRadius } from "@/src/learn/theme";

export default function VocabLessons() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const [q, setQ] = useState("");
  const filtered = useMemo(() => {
    const s = q.trim().toLowerCase();
    if (!s) return lessons;
    return lessons.filter(
      (l) => l.title.toLowerCase().includes(s) || l.description.toLowerCase().includes(s),
    );
  }, [q]);

  return (
    <View style={{ flex: 1, backgroundColor: learnColors.bg }}>
      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          paddingTop: insets.top + 12,
          paddingBottom: 40,
          paddingHorizontal: 18,
        }}
      >
        {/* Search + Filter */}
        <View style={styles.searchRow}>
          <View style={styles.searchPill}>
            <Ionicons name="search" size={18} color="#7A7A85" />
            <TextInput
              value={q}
              onChangeText={setQ}
              placeholder="Search video lessons"
              placeholderTextColor="#7A7A85"
              style={styles.searchInput}
            />
          </View>
          <Pressable style={styles.filterBtn}>
            <Ionicons name="options-outline" size={20} color="#FFFFFF" />
          </Pressable>
        </View>

        <Text style={styles.section}>Lessons for you</Text>

        <View style={{ gap: 14 }}>
          {filtered.map((l) => (
            <View key={l.id} style={styles.lessonCard}>
              <Text style={styles.lessonTitle}>{l.title}</Text>
              <Text style={styles.lessonDesc}>{l.description}</Text>
              <View style={styles.metaRow}>
                <View style={styles.metaItem}>
                  <Ionicons name="time-outline" size={16} color="#0B0B0F" />
                  <Text style={styles.metaText}>{l.minutes} min</Text>
                </View>
                <View style={styles.metaItem}>
                  <Ionicons name="stats-chart" size={16} color="#0B0B0F" />
                  <Text style={styles.metaText}>{l.level}</Text>
                </View>
              </View>
              <Pressable
                style={({ pressed }) => [styles.startBtn, pressed && { opacity: 0.9 }]}
                onPress={() => router.push("/learn/(tabs)")}
              >
                <Ionicons name="play" size={16} color="#FFFFFF" />
                <Text style={styles.startText}>Start lesson</Text>
              </Pressable>
            </View>
          ))}
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  searchRow: {
    flexDirection: "row",
    gap: 10,
    marginBottom: 22,
    alignItems: "center",
  },
  searchPill: {
    flex: 1,
    backgroundColor: learnColors.cardLight,
    borderRadius: learnRadius.chip,
    paddingHorizontal: 18,
    height: 48,
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
  },
  searchInput: {
    flex: 1,
    color: learnColors.onLight,
    fontSize: 15,
    padding: 0,
  },
  filterBtn: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: learnColors.purple,
    alignItems: "center",
    justifyContent: "center",
  },
  section: {
    color: learnColors.text,
    fontSize: 22,
    fontWeight: "800",
    marginBottom: 16,
  },
  lessonCard: {
    backgroundColor: learnColors.cardLight,
    borderRadius: 24,
    padding: 18,
  },
  lessonTitle: {
    color: learnColors.onLight,
    fontSize: 20,
    fontWeight: "800",
    lineHeight: 26,
    marginBottom: 10,
  },
  lessonDesc: {
    color: "#3E3E48",
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 12,
  },
  metaRow: {
    flexDirection: "row",
    gap: 20,
    marginBottom: 14,
  },
  metaItem: {
    flexDirection: "row",
    alignItems: "center",
    gap: 5,
  },
  metaText: {
    color: "#0B0B0F",
    fontSize: 13,
    fontWeight: "600",
  },
  startBtn: {
    backgroundColor: learnColors.onLight,
    borderRadius: learnRadius.chip,
    paddingVertical: 14,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
  },
  startText: {
    color: "#FFFFFF",
    fontSize: 15,
    fontWeight: "700",
  },
});
