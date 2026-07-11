import { Ionicons } from "@expo/vector-icons";
import React, { useMemo, useState } from "react";
import { Pressable, ScrollView, StyleSheet, Text, TextInput, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { allTopics, exploreTopics } from "@/src/learn/data";
import { useLearnTheme } from "@/src/learn/ThemeContext";
import { learnRadius, LearnPalette } from "@/src/learn/theme";

export default function VocabVocabulary() {
  const insets = useSafeAreaInsets();
  const [q, setQ] = useState("");
  const { colors } = useLearnTheme();
  const s = useMemo(() => makeStyles(colors), [colors]);

  const shown = useMemo(() => {
    const x = q.trim().toLowerCase();
    if (!x) return allTopics;
    return allTopics.filter((t) => t.name.toLowerCase().includes(x) || t.subtitle.toLowerCase().includes(x));
  }, [q]);

  const chipBgs = [colors.cardPurple, colors.cardMint, colors.cardPurpleSoft, colors.cardMintDeep];

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
        <View style={s.searchPill}>
          <Ionicons name="search" size={18} color="#7A7A85" />
          <TextInput
            value={q}
            onChangeText={setQ}
            placeholder="Search topics"
            placeholderTextColor="#7A7A85"
            style={s.searchInput}
          />
        </View>

        <Text style={s.section}>Topics for you</Text>
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={{ paddingRight: 16, gap: 12 }}
          style={{ marginHorizontal: -18, paddingHorizontal: 18 }}
        >
          {exploreTopics.map((t, i) => (
            <View key={t.id} style={[s.smallChip, { backgroundColor: chipBgs[i % chipBgs.length] }]}>
              <View style={s.smallChipIcon}>
                <Ionicons name={t.icon} size={22} color={colors.onLight} />
              </View>
              <Text style={s.smallChipText}>{t.name}</Text>
            </View>
          ))}
        </ScrollView>

        <Text style={s.section}>All topics</Text>
        <View style={s.grid}>
          {shown.map((t) => (
            <Pressable key={t.id} style={s.tile}>
              <View style={s.tileIcon}>
                <Ionicons name={t.icon} size={22} color={colors.onLight} />
              </View>
              <View>
                <Text style={s.tileTitle}>{t.name}</Text>
                <Text style={s.tileSub}>{t.subtitle}</Text>
              </View>
            </Pressable>
          ))}
        </View>
      </ScrollView>
    </View>
  );
}

const makeStyles = (c: LearnPalette) =>
  StyleSheet.create({
    searchPill: {
      backgroundColor: c.mode === "dark" ? c.cardLight : "#FFFFFF",
      borderRadius: learnRadius.chip,
      paddingHorizontal: 18,
      height: 48,
      flexDirection: "row",
      alignItems: "center",
      gap: 10,
      marginBottom: 22,
      borderWidth: c.mode === "light" ? 1 : 0,
      borderColor: c.border,
    },
    searchInput: { flex: 1, color: c.onLight, fontSize: 15, padding: 0 },
    section: { color: c.text, fontSize: 22, fontWeight: "800", marginBottom: 14, marginTop: 4 },
    smallChip: {
      width: 118,
      height: 118,
      borderRadius: 22,
      padding: 12,
      justifyContent: "space-between",
      marginBottom: 22,
    },
    smallChipIcon: {
      width: 40,
      height: 40,
      borderRadius: 20,
      backgroundColor: "rgba(255,255,255,0.55)",
      alignItems: "center",
      justifyContent: "center",
    },
    smallChipText: { color: c.onLight, fontSize: 14, fontWeight: "700" },
    grid: { flexDirection: "row", flexWrap: "wrap", justifyContent: "space-between" },
    tile: {
      width: "48%",
      minHeight: 152,
      backgroundColor: c.cardLime,
      borderRadius: 22,
      padding: 14,
      marginBottom: 12,
      justifyContent: "space-between",
    },
    tileIcon: {
      width: 42,
      height: 42,
      borderRadius: 21,
      backgroundColor: "rgba(255,255,255,0.45)",
      alignItems: "center",
      justifyContent: "center",
    },
    tileTitle: { color: c.onLight, fontSize: 17, fontWeight: "800", marginBottom: 2 },
    tileSub: { color: "#2A2A34", fontSize: 12, fontWeight: "500", lineHeight: 16 },
  });
