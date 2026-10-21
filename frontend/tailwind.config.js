/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        darkSidebar: "#0d1127",
        darkSidebarHover: "#181e3a",
        cardBg: "#ffffff",
        subtleBg: "#f4f6fa",
        brandPurple: "#6366f1",
        brandPurpleDark: "#4f46e5",
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem',
        '4xl': '2rem',
      },
      boxShadow: {
        'soft': '0 4px 20px -2px rgba(50, 50, 93, 0.05), 0 2px 6px -1px rgba(0, 0, 0, 0.04)',
        'glow': '0 0 15px rgba(99, 102, 241, 0.35)',
      }
    },
  },
  plugins: [],
}
