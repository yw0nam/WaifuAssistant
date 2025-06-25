/* eslint-disable no-use-before-define */
import { useState, useEffect } from 'react';
import { BgUrlContextState } from '@/context/bgurl-context';
import { defaultBaseUrl, defaultWsUrl } from '@/context/websocket-context';
import { useSubtitle } from '@/context/subtitle-context';
import { useCamera } from '@/context/camera-context';
import { useSwitchCharacter } from '@/hooks/utils/use-switch-character';
import { useConfig } from '@/context/character-config-context';

interface GeneralSettings {
  language: string[]
  customBgUrl: string
  selectedBgUrl: string[]
  backgroundUrl: string
  selectedCharacterPreset: string[]
  useCameraBackground: boolean
  wsUrl: string
  baseUrl: string
  showSubtitle: boolean
}

interface UseGeneralSettingsProps {
  bgUrlContext: BgUrlContextState | null
  confName: string | undefined
  setConfName: (name: string) => void
  baseUrl: string
  wsUrl: string
  onWsUrlChange: (url: string) => void
  onBaseUrlChange: (url: string) => void
  onSave?: (callback: () => void) => () => void
  onCancel?: (callback: () => void) => () => void
}

export const useGeneralSettings = ({
  bgUrlContext,
  confName,
  setConfName,
  baseUrl,
  wsUrl,
  onWsUrlChange,
  onBaseUrlChange,
  onSave,
  onCancel,
}: UseGeneralSettingsProps) => {
  const { showSubtitle, setShowSubtitle } = useSubtitle();
  const { setUseCameraBackground } = bgUrlContext || {};
  const { startBackgroundCamera, stopBackgroundCamera } = useCamera();
  const { configFiles, getFilenameByName } = useConfig();
  const { switchCharacter } = useSwitchCharacter();

  const getCurrentBgKey = (): string[] => {
    if (!bgUrlContext?.backgroundUrl) return [];
    const currentBgUrl = bgUrlContext.backgroundUrl;
    const path = currentBgUrl.replace(baseUrl, '');
    return path.startsWith('/bg/') ? [path] : [];
  };

  const initialSettings: GeneralSettings = {
    language: ['en'],
    customBgUrl: !bgUrlContext?.backgroundUrl?.includes('/bg/')
      ? bgUrlContext?.backgroundUrl || ''
      : '',
    selectedBgUrl: getCurrentBgKey(),
    backgroundUrl: bgUrlContext?.backgroundUrl || '',
    selectedCharacterPreset: [],
    useCameraBackground: bgUrlContext?.useCameraBackground || false,
    wsUrl: wsUrl || defaultWsUrl,
    baseUrl: baseUrl || defaultBaseUrl,
    showSubtitle,
  };

  const [settings, setSettings] = useState<GeneralSettings>(initialSettings);
  const [originalSettings, setOriginalSettings] = useState<GeneralSettings>(initialSettings);
  const originalConfName = confName;

  useEffect(() => {
    setShowSubtitle(settings.showSubtitle);

    const newBgUrl = settings.customBgUrl || settings.selectedBgUrl[0];
    if (newBgUrl && bgUrlContext) {
      const fullUrl = newBgUrl.startsWith('http') ? newBgUrl : `${baseUrl}${newBgUrl}`;
      bgUrlContext.setBackgroundUrl(fullUrl);
    }

    onWsUrlChange(settings.wsUrl);
    onBaseUrlChange(settings.baseUrl);
  }, [settings]);

  useEffect(() => {
    if (confName) {
      const newSettings = {
        ...settings,
        selectedCharacterPreset: [confName],
      };
      setSettings(newSettings);
      setOriginalSettings(newSettings);
    }
  }, [confName]);

  // Add save/cancel effect
  useEffect(() => {
    if (!onSave || !onCancel) return;

    const cleanupSave = onSave(() => {
      handleSave();
    });

    const cleanupCancel = onCancel(() => {
      handleCancel();
    });

    return () => {
      cleanupSave?.();
      cleanupCancel?.();
    };
  }, [onSave, onCancel]);

  const handleSettingChange = (
    key: keyof GeneralSettings,
    value: GeneralSettings[keyof GeneralSettings],
  ): void => {
    setSettings((prev) => ({ ...prev, [key]: value }));

    if (key === 'wsUrl') {
      onWsUrlChange(value as string);
    }
    if (key === 'baseUrl') {
      onBaseUrlChange(value as string);
    }
  };

  const handleSave = (): void => {
    setOriginalSettings(settings);
  };

  const handleCancel = (): void => {
    setSettings(originalSettings);

    // Restore all settings to original values
    setShowSubtitle(originalSettings.showSubtitle);
    if (bgUrlContext) {
      bgUrlContext.setBackgroundUrl(originalSettings.backgroundUrl);
      bgUrlContext.setUseCameraBackground(originalSettings.useCameraBackground);
    }
    onWsUrlChange(originalSettings.wsUrl);
    onBaseUrlChange(originalSettings.baseUrl);

    // Restore original character preset
    if (originalConfName) {
      setConfName(originalConfName);
    }

    // Handle camera state
    if (originalSettings.useCameraBackground) {
      startBackgroundCamera();
    } else {
      stopBackgroundCamera();
    }
  };

  const handleCharacterPresetChange = (value: string[]): void => {
    const selectedFilename = value[0];
    const selectedConfig = configFiles.find((config) => config.filename === selectedFilename);
    const currentFilename = confName ? getFilenameByName(confName) : '';

    handleSettingChange('selectedCharacterPreset', value);

    if (currentFilename === selectedFilename) {
      return;
    }

    if (selectedConfig) {
      switchCharacter(selectedFilename);
    }
  };

  const handleCameraToggle = async (checked: boolean) => {
    if (!setUseCameraBackground) return;

    if (checked) {
      try {
        await startBackgroundCamera();
        handleSettingChange('useCameraBackground', true);
        setUseCameraBackground(true);
      } catch (error) {
        console.error('Failed to start camera:', error);
        handleSettingChange('useCameraBackground', false);
        setUseCameraBackground(false);
      }
    } else {
      stopBackgroundCamera();
      handleSettingChange('useCameraBackground', false);
      setUseCameraBackground(false);
    }
  };

  return {
    settings,
    handleSettingChange,
    handleSave,
    handleCancel,
    handleCameraToggle,
    handleCharacterPresetChange,
    showSubtitle,
    setShowSubtitle,
  };
};
