/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        midnight: {
          950: '#040714',
          900: '#050b1a',
          800: '#0a1326',
        },
        horizon: {
          900: '#0f1e38',
          800: '#142746',
          700: '#1b3359',
        },
        surface: {
          900: '#10172a',
          800: '#152036',
          700: '#1f2d47',
        },
        primary: '#6366f1',
        secondary: '#22d3ee',
        fuchsia: '#c084fc',
        success: '#34d399',
        warning: '#fbbf24',
        error: '#f87171',
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 45%, #22d3ee 100%)',
        'gradient-haze': 'radial-gradient(circle at top right, rgba(99,102,241,0.25), transparent 55%), radial-gradient(circle at bottom left, rgba(34,211,238,0.15), transparent 50%)',
        'grid-pattern': 'linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 0), linear-gradient(180deg, rgba(255,255,255,0.04) 1px, transparent 0)',
      },
      boxShadow: {
        'glow-primary': '0 0 45px rgba(99, 102, 241, 0.45)',
        'glow-secondary': '0 0 45px rgba(34, 211, 238, 0.35)',
        'glow-success': '0 0 32px rgba(52, 211, 153, 0.35)',
        'card': '0 24px 60px -15px rgba(8, 12, 30, 0.65)',
        'floating': '0 18px 30px -15px rgba(12, 18, 38, 0.75)',
      },
      borderRadius: {
        '3xl': '1.75rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.45s ease-in-out both',
        'slide-up': 'slideUp 0.45s ease-out both',
        'float': 'float 6s ease-in-out infinite',
        'pulse-slow': 'pulse 3.5s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(24px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(-6px)' },
          '50%': { transform: 'translateY(4px)' },
        },
      },
    },
  },
  plugins: [],
};
