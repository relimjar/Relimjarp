import { Ionicons } from "@expo/vector-icons";
import { useRouter } from "expo-router";
import React, { useMemo } from "react";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { challenges, currentCourse, exploreTopics } from "@/src/learn/data";
import { useLearnTheme } from "@/src/learn/ThemeContext";
import { learnRadius, LearnPalette } from "@/src/learn/theme";

export default function VocabHome() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { colors, mode, toggle } = useLearnTheme();
  const s = useMemo(() => makeStyles(colors), [colors]);

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
        {/* Top row: greeting + theme toggle */}
        <View style={s.topRow}>
          <View>
            <Text style={s.hello}>Hey there 👋</Text>
            <Text style={s.subtitle}>Let’s learn something new today</Text>
          </View>
          <Pressable onPress={toggle} style={s.themeBtn} hitSlop={8}>
            <Ionicons name={mode === "dark" ? "sunny" : "moon"} size={18} color={colors.text} />
          </Pressable>
        </View>

        {/* In-progress card */}
        <View style={s.progressCard}>
          <View style={s.tagPill}>
            <Text style={s.tagPillText}>{currentCourse.tag}</Text>
          </View>
          <Text style={s.progressTitle}>{currentCourse.title}</Text>
          <View style={s.progressTrack}>
            <View style={[s.progressFill, { width: `${Math.max(6, Math.min(100, currentCourse.progress * 100))}%` }]} />
          </View>
          <Pressable
            style={({ pressed }) => [s.continueBtn, pressed && { opacity: 0.9 }]}
            onPress={() => router.push("/learn/(tabs)/lessons")}
          >
            <Ionicons name="play" size={16} color="#FFFFFF" />
            <Text style={s.continueText}>Continue lesson</Text>
          </Pressable>
        </View>

        <Text style={s.section}>Explore topics</Text>
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={{ paddingRight: 16, gap: 12 }}
          style={{ marginHorizontal: -18, paddingHorizontal: 18 }}
        >
          {exploreTopics.map((t) => (
            <Pressable
              key={t.id}
              onPress={() => router.push("/learn/(tabs)/vocabulary")}
              style={s.topicChip}
            >
              <View style={s.topicIconWrap}>
                <Ionicons name={t.icon} size={22} color={colors.onLight} />
              </View>
              <Text style={s.topicName}>{t.name}</Text>
            </Pressable>
          ))}
        </ScrollView>

        <Text style={s.section}>Challenges</Text>
        <View style={{ gap: 12 }}>
          {challenges.map((c) => (
            <Pressable key={c.id} style={s.challengeCard}>
              <View style={s.challengeIconBox}>
                <Ionicons name={c.icon} size={22} color="#FFFFFF" />
              </View>
              <View style={{ flex: 1 }}>
                <Text style={s.challengeTitle}>{c.title}</Text>
                <Text style={s.challengeSub}>{c.daysLeft} days left</Text>
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
    topRow: {
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "space-between",
      marginBottom: 18,
    },
    hello: { color: c.text, fontSize: 20, fontWeight: "800" },
    subtitle: { color: c.textDim, fontSize: 13, marginTop: 2 },
    themeBtn: {
      width: 40,
      height: 40,
      borderRadius: 20,
      backgroundColor: c.surfaceRaised,
      borderWidth: c.mode === "light" ? 1 : 0,
      borderColor: c.border,
      alignItems: "center",
      justifyContent: "center",
    },
    progressCard: {
      backgroundColor: c.cardPurple,
      borderRadius: learnRadius.lg,
      padding: 18,
      marginBottom: 22,
    },
    tagPill: {
      alignSelf: "flex-start",
      backgroundColor: "#F2F2F4",
      borderRadius: learnRadius.chip,
      paddingHorizontal: 12,
      paddingVertical: 4,
      marginBottom: 14,
    },
    tagPillText: { color: c.onLight, fontSize: 12, fontWeight: "600" },
    progressTitle: {
      color: c.onLight,
      fontSize: 22,
      fontWeight: "800",
      lineHeight: 28,
      marginBottom: 14,
    },
    progressTrack: {
      height: 6,
      borderRadius: 3,
      backgroundColor: "#F2F2F4",
      overflow: "hidden",
      marginBottom: 18,
    },
    progressFill: { height: "100%", backgroundColor: c.onLight, borderRadius: 3 },
    continueBtn: {
      backgroundColor: c.onLight,
      borderRadius: learnRadius.chip,
      paddingVertical: 14,
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "center",
      gap: 8,
    },
    continueText: { color: "#FFFFFF", fontSize: 15, fontWeight: "700" },
    section: {
      color: c.text,
      fontSize: 20,
      fontWeight: "800",
      marginTop: 4,
      marginBottom: 14,
    },
    topicChip: {
      width: 116,
      height: 116,
      borderRadius: 22,
      backgroundColor: c.cardMint,
      paddingHorizontal: 12,
      paddingVertical: 12,
      justifyContent: "space-between",
      marginBottom: 22,
    },
    topicIconWrap: {
      width: 40,
      height: 40,
      borderRadius: 20,
      backgroundColor: "rgba(255,255,255,0.55)",
      alignItems: "center",
      justifyContent: "center",
    },
    topicName: { color: c.onLight, fontSize: 14, fontWeight: "700" },
    challengeCard: {
      flexDirection: "row",
      alignItems: "center",
      backgroundColor: c.cardCoral,
      borderRadius: learnRadius.chip,
      paddingHorizontal: 14,
      paddingVertical: 14,
      gap: 14,
    },
    challengeIconBox: {
      width: 40,
      height: 40,
      borderRadius: 12,
      backgroundColor: "#0B0B0F",
      alignItems: "center",
      justifyContent: "center",
    },
    challengeTitle: { color: "#0B0B0F", fontSize: 16, fontWeight: "800" },
    challengeSub: {
      color: "#0B0B0F",
      fontSize: 12,
      fontWeight: "600",
      opacity: 0.8,
      marginTop: 2,
    },
  });
