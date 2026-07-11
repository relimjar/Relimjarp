import { Ionicons } from "@expo/vector-icons";
import { useRouter } from "expo-router";
import React, { useEffect, useMemo, useState } from "react";
import { ActivityIndicator, Image, Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { api } from "@/src/utils/api";
import { useLearnTheme } from "@/src/learn/ThemeContext";
import { learnRadius, LearnPalette } from "@/src/learn/theme";

type ProTutor = {
  id: string;
  name: string;
  avatar_url?: string | null;
  headline?: string;
  native_accent?: string;
  rating?: number;
  reviews_count?: number;
  lessons_taught?: number;
  students_count?: number;
  specialties?: string[];
  is_online?: boolean;
  featured?: boolean;
};

export default function VocabTutors() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { colors } = useLearnTheme();
  const s = useMemo(() => makeStyles(colors), [colors]);
  const [tutors, setTutors] = useState<ProTutor[]>([]);
  const [loading, setLoading] = useState(true);

  const cardBgs = [colors.cardMint, colors.cardPurple, colors.cardLime];

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const data = await api.get<ProTutor[]>("/pro/tutors");
        if (mounted) setTutors(Array.isArray(data) ? data : []);
      } catch {
        if (mounted) setTutors([]);
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <View style={{ flex: 1, backgroundColor: colors.bg }}>
      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          paddingTop: insets.top + 16,
          paddingBottom: 40,
          paddingHorizontal: 18,
        }}
      >
        <Text style={s.title}>Tutors for private online lessons</Text>

        <Pressable style={s.filtersBtn}>
          <Ionicons name="options-outline" size={18} color={colors.onLight} />
          <Text style={s.filtersText}>Filters</Text>
        </Pressable>

        <Text style={s.section}>Top tutors for your level</Text>

        {loading ? (
          <View style={{ paddingVertical: 40, alignItems: "center" }}>
            <ActivityIndicator color={colors.cardPurple} />
          </View>
        ) : tutors.length === 0 ? (
          <View style={s.emptyBox}>
            <Text style={s.emptyText}>No tutors available yet. Check back soon.</Text>
          </View>
        ) : (
          <View style={{ gap: 14 }}>
            {tutors.slice(0, 12).map((t, idx) => (
              <View
                key={t.id}
                style={[s.tutorCard, { backgroundColor: cardBgs[idx % cardBgs.length] }]}
              >
                <View style={s.tutorTopRow}>
                  <View style={s.avatarRing}>
                    {t.avatar_url ? (
                      <Image source={{ uri: t.avatar_url }} style={s.avatar} />
                    ) : (
                      <View style={[s.avatar, { backgroundColor: "#DAD1FF", alignItems: "center", justifyContent: "center" }]}>
                        <Text style={{ fontSize: 22, fontWeight: "800", color: "#4B3F82" }}>
                          {t.name?.[0] ?? "?"}
                        </Text>
                      </View>
                    )}
                  </View>
                  <View style={{ flex: 1 }}>
                    <Text style={s.tutorName}>{t.name}</Text>
                    <Text style={s.tutorRole}>
                      {t.headline ||
                        `Certified ${(t.native_accent || "English").toString().replace(/^./, (c) => c.toUpperCase())} Teacher`}
                    </Text>
                  </View>
                </View>

                <View style={s.metaRow}>
                  <Ionicons name="star" size={16} color="#0B0B0F" />
                  <Text style={s.metaText}>
                    {(t.rating ?? 5).toFixed(0)} · {t.reviews_count ?? 24} reviews
                  </Text>
                </View>
                <View style={s.metaRow}>
                  <View style={s.metaItem}>
                    <Ionicons name="school-outline" size={16} color="#0B0B0F" />
                    <Text style={s.metaText}>{t.lessons_taught ?? 256} lessons</Text>
                  </View>
                  <View style={s.metaItem}>
                    <Ionicons name="people-outline" size={16} color="#0B0B0F" />
                    <Text style={s.metaText}>{t.students_count ?? 32} students</Text>
                  </View>
                </View>

                <View style={s.actionRow}>
                  <Pressable
                    style={({ pressed }) => [s.bookBtn, pressed && { opacity: 0.9 }]}
                    onPress={() => router.push({ pathname: "/learn/tutor/[id]", params: { id: t.id } })}
                  >
                    <Ionicons name="calendar-outline" size={16} color="#FFFFFF" />
                    <Text style={s.bookText}>Book lesson</Text>
                  </Pressable>
                  <Pressable style={s.chatBtn}>
                    <Ionicons name="chatbubble-ellipses-outline" size={20} color={colors.onLight} />
                  </Pressable>
                </View>
              </View>
            ))}
          </View>
        )}
      </ScrollView>
    </View>
  );
}

const makeStyles = (c: LearnPalette) =>
  StyleSheet.create({
    title: { color: c.text, fontSize: 28, fontWeight: "800", lineHeight: 34, marginBottom: 20 },
    filtersBtn: {
      backgroundColor: c.mode === "dark" ? c.cardLight : "#FFFFFF",
      borderRadius: learnRadius.chip,
      height: 52,
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "center",
      gap: 10,
      marginBottom: 24,
      borderWidth: c.mode === "light" ? 1 : 0,
      borderColor: c.border,
    },
    filtersText: { color: c.onLight, fontSize: 16, fontWeight: "700" },
    section: { color: c.text, fontSize: 20, fontWeight: "800", marginBottom: 14 },
    tutorCard: { borderRadius: 24, padding: 14 },
    tutorTopRow: { flexDirection: "row", alignItems: "center", gap: 12, marginBottom: 12 },
    avatarRing: {
      width: 56,
      height: 56,
      borderRadius: 28,
      borderWidth: 2,
      borderColor: "#F0715C",
      alignItems: "center",
      justifyContent: "center",
      overflow: "hidden",
    },
    avatar: { width: 52, height: 52, borderRadius: 26 },
    tutorName: { color: c.onLight, fontSize: 18, fontWeight: "800" },
    tutorRole: { color: "#2A2A34", fontSize: 13, fontWeight: "500", marginTop: 2 },
    metaRow: {
      flexDirection: "row",
      gap: 20,
      alignItems: "center",
      marginTop: 4,
      marginBottom: 6,
    },
    metaItem: { flexDirection: "row", alignItems: "center", gap: 6 },
    metaText: { color: "#0B0B0F", fontSize: 13, fontWeight: "600" },
    actionRow: { flexDirection: "row", alignItems: "center", gap: 8, marginTop: 10 },
    bookBtn: {
      flex: 1,
      backgroundColor: c.onLight,
      borderRadius: learnRadius.chip,
      paddingVertical: 14,
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "center",
      gap: 8,
    },
    bookText: { color: "#FFFFFF", fontSize: 15, fontWeight: "700" },
    chatBtn: {
      width: 48,
      height: 48,
      borderRadius: 24,
      backgroundColor: "#FFFFFF",
      alignItems: "center",
      justifyContent: "center",
    },
    emptyBox: {
      backgroundColor: c.surfaceRaised,
      borderRadius: 20,
      padding: 24,
      alignItems: "center",
      borderWidth: c.mode === "light" ? 1 : 0,
      borderColor: c.border,
    },
    emptyText: { color: c.textDim, fontSize: 14, textAlign: "center" },
  });
