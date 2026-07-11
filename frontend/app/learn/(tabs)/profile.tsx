import { Ionicons } from "@expo/vector-icons";
import { useRouter } from "expo-router";
import React from "react";
import { Image, Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { useAuth } from "@/src/context/AuthContext";
import { learnColors, learnRadius } from "@/src/learn/theme";

type Stat = { label: string; value: string; icon: keyof typeof Ionicons.glyphMap };

export default function VocabProfile() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { user, logout } = useAuth();

  const stats: Stat[] = [
    { label: "Words learned", value: "128", icon: "reader-outline" },
    { label: "Lessons", value: "12", icon: "school-outline" },
    { label: "Streak", value: "3", icon: "flame-outline" },
    { label: "Rank", value: "Silver", icon: "trophy-outline" },
  ];

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
        <View style={styles.headerRow}>
          <View style={styles.avatarWrap}>
            {user?.avatar_url ? (
              <Image source={{ uri: user.avatar_url }} style={styles.avatar} />
            ) : (
              <View style={[styles.avatar, { backgroundColor: "#D8CBFF", alignItems: "center", justifyContent: "center" }]}>
                <Text style={{ fontSize: 32, fontWeight: "800", color: "#4B3F82" }}>
                  {user?.name?.[0] ?? "?"}
                </Text>
              </View>
            )}
          </View>
          <View style={{ flex: 1, marginLeft: 14 }}>
            <Text style={styles.name}>{user?.name || "Learner"}</Text>
            <Text style={styles.email}>{user?.email || ""}</Text>
          </View>
          <Pressable style={styles.settingsBtn} onPress={() => router.push("/(tabs)/me")}>
            <Ionicons name="settings-outline" size={20} color="#FFFFFF" />
          </Pressable>
        </View>

        <View style={styles.progressCard}>
          <View style={styles.tagPill}>
            <Text style={styles.tagPillText}>Level 2</Text>
          </View>
          <Text style={styles.progressTitle}>You’re doing great!</Text>
          <View style={styles.progressTrack}>
            <View style={[styles.progressFill, { width: `52%` }]} />
          </View>
          <Text style={styles.progressCaption}>52 XP to next level</Text>
        </View>

        <Text style={styles.section}>Stats</Text>
        <View style={styles.statsGrid}>
          {stats.map((s) => (
            <View key={s.label} style={styles.statCard}>
              <View style={styles.statIconWrap}>
                <Ionicons name={s.icon} size={20} color="#0B0B0F" />
              </View>
              <Text style={styles.statValue}>{s.value}</Text>
              <Text style={styles.statLabel}>{s.label}</Text>
            </View>
          ))}
        </View>

        <Text style={styles.section}>Settings</Text>
        <View style={styles.settingsList}>
          {[
            { icon: "notifications-outline", label: "Notifications" },
            { icon: "language-outline", label: "Language preferences" },
            { icon: "card-outline", label: "Subscription" },
            { icon: "help-circle-outline", label: "Help & support" },
          ].map((row) => (
            <Pressable key={row.label} style={styles.settingsRow}>
              <Ionicons name={row.icon as any} size={20} color="#FFFFFF" />
              <Text style={styles.settingsLabel}>{row.label}</Text>
              <Ionicons name="chevron-forward" size={18} color="#9A9AA5" style={{ marginLeft: "auto" }} />
            </Pressable>
          ))}
        </View>

        <Pressable
          style={({ pressed }) => [styles.logoutBtn, pressed && { opacity: 0.85 }]}
          onPress={() => logout()}
        >
          <Text style={styles.logoutText}>Log out</Text>
        </Pressable>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  headerRow: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 22,
  },
  avatarWrap: {
    width: 64,
    height: 64,
    borderRadius: 32,
    borderWidth: 2,
    borderColor: learnColors.cardPurple,
    overflow: "hidden",
  },
  avatar: { width: "100%", height: "100%" },
  name: { color: learnColors.text, fontSize: 20, fontWeight: "800" },
  email: { color: learnColors.textDim, fontSize: 13, marginTop: 2 },
  settingsBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: learnColors.surfaceRaised,
    alignItems: "center",
    justifyContent: "center",
  },
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
    marginBottom: 12,
  },
  tagPillText: { color: learnColors.onLight, fontSize: 12, fontWeight: "600" },
  progressTitle: { color: learnColors.onLight, fontSize: 22, fontWeight: "800", marginBottom: 14 },
  progressTrack: { height: 6, borderRadius: 3, backgroundColor: "#F2F2F4", overflow: "hidden" },
  progressFill: { height: "100%", backgroundColor: learnColors.onLight, borderRadius: 3 },
  progressCaption: { color: learnColors.onLight, fontSize: 12, fontWeight: "600", marginTop: 8 },
  section: {
    color: learnColors.text,
    fontSize: 20,
    fontWeight: "800",
    marginBottom: 14,
  },
  statsGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "space-between",
    marginBottom: 22,
  },
  statCard: {
    width: "48%",
    backgroundColor: learnColors.cardMint,
    borderRadius: 22,
    padding: 14,
    marginBottom: 12,
  },
  statIconWrap: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: "rgba(255,255,255,0.55)",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 12,
  },
  statValue: { color: learnColors.onLight, fontSize: 22, fontWeight: "800" },
  statLabel: { color: "#2A2A34", fontSize: 12, fontWeight: "600", marginTop: 2 },
  settingsList: {
    backgroundColor: learnColors.surfaceRaised,
    borderRadius: 22,
    paddingHorizontal: 6,
    paddingVertical: 4,
    marginBottom: 22,
  },
  settingsRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 14,
    paddingHorizontal: 12,
    paddingVertical: 14,
  },
  settingsLabel: { color: "#FFFFFF", fontSize: 15, fontWeight: "600" },
  logoutBtn: {
    backgroundColor: learnColors.surfaceRaised,
    borderRadius: learnRadius.chip,
    paddingVertical: 14,
    alignItems: "center",
  },
  logoutText: { color: "#F0715C", fontSize: 15, fontWeight: "700" },
});
