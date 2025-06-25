import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App';

const originalConsoleWarn = console.warn;
console.warn = (...args) => {
  if (typeof args[0] === 'string' && args[0].includes('onnxruntime')) {
    return;
  }
  originalConsoleWarn.apply(console, args);
};

if (typeof window !== 'undefined') {
  createRoot(document.getElementById('root')!).render(
    <App />,
  );
}
