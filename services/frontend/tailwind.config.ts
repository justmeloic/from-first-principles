import type { Config } from "tailwindcss";
const defaultTheme = require('tailwindcss/defaultTheme'); // Import defaultTheme

const config = {
  darkMode: ["class"],
  content: ["./pages/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./app/**/*.{ts,tsx}", "./src/**/*.{ts,tsx}"],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      fontFamily: {
        serif: ["Playfair Display", "serif"], // Existing font
        // Sans-Serif
        'inter': ['Inter', ...defaultTheme.fontFamily.sans],
        'roboto': ['Roboto', ...defaultTheme.fontFamily.sans],
        'open-sans': ['"Open Sans"', ...defaultTheme.fontFamily.sans],
        'lato': ['Lato', ...defaultTheme.fontFamily.sans],
        'montserrat': ['Montserrat', ...defaultTheme.fontFamily.sans],
        'source-sans': ['"Source Sans 3"', ...defaultTheme.fontFamily.sans],

        // Serif
        'lora': ['Lora', ...defaultTheme.fontFamily.serif],
        'merriweather': ['Merriweather', ...defaultTheme.fontFamily.serif],
        'pt-serif': ['"PT Serif"', ...defaultTheme.fontFamily.serif],
        'playfair-display': ['"Playfair Display"', ...defaultTheme.fontFamily.serif],

        // Monospace
        'fira-code': ['"Fira Code"', ...defaultTheme.fontFamily.mono],
        'source-code-pro': ['"Source Code Pro"', ...defaultTheme.fontFamily.mono],
        'jetbrains-mono': ['"JetBrains Mono"', ...defaultTheme.fontFamily.mono],
        'roboto-mono': ['"Roboto Mono"', ...defaultTheme.fontFamily.mono],
        'space-mono': ['"Space Mono"', ...defaultTheme.fontFamily.mono],

        // Display/Decorative
        'raleway': ['Raleway', 'sans-serif'],
        'poppins': ['Poppins', 'sans-serif'],
        'oswald': ['Oswald', 'sans-serif'],
      },
      boxShadow: {
        'custom': '-10px 10px 15px 5px rgba(1, 0.1, 0.1, 0.2)',
        'custom-lg': '-15px 15px 20px 7px rgba(1, 0.1, 0.1, 0.3)',
        'custom-white': '0px 8px 15px 5px rgba(255, 255, 255, 0.1)',
        'custom-lg-white': '-15px 15px 20px 7px rgba(255, 255, 255, 0.15)',
        'none': 'none'
      },
      colors: {
        'light-mode-white': '#f4f4f4',
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: '#d7b065',
          foreground: '#000000', // dark text on accent background
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      keyframes: {
        "fade-up": {
          "0%": {
            opacity: "0",
            transform: "translateY(10px)",
          },
          "100%": {
            opacity: "1",
            transform: "translateY(0)",
          },
        },
      },
      animation: {
        "fade-up": "fade-up 0.5s ease-out forwards",
      },
      typography: {
        DEFAULT: {
          css: {
            "code::before": {
              content: '""',
            },
            "code::after": {
              content: '""',
            },
          },
        },
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
} satisfies Config;

export default config;
