import { Ionicons } from "@expo/vector-icons";
import { Tabs } from "expo-router";
import React from "react";
import { Platform, Pressable, StyleSheet, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { learnColors, learnRadius } from "@/src/learn/theme";

type IonIcon = keyof typeof Ionicons.glyphMap;

type TabDef = {
  name: string;
  label: string;
  icon: IonIcon;
  iconActive: IonIcon;
};

const TABS: TabDef[] = [
  { name: "index", label: "Home", icon: "home-outline", iconActive: "home" },
  { name: "lessons", label: "Lessons", icon: "play-circle-outline", iconActive: "play-circle" },
  { name: "vocabulary", label: "Vocabulary", icon: "book-outline", iconActive: "book" },
  { name: "tutors", label: "Tutors", icon: "happy-outline", iconActive: "happy" },
  { name: "profile", label: "Profile", icon: "person-outline", iconActive: "person" },
];

function VocabTabBar({ state, navigation }: any) {
  const insets = useSafeAreaInsets();
  const bottomGap = Math.max(insets.bottom, 10);
  return (
    <View style={[styles.barWrap, { paddingBottom: bottomGap }]}>
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
          return (
            <Pressable
              key={route.key}
              onPress={onPress}
              android_ripple={{ color: "transparent" }}
              hitSlop={8}
              style={styles.tabBtn}
            >
              <View style={[styles.pill, focused && styles.pillActive]}>
                <Ionicons
                  name={focused ? def.iconActive : def.icon}
                  size={22}
                  color={focused ? learnColors.tabActiveText : learnColors.tabInactive}
                />
                <Text
                  numberOfLines={1}
                  style={[styles.label, { color: focused ? learnColors.tabActiveText : learnColors.tabInactive }]}
                >
                  {def.label}
                </Text>
              </View>
            </Pressable>
          );
        })}
      </View>
    </View>
  );
}

export default function VocabTabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        sceneStyle: { backgroundColor: learnColors.bg },
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
    backgroundColor: learnColors.bg,
    borderTopWidth: 0,
  },
  bar: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 6,
    paddingTop: 8,
    paddingBottom: 4,
    backgroundColor: learnColors.bg,
  },
  tabBtn: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 2,
  },
  pill: {
    minWidth: 44,
    minHeight: 44,
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: learnRadius.chip,
    alignItems: "center",
    justifyContent: "center",
    gap: 2,
  },
  pillActive: {
    backgroundColor: learnColors.tabActivePill,
    paddingHorizontal: 14,
  },
  label: {
    fontSize: 11,
    fontWeight: Platform.OS === "ios" ? "600" : "700",
    marginTop: 1,
  },
});
