import { Tabs } from "expo-router";
import React from "react";
import { Platform, Pressable, StyleSheet, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { useLearnTheme } from "@/src/learn/ThemeContext";
import {
  HomeTabIcon,
  LessonsTabIcon,
  ProfileTabIcon,
  TabIconProps,
  TutorsTabIcon,
  VocabTabIcon,
} from "@/src/learn/tabIcons";

type TabDef = {
  name: string;
  label: string;
  Icon: (p: TabIconProps) => React.ReactElement;
};

const TABS: TabDef[] = [
  { name: "index", label: "Home", Icon: HomeTabIcon },
  { name: "lessons", label: "Lessons", Icon: LessonsTabIcon },
  { name: "vocabulary", label: "Vocabulary", Icon: VocabTabIcon },
  { name: "tutors", label: "Tutors", Icon: TutorsTabIcon },
  { name: "profile", label: "Profile", Icon: ProfileTabIcon },
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
          const Icon = def.Icon;
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
                <Icon size={24} color={iconColor} strokeWidth={1.8} />
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
    width: 46,
    height: 32,
    borderRadius: 16,
    alignItems: "center",
    justifyContent: "center",
  },
  label: {
    fontSize: 11,
    marginTop: 1,
    ...Platform.select({ ios: { fontWeight: "600" }, default: {} }),
  },
});
