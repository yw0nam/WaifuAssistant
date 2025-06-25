import { Box, Text } from '@chakra-ui/react';
import { useAiState } from '@/context/ai-state-context';
import { footerStyles } from './footer-styles';

function AIStateIndicator(): JSX.Element {
  const { aiState } = useAiState();
  const styles = footerStyles.aiIndicator;

  return (
    <Box {...styles.container}>
      <Text {...styles.text}>{aiState}</Text>
    </Box>
  );
}

export default AIStateIndicator;
