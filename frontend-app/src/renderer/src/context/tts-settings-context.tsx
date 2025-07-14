import { createContext, useContext, useState, ReactNode } from 'react';

interface TTSSettings {
  referenceId: string;
}

interface TTSSettingsContextType {
  settings: TTSSettings;
  updateReferenceId: (referenceId: string) => void;
  resetSettings: () => void;
}

const defaultSettings: TTSSettings = {
  referenceId: '',
};

const TTSSettingsContext = createContext<TTSSettingsContextType | undefined>(undefined);

interface TTSSettingsProviderProps {
  children: ReactNode;
}

export function TTSSettingsProvider({ children }: TTSSettingsProviderProps): JSX.Element {
  const [settings, setSettings] = useState<TTSSettings>(defaultSettings);

  const updateReferenceId = (referenceId: string) => {
    setSettings(prev => ({
      ...prev,
      referenceId,
    }));
  };

  const resetSettings = () => {
    setSettings(defaultSettings);
  };

  const value: TTSSettingsContextType = {
    settings,
    updateReferenceId,
    resetSettings,
  };

  return (
    <TTSSettingsContext.Provider value={value}>
      {children}
    </TTSSettingsContext.Provider>
  );
}

export function useTTSSettings(): TTSSettingsContextType {
  const context = useContext(TTSSettingsContext);
  if (context === undefined) {
    throw new Error('useTTSSettings must be used within a TTSSettingsProvider');
  }
  return context;
}
