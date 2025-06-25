import { Stack, createListCollection } from '@chakra-ui/react';
import { useBgUrl } from '@/context/bgurl-context';
import { settingStyles } from './setting-styles';
import { useConfig } from '@/context/character-config-context';
import { useGeneralSettings } from '@/hooks/sidebar/setting/use-general-settings';
import { useWebSocket } from '@/context/websocket-context';
import { SelectField, SwitchField, InputField } from './common';

interface GeneralProps {
  onSave?: (callback: () => void) => () => void
  onCancel?: (callback: () => void) => () => void
}

// Data collection definition
const useCollections = () => {
  const { backgroundFiles } = useBgUrl() || {};
  const { configFiles } = useConfig();

  const languages = createListCollection({
    items: [
      { label: 'English', value: 'en' },
      { label: '中文', value: 'zh' },
    ],
  });

  const backgrounds = createListCollection({
    items: backgroundFiles?.map((filename) => ({
      label: String(filename),
      value: `/bg/${filename}`,
    })) || [],
  });

  const characterPresets = createListCollection({
    items: configFiles.map((config) => ({
      label: config.name,
      value: config.filename,
    })),
  });

  return {
    languages,
    backgrounds,
    characterPresets,
  };
};

function General({ onSave, onCancel }: GeneralProps): JSX.Element {
  const bgUrlContext = useBgUrl();
  const { confName, setConfName } = useConfig();
  const {
    wsUrl, setWsUrl, baseUrl, setBaseUrl,
  } = useWebSocket();
  const collections = useCollections();

  const {
    settings,
    handleSettingChange,
    handleCameraToggle,
    handleCharacterPresetChange,
    showSubtitle,
    setShowSubtitle,
  } = useGeneralSettings({
    bgUrlContext,
    confName,
    setConfName,
    baseUrl,
    wsUrl,
    onWsUrlChange: setWsUrl,
    onBaseUrlChange: setBaseUrl,
    onSave,
    onCancel,
  });

  return (
    <Stack {...settingStyles.common.container}>
      <SelectField
        label="Language"
        value={settings.language}
        onChange={(value) => handleSettingChange('language', value)}
        collection={collections.languages}
        placeholder="Select language"
      />

      <SwitchField
        label="Use Camera Background"
        checked={settings.useCameraBackground}
        onChange={handleCameraToggle}
      />

      <SwitchField
        label="Show Subtitle"
        checked={showSubtitle}
        onChange={setShowSubtitle}
      />

      {!settings.useCameraBackground && (
        <>
          <SelectField
            label="Background Image"
            value={settings.selectedBgUrl}
            onChange={(value) => handleSettingChange('selectedBgUrl', value)}
            collection={collections.backgrounds}
            placeholder="Select from available backgrounds"
          />

          <InputField
            label="Or enter a custom background URL"
            value={settings.customBgUrl}
            onChange={(value) => handleSettingChange('customBgUrl', value)}
            placeholder="Enter image URL"
          />
        </>
      )}

      <SelectField
        label="Character Preset"
        value={settings.selectedCharacterPreset}
        onChange={handleCharacterPresetChange}
        collection={collections.characterPresets}
        placeholder={confName || 'Select character preset'}
      />

      <InputField
        label="WebSocket URL"
        value={settings.wsUrl}
        onChange={(value) => handleSettingChange('wsUrl', value)}
        placeholder="Enter WebSocket URL"
      />

      <InputField
        label="Base URL"
        value={settings.baseUrl}
        onChange={(value) => handleSettingChange('baseUrl', value)}
        placeholder="Enter Base URL"
      />
    </Stack>
  );
}

export default General;
