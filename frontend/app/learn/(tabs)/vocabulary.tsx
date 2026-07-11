import { Ionicons } from "@expo/vector-icons";
import React, { useMemo, useState } from "react";
import { Pressable, ScrollView, StyleSheet, Text, TextInput, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { allTopics, exploreTopics } from "@/src/learn/data";
import { learnColors, learnRadius } from "@/src/learn/theme";

export default function VocabVocabulary() {
  const insets = useSafeAreaInsets();
  const [q, setQ] = useState("");

  const shown = useMemo(() => {
    const s = q.trim().toLowerCase();
    if (!s) return allTopics;
    return allTopics.filter((t) => t.name.toLowerCase().includes(s) || t.subtitle.toLowerCase().includes(s));
  }, [q]);

  // 2-column grid alternating purple/mint on chips; large cards keep lime
  const chipBgs = [learnColors.cardPurple, learnColors.cardMint, learnColors.cardPurpleSoft, learnColors.cardMintDeep];

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
        <View style={styles.searchPill}>
          <Ionicons name="search" size={18} color="#7A7A85" />
          <TextInput
            value={q}
            onChangeText={setQ}
            placeholder="Search topics"
            placeholderTextColor="#7A7A85"
            style={styles.searchInput}
          />
        </View>

        <Text style={styles.section}>Topics for you</Text>
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={{ paddingRight: 16, gap: 12 }}
          style={{ marginHorizontal: -18, paddingHorizontal: 18 }}
        >
          {exploreTopics.map((t, i) => (
            <View key={t.id} style={[styles.smallChip, { backgroundColor: chipBgs[i % chipBgs.length] }]}>
              <View style={styles.smallChipIcon}>
                <Ionicons name={t.icon} size={22} color={learnColors.onLight} />
              </View>
              <Text style={styles.smallChipText}>{t.name}</Text>
            </View>
          ))}
        </ScrollView>

        <Text style={styles.section}>All topics</Text>
        <View style={styles.grid}>
          {shown.map((t) => (
            <Pressable key={t.id} style={styles.tile}>
              <View style={styles.tileIcon}>
                <Ionicons name={t.icon} size={22} color={learnColors.onLight} />
              </View>
              <View>
                <Text style={styles.tileTitle}>{t.name}</Text>
                <Text style={styles.tileSub}>{t.subtitle}</Text>
              </View>
            </Pressable>
          ))}
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  searchPill: {
    backgroundColor: learnColors.cardLight,
    borderRadius: learnRadius.chip,
    paddingHorizontal: 18,
    height: 48,
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    marginBottom: 22,
  },
  searchInput: {
    flex: 1,
    color: learnColors.onLight,
    fontSize: 15,
    padding: 0,
  },
  section: {
    color: learnColors.text,
    fontSize: 22,
    fontWeight: "800",
    marginBottom: 14,
    marginTop: 4,
  },
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
  smallChipText: {
    color: learnColors.onLight,
    fontSize: 14,
    fontWeight: "700",
  },
  grid: {
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "space-between",
  },
  tile: {
    width: "48%",
    minHeight: 152,
    backgroundColor: learnColors.cardLime,
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
  tileTitle: {
    color: learnColors.onLight,
    fontSize: 17,
    fontWeight: "800",
    marginBottom: 2,
  },
  tileSub: {
    color: "#2A2A34",
    fontSize: 12,
    fontWeight: "500",
    lineHeight: 16,
  },
});
