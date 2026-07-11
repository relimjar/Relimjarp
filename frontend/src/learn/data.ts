// Static content for the Vocab sub-app (matches reference designs).
// Tutors are fetched live from /api/pro/tutors.

import { Ionicons } from "@expo/vector-icons";

export type IonIcon = keyof typeof Ionicons.glyphMap;

export type Topic = {
  id: string;
  name: string;
  subtitle: string;
  icon: IonIcon;
};

export type Lesson = {
  id: string;
  title: string;
  description: string;
  minutes: number;
  level: "Beginner" | "Intermediate" | "Advanced";
  topicId: string;
};

export type Challenge = {
  id: string;
  title: string;
  daysLeft: number;
  icon: IonIcon;
};

export const currentCourse = {
  id: "medicine-healthcare",
  tag: "In progress",
  title: "Medicine for healthcare professionals",
  progress: 0.32,
};

export const exploreTopics: Topic[] = [
  { id: "virology", name: "Virology", subtitle: "For healthcare providers", icon: "nutrition-outline" },
  { id: "pharmacy", name: "Pharmacy", subtitle: "Medicines & prescriptions", icon: "medkit-outline" },
  { id: "genetics", name: "Genetics", subtitle: "DNA & heredity", icon: "git-branch-outline" },
  { id: "anatomy", name: "Anatomy", subtitle: "Body systems", icon: "body-outline" },
];

export const allTopics: Topic[] = [
  { id: "medicine", name: "Medicine", subtitle: "For healthcare providers", icon: "medical-outline" },
  { id: "education", name: "Education", subtitle: "For education professionals", icon: "school-outline" },
  { id: "business", name: "Business", subtitle: "For career development", icon: "briefcase-outline" },
  { id: "science", name: "Science", subtitle: "For university students", icon: "flask-outline" },
  { id: "tech", name: "Tech", subtitle: "For software engineers", icon: "code-slash-outline" },
  { id: "travel", name: "Travel", subtitle: "For nomads & tourists", icon: "airplane-outline" },
];

export const lessons: Lesson[] = [
  {
    id: "hc-job-interview",
    title: "Prepare for a healthcare job interview",
    description: "The lesson contains some common healthcare interview questions and tips on how to answer them.",
    minutes: 35,
    level: "Advanced",
    topicId: "medicine",
  },
  {
    id: "hc-cv",
    title: "Writing a healthcare CV",
    description: "Learn how to write a good CV to apply for a role in healthcare. Practise common vocabulary and write your own CV.",
    minutes: 25,
    level: "Intermediate",
    topicId: "medicine",
  },
  {
    id: "pharmacy-basics",
    title: "Talking to patients in a pharmacy",
    description: "Common phrases and vocabulary used when helping customers at the pharmacy counter.",
    minutes: 20,
    level: "Beginner",
    topicId: "pharmacy",
  },
  {
    id: "virology-terms",
    title: "Essential virology vocabulary",
    description: "Master core virology terms with real-world examples used in hospitals and labs.",
    minutes: 30,
    level: "Advanced",
    topicId: "virology",
  },
];

export const challenges: Challenge[] = [
  { id: "c1", title: "Learn 20 new words", daysLeft: 3, icon: "reader-outline" },
  { id: "c2", title: "Complete 3 lessons", daysLeft: 5, icon: "trophy-outline" },
];

export const levelIcon = (level: Lesson["level"]): IonIcon => {
  if (level === "Beginner") return "stats-chart-outline";
  if (level === "Intermediate") return "stats-chart-outline";
  return "stats-chart-outline";
};
