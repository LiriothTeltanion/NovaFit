import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Relative base: the same build works from GitHub Pages (/NovaFit/app/) or any static folder.
export default defineConfig({
  base: './',
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test-setup.ts'],
  },
});
