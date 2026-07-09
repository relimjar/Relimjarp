// "Lessons" — an original, playful gamified language-learning design system.
// Bright, friendly, high-energy. Its own module so it never touches the main
// app or other sub-apps. All values are original choices for this project.

export const lessonColors = {
  bg: "#FFFFFF",
  bgSoft: "#F5F8FB",
  surface: "#FFFFFF",
  surfaceSoft: "#F1F5F9",

  ink: "#2B2D3A",
  inkSoft: "#6E7488",
  inkFaint: "#AFB6C7",

  // Primary "go / correct" green
  green: "#3AC569",
  greenDark: "#2AA657",
  greenSoft: "#E4F7EB",
  onGreen: "#FFFFFF",

  // Accents
  coral: "#FF6B5A",
  coralSoft: "#FFE5E1",
  blue: "#26A9F4",
  blueSoft: "#DCF0FD",
  purple: "#A66BFF",
  purpleSoft: "#EEE3FF",
  gold: "#FFC93C",
  goldSoft: "#FFF3D6",

  // Semantic
  correct: "#3AC569",
  correctSoft: "#E4F7EB",
  wrong: "#FF4E5B",
  wrongSoft: "#FFE3E5",
  heart: "#FF4E5B",
  streak: "#FF9500",
  gem: "#26A9F4",

  border: "#E6EAF0",
  borderStrong: "#D3D9E3",
  shadow: "#8A93A6",
} as const;

export const lessonRadius = {
  sm: 12,
  md: 16,
  lg: 22,
  xl: 28,
  pill: 999,
} as const;

export const lessonFonts = {
  // Nunito is rounded + friendly — already loaded app-wide.
  black: "Nunito_700Bold",
  bold: "Nunito_700Bold",
  semi: "Nunito_600SemiBold",
  regular: "Nunito_400Regular",
} as const;

export const lessonShadow = {
  // Chunky "3D button" bottom shadow used across the app.
  card: {
    shadowColor: "#8A93A6",
    shadowOpacity: 0.18,
    shadowRadius: 10,
    shadowOffset: { width: 0, height: 4 },
    elevation: 3,
  },
} as const;
