import type { Config } from 'tailwindcss';
export default {
  content: ['./app/**/*.{js,ts,jsx,tsx,mdx}', './components/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: { extend: { fontFamily: { sans: ['Inter','Geist','ui-sans-serif','system-ui','-apple-system','BlinkMacSystemFont','SF Pro Display','sans-serif'] } } },
  plugins: [],
} satisfies Config;
