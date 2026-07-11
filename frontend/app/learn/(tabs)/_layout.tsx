import { MaterialCommunityIcons } from "@expo/vector-icons";
import { Tabs } from "expo-router";
import React from "react";
import { Platform, Pressable, StyleSheet, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { useLearnTheme } from "@/src/learn/ThemeContext";

type MciIcon = keyof typeof MaterialCommunityIcons.glyphMap;

type TabDef = {
  name: string;
  label: string;
  icon: MciIcon;
  iconActive: MciIcon;
};

const TABS: TabDef[] = [
  { name: "index", label: "Home", icon: "home-outline", iconActive: "home" },
  { name: "lessons", label: "Lessons", icon: "play-box-outline", iconActive: "play-box" },
  { name: "vocabulary", label: "Vocabulary", icon: "book-outline", iconActive: "book" },
  { name: "tutors", label: "Tutors", icon: "emoticon-happy-outline", iconActive: "emoticon-happy" },
  { name: "profile", label: "Profile", icon: "account-box-outline", iconActive: "account-box" },
];

function VocabTabBar({ state, navigation }: any) {
  const insets = useSafeAreaInsets();
  const { colors } = useLearnTheme();
  const bottomGap = Math.max(insets.bottom, 8);
  return (
    <View style={[styles.barWrap, { paddingBottom: bottomGap, backgroundColor: colors.tabBg }]}>
      <View style={styles.bar}>
        {state.routes.map((route: any, index: number) => {
          const def = TABS.find((t) => t.name === route.name);
          if (!def) return null;
          const focused = state.index === index;
          const onPress = () => {
            const event = navigation.emit({
              type: "tabPress",
              target: route.key,
              canPreventDefault: true,
            });
            if (!focused && !event.defaultPrevented) {
              navigation.navigate(route.name);
            }
          };
          const iconColor = focused ? colors.tabActiveText : colors.tabInactive;
          const labelColor = focused ? colors.tabActivePill : colors.tabInactiveLabel;
          return (
            <Pressable
              key={route.key}
              onPress={onPress}
              android_ripple={{ color: "transparent" }}
              hitSlop={8}
              style={styles.tabBtn}
            >
              <View
                style={[
                  styles.iconPill,
                  focused && { backgroundColor: colors.tabActivePill },
                ]}
              >
                <MaterialCommunityIcons
                  name={focused ? def.iconActive : def.icon}
                  size={22}
                  color={iconColor}
                />
              </View>
              <Text
                numberOfLines={1}
                style={[styles.label, { color: labelColor, fontWeight: focused ? "700" : "500" }]}
              >
                {def.label}
              </Text>
            </Pressable>
          );
        })}
      </View>
    </View>
  );
}

export default function VocabTabsLayout() {
  const { colors } = useLearnTheme();
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        sceneStyle: { backgroundColor: colors.bg },
      } as any}
      tabBar={(props) => <VocabTabBar {...props} />}
    >
      {TABS.map((t) => (
        <Tabs.Screen key={t.name} name={t.name} options={{ title: t.label }} />
      ))}
    </Tabs>
  );
}

const styles = StyleSheet.create({
  barWrap: {
    borderTopWidth: 0,
  },
  bar: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-around",
    paddingHorizontal: 4,
    paddingTop: 6,
    paddingBottom: 2,
  },
  tabBtn: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 2,
    gap: 2,
  },
  iconPill: {
    width: 44,
    height: 28,
    borderRadius: 14,
    alignItems: "center",
    justifyContent: "center",
  },
  label: {
    fontSize: 11,
    marginTop: 1,
    ...Platform.select({ ios: { fontWeight: "600" }, default: {} }),
  },
});
