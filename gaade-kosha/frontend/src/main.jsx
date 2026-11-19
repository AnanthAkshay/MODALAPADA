import React from 'react';
import ReactDOM from 'react-dom/client';

// Self-hosted fonts (bundled by Vite, no render-blocking CDN).
import '@fontsource/inter/400.css';
import '@fontsource/inter/500.css';
import '@fontsource/inter/600.css';
import '@fontsource/noto-sans-kannada/kannada-400.css';
import '@fontsource/noto-sans-kannada/kannada-500.css';
import '@fontsource/noto-sans-kannada/kannada-600.css';
import '@fontsource/noto-serif-kannada/kannada-500.css';
import '@fontsource/noto-serif-kannada/kannada-700.css';

import './index.css';
import App from './App.jsx';
import { applyTheme, readTheme } from './lib/theme.js';

applyTheme(readTheme(), { persist: false });

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
