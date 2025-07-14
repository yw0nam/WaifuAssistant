import { Stack } from '@chakra-ui/react';
import { InputField } from './common';
import { useTTSSettings } from '@/context/tts-settings-context';
import { settingStyles } from './setting-styles';

function TTS(): JSX.Element {
  const { settings, updateReferenceId } = useTTSSettings();

  return (
    <Stack {...settingStyles.common.container}>
      <InputField
        label="Voice Reference ID"
        value={settings.referenceId}
        onChange={updateReferenceId}
        placeholder="Enter voice reference ID (e.g., ナツメ)"
      />
    </Stack>
  );
}

export default TTS;
