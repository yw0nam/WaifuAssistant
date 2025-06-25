/* eslint-disable */
import { Box, Text } from "@chakra-ui/react";
import { FiMonitor } from "react-icons/fi";
import { Tooltip } from "@/components/ui/tooltip";
import { sidebarStyles } from "./sidebar-styles";
import { useCaptureScreen } from "@/hooks/sidebar/use-capture-screen";

// Reusable components
function ScreenIndicator() {
  return (
    <Box color="red.500" display="flex" alignItems="center" gap={2}>
      <Box
        w="8px"
        h="8px"
        borderRadius="full"
        bg="red.500"
        animation="pulse 2s infinite"
      />
      <Text fontSize="sm">Screen</Text>
    </Box>
  );
}

function ScreenPlaceholder() {
  return (
    <Box
      position="absolute"
      display="flex"
      flexDirection="column"
      alignItems="center"
      gap={2}
    >
      <FiMonitor size={24} />
      <Text color="whiteAlpha.600" fontSize="sm" textAlign="center">
        Click to start screen capture
      </Text>
    </Box>
  );
}

function VideoStream({
  videoRef,
  isStreaming,
}: {
  videoRef: React.RefObject<HTMLVideoElement>;
  isStreaming: boolean;
}) {
  return (
    <video
      ref={videoRef}
      autoPlay
      playsInline
      muted
      style={sidebarStyles.screenPanel.video}
      {...(isStreaming ? {} : { display: "none" })}
    />
  );
}

function ScreenPanel(): JSX.Element {
  const {
    videoRef,
    error,
    isHovering,
    isStreaming,
    toggleCapture,
    handleMouseEnter,
    handleMouseLeave,
  } = useCaptureScreen();

  return (
    <Box {...sidebarStyles.screenPanel.container}>
      <Box {...sidebarStyles.screenPanel.header}>
        {isStreaming && <ScreenIndicator />}
      </Box>

      <Tooltip
        showArrow
        content={
          isStreaming
            ? "Click to stop screen capture"
            : "Click to start screen capture"
        }
        open={isHovering && !error}
      >
        <Box
          {...sidebarStyles.screenPanel.screenContainer}
          onClick={toggleCapture}
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
          cursor="pointer"
          position="relative"
          _hover={{
            bg: "whiteAlpha.100",
          }}
        >
          {error ? (
            <Text color="red.300" fontSize="sm" textAlign="center">
              {error}
            </Text>
          ) : (
            <>
              <VideoStream videoRef={videoRef} isStreaming={isStreaming} />
              {!isStreaming && <ScreenPlaceholder />}
            </>
          )}
        </Box>
      </Tooltip>
    </Box>
  );
}

export default ScreenPanel;
