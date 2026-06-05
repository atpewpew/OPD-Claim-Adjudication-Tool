/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#8B5CF6", // Plum Purple
        primary_hover: "#7C3AED",
        secondary: "#10B981", // Emerald Green - for approvals
        destructive: "#EF4444", // Red - for rejections
        warning: "#F59E0B", // Amber - for partials/manual review
        surface: "#FFFFFF",
        background: "#F8FAFC", // Slate 50
      },
    },
  },
  plugins: [],
}
