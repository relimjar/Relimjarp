import { Ionicons } from "@expo/vector-icons";
import { useRouter } from "expo-router";
import React, { useMemo } from "react";
import { Image, Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { useAuth } from "@/src/context/AuthContext";
import { useLearnTheme } from "@/src/learn/ThemeContext";
import { learnRadius, LearnPalette } from "@/src/learn/theme";

type Stat = { label: string; value: string; icon: keyof typeof import("@expo/vector-icons").Ionicons.glyphMap };

export default function VocabProfile() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { user, logout } = useAuth();
  const { colors, mode, toggle } = useLearnTheme();
  const s = useMemo(() => makeStyles(colors), [colors]);

  const stats: Stat[] = [
    { label: "Words learned", value: "128", icon: "reader-outline" },
    { label: "Lessons", value: "12", icon: "school-outline" },
    { label: "Streak", value: "3", icon: "flame-outline" },
    { label: "Rank", value: "Silver", icon: "trophy-outline" },
  ];

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
        <View style={s.headerRow}>
          <View style={s.avatarWrap}>
            {user?.avatar_url ? (
              <Image source={{ uri: user.avatar_url }} style={s.avatar} />
            ) : (
              <View style={[s.avatar, { backgroundColor: "#D8CBFF", alignItems: "center", justifyContent: "center" }]}>
                <Text style={{ fontSize: 32, fontWeight: "800", color: "#4B3F82" }}>
                  {user?.name?.[0] ?? "?"}
                </Text>
              </View>
            )}
          </View>
          <View style={{ flex: 1, marginLeft: 14 }}>
            <Text style={s.name}>{user?.name || "Learner"}</Text>
            <Text style={s.email}>{user?.email || ""}</Text>
          </View>
          <Pressable style={s.settingsBtn} onPress={toggle} hitSlop={8}>
            <Ionicons name={mode === "dark" ? "sunny" : "moon"} size={20} color={colors.text} />
          </Pressable>
        </View>

        <View style={s.progressCard}>
          <View style={s.tagPill}>
            <Text style={s.tagPillText}>Level 2</Text>
          </View>
          <Text style={s.progressTitle}>You’re doing great!</Text>
          <View style={s.progressTrack}>
            <View style={[s.progressFill, { width: `52%` }]} />
          </View>
          <Text style={s.progressCaption}>52 XP to next level</Text>
        </View>

        <Text style={s.section}>Stats</Text>
        <View style={s.statsGrid}>
          {stats.map((st) => (
            <View key={st.label} style={s.statCard}>
              <View style={s.statIconWrap}>
                <Ionicons name={st.icon} size={20} color="#0B0B0F" />
              </View>
              <Text style={s.statValue}>{st.value}</Text>
              <Text style={s.statLabel}>{st.label}</Text>
            </View>
          ))}
        </View>

        <Text style={s.section}>Appearance</Text>
        <View style={s.settingsList}>
          <Pressable style={s.settingsRow} onPress={toggle}>
            <Ionicons name={mode === "dark" ? "moon" : "sunny"} size={20} color={colors.text} />
            <Text style={s.settingsLabel}>Theme</Text>
            <View style={s.modePillWrap}>
              <View style={[s.modePill, mode === "light" && s.modePillActive]}>
                <Text style={[s.modePillText, mode === "light" && s.modePillTextActive]}>Light</Text>
              </View>
              <View style={[s.modePill, mode === "dark" && s.modePillActive]}>
                <Text style={[s.modePillText, mode === "dark" && s.modePillTextActive]}>Dark</Text>
              </View>
            </View>
          </Pressable>
        </View>

        <Text style={s.section}>Settings</Text>
        <View style={s.settingsList}>
          {[
            { icon: "notifications-outline", label: "Notifications" },
            { icon: "language-outline", label: "Language preferences" },
            { icon: "card-outline", label: "Subscription" },
            { icon: "help-circle-outline", label: "Help & support" },
          ].map((row) => (
            <Pressable key={row.label} style={s.settingsRow}>
              <Ionicons name={row.icon as any} size={20} color={colors.text} />
              <Text style={s.settingsLabel}>{row.label}</Text>
              <Ionicons name="chevron-forward" size={18} color={colors.textDim} style={{ marginLeft: "auto" }} />
            </Pressable>
          ))}
        </View>

        <Pressable
          style={({ pressed }) => [s.logoutBtn, pressed && { opacity: 0.85 }]}
          onPress={() => logout()}
        >
          <Text style={s.logoutText}>Log out</Text>
        </Pressable>
      </ScrollView>
    </View>
  );
}

const makeStyles = (c: LearnPalette) =>
  StyleSheet.create({
    headerRow: { flexDirection: "row", alignItems: "center", marginBottom: 22 },
    avatarWrap: {
      width: 64,
      height: 64,
      borderRadius: 32,
      borderWidth: 2,
      borderColor: c.cardPurple,
      overflow: "hidden",
    },
    avatar: { width: "100%", height: "100%" },
    name: { color: c.text, fontSize: 20, fontWeight: "800" },
    email: { color: c.textDim, fontSize: 13, marginTop: 2 },
    settingsBtn: {
      width: 44,
      height: 44,
      borderRadius: 22,
      backgroundColor: c.surfaceRaised,
      alignItems: "center",
      justifyContent: "center",
      borderWidth: c.mode === "light" ? 1 : 0,
      borderColor: c.border,
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
      marginBottom: 12,
    },
    tagPillText: { color: c.onLight, fontSize: 12, fontWeight: "600" },
    progressTitle: { color: c.onLight, fontSize: 22, fontWeight: "800", marginBottom: 14 },
    progressTrack: {
      height: 6,
      borderRadius: 3,
      backgroundColor: "#F2F2F4",
      overflow: "hidden",
    },
    progressFill: { height: "100%", backgroundColor: c.onLight, borderRadius: 3 },
    progressCaption: {
      color: c.onLight,
      fontSize: 12,
      fontWeight: "600",
      marginTop: 8,
    },
    section: { color: c.text, fontSize: 20, fontWeight: "800", marginBottom: 14 },
    statsGrid: {
      flexDirection: "row",
      flexWrap: "wrap",
      justifyContent: "space-between",
      marginBottom: 22,
    },
    statCard: {
      width: "48%",
      backgroundColor: c.cardMint,
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
    statValue: { color: c.onLight, fontSize: 22, fontWeight: "800" },
    statLabel: { color: "#2A2A34", fontSize: 12, fontWeight: "600", marginTop: 2 },
    settingsList: {
      backgroundColor: c.surfaceRaised,
      borderRadius: 22,
      paddingHorizontal: 6,
      paddingVertical: 4,
      marginBottom: 22,
      borderWidth: c.mode === "light" ? 1 : 0,
      borderColor: c.border,
    },
    settingsRow: {
      flexDirection: "row",
      alignItems: "center",
      gap: 14,
      paddingHorizontal: 12,
      paddingVertical: 14,
    },
    settingsLabel: { color: c.text, fontSize: 15, fontWeight: "600" },
    modePillWrap: {
      marginLeft: "auto",
      flexDirection: "row",
      backgroundColor: c.mode === "dark" ? "#0B0B0F" : "#EDEDF1",
      borderRadius: 999,
      padding: 3,
      gap: 2,
    },
    modePill: {
      paddingHorizontal: 12,
      paddingVertical: 5,
      borderRadius: 999,
    },
    modePillActive: { backgroundColor: c.cardPurple },
    modePillText: {
      fontSize: 12,
      fontWeight: "700",
      color: c.mode === "dark" ? "#9A9AA5" : "#5A5A63",
    },
    modePillTextActive: { color: "#0B0B0F" },
    logoutBtn: {
      backgroundColor: c.surfaceRaised,
      borderRadius: learnRadius.chip,
      paddingVertical: 14,
      alignItems: "center",
      borderWidth: c.mode === "light" ? 1 : 0,
      borderColor: c.border,
    },
    logoutText: { color: "#F0715C", fontSize: 15, fontWeight: "700" },
  });
