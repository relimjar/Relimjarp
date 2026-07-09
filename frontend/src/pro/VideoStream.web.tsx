// Web implementation — renders a real DOM <video> element (via
// react-native-web's createElement) and attaches the given MediaStream.
import { useEffect, useRef } from "react";
import { unstable_createElement } from "react-native-web";

interface Props {
  stream?: MediaStream | null;
  muted?: boolean;
  mirror?: boolean;
  style?: Record<string, unknown>;
}

export function VideoStream({ stream, muted, mirror, style }: Props) {
  const ref = useRef<HTMLVideoElement | null>(null);

  useEffect(() => {
    const el = ref.current;
    if (el && stream && el.srcObject !== stream) {
      el.srcObject = stream;
      const p = el.play();
      if (p && typeof p.catch === "function") p.catch(() => {});
    }
  }, [stream]);

  return unstable_createElement("video", {
    ref,
    autoPlay: true,
    playsInline: true,
    muted,
    style: {
      width: "100%",
      height: "100%",
      objectFit: "cover",
      transform: mirror ? "scaleX(-1)" : undefined,
      backgroundColor: "transparent",
      ...(style || {}),
    },
  });
}
