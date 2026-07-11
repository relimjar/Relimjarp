import { Ionicons } from "@expo/vector-icons";
import { useLocalSearchParams, useRouter } from "expo-router";
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
  bio?: string;
  native_accent?: string;
  rating?: number;
  reviews_count?: number;
  lessons_taught?: number;
  students_count?: number;
  specialties?: string[];
};

type Review = { id: string; name: string; date: string; text: string };

const FALLBACK_REVIEWS: Review[] = [
  {
    id: "r1",
    name: "Rachel M.",
    date: "November 12, 2023",
    text: "Working with Emily has been an absolute game-changer for me. Her tailored approach to teaching English within the medical domain is exceptional.",
  },
  {
    id: "r2",
    name: "Marco P.",
    date: "October 04, 2023",
    text: "Clear explanations, patient, and always prepared. My interview vocabulary improved massively.",
  },
];

export default function TutorDetail() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { id } = useLocalSearchParams<{ id: string }>();
  const [tutor, setTutor] = useState<ProTutor | null>(null);
  const [loading, setLoading] = useState(true);
  const { colors } = useLearnTheme();
  const s = useMemo(() => makeStyles(colors), [colors]);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const data = await api.get<ProTutor>(`/pro/tutors/${id}`);
        if (mounted) setTutor(data);
      } catch {
        if (mounted) setTutor(null);
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, [id]);

  if (loading) {
    return (
      <View style={{ flex: 1, backgroundColor: colors.bg, alignItems: "center", justifyContent: "center" }}>
        <ActivityIndicator color={colors.cardPurple} />
      </View>
    );
  }

  if (!tutor) {
    return (
      <View style={{ flex: 1, backgroundColor: colors.bg, alignItems: "center", justifyContent: "center", padding: 24 }}>
        <Text style={{ color: colors.textDim, textAlign: "center", marginBottom: 12 }}>Tutor not found.</Text>
        <Pressable onPress={() => router.back()} style={s.roundBtn}>
          <Ionicons name="arrow-back" size={20} color={colors.text} />
        </Pressable>
      </View>
    );
  }

  const rating = Math.round(tutor.rating ?? 5);
  const reviewsCount = tutor.reviews_count ?? 24;
  const bio =
    tutor.bio ||
    "I’m a dedicated English educator with over five years of experience specializing in teaching healthcare professionals, including doctors and nurses, the language skills essential for their professional success.";

  return (
    <View style={{ flex: 1, backgroundColor: colors.bg }}>
      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          paddingTop: insets.top + 8,
          paddingBottom: 40,
          paddingHorizontal: 18,
        }}
      >
        <View style={s.topBar}>
          <Pressable onPress={() => router.back()} style={s.roundBtn}>
            <Ionicons name="arrow-back" size={20} color={colors.text} />
          </Pressable>
          <View style={{ flexDirection: "row", gap: 10 }}>
            <Pressable style={s.roundBtn}>
              <Ionicons name="chatbubble-ellipses-outline" size={20} color={colors.text} />
            </Pressable>
            <Pressable style={s.roundBtn}>
              <Ionicons name="bookmark-outline" size={20} color={colors.text} />
            </Pressable>
          </View>
        </View>

        <View style={{ flexDirection: "row", alignItems: "center", marginTop: 16, marginBottom: 18 }}>
          <View style={s.avatarRing}>
            {tutor.avatar_url ? (
              <Image source={{ uri: tutor.avatar_url }} style={s.avatar} />
            ) : (
              <View style={[s.avatar, { backgroundColor: "#DAD1FF", alignItems: "center", justifyContent: "center" }]}>
                <Text style={{ fontSize: 26, fontWeight: "800", color: "#4B3F82" }}>
                  {tutor.name?.[0] ?? "?"}
                </Text>
              </View>
            )}
          </View>
          <View style={{ flex: 1, marginLeft: 14 }}>
            <Text style={s.name}>{tutor.name}</Text>
            <Text style={s.role}>
              {tutor.headline ||
                `Certified ${(tutor.native_accent || "English").toString().replace(/^./, (c) => c.toUpperCase())} Teacher`}
            </Text>
          </View>
        </View>

        <View style={{ flexDirection: "row", gap: 20, marginBottom: 20 }}>
          <View style={s.iconMeta}>
            <Ionicons name="school-outline" size={18} color={colors.text} />
            <Text style={s.iconMetaText}>{tutor.lessons_taught ?? 256} lessons</Text>
          </View>
          <View style={s.iconMeta}>
            <Ionicons name="people-outline" size={18} color={colors.text} />
            <Text style={s.iconMetaText}>{tutor.students_count ?? 32} students</Text>
          </View>
        </View>

        <View style={s.aboutCard}>
          <Text style={s.aboutTitle}>About me</Text>
          <Text style={s.aboutText}>{bio}</Text>
        </View>

        <Pressable style={({ pressed }) => [s.bookBtn, pressed && { opacity: 0.9 }]}>
          <Ionicons name="calendar-outline" size={18} color={colors.onLight} />
          <Text style={s.bookText}>Book lesson</Text>
        </Pressable>

        <View style={s.reviewsCard}>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 6, marginBottom: 12 }}>
            <Ionicons name="star" size={16} color="#0B0B0F" />
            <Text style={s.reviewsHeader}>
              {rating} · {reviewsCount} reviews
            </Text>
          </View>
          {FALLBACK_REVIEWS.map((r) => (
            <View key={r.id} style={s.reviewItem}>
              <View style={s.reviewAvatar}>
                <Text style={{ fontWeight: "800", color: "#4B3F82" }}>{r.name[0]}</Text>
              </View>
              <View style={{ flex: 1 }}>
                <Text style={s.reviewerName}>{r.name}</Text>
                <Text style={s.reviewDate}>{r.date}</Text>
                <Text style={s.reviewText}>{r.text}</Text>
              </View>
            </View>
          ))}
        </View>
      </ScrollView>
    </View>
  );
}

const makeStyles = (c: LearnPalette) =>
  StyleSheet.create({
    topBar: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
    roundBtn: {
      width: 44,
      height: 44,
      borderRadius: 22,
      backgroundColor: c.surfaceRaised,
      alignItems: "center",
      justifyContent: "center",
      borderWidth: c.mode === "light" ? 1 : 0,
      borderColor: c.border,
    },
    avatarRing: {
      width: 68,
      height: 68,
      borderRadius: 34,
      borderWidth: 2,
      borderColor: "#F0715C",
      overflow: "hidden",
    },
    avatar: { width: "100%", height: "100%" },
    name: { color: c.text, fontSize: 26, fontWeight: "800" },
    role: { color: c.textDim, fontSize: 14, marginTop: 2 },
    iconMeta: { flexDirection: "row", alignItems: "center", gap: 8 },
    iconMetaText: { color: c.text, fontSize: 14, fontWeight: "600" },
    aboutCard: {
      backgroundColor: c.mode === "dark" ? c.cardLight : "#FFFFFF",
      borderRadius: 22,
      padding: 18,
      marginBottom: 16,
      borderWidth: c.mode === "light" ? 1 : 0,
      borderColor: c.border,
    },
    aboutTitle: { color: c.onLight, fontSize: 18, fontWeight: "800", marginBottom: 10 },
    aboutText: { color: "#2A2A34", fontSize: 14, lineHeight: 22 },
    bookBtn: {
      backgroundColor: c.cardPurple,
      borderRadius: learnRadius.chip,
      paddingVertical: 16,
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "center",
      gap: 8,
      marginBottom: 16,
    },
    bookText: { color: c.onLight, fontSize: 16, fontWeight: "700" },
    reviewsCard: {
      backgroundColor: c.mode === "dark" ? c.cardLight : "#FFFFFF",
      borderRadius: 22,
      padding: 18,
      borderWidth: c.mode === "light" ? 1 : 0,
      borderColor: c.border,
    },
    reviewsHeader: { color: c.onLight, fontSize: 16, fontWeight: "800" },
    reviewItem: { flexDirection: "row", gap: 12, marginTop: 12 },
    reviewAvatar: {
      width: 34,
      height: 34,
      borderRadius: 17,
      backgroundColor: "#D8CBFF",
      alignItems: "center",
      justifyContent: "center",
    },
    reviewerName: { color: c.onLight, fontSize: 14, fontWeight: "700" },
    reviewDate: { color: "#6B6B75", fontSize: 12, marginBottom: 4 },
    reviewText: { color: "#2A2A34", fontSize: 13, lineHeight: 19 },
  });
