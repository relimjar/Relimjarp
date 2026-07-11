// Learn / Vocab sub-app design tokens — matches uploaded reference designs
// Dark near-black background with pastel accents (purple, mint, lime, coral).

export const learnColors = {
  // Base
  bg: "#0B0B0F",
  surface: "#121218",
  surfaceRaised: "#1A1A21",
  border: "#2A2A34",
  // Text
  text: "#FFFFFF",
  textDim: "#9A9AA5",
  textFaint: "#6B6B75",
  onLight: "#0B0B0F",
  // Card / chip surfaces
  cardLight: "#F2F2F4",     // white lesson cards
  cardMint: "#C8E4B4",      // tutor & chip mint
  cardMintDeep: "#B7D8A2",
  cardLime: "#E8F569",      // vocabulary topic tiles
  cardCoral: "#F0715C",     // challenge card
  cardPurple: "#B7A0F5",    // in-progress + book lesson button
  cardPurpleSoft: "#D8CBFF",
  // Accents
  purple: "#A78BFA",
  purpleDark: "#7C5CE0",
  green: "#8FCB6F",
  lime: "#D6E85E",
  coral: "#F0715C",
  // Tab bar
  tabBg: "#0B0B0F",
  tabActivePill: "#B7A0F5",
  tabActiveText: "#0B0B0F",
  tabInactive: "#E4E4EA",
} as const;

export const learnRadius = {
  chip: 999,
  sm: 12,
  md: 20,
  lg: 28,
  xl: 36,
} as const;

export const learnFont = {
  h1: 32,
  h2: 26,
  h3: 20,
  body: 15,
  small: 13,
  tiny: 11,
};
