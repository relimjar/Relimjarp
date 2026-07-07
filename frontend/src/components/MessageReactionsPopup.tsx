import { Ionicons } from "@expo/vector-icons";
import * as Haptics from "expo-haptics";
import React, { useEffect, useState } from "react";
import { Dimensions, Modal, Pressable, StyleSheet, Text, View } from "react-native";
import Animated, {
  FadeIn,
  FadeInDown,
  FadeOut,
  ZoomIn,
} from "react-native-reanimated";

import { fonts, radius, spacing } from "@/src/theme";

/**
 * Instagram / HelloTalk-style reaction picker that pops above a long-pressed
 * message bubble. Shows 7 quick emojis + a "more" chip that expands to a full
 * 4x6 emoji grid, plus a compact context menu (Reply · Copy · Delete).
 */

export const QUICK_REACTIONS = ["❤️", "😂", "😮", "😢", "🙏", "👍", "🔥"];

const EXPANDED_EMOJIS = [
  "❤️", "😂", "😮", "😢", "😡", "👍", "👎", "🙏",
  "🔥", "🎉", "💯", "✨", "😍", "🥺", "😅", "😎",
  "🙌", "👏", "💜", "🥰", "🤗", "😴", "🤔", "🙄",
];

type MenuAction = "reply" | "copy" | "delete" | "translate" | "correct";

interface Props {
  visible: boolean;
  anchor: { x: number; y: number; width: number; height: number } | null;
  mine: boolean;
  hasText: boolean;
  currentReaction?: string;
  onClose: () => void;
  onReact: (emoji: string) => void;
  onAction: (action: MenuAction) => void;
}

export function MessageReactionsPopup({
  visible,
  anchor,
  mine,
  hasText,
  currentReaction,
  onClose,
  onReact,
  onAction,
}: Props) {
  const [expanded, setExpanded] = useState(false);
  const { width: screenW, height: screenH } = Dimensions.get("window");

  useEffect(() => {
    if (!visible) setExpanded(false);
  }, [visible]);

  if (!visible || !anchor) return null;

  const POPUP_WIDTH = expanded ? 300 : 306;
  const POPUP_HEIGHT = expanded ? 220 : 52;
  const MENU_HEIGHT = 168;

  // Position: prefer above the bubble; fall back below if too close to top.
  const centerX = anchor.x + anchor.width / 2;
  let popupLeft = centerX - POPUP_WIDTH / 2;
  popupLeft = Math.max(12, Math.min(popupLeft, screenW - POPUP_WIDTH - 12));

  const canFitAbove = anchor.y > POPUP_HEIGHT + MENU_HEIGHT + 40;
  const popupTop = canFitAbove
    ? anchor.y - POPUP_HEIGHT - 12
    : Math.min(anchor.y + anchor.height + 12, screenH - POPUP_HEIGHT - MENU_HEIGHT - 40);

  const menuTop = canFitAbove
    ? anchor.y + anchor.height + 10
    : popupTop + POPUP_HEIGHT + 10;
  const menuLeft = mine
    ? Math.max(12, anchor.x + anchor.width - 180)
    : Math.min(anchor.x, screenW - 192);

  const handleReact = (emoji: string) => {
    Haptics.selectionAsync().catch(() => {});
    onReact(emoji);
  };

  return (
    <Modal
      visible={visible}
      transparent
      animationType="none"
      onRequestClose={onClose}
    >
      <Pressable style={styles.backdrop} onPress={onClose}>
        {/* Reaction bar */}
        <Animated.View
          entering={ZoomIn.duration(180)}
          exiting={FadeOut.duration(120)}
          style={[
            styles.popup,
            { left: popupLeft, top: popupTop, width: POPUP_WIDTH },
          ]}
        >
          <Pressable onPress={(e) => e.stopPropagation?.()}>
            {!expanded ? (
              <View style={styles.reactionRow}>
                {QUICK_REACTIONS.map((emoji) => (
                  <Pressable
                    key={emoji}
                    testID={`reaction-${emoji}`}
                    onPress={() => handleReact(emoji)}
                    style={({ pressed }) => [
                      styles.reactionBtn,
                      currentReaction === emoji && styles.reactionActive,
                      pressed && styles.reactionPressed,
                    ]}
                    hitSlop={4}
                  >
                    <Text style={styles.reactionEmoji}>{emoji}</Text>
                  </Pressable>
                ))}
                <Pressable
                  testID="reaction-more"
                  onPress={() => {
                    Haptics.selectionAsync().catch(() => {});
                    setExpanded(true);
                  }}
                  style={styles.moreBtn}
                >
                  <Ionicons name="add" size={18} color="#5D4EE8" />
                </Pressable>
              </View>
            ) : (
              <Animated.View
                entering={FadeIn.duration(140)}
                style={styles.expandedGrid}
              >
                {EXPANDED_EMOJIS.map((emoji) => (
                  <Pressable
                    key={emoji}
                    testID={`reaction-full-${emoji}`}
                    onPress={() => handleReact(emoji)}
                    style={styles.gridBtn}
                  >
                    <Text style={styles.reactionEmoji}>{emoji}</Text>
                  </Pressable>
                ))}
              </Animated.View>
            )}
          </Pressable>
        </Animated.View>

        {/* Context menu */}
        <Animated.View
          entering={FadeInDown.duration(200)}
          exiting={FadeOut.duration(120)}
          style={[styles.menu, { left: menuLeft, top: menuTop }]}
        >
          <Pressable
            testID="msg-menu-reply"
            style={styles.menuItem}
            onPress={() => onAction("reply")}
          >
            <Ionicons name="arrow-undo" size={17} color="#1F2937" />
            <Text style={styles.menuText}>Reply</Text>
          </Pressable>
          {hasText && (
            <Pressable
              testID="msg-menu-copy"
              style={styles.menuItem}
              onPress={() => onAction("copy")}
            >
              <Ionicons name="copy-outline" size={17} color="#1F2937" />
              <Text style={styles.menuText}>Copy</Text>
            </Pressable>
          )}
          {hasText && !mine && (
            <Pressable
              testID="msg-menu-translate"
              style={styles.menuItem}
              onPress={() => onAction("translate")}
            >
              <Ionicons name="language" size={17} color="#1F2937" />
              <Text style={styles.menuText}>Translate</Text>
            </Pressable>
          )}
          {hasText && (
            <Pressable
              testID="msg-menu-correct"
              style={styles.menuItem}
              onPress={() => onAction("correct")}
            >
              <Ionicons name="school-outline" size={17} color="#1F2937" />
              <Text style={styles.menuText}>Correct</Text>
            </Pressable>
          )}
          {mine && (
            <Pressable
              testID="msg-menu-delete"
              style={styles.menuItem}
              onPress={() => onAction("delete")}
            >
              <Ionicons name="trash-outline" size={17} color="#EF4444" />
              <Text style={[styles.menuText, { color: "#EF4444" }]}>Delete</Text>
            </Pressable>
          )}
        </Animated.View>
      </Pressable>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: "rgba(15, 12, 40, 0.35)",
  },
  popup: {
    position: "absolute",
    backgroundColor: "#FFFFFF",
    borderRadius: 30,
    paddingHorizontal: 6,
    paddingVertical: 6,
    shadowColor: "#000",
    shadowOpacity: 0.18,
    shadowRadius: 18,
    shadowOffset: { width: 0, height: 8 },
    elevation: 12,
  },
  reactionRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 2,
  },
  reactionBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    alignItems: "center",
    justifyContent: "center",
  },
  reactionActive: {
    backgroundColor: "#EDE9FF",
    transform: [{ scale: 1.08 }],
  },
  reactionPressed: {
    transform: [{ scale: 0.85 }],
  },
  reactionEmoji: {
    fontSize: 24,
  },
  moreBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#F1EFFF",
    marginLeft: 2,
  },
  expandedGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "center",
    padding: 4,
    gap: 2,
  },
  gridBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: "center",
    justifyContent: "center",
  },
  menu: {
    position: "absolute",
    width: 180,
    backgroundColor: "#FFFFFF",
    borderRadius: radius.md,
    paddingVertical: 6,
    shadowColor: "#000",
    shadowOpacity: 0.15,
    shadowRadius: 16,
    shadowOffset: { width: 0, height: 6 },
    elevation: 10,
  },
  menuItem: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    paddingHorizontal: spacing.md,
    paddingVertical: 10,
  },
  menuText: {
    fontFamily: fonts.textSemi,
    fontSize: 14,
    color: "#1F2937",
  },
});
