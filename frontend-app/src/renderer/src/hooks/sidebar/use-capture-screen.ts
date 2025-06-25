import { useRef, useState, useEffect } from 'react';
import { useScreenCaptureContext } from '@/context/screen-capture-context';

export function useCaptureScreen() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isHovering, setIsHovering] = useState(false);
  const { stream, isStreaming, error, startCapture, stopCapture } = useScreenCaptureContext();

  const toggleCapture = () => {
    if (isStreaming) {
      stopCapture();
    } else {
      startCapture();
    }
  };

  const handleMouseEnter = () => setIsHovering(true);
  const handleMouseLeave = () => setIsHovering(false);

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.srcObject = stream;
    }
  }, [stream]);

  return {
    videoRef,
    error,
    isHovering,
    isStreaming,
    stream,
    toggleCapture,
    handleMouseEnter,
    handleMouseLeave,
  };
}
