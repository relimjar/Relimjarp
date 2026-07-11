import { Ionicons } from "@expo/vector-icons";
import { useLocalSearchParams, useRouter } from "expo-router";
import React, { useEffect, useState } from "react";
import { ActivityIndicator, Image, Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { api } from "@/src/utils/api";
import { learnColors, learnRadius } from "@/src/learn/theme";

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

type Review = { id: string; name: string; date: string; text: string; avatar?: string };

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
      <View style={{ flex: 1, backgroundColor: learnColors.bg, alignItems: "center", justifyContent: "center" }}>
        <ActivityIndicator color={learnColors.cardPurple} />
      </View>
    );
  }

  if (!tutor) {
    return (
      <View style={{ flex: 1, backgroundColor: learnColors.bg, alignItems: "center", justifyContent: "center", padding: 24 }}>
        <Text style={{ color: learnColors.textDim, textAlign: "center", marginBottom: 12 }}>Tutor not found.</Text>
        <Pressable onPress={() => router.back()} style={styles.roundBtn}>
          <Ionicons name="arrow-back" size={20} color="#FFFFFF" />
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
    <View style={{ flex: 1, backgroundColor: learnColors.bg }}>
      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          paddingTop: insets.top + 8,
          paddingBottom: 40,
          paddingHorizontal: 18,
        }}
      >
        {/* Top bar */}
        <View style={styles.topBar}>
          <Pressable onPress={() => router.back()} style={styles.roundBtn}>
            <Ionicons name="arrow-back" size={20} color="#FFFFFF" />
          </Pressable>
          <View style={{ flexDirection: "row", gap: 10 }}>
            <Pressable style={styles.roundBtn}>
              <Ionicons name="chatbubble-ellipses-outline" size={20} color="#FFFFFF" />
            </Pressable>
            <Pressable style={styles.roundBtn}>
              <Ionicons name="bookmark-outline" size={20} color="#FFFFFF" />
            </Pressable>
          </View>
        </View>

        {/* Identity */}
        <View style={{ flexDirection: "row", alignItems: "center", marginTop: 16, marginBottom: 18 }}>
          <View style={styles.avatarRing}>
            {tutor.avatar_url ? (
              <Image source={{ uri: tutor.avatar_url }} style={styles.avatar} />
            ) : (
              <View style={[styles.avatar, { backgroundColor: "#DAD1FF", alignItems: "center", justifyContent: "center" }]}>
                <Text style={{ fontSize: 26, fontWeight: "800", color: "#4B3F82" }}>
                  {tutor.name?.[0] ?? "?"}
                </Text>
              </View>
            )}
          </View>
          <View style={{ flex: 1, marginLeft: 14 }}>
            <Text style={styles.name}>{tutor.name}</Text>
            <Text style={styles.role}>
              {tutor.headline ||
                `Certified ${(tutor.native_accent || "English").toString().replace(/^./, (c) => c.toUpperCase())} Teacher`}
            </Text>
          </View>
        </View>

        <View style={{ flexDirection: "row", gap: 20, marginBottom: 20 }}>
          <View style={styles.iconMeta}>
            <Ionicons name="school-outline" size={18} color="#FFFFFF" />
            <Text style={styles.iconMetaText}>{tutor.lessons_taught ?? 256} lessons</Text>
          </View>
          <View style={styles.iconMeta}>
            <Ionicons name="people-outline" size={18} color="#FFFFFF" />
            <Text style={styles.iconMetaText}>{tutor.students_count ?? 32} students</Text>
          </View>
        </View>

        {/* About me card */}
        <View style={styles.aboutCard}>
          <Text style={styles.aboutTitle}>About me</Text>
          <Text style={styles.aboutText}>{bio}</Text>
        </View>

        {/* Book lesson button */}
        <Pressable style={({ pressed }) => [styles.bookBtn, pressed && { opacity: 0.9 }]}>
          <Ionicons name="calendar-outline" size={18} color={learnColors.onLight} />
          <Text style={styles.bookText}>Book lesson</Text>
        </Pressable>

        {/* Reviews */}
        <View style={styles.reviewsCard}>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 6, marginBottom: 12 }}>
            <Ionicons name="star" size={16} color="#0B0B0F" />
            <Text style={styles.reviewsHeader}>
              {rating} · {reviewsCount} reviews
            </Text>
          </View>
          {FALLBACK_REVIEWS.map((r) => (
            <View key={r.id} style={styles.reviewItem}>
              <View style={styles.reviewAvatar}>
                <Text style={{ fontWeight: "800", color: "#4B3F82" }}>{r.name[0]}</Text>
              </View>
              <View style={{ flex: 1 }}>
                <Text style={styles.reviewerName}>{r.name}</Text>
                <Text style={styles.reviewDate}>{r.date}</Text>
                <Text style={styles.reviewText}>{r.text}</Text>
              </View>
            </View>
          ))}
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  topBar: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  roundBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: learnColors.surfaceRaised,
    alignItems: "center",
    justifyContent: "center",
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
  name: { color: learnColors.text, fontSize: 26, fontWeight: "800" },
  role: { color: learnColors.textDim, fontSize: 14, marginTop: 2 },
  iconMeta: { flexDirection: "row", alignItems: "center", gap: 8 },
  iconMetaText: { color: "#FFFFFF", fontSize: 14, fontWeight: "600" },
  aboutCard: {
    backgroundColor: learnColors.cardLight,
    borderRadius: 22,
    padding: 18,
    marginBottom: 16,
  },
  aboutTitle: {
    color: learnColors.onLight,
    fontSize: 18,
    fontWeight: "800",
    marginBottom: 10,
  },
  aboutText: {
    color: "#2A2A34",
    fontSize: 14,
    lineHeight: 22,
  },
  bookBtn: {
    backgroundColor: learnColors.cardPurple,
    borderRadius: learnRadius.chip,
    paddingVertical: 16,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
    marginBottom: 16,
  },
  bookText: {
    color: learnColors.onLight,
    fontSize: 16,
    fontWeight: "700",
  },
  reviewsCard: {
    backgroundColor: learnColors.cardLight,
    borderRadius: 22,
    padding: 18,
  },
  reviewsHeader: {
    color: learnColors.onLight,
    fontSize: 16,
    fontWeight: "800",
  },
  reviewItem: {
    flexDirection: "row",
    gap: 12,
    marginTop: 12,
  },
  reviewAvatar: {
    width: 34,
    height: 34,
    borderRadius: 17,
    backgroundColor: "#D8CBFF",
    alignItems: "center",
    justifyContent: "center",
  },
  reviewerName: { color: learnColors.onLight, fontSize: 14, fontWeight: "700" },
  reviewDate: { color: "#6B6B75", fontSize: 12, marginBottom: 4 },
  reviewText: { color: "#2A2A34", fontSize: 13, lineHeight: 19 },
});
