/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        keto: {
          green: '#22c55e',
          teal: '#14b8a6',
          amber: '#f59e0b',
          red: '#ef4444',
          bg: '#f0fdf4',
          card: '#ffffff',
        },
      },
    },
  },
  plugins: [],
}
