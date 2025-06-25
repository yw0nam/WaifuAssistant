import {
  createContext,
  useContext,
  useRef,
  useState,
  useMemo,
  useCallback,
  ReactNode,
} from 'react';
import { toaster } from '@/components/ui/toaster';

/**
 * Camera configuration interface
 * @interface CameraConfig
 */
interface CameraConfig {
  width: number;
  height: number;
}

/**
 * Camera context state interface
 * @interface CameraContextState
 */
interface CameraContextState {
  isStreaming: boolean;
  stream: MediaStream | null;
  startCamera: () => Promise<void>;
  stopCamera: () => void;
  cameraConfig: CameraConfig;
  setCameraConfig: (config: CameraConfig) => void;
  videoRef: React.RefObject<HTMLVideoElement>;
  backgroundStream: MediaStream | null;
  startBackgroundCamera: () => Promise<void>;
  stopBackgroundCamera: () => void;
  isBackgroundStreaming: boolean;
}

/**
 * Default values and constants
 */
const DEFAULT_CAMERA_CONFIG: CameraConfig = {
  width: 320,
  height: 240,
};

/**
 * Create the camera context
 */
const CameraContext = createContext<CameraContextState | null>(null);

/**
 * Camera Provider Component
 * @param {Object} props - Provider props
 * @param {React.ReactNode} props.children - Child components
 */
export function CameraProvider({ children }: { children: ReactNode }) {
  // State management
  const [isStreaming, setIsStreaming] = useState(false);
  const [isBackgroundStreaming, setIsBackgroundStreaming] = useState(false);
  const [cameraConfig, setCameraConfig] = useState<CameraConfig>(
    DEFAULT_CAMERA_CONFIG,
  );
  const streamRef = useRef<MediaStream | null>(null);
  const backgroundStreamRef = useRef<MediaStream | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  // Start camera stream
  const startCamera = useCallback(async () => {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Camera API is not supported on this device');
      }

      const devices = await navigator.mediaDevices.enumerateDevices();
      const hasCamera = devices.some((device) => device.kind === 'videoinput');
      if (!hasCamera) {
        throw new Error('No camera found on this device');
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: cameraConfig.width },
          height: { ideal: cameraConfig.height },
        },
      });

      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setIsStreaming(true);
    } catch (err) {
      console.error('Failed to start camera:', err);
      toaster.create({
        title: `Failed to start camera: ${err}`,
        type: 'error',
        duration: 2000,
      });
      throw err;
    }
  }, [cameraConfig]);

  // Stop camera stream
  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
      setIsStreaming(false);
      // stopStreamingToBackend();
    }
  }, []);

  const startBackgroundCamera = useCallback(async () => {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Camera API is not supported on this device');
      }

      const devices = await navigator.mediaDevices.enumerateDevices();
      const hasCamera = devices.some((device) => device.kind === 'videoinput');
      if (!hasCamera) {
        throw new Error('No camera found on this device');
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: cameraConfig.width },
          height: { ideal: cameraConfig.height },
        },
      });

      backgroundStreamRef.current = stream;
      setIsBackgroundStreaming(true);
    } catch (err) {
      console.error('Failed to start background camera:', err);
      toaster.create({
        title: `Failed to start background camera: ${err}`,
        type: 'error',
        duration: 2000,
      });
      throw err;
    }
  }, [cameraConfig]);

  const stopBackgroundCamera = useCallback(() => {
    if (backgroundStreamRef.current) {
      backgroundStreamRef.current.getTracks().forEach((track) => track.stop());
      backgroundStreamRef.current = null;
      setIsBackgroundStreaming(false);
    }
  }, []);

  // Memoized context value
  const contextValue = useMemo(
    () => ({
      isStreaming,
      stream: streamRef.current,
      startCamera,
      stopCamera,
      cameraConfig,
      setCameraConfig,
      videoRef,
      backgroundStream: backgroundStreamRef.current,
      startBackgroundCamera,
      stopBackgroundCamera,
      isBackgroundStreaming,
    }),
    [isStreaming, startCamera, stopCamera, cameraConfig, isBackgroundStreaming, startBackgroundCamera, stopBackgroundCamera],
  );

  return (
    <CameraContext.Provider value={contextValue}>
      {children}
    </CameraContext.Provider>
  );
}

/**
 * Custom hook to use the camera context
 * @throws {Error} If used outside of CameraProvider
 */
export function useCamera() {
  const context = useContext(CameraContext);

  if (!context) {
    throw new Error('useCamera must be used within a CameraProvider');
  }

  return context;
}
