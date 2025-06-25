import { Box, Button } from '@chakra-ui/react';
import { FiTrash2 } from 'react-icons/fi';
import { formatDistanceToNow } from 'date-fns';
import { memo } from 'react';
import {
  DrawerRoot,
  DrawerTrigger,
  DrawerContent,
  DrawerHeader,
  DrawerTitle,
  DrawerBody,
  DrawerFooter,
  DrawerActionTrigger,
  DrawerBackdrop,
  DrawerCloseTrigger,
} from '@/components/ui/drawer';
import { sidebarStyles } from './sidebar-styles';
import { useHistoryDrawer } from '@/hooks/sidebar/use-history-drawer';
import { HistoryInfo } from '@/context/websocket-context';

// Type definitions
interface HistoryDrawerProps {
  children: React.ReactNode;
}

interface HistoryItemProps {
  isSelected: boolean;
  latestMessage: { content: string; timestamp: string | null };
  onSelect: () => void;
  onDelete: (e: React.MouseEvent) => void;
  isDeleteDisabled: boolean;
}

// Reusable components
const HistoryItem = memo(({
  isSelected,
  latestMessage,
  onSelect,
  onDelete,
  isDeleteDisabled,
}: HistoryItemProps): JSX.Element => (
  <Box
    {...sidebarStyles.historyDrawer.historyItem}
    {...(isSelected ? sidebarStyles.historyDrawer.historyItemSelected : {})}
    onClick={onSelect}
  >
    <Box {...sidebarStyles.historyDrawer.historyHeader}>
      <Box {...sidebarStyles.historyDrawer.timestamp}>
        {latestMessage.timestamp
          ? formatDistanceToNow(new Date(latestMessage.timestamp), { addSuffix: true })
          : 'No messages'}
      </Box>
      <Button
        onClick={onDelete}
        disabled={isDeleteDisabled}
        {...sidebarStyles.historyDrawer.deleteButton}
      >
        <FiTrash2 />
      </Button>
    </Box>
    {latestMessage.content && (
      <Box {...sidebarStyles.historyDrawer.messagePreview}>
        {latestMessage.content}
      </Box>
    )}
  </Box>
));

HistoryItem.displayName = 'HistoryItem';

// Main component
function HistoryDrawer({ children }: HistoryDrawerProps): JSX.Element {
  const {
    open,
    setOpen,
    historyList,
    currentHistoryUid,
    fetchAndSetHistory,
    deleteHistory,
    getLatestMessageContent,
  } = useHistoryDrawer();

  return (
    <DrawerRoot
      open={open}
      onOpenChange={(e) => setOpen(e.open)}
      placement="start"
    >
      <DrawerBackdrop />
      <DrawerTrigger asChild>{children}</DrawerTrigger>
      <DrawerContent style={sidebarStyles.historyDrawer.drawer.content}>
        <DrawerHeader>
          <DrawerTitle style={sidebarStyles.historyDrawer.drawer.title}>
            Chat History List
          </DrawerTitle>
          <DrawerCloseTrigger style={sidebarStyles.historyDrawer.drawer.closeButton} />
        </DrawerHeader>

        <DrawerBody>
          <Box {...sidebarStyles.historyDrawer.listContainer}>
            {historyList.map((history: HistoryInfo) => (
              <HistoryItem
                key={history.uid}
                isSelected={currentHistoryUid === history.uid}
                latestMessage={getLatestMessageContent(history)}
                onSelect={() => fetchAndSetHistory(history.uid)}
                onDelete={(e) => {
                  e.stopPropagation();
                  deleteHistory(history.uid);
                }}
                isDeleteDisabled={currentHistoryUid === history.uid}
              />
            ))}
          </Box>
        </DrawerBody>

        <DrawerFooter>
          <DrawerActionTrigger asChild>
            <Button {...sidebarStyles.historyDrawer.drawer.actionButton}>
              Close
            </Button>
          </DrawerActionTrigger>
        </DrawerFooter>
      </DrawerContent>
    </DrawerRoot>
  );
}

export default HistoryDrawer;
