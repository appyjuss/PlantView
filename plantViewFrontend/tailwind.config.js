/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        // Brand palette taken from landing page choices
        brand: {
          50: '#eef6ef',
          100: '#d9efe0',
          200: '#b3e0bf',
          300: '#7fd39a',
          400: '#4fc77a',
          500: '#1f7a3e', // primary brand color
          600: '#196433',
          700: '#124e28',
          800: '#0c391e',
          900: '#06220f'
        },
        // Accent (bright green) and muted teal used on landing
        accent: {
          500: '#27ae60'
        },
        mutedGreen: {
          500: '#577b6b'
        }
      },
      borderRadius: {
        lg: '0.75rem'
      }
    }
  },
  plugins: []
};
