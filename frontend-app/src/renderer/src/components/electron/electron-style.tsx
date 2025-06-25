import { SystemStyleObject } from '@chakra-ui/react';

export const inputSubtitleStyles = {
  container: {
    display: 'flex',
    alignItems: 'flex-end',
    justifyContent: 'center',
    maxW: 'fit-content',
    position: 'absolute' as const,
    bottom: '120px',
    left: '50%',
    transform: 'translateX(-50%)',
    zIndex: 1000,
    userSelect: 'none',
    willChange: 'transform',
    padding: 0,
  },

  box: {
    w: '400px',
    rounded: 'xl',
    overflow: 'hidden',
    boxShadow: 'lg',
    bg: 'blackAlpha.700',
    backdropFilter: 'blur(8px)',
    css: { WebkitUserSelect: 'none' },
  },

  messageStack: {
    p: '3',
    gap: 1,
    alignItems: 'stretch',
    justify: 'flex-end',
  },

  messageText: {
    color: 'white',
    fontSize: 'sm',
    lineHeight: '1.5',
    transition: 'all 0.3s',
  },

  statusBox: {
    bg: 'blackAlpha.600',
    p: '3',
    borderTop: '1px',
    borderColor: 'whiteAlpha.200',
  },

  statusText: {
    fontSize: 'xs',
    color: 'whiteAlpha.800',
    transition: 'all 0.3s',
  },

  iconButton: {
    size: 'xs',
    variant: 'ghost',
    color: 'whiteAlpha.800',
    _hover: { bg: 'whiteAlpha.200' },
  },

  inputBox: {
    bg: 'blackAlpha.600',
    borderTop: '1px',
    borderColor: 'whiteAlpha.200',
  },

  input: {
    size: 'sm',
    bg: 'blackAlpha.500',
    color: 'white',
    _placeholder: { color: 'whiteAlpha.500' },
    borderColor: 'whiteAlpha.300',
    _focus: {
      borderColor: 'whiteAlpha.500',
      outline: 'none',
    },
    flex: '1',
  },

  sendButton: {
    p: '1.5',
    bg: 'blackAlpha.500',
    rounded: 'lg',
    _hover: { bg: 'blackAlpha.600' },
    transition: 'colors',
    color: 'whiteAlpha.800',
    size: 'sm',
  },

  draggableContainer: (isDragging: boolean): SystemStyleObject => ({
    cursor: isDragging ? 'grabbing' : 'grab',
    transition: isDragging ? 'none' : 'transform 0.1s ease',
    _active: { cursor: 'grabbing' },
  }),

  closeButton: {
    position: 'absolute' as const,
    top: 0,
    right: 0,
    size: '2xs',
    minW: '6',
    height: '6',
    padding: 0,
    variant: 'ghost',
    color: 'whiteAlpha.400',
    bg: 'transparent',
    _hover: {
      bg: 'blackAlpha.300',
      color: 'whiteAlpha.800',
    },
    zIndex: 10,
  },
} as const;
