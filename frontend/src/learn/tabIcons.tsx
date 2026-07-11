import React from "react";
import Svg, { Circle, Path, Polygon, Rect, Line } from "react-native-svg";

// -----------------------------------------------------------------------------
// Vocab tab-bar icons — hand-drawn SVGs matching the reference designs exactly.
// All icons share the same 24×24 viewbox and stroke weight so they read as a
// coherent set. Pass `color` for the stroke; `filled` variants use fill.
// -----------------------------------------------------------------------------

export type TabIconProps = {
  size?: number;
  color: string;
  strokeWidth?: number;
};

// House drawn as: peaked roof triangle + rounded-square body + small door.
export function HomeTabIcon({ size = 26, color, strokeWidth = 1.8 }: TabIconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Path
        d="M4 10.5L12 4l8 6.5V19a1.5 1.5 0 0 1-1.5 1.5H5.5A1.5 1.5 0 0 1 4 19v-8.5Z"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinejoin="round"
        strokeLinecap="round"
      />
      <Path
        d="M10 20.5v-4.5a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v4.5"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinejoin="round"
        strokeLinecap="round"
      />
    </Svg>
  );
}

// Play button inside a circle — outer stroked circle + filled play triangle.
export function LessonsTabIcon({ size = 26, color, strokeWidth = 1.8 }: TabIconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Circle cx={12} cy={12} r={9} stroke={color} strokeWidth={strokeWidth} />
      <Polygon points="10,8 16,12 10,16" fill={color} />
    </Svg>
  );
}

// Vocabulary card — rounded rectangle with a small tab on top + content lines.
export function VocabTabIcon({ size = 26, color, strokeWidth = 1.8 }: TabIconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      {/* Outer card */}
      <Rect x={4} y={5.5} width={16} height={14} rx={2.4} stroke={color} strokeWidth={strokeWidth} />
      {/* Little tab / bookmark-notch on top */}
      <Path
        d="M10.5 5.5V4a.6.6 0 0 1 .6-.6h1.8a.6.6 0 0 1 .6.6v1.5"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
      />
      {/* Content lines */}
      <Line x1={7} y1={11} x2={17} y2={11} stroke={color} strokeWidth={strokeWidth} strokeLinecap="round" />
      <Line x1={7} y1={14} x2={17} y2={14} stroke={color} strokeWidth={strokeWidth} strokeLinecap="round" />
      <Line x1={7} y1={17} x2={13} y2={17} stroke={color} strokeWidth={strokeWidth} strokeLinecap="round" />
    </Svg>
  );
}

// Smiley face — outer circle + two dot eyes + curved mouth.
export function TutorsTabIcon({ size = 26, color, strokeWidth = 1.8 }: TabIconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Circle cx={12} cy={12} r={9} stroke={color} strokeWidth={strokeWidth} />
      <Circle cx={9.2} cy={10.5} r={1.05} fill={color} />
      <Circle cx={14.8} cy={10.5} r={1.05} fill={color} />
      <Path
        d="M9 14.4c.9 1.1 1.9 1.6 3 1.6s2.1-.5 3-1.6"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        fill="none"
      />
    </Svg>
  );
}

// Person inside a circle — outer stroked circle + head + shoulders.
export function ProfileTabIcon({ size = 26, color, strokeWidth = 1.8 }: TabIconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Circle cx={12} cy={12} r={9} stroke={color} strokeWidth={strokeWidth} />
      <Circle cx={12} cy={10} r={2.6} stroke={color} strokeWidth={strokeWidth} fill="none" />
      <Path
        d="M6.5 19.5c1.1-2.6 3.2-3.9 5.5-3.9s4.4 1.3 5.5 3.9"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        fill="none"
      />
    </Svg>
  );
}
