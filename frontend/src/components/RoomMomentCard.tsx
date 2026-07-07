import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import React from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";

import { Avatar } from "@/src/components/Avatar";
import { FlagIcon } from "@/src/components/FlagIcon";
import { SpeakingBars } from "@/src/components/SpeakingBars";
import { countryToCode } from "@/src/constants/countries";
import { langName } from "@/src/constants/languages";
import { fonts, radius, spacing } from "@/src/theme";
import { RoomCardInfo } from "@/src/utils/api";

/**
 * Rich "live voice room" card used everywhere a room is embedded — Moments
 * feed, single moment detail, chat messages. Same visuals so users get an
 * instantly-recognisable "this is a voice room" card wherever they see it:
 * colorful gradient, LIVE bars while the room is ongoing, host avatar + name
 * inline, language flag, member count, and a big Join button.
 */
export const RoomMomentCard = ({
  room,
  onPress,
  testID,
  compact = false,
}: {
  room: RoomCardInfo;
  onPress: () => void;
  testID?: string;
  compact?: boolean;
}) => {
  const host = room.host;
  return (
    <Pressable testID={testID} disabled={!room.is_live} onPress={onPress}>
      <LinearGradient
        colors={room.is_live ? ["#6D5AE8", "#4B3F87"] : ["#9CA3AF", "#6B7280"]}
        style={[styles.card, compact && styles.cardCompact]}
      >
        <View style={styles.top}>
          {room.is_live ? (
            <View style={styles.liveBadge}>
              <SpeakingBars />
              <Text style={styles.liveText}>LIVE</Text>
            </View>
          ) : (
            <View style={styles.liveBadge}>
              <Ionicons name="mic-off" size={11} color="#FFFFFF" />
              <Text style={styles.liveText}>ROOM ENDED</Text>
            </View>
          )}
          {room.language ? (
            <View style={styles.langBadge}>
              <FlagIcon code={room.language} size={11} />
              <Text style={styles.langText}>{langName(room.language)}</Text>
            </View>
          ) : null}
        </View>

        {host && (
          <View style={styles.hostRow}>
            <Avatar
              name={host.name}
              url={host.avatar_url}
              size={compact ? 34 : 38}
              flagCode={countryToCode(host.country)}
            />
            <View style={{ flex: 1 }}>
              <Text style={styles.hostName} numberOfLines={1}>
                {host.name}
              </Text>
              <Text style={styles.hostRole} numberOfLines={1}>
                Host{room.topic ? ` · ${room.topic}` : ""}
              </Text>
            </View>
          </View>
        )}

        <Text style={styles.title} numberOfLines={2}>
          {room.title || "Voice room"}
        </Text>
        <View style={styles.bottom}>
          <Ionicons name="people" size={13} color="rgba(255,255,255,0.85)" />
          <Text style={styles.members}>
            {room.member_count || 0}{" "}
            {room.is_live ? "listening now" : "were in this room"}
          </Text>
          {room.is_live && (
            <View style={styles.joinBtn}>
              <Text style={styles.joinText}>Join</Text>
            </View>
          )}
        </View>
      </LinearGradient>
    </Pressable>
  );
};

const styles = StyleSheet.create({
  card: {
    borderRadius: radius.md,
    padding: spacing.lg,
    gap: spacing.sm,
  },
  cardCompact: {
    padding: spacing.md,
    gap: 8,
  },
  top: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  hostRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    paddingVertical: 2,
  },
  hostName: {
    fontFamily: fonts.textBold,
    fontSize: 13,
    color: "#FFFFFF",
  },
  hostRole: {
    fontFamily: fonts.textSemi,
    fontSize: 11,
    color: "rgba(255,255,255,0.78)",
    marginTop: 1,
  },
  liveBadge: {
    flexDirection: "row",
    alignItems: "center",
    gap: 5,
    backgroundColor: "rgba(0,0,0,0.28)",
    borderRadius: radius.pill,
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
  },
  liveText: {
    fontFamily: fonts.textBold,
    fontSize: 10,
    color: "#FFFFFF",
    letterSpacing: 0.6,
  },
  langBadge: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    backgroundColor: "rgba(255,255,255,0.2)",
    borderRadius: radius.pill,
    paddingHorizontal: spacing.sm,
    paddingVertical: 3,
  },
  langText: {
    fontFamily: fonts.textBold,
    fontSize: 10,
    color: "#FFFFFF",
  },
  title: {
    fontFamily: fonts.displaySemi,
    fontSize: 16,
    color: "#FFFFFF",
    lineHeight: 22,
  },
  bottom: {
    flexDirection: "row",
    alignItems: "center",
    gap: 5,
  },
  members: {
    flex: 1,
    fontFamily: fonts.textSemi,
    fontSize: 12,
    color: "rgba(255,255,255,0.85)",
  },
  joinBtn: {
    backgroundColor: "rgba(255,255,255,0.92)",
    borderRadius: radius.pill,
    paddingHorizontal: spacing.md,
    paddingVertical: 5,
  },
  joinText: {
    fontFamily: fonts.textBold,
    fontSize: 12,
    color: "#4B3F87",
  },
});
