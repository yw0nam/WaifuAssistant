/* eslint-disable no-nested-ternary */
/* eslint-disable import/order */
/* eslint-disable import/no-extraneous-dependencies */
/* eslint-disable react/require-default-props */
import { Box } from '@chakra-ui/react';
import {
  memo, useEffect, useRef, useCallback,
} from 'react';
import { ChatBubble } from './chat-bubble';
import { sidebarStyles, chatPanelStyles } from './sidebar-styles';
import { Message } from '@/services/websocket-service';
import { MainContainer, ChatContainer, MessageList as ChatMessageList, Message as ChatMessage, Avatar as ChatAvatar } from '@chatscope/chat-ui-kit-react';
import '@chatscope/chat-ui-kit-styles/dist/default/styles.min.css';
import { useChatHistory } from '@/context/chat-history-context';
import { Global } from '@emotion/react';
import { useConfig } from '@/context/character-config-context';
import { useWebSocket } from '@/context/websocket-context';

// Type definitions
interface MessageListProps {
  messages: Message[]
  messageListRef: React.RefObject<HTMLDivElement>
  onMessageUpdate?: (message: Message) => void
}

// Memoized message list component with scroll handling
const MessageList = memo(({ messages, messageListRef }: MessageListProps): JSX.Element => {
  const lastMessageRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    if (messageListRef.current) {
      const { scrollHeight } = messageListRef.current;
      const height = messageListRef.current.clientHeight;
      const maxScrollTop = scrollHeight - height;

      messageListRef.current.scrollTo({
        top: maxScrollTop + 100,
        behavior: 'smooth',
      });
    }
  }, [messageListRef]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  useEffect(() => {
    scrollToBottom();
  }, [scrollToBottom]);

  return (
    <Box {...sidebarStyles.chatHistoryPanel.messageList} ref={messageListRef}>
      {messages.map((message, index) => (
        <Box
          key={`${message.role}-${message.timestamp}-${message.id}`}
          ref={index === messages.length - 1 ? lastMessageRef : null}
        >
          <ChatBubble
            message={message}
          />
        </Box>
      ))}
    </Box>
  );
});

MessageList.displayName = 'MessageList';

// Main component
function ChatHistoryPanel(): JSX.Element {
  const { messages } = useChatHistory();
  const { confName } = useConfig();
  const { baseUrl } = useWebSocket();
  const userName = "Me";

  const validMessages = messages.filter((msg) => msg.content && msg.content.trim().length > 0);

  return (
    <Box
      h="full"
      overflow="hidden"
      bg="gray.900"
    >
      <Global styles={chatPanelStyles} />
      <MainContainer>
        <ChatContainer>
          <ChatMessageList>
            {validMessages.length === 0 ? (
              <Box
                display="flex"
                alignItems="center"
                justifyContent="center"
                height="100%"
                color="whiteAlpha.500"
                fontSize="sm"
              >
                No messages yet. Start a conversation!
              </Box>
            ) : (
              validMessages.map((msg) => (
                <ChatMessage
                  key={msg.id}
                  model={{
                    message: msg.content,
                    sentTime: msg.timestamp,
                    sender: msg.role === 'ai'
                      ? (msg.name || confName || 'AI')
                      : userName,
                    direction: msg.role === 'ai' ? 'incoming' : 'outgoing',
                    position: 'single',
                  }}
                  avatarPosition={msg.role === 'ai' ? 'tl' : 'tr'}
                  avatarSpacer={false}
                >
                  <ChatAvatar>
                    {msg.role === 'ai' ? (
                      msg.avatar ? (
                        <img
                          src={`${baseUrl}/avatars/${msg.avatar}`}
                          alt="avatar"
                          style={{ width: '100%', height: '100%', borderRadius: '50%' }}
                        />
                      ) : (
                        (msg.name && msg.name[0].toUpperCase()) ||
                        (confName && confName[0].toUpperCase()) ||
                        'A'
                      )
                    ) : (
                      userName[0].toUpperCase()
                    )}
                  </ChatAvatar>
                </ChatMessage>
              ))
            )}
          </ChatMessageList>
        </ChatContainer>
      </MainContainer>
    </Box>
  );
}

export default ChatHistoryPanel;
