/**
 * Debug utilities for Live2D model loading and state tracking
 */

export const debugLive2D = {
  log: (message: string, data?: any) => {
    if (process.env.NODE_ENV === 'development') {
      console.log(`[Live2D Debug] ${message}`, data || '');
    }
  },
  
  error: (message: string, error?: any) => {
    console.error(`[Live2D Error] ${message}`, error || '');
  },
  
  warn: (message: string, data?: any) => {
    console.warn(`[Live2D Warning] ${message}`, data || '');
  },
  
  checkModelUrl: async (url: string): Promise<boolean> => {
    try {
      const response = await fetch(url, { method: 'HEAD' });
      const exists = response.ok;
      debugLive2D.log(`Model URL check: ${url}`, { exists, status: response.status });
      return exists;
    } catch (error) {
      debugLive2D.error(`Failed to check model URL: ${url}`, error);
      return false;
    }
  }
};
