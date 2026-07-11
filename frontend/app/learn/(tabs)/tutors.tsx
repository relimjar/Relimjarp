import { Ionicons } from "@expo/vector-icons";
import { useRouter } from "expo-router";
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
  native_accent?: string;
  rating?: number;
  reviews_count?: number;
  lessons_taught?: number;
  students_count?: number;
  specialties?: string[];
  is_online?: boolean;
  featured?: boolean;
};

const TUTOR_CARD_BGS = [learnColors.cardMint, learnColors.cardPurple, learnColors.cardLime];

export default function VocabTutors() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const [tutors, setTutors] = useState<ProTutor[]>([]);
  const [loading, setLoading] = useState(true);

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
    <View style={{ flex: 1, backgroundColor: learnColors.bg }}>
      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          paddingTop: insets.top + 16,
          paddingBottom: 40,
          paddingHorizontal: 18,
        }}
      >
        <Text style={styles.title}>Tutors for private online lessons</Text>

        <Pressable style={styles.filtersBtn}>
          <Ionicons name="options-outline" size={18} color={learnColors.onLight} />
          <Text style={styles.filtersText}>Filters</Text>
        </Pressable>

        <Text style={styles.section}>Top tutors for your level</Text>

        {loading ? (
          <View style={{ paddingVertical: 40, alignItems: "center" }}>
            <ActivityIndicator color={learnColors.cardPurple} />
          </View>
        ) : tutors.length === 0 ? (
          <View style={styles.emptyBox}>
            <Text style={styles.emptyText}>No tutors available yet. Check back soon.</Text>
          </View>
        ) : (
          <View style={{ gap: 14 }}>
            {tutors.slice(0, 12).map((t, idx) => (
              <View
                key={t.id}
                style={[styles.tutorCard, { backgroundColor: TUTOR_CARD_BGS[idx % TUTOR_CARD_BGS.length] }]}
              >
                <View style={styles.tutorTopRow}>
                  <View style={styles.avatarRing}>
                    {t.avatar_url ? (
                      <Image source={{ uri: t.avatar_url }} style={styles.avatar} />
                    ) : (
                      <View style={[styles.avatar, { backgroundColor: "#DAD1FF", alignItems: "center", justifyContent: "center" }]}>
                        <Text style={{ fontSize: 22, fontWeight: "800", color: "#4B3F82" }}>
                          {t.name?.[0] ?? "?"}
                        </Text>
                      </View>
                    )}
                  </View>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.tutorName}>{t.name}</Text>
                    <Text style={styles.tutorRole}>{t.headline || `Certified ${(t.native_accent || "English").toString().replace(/^./, (c) => c.toUpperCase())} Teacher`}</Text>
                  </View>
                </View>

                <View style={styles.metaRow}>
                  <Ionicons name="star" size={16} color="#0B0B0F" />
                  <Text style={styles.metaText}>
                    {(t.rating ?? 5).toFixed(0)} · {t.reviews_count ?? 24} reviews
                  </Text>
                </View>
                <View style={styles.metaRow}>
                  <View style={styles.metaItem}>
                    <Ionicons name="school-outline" size={16} color="#0B0B0F" />
                    <Text style={styles.metaText}>{t.lessons_taught ?? 256} lessons</Text>
                  </View>
                  <View style={styles.metaItem}>
                    <Ionicons name="people-outline" size={16} color="#0B0B0F" />
                    <Text style={styles.metaText}>{t.students_count ?? 32} students</Text>
                  </View>
                </View>

                <View style={styles.actionRow}>
                  <Pressable
                    style={({ pressed }) => [styles.bookBtn, pressed && { opacity: 0.9 }]}
                    onPress={() => router.push({ pathname: "/learn/tutor/[id]", params: { id: t.id } })}
                  >
                    <Ionicons name="calendar-outline" size={16} color="#FFFFFF" />
                    <Text style={styles.bookText}>Book lesson</Text>
                  </Pressable>
                  <Pressable style={styles.chatBtn}>
                    <Ionicons name="chatbubble-ellipses-outline" size={20} color={learnColors.onLight} />
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

const styles = StyleSheet.create({
  title: {
    color: learnColors.text,
    fontSize: 28,
    fontWeight: "800",
    lineHeight: 34,
    marginBottom: 20,
  },
  filtersBtn: {
    backgroundColor: learnColors.cardLight,
    borderRadius: learnRadius.chip,
    height: 52,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 10,
    marginBottom: 24,
  },
  filtersText: {
    color: learnColors.onLight,
    fontSize: 16,
    fontWeight: "700",
  },
  section: {
    color: learnColors.text,
    fontSize: 20,
    fontWeight: "800",
    marginBottom: 14,
  },
  tutorCard: {
    borderRadius: 24,
    padding: 14,
  },
  tutorTopRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    marginBottom: 12,
  },
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
  avatar: {
    width: 52,
    height: 52,
    borderRadius: 26,
  },
  tutorName: {
    color: learnColors.onLight,
    fontSize: 18,
    fontWeight: "800",
  },
  tutorRole: {
    color: "#2A2A34",
    fontSize: 13,
    fontWeight: "500",
    marginTop: 2,
  },
  metaRow: {
    flexDirection: "row",
    gap: 20,
    alignItems: "center",
    marginTop: 4,
    marginBottom: 6,
  },
  metaItem: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
  },
  metaText: {
    color: "#0B0B0F",
    fontSize: 13,
    fontWeight: "600",
  },
  actionRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    marginTop: 10,
  },
  bookBtn: {
    flex: 1,
    backgroundColor: learnColors.onLight,
    borderRadius: learnRadius.chip,
    paddingVertical: 14,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
  },
  bookText: {
    color: "#FFFFFF",
    fontSize: 15,
    fontWeight: "700",
  },
  chatBtn: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: "#FFFFFF",
    alignItems: "center",
    justifyContent: "center",
  },
  emptyBox: {
    backgroundColor: learnColors.surfaceRaised,
    borderRadius: 20,
    padding: 24,
    alignItems: "center",
  },
  emptyText: {
    color: learnColors.textDim,
    fontSize: 14,
    textAlign: "center",
  },
});
