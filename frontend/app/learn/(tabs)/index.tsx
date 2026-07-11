import { Ionicons } from "@expo/vector-icons";
import { useRouter } from "expo-router";
import React from "react";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { challenges, currentCourse, exploreTopics } from "@/src/learn/data";
import { learnColors, learnRadius } from "@/src/learn/theme";

export default function VocabHome() {
  const insets = useSafeAreaInsets();
  const router = useRouter();

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
        {/* In-progress card */}
        <View style={styles.progressCard}>
          <View style={styles.tagPill}>
            <Text style={styles.tagPillText}>{currentCourse.tag}</Text>
          </View>
          <Text style={styles.progressTitle}>{currentCourse.title}</Text>
          <View style={styles.progressTrack}>
            <View style={[styles.progressFill, { width: `${Math.max(6, Math.min(100, currentCourse.progress * 100))}%` }]} />
          </View>
          <Pressable
            style={({ pressed }) => [styles.continueBtn, pressed && { opacity: 0.9 }]}
            onPress={() => router.push("/learn/(tabs)/lessons")}
          >
            <Ionicons name="play" size={16} color="#FFFFFF" />
            <Text style={styles.continueText}>Continue lesson</Text>
          </Pressable>
        </View>

        {/* Explore topics */}
        <Text style={styles.section}>Explore topics</Text>
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
              style={styles.topicChip}
            >
              <View style={styles.topicIconWrap}>
                <Ionicons name={t.icon} size={22} color={learnColors.onLight} />
              </View>
              <Text style={styles.topicName}>{t.name}</Text>
            </Pressable>
          ))}
        </ScrollView>

        {/* Challenges */}
        <Text style={styles.section}>Challenges</Text>
        <View style={{ gap: 12 }}>
          {challenges.map((c) => (
            <Pressable key={c.id} style={styles.challengeCard}>
              <View style={styles.challengeIconBox}>
                <Ionicons name={c.icon} size={22} color="#FFFFFF" />
              </View>
              <View style={{ flex: 1 }}>
                <Text style={styles.challengeTitle}>{c.title}</Text>
                <Text style={styles.challengeSub}>{c.daysLeft} days left</Text>
              </View>
            </Pressable>
          ))}
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  progressCard: {
    backgroundColor: learnColors.cardPurple,
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
  tagPillText: {
    color: learnColors.onLight,
    fontSize: 12,
    fontWeight: "600",
  },
  progressTitle: {
    color: learnColors.onLight,
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
  progressFill: {
    height: "100%",
    backgroundColor: learnColors.onLight,
    borderRadius: 3,
  },
  continueBtn: {
    backgroundColor: learnColors.onLight,
    borderRadius: learnRadius.chip,
    paddingVertical: 14,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
  },
  continueText: {
    color: "#FFFFFF",
    fontSize: 15,
    fontWeight: "700",
  },
  section: {
    color: learnColors.text,
    fontSize: 20,
    fontWeight: "800",
    marginTop: 4,
    marginBottom: 14,
  },
  topicChip: {
    width: 116,
    height: 116,
    borderRadius: 22,
    backgroundColor: learnColors.cardMint,
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
  topicName: {
    color: learnColors.onLight,
    fontSize: 14,
    fontWeight: "700",
  },
  challengeCard: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: learnColors.cardCoral,
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
  challengeTitle: {
    color: "#0B0B0F",
    fontSize: 16,
    fontWeight: "800",
  },
  challengeSub: {
    color: "#0B0B0F",
    fontSize: 12,
    fontWeight: "600",
    opacity: 0.8,
    marginTop: 2,
  },
});
