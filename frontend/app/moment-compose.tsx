import { Ionicons } from "@expo/vector-icons";
import { Image } from "expo-image";
import * as ImagePicker from "expo-image-picker";
import { useRouter } from "expo-router";
import React, { useMemo, useRef, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Animated,
  KeyboardAvoidingView,
  Modal,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { Avatar } from "@/src/components/Avatar";
import { BackButton } from "@/src/components/BackButton";
import { countryToCode } from "@/src/constants/countries";
import { useAuth } from "@/src/context/AuthContext";
import { useTheme } from "@/src/context/ThemeContext";
import { fonts, radius, spacing, ThemeColors } from "@/src/theme";
import { api } from "@/src/utils/api";

/**
 * Full-page moment composer.
 *
 * Layout — inspired by Twitter/Instagram post composers:
 *   • Header (avatar · name · Post button)
 *   • Big autofocused TextInput as the primary surface — the user starts by
 *     writing straight away.
 *   • Attachment previews slide in below the text (photo · poll · selected
 *     tag chips) as the user adds them.
 *   • Bottom action rail — Photo (+), Poll, Tags, Emoji, Location, GIF —
 *     tapping each opens the relevant surface.
 *
 * Tags remain hidden by default in a bottom-sheet picker; a chip row appears
 * only after the user has picked at least one, matching the request that
 * "tags stay hidden as a list, available on demand".
 */

const SUGGESTED_TAGS = [
  "language",
  "practice",
  "questions",
  "grammar",
  "culture",
  "travel",
  "music",
  "food",
  "study",
  "motivation",
  "meetnewfriends",
  "exchange",
];

export default function MomentComposeScreen() {
  const router = useRouter();
  const { colors } = useTheme();
  const { user } = useAuth();
  const styles = useMemo(() => makeStyles(colors), [colors]);
  const [text, setText] = useState("");
  const [photo, setPhoto] = useState<{ base64: string; uri: string; mime: string } | null>(null);
  const [tags, setTags] = useState<string[]>([]);
  const [customTag, setCustomTag] = useState("");
  const [tagSheetOpen, setTagSheetOpen] = useState(false);
  const [pollOpen, setPollOpen] = useState(false);
  const [pollOptions, setPollOptions] = useState<string[]>(["", ""]);
  const [posting, setPosting] = useState(false);
  const focusHint = useRef(new Animated.Value(0)).current;

  const pickPhoto = async () => {
    if (posting) return;
    if (Platform.OS !== "web") {
      const perm = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (!perm.granted) {
        Alert.alert(
          "Photos",
          "We need photo access to attach a picture. Enable it from Settings.",
        );
        return;
      }
    }
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ["images"],
      quality: 0.6,
      base64: true,
    });
    const asset = result.assets?.[0];
    if (result.canceled || !asset?.base64) return;
    setPhoto({
      base64: asset.base64,
      uri: asset.uri,
      mime: asset.mimeType || "image/jpeg",
    });
  };

  const toggleTag = (tag: string) => {
    setTags((prev) => {
      if (prev.includes(tag)) return prev.filter((t) => t !== tag);
      if (prev.length >= 8) return prev;
      return [...prev, tag];
    });
  };

  const addCustomTag = () => {
    const raw = customTag.trim().replace(/^#/, "").toLowerCase();
    const clean = raw.replace(/[^a-z0-9_]/g, "");
    if (!clean) return;
    if (!tags.includes(clean) && tags.length < 8) {
      setTags((prev) => [...prev, clean]);
    }
    setCustomTag("");
  };

  const setPollOption = (i: number, value: string) => {
    setPollOptions((prev) => prev.map((o, idx) => (idx === i ? value : o)));
  };

  const addPollOption = () => {
    if (pollOptions.length >= 4) return;
    setPollOptions((prev) => [...prev, ""]);
  };

  const removePollOption = (i: number) => {
    if (pollOptions.length <= 2) return;
    setPollOptions((prev) => prev.filter((_, idx) => idx !== i));
  };

  const removePoll = () => {
    setPollOpen(false);
    setPollOptions(["", ""]);
  };

  const publish = async () => {
    if (posting) return;
    const validPollOptions = pollOptions.map((o) => o.trim()).filter(Boolean);
    if (!text.trim() && !photo && !pollOpen) {
      Alert.alert("Nothing to post", "Add some text, a photo, or a poll.");
      return;
    }
    if (pollOpen && validPollOptions.length < 2) {
      Alert.alert("Poll", "Please fill in at least 2 poll options.");
      return;
    }
    setPosting(true);
    try {
      await api.post("/moments", {
        text: text.trim(),
        image_base64: photo?.base64,
        mime: photo?.mime,
        tags,
        poll: pollOpen
          ? {
              question: text.trim() || null,
              options: validPollOptions.map((t) => ({ text: t })),
            }
          : null,
      });
      router.back();
    } catch (e) {
      Alert.alert("Post", e instanceof Error ? e.message : "Could not post.");
    } finally {
      setPosting(false);
    }
  };

  const canPost =
    (text.trim().length > 0 || !!photo || pollOpen) && !posting;

  return (
    <SafeAreaView style={styles.screen} edges={["top", "bottom"]}>
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : undefined}
        style={{ flex: 1 }}
      >
        {/* Header */}
        <View style={styles.header}>
          <BackButton testID="compose-back-btn" />
          <Text style={styles.title}>New Moment</Text>
          <Pressable
            testID="compose-post-btn"
            onPress={publish}
            disabled={!canPost}
            style={[styles.postBtn, !canPost && { opacity: 0.4 }]}
          >
            {posting ? (
              <ActivityIndicator color="#FFFFFF" size="small" />
            ) : (
              <Text style={styles.postBtnText}>Post</Text>
            )}
          </Pressable>
        </View>

        <ScrollView
          contentContainerStyle={styles.body}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          {/* Author strip */}
          <View style={styles.authorRow}>
            <Avatar
              name={user?.name || ""}
              url={user?.avatar_url}
              size={40}
              flagCode={countryToCode(user?.country)}
            />
            <View style={{ flex: 1 }}>
              <Text style={styles.authorName}>{user?.name || "You"}</Text>
              <View style={styles.audiencePill}>
                <Ionicons name="earth" size={11} color={colors.brand} />
                <Text style={styles.audienceText}>Public — everyone can see</Text>
              </View>
            </View>
          </View>

          {/* Main text */}
          <TextInput
            testID="compose-text-input"
            style={styles.textInput}
            placeholder="What's on your mind? Share a story, ask a question, celebrate a win…"
            placeholderTextColor={colors.onSurfaceSecondary}
            value={text}
            onChangeText={setText}
            multiline
            maxLength={1000}
            autoFocus
          />

          {/* Photo preview */}
          {photo && (
            <View style={styles.photoBox}>
              <Image
                source={{ uri: photo.uri }}
                style={styles.photo}
                contentFit="cover"
              />
              <Pressable
                testID="compose-photo-remove-btn"
                style={styles.photoRemove}
                onPress={() => setPhoto(null)}
              >
                <Ionicons name="close" size={16} color="#FFF" />
              </Pressable>
            </View>
          )}

          {/* Poll editor */}
          {pollOpen && (
            <View style={styles.pollBox}>
              <View style={styles.pollHeader}>
                <Ionicons name="stats-chart" size={16} color={colors.brand} />
                <Text style={styles.pollHeaderText}>Poll</Text>
                <Pressable
                  testID="compose-poll-remove-btn"
                  onPress={removePoll}
                  hitSlop={8}
                >
                  <Ionicons name="close" size={18} color={colors.onSurfaceSecondary} />
                </Pressable>
              </View>
              {pollOptions.map((opt, i) => (
                <View key={i} style={styles.pollOptionRow}>
                  <View style={styles.pollOptionInputWrap}>
                    <Text style={styles.pollOptionIndex}>{i + 1}</Text>
                    <TextInput
                      testID={`compose-poll-option-${i}`}
                      style={styles.pollOptionInput}
                      placeholder={`Option ${i + 1}`}
                      placeholderTextColor={colors.onSurfaceSecondary}
                      value={opt}
                      onChangeText={(v) => setPollOption(i, v)}
                      maxLength={60}
                    />
                  </View>
                  {pollOptions.length > 2 && (
                    <Pressable
                      testID={`compose-poll-remove-option-${i}`}
                      onPress={() => removePollOption(i)}
                      hitSlop={8}
                    >
                      <Ionicons
                        name="close-circle"
                        size={20}
                        color={colors.onSurfaceSecondary}
                      />
                    </Pressable>
                  )}
                </View>
              ))}
              {pollOptions.length < 4 && (
                <Pressable
                  testID="compose-poll-add-option-btn"
                  onPress={addPollOption}
                  style={styles.pollAddBtn}
                >
                  <Ionicons name="add-circle" size={18} color={colors.brand} />
                  <Text style={styles.pollAddText}>Add option</Text>
                </Pressable>
              )}
            </View>
          )}

          {/* Selected tag chips */}
          {tags.length > 0 && (
            <View style={styles.chipRow}>
              {tags.map((t) => (
                <Pressable
                  key={t}
                  testID={`compose-tag-selected-${t}`}
                  onPress={() => toggleTag(t)}
                  style={styles.chipSelected}
                >
                  <Text style={styles.chipSelectedText}>#{t}</Text>
                  <Ionicons name="close" size={12} color="#FFFFFF" />
                </Pressable>
              ))}
            </View>
          )}
        </ScrollView>

        {/* Bottom action rail */}
        <View style={styles.actionRail}>
          <ActionBtn
            testID="compose-action-photo"
            icon="image"
            label="Photo"
            active={!!photo}
            onPress={pickPhoto}
            color={colors.brand}
          />
          <ActionBtn
            testID="compose-action-poll"
            icon="stats-chart"
            label="Poll"
            active={pollOpen}
            onPress={() => setPollOpen((v) => !v)}
            color="#F59E0B"
          />
          <ActionBtn
            testID="compose-action-tags"
            icon="pricetag"
            label={tags.length > 0 ? `Tags · ${tags.length}` : "Tags"}
            active={tags.length > 0}
            onPress={() => setTagSheetOpen(true)}
            color="#EC4899"
          />
          <View style={{ flex: 1 }} />
          <Text style={styles.counter}>{text.length}/1000</Text>
        </View>
      </KeyboardAvoidingView>

      {/* Tag picker bottom sheet */}
      <Modal
        visible={tagSheetOpen}
        transparent
        animationType="slide"
        onRequestClose={() => setTagSheetOpen(false)}
      >
        <Pressable
          style={styles.sheetBackdrop}
          onPress={() => setTagSheetOpen(false)}
        >
          <Pressable
            style={styles.sheet}
            onPress={(e) => e.stopPropagation?.()}
          >
            <View style={styles.sheetHandle} />
            <View style={styles.sheetHeader}>
              <Text style={styles.sheetTitle}>Add tags</Text>
              <Text style={styles.tagCounter}>{tags.length}/8</Text>
            </View>

            <Text style={styles.sheetSectionLabel}>Suggested</Text>
            <ScrollView
              style={{ maxHeight: 360 }}
              contentContainerStyle={{ paddingBottom: spacing.md }}
              showsVerticalScrollIndicator={false}
            >
              {SUGGESTED_TAGS.map((t) => {
                const selected = tags.includes(t);
                return (
                  <Pressable
                    key={t}
                    testID={`compose-tag-suggest-${t}`}
                    onPress={() => toggleTag(t)}
                    style={styles.tagListRow}
                  >
                    <Text style={styles.tagListText}>#{t}</Text>
                    {selected ? (
                      <Ionicons name="checkmark-circle" size={22} color={colors.brand} />
                    ) : (
                      <Ionicons
                        name="add-circle-outline"
                        size={22}
                        color={colors.onSurfaceSecondary}
                      />
                    )}
                  </Pressable>
                );
              })}
            </ScrollView>

            <View style={styles.customRow}>
              <View style={styles.customInputWrap}>
                <Text style={styles.hashPrefix}>#</Text>
                <TextInput
                  testID="compose-tag-custom-input"
                  style={styles.customInput}
                  value={customTag}
                  onChangeText={setCustomTag}
                  placeholder="add your own"
                  placeholderTextColor={colors.onSurfaceSecondary}
                  autoCapitalize="none"
                  onSubmitEditing={addCustomTag}
                  returnKeyType="done"
                  maxLength={30}
                />
              </View>
              <Pressable
                testID="compose-tag-add-btn"
                onPress={addCustomTag}
                disabled={!customTag.trim() || tags.length >= 8}
                style={[
                  styles.addTagBtn,
                  (!customTag.trim() || tags.length >= 8) && { opacity: 0.4 },
                ]}
              >
                <Ionicons name="add" size={22} color="#FFFFFF" />
              </Pressable>
            </View>

            <Pressable
              testID="compose-tag-sheet-done"
              onPress={() => setTagSheetOpen(false)}
              style={styles.sheetDoneBtn}
            >
              <Text style={styles.sheetDoneText}>Done</Text>
            </Pressable>
          </Pressable>
        </Pressable>
      </Modal>
    </SafeAreaView>
  );
}

const ActionBtn = ({
  icon,
  label,
  onPress,
  active,
  color,
  testID,
}: {
  icon: keyof typeof Ionicons.glyphMap;
  label: string;
  onPress: () => void;
  active?: boolean;
  color: string;
  testID: string;
}) => {
  const { colors } = useTheme();
  return (
    <Pressable
      testID={testID}
      onPress={onPress}
      style={({ pressed }) => [
        railStyles.btn,
        active && { backgroundColor: color + "22" },
        pressed && { opacity: 0.7 },
      ]}
      hitSlop={4}
    >
      <Ionicons name={icon} size={20} color={active ? color : colors.onSurface} />
      <Text
        style={[
          railStyles.label,
          { color: active ? color : colors.onSurface },
        ]}
        numberOfLines={1}
      >
        {label}
      </Text>
    </Pressable>
  );
};

const railStyles = StyleSheet.create({
  btn: {
    flexDirection: "row",
    alignItems: "center",
    gap: 5,
    paddingHorizontal: 10,
    paddingVertical: 8,
    borderRadius: 999,
  },
  label: { fontFamily: fonts.textBold, fontSize: 12 },
});

const makeStyles = (colors: ThemeColors) =>
  StyleSheet.create({
    screen: { flex: 1, backgroundColor: colors.background },
    header: {
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "space-between",
      paddingHorizontal: spacing.md,
      paddingVertical: spacing.sm,
      borderBottomWidth: StyleSheet.hairlineWidth,
      borderBottomColor: colors.border,
    },
    title: { fontFamily: fonts.displaySemi, fontSize: 17, color: colors.onSurface },
    postBtn: {
      backgroundColor: colors.brand,
      borderRadius: radius.pill,
      paddingHorizontal: spacing.lg,
      paddingVertical: 8,
      minWidth: 72,
      alignItems: "center",
    },
    postBtnText: { fontFamily: fonts.textBold, fontSize: 14, color: "#FFFFFF" },
    body: {
      padding: spacing.lg,
      paddingBottom: spacing.xxl,
      gap: spacing.md,
    },
    authorRow: {
      flexDirection: "row",
      alignItems: "center",
      gap: spacing.sm,
    },
    authorName: {
      fontFamily: fonts.textBold,
      fontSize: 15,
      color: colors.onSurface,
    },
    audiencePill: {
      flexDirection: "row",
      alignSelf: "flex-start",
      alignItems: "center",
      gap: 4,
      backgroundColor: colors.brandTertiary,
      paddingHorizontal: 8,
      paddingVertical: 3,
      borderRadius: 999,
      marginTop: 3,
    },
    audienceText: {
      fontFamily: fonts.textBold,
      fontSize: 11,
      color: colors.onBrandTertiary,
    },
    textInput: {
      minHeight: 130,
      fontFamily: fonts.textSemi,
      fontSize: 17,
      color: colors.onSurface,
      lineHeight: 24,
      textAlignVertical: "top",
      paddingTop: spacing.sm,
      ...(Platform.OS === "web" ? ({ outlineStyle: "none" } as object) : {}),
    },
    photoBox: {
      borderRadius: radius.md,
      overflow: "hidden",
      backgroundColor: colors.surfaceSecondary,
      aspectRatio: 4 / 3,
    },
    photo: { width: "100%", height: "100%" },
    photoRemove: {
      position: "absolute",
      top: 10,
      right: 10,
      width: 28,
      height: 28,
      borderRadius: 14,
      backgroundColor: "rgba(0,0,0,0.55)",
      alignItems: "center",
      justifyContent: "center",
    },
    pollBox: {
      backgroundColor: colors.surfaceSecondary,
      borderRadius: radius.md,
      padding: spacing.md,
      gap: spacing.sm,
    },
    pollHeader: {
      flexDirection: "row",
      alignItems: "center",
      gap: 6,
    },
    pollHeaderText: {
      fontFamily: fonts.textBold,
      fontSize: 13,
      color: colors.onSurface,
      textTransform: "uppercase",
      letterSpacing: 0.5,
      flex: 1,
    },
    pollOptionRow: {
      flexDirection: "row",
      alignItems: "center",
      gap: 6,
    },
    pollOptionInputWrap: {
      flex: 1,
      flexDirection: "row",
      alignItems: "center",
      backgroundColor: colors.surface,
      borderRadius: radius.pill,
      paddingHorizontal: 14,
      paddingVertical: 10,
      gap: 8,
    },
    pollOptionIndex: {
      fontFamily: fonts.textBold,
      fontSize: 12,
      color: colors.brand,
      width: 16,
    },
    pollOptionInput: {
      flex: 1,
      fontFamily: fonts.textSemi,
      fontSize: 14,
      color: colors.onSurface,
      padding: 0,
      ...(Platform.OS === "web" ? ({ outlineStyle: "none" } as object) : {}),
    },
    pollAddBtn: {
      flexDirection: "row",
      alignItems: "center",
      gap: 6,
      alignSelf: "flex-start",
      paddingVertical: 6,
      paddingHorizontal: 8,
    },
    pollAddText: {
      fontFamily: fonts.textBold,
      fontSize: 13,
      color: colors.brand,
    },
    chipRow: {
      flexDirection: "row",
      flexWrap: "wrap",
      gap: 6,
    },
    chipSelected: {
      flexDirection: "row",
      alignItems: "center",
      gap: 4,
      backgroundColor: colors.brand,
      borderRadius: radius.pill,
      paddingHorizontal: 12,
      paddingVertical: 6,
    },
    chipSelectedText: {
      fontFamily: fonts.textBold,
      fontSize: 12,
      color: "#FFFFFF",
    },
    actionRail: {
      flexDirection: "row",
      alignItems: "center",
      gap: 4,
      paddingHorizontal: spacing.md,
      paddingVertical: 8,
      borderTopWidth: StyleSheet.hairlineWidth,
      borderTopColor: colors.border,
      backgroundColor: colors.surface,
    },
    counter: {
      fontFamily: fonts.textSemi,
      fontSize: 11,
      color: colors.onSurfaceSecondary,
      paddingHorizontal: 6,
    },
    sheetBackdrop: {
      flex: 1,
      justifyContent: "flex-end",
      backgroundColor: "rgba(0,0,0,0.45)",
    },
    sheet: {
      backgroundColor: colors.surface,
      borderTopLeftRadius: 22,
      borderTopRightRadius: 22,
      paddingHorizontal: spacing.lg,
      paddingBottom: spacing.xl,
      paddingTop: spacing.sm,
      gap: spacing.sm,
    },
    sheetHandle: {
      alignSelf: "center",
      width: 40,
      height: 4,
      borderRadius: 2,
      backgroundColor: colors.borderStrong,
      marginBottom: spacing.sm,
    },
    sheetHeader: {
      flexDirection: "row",
      justifyContent: "space-between",
      alignItems: "center",
    },
    sheetTitle: {
      fontFamily: fonts.displaySemi,
      fontSize: 17,
      color: colors.onSurface,
    },
    tagCounter: {
      fontFamily: fonts.textSemi,
      fontSize: 12,
      color: colors.onSurfaceSecondary,
    },
    sheetSectionLabel: {
      fontFamily: fonts.textBold,
      fontSize: 11,
      color: colors.onSurfaceSecondary,
      textTransform: "uppercase",
      letterSpacing: 0.5,
    },
    tagListRow: {
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "space-between",
      paddingVertical: 12,
      borderBottomWidth: StyleSheet.hairlineWidth,
      borderBottomColor: colors.border,
    },
    tagListText: {
      fontFamily: fonts.textBold,
      fontSize: 15,
      color: colors.onSurface,
    },
    customRow: {
      flexDirection: "row",
      alignItems: "center",
      gap: 8,
      marginTop: 6,
    },
    customInputWrap: {
      flex: 1,
      flexDirection: "row",
      alignItems: "center",
      backgroundColor: colors.surfaceSecondary,
      borderRadius: radius.pill,
      paddingHorizontal: 14,
      paddingVertical: 10,
    },
    hashPrefix: {
      fontFamily: fonts.textBold,
      fontSize: 16,
      color: colors.brand,
      marginRight: 4,
    },
    customInput: {
      flex: 1,
      fontFamily: fonts.textSemi,
      fontSize: 14,
      color: colors.onSurface,
      padding: 0,
      ...(Platform.OS === "web" ? ({ outlineStyle: "none" } as object) : {}),
    },
    addTagBtn: {
      width: 42,
      height: 42,
      borderRadius: 21,
      backgroundColor: colors.brand,
      alignItems: "center",
      justifyContent: "center",
    },
    sheetDoneBtn: {
      alignSelf: "stretch",
      backgroundColor: colors.brand,
      borderRadius: radius.pill,
      paddingVertical: 12,
      alignItems: "center",
      marginTop: 6,
    },
    sheetDoneText: {
      fontFamily: fonts.textBold,
      fontSize: 15,
      color: "#FFFFFF",
    },
  });
