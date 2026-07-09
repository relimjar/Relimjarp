// Native fallback — react-native-webrtc is not available in Expo Go, so on
// native we don't render a live <video>. The parent screen shows an avatar
// placeholder underneath instead. (Live video runs on web / dev-builds.)
import React from "react";
import { View } from "react-native";

export function VideoStream({ style }: { stream?: unknown; muted?: boolean; mirror?: boolean; style?: object }) {
  return <View style={style} />;
}
