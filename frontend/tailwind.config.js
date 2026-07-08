/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        clinic: {
          navy: '#0B2545',       // Primary medical navy
          blue: '#134074',       // Secondary clinic slate blue
          accent: '#C5A880',     // Luxury champagne gold/bronze
          gold: '#D4AF37',       // Bright accents
          ice: '#F4F7F6',        // Clean clinical background (soft sage/white)
          charcoal: '#1E252B',   // Dark text/backgrounds
          emerald: '#10B981',    // Positive promo indicators
          coral: '#EF4444'       // Warnings/low stock alert
        }
      },
      fontFamily: {
        display: ['Cormorant Garamond', 'serif'],
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      }
    },
  },
  plugins: [],
}
