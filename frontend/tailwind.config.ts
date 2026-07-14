import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
    "./hooks/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // "Marked-up manuscript at night" — warm archival paper dimmed under a
        // desk lamp, NOT a blue-black IDE. Every neutral carries a warm bias.
        bg: "#1a1613",
        panel: "#221d18",
        elevated: "#2b241d",
        raised: "#352c23",
        border: "#3a3128",
        borderStrong: "#4d4234",
        muted: "#8a7d6d",
        subtle: "#b3a693",
        text: "#efe7d8", // warm paper white
        // The single bold voice: a proofreader's / "record" red. Primary +
        // active/live path ONLY. This is where the boldness is spent.
        accent: {
          DEFAULT: "#d1495b",
          hover: "#e05e6f",
          dark: "#a83545", // deeper red for generate/regenerate action buttons
          darkHover: "#bd3e50",
          muted: "#7a2e39",
          soft: "#2e1a1b",
        },
        // Semantics — deliberately distinct from the red accent.
        success: { DEFAULT: "#7d8c5c", soft: "#242a1a" }, // approved-margin sage
        warning: "#d99a45",
        danger: "#b23b3b",
        info: "#6d8ba3",
      },
      fontFamily: {
        // Body: clean humanist sans for dense UI legibility.
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        // Display: an editorial SERIF — the manuscript voice. Non-default for a tool.
        display: ["var(--font-display)", "Georgia", "serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      letterSpacing: {
        label: "0.14em",
      },
      borderRadius: {
        // Paper and index cards read square. Keep corners tight.
        DEFAULT: "2px",
        md: "3px",
        lg: "4px",
      },
      keyframes: {
        shimmer: {
          "100%": { transform: "translateX(100%)" },
        },
        "fade-in": {
          "0%": { opacity: "0", transform: "translateY(2px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        shimmer: "shimmer 1.5s infinite",
        "fade-in": "fade-in 0.18s ease-out",
      },
    },
  },
  plugins: [],
};

export default config;
