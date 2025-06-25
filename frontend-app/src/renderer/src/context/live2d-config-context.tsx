import {
  createContext, useContext, useState, useMemo, useEffect, useCallback,
} from 'react';
import { useLocalStorage } from '@/hooks/utils/use-local-storage';
import { useConfig } from '@/context/character-config-context';
import { toaster } from '@/components/ui/toaster';

/**
 * Model emotion mapping interface
 * @interface EmotionMap
 */
interface EmotionMap {
  [key: string]: number | string;
}

/**
 * Motion weight mapping interface
 * @interface MotionWeightMap
 */
export interface MotionWeightMap {
  [key: string]: number;
}

/**
 * Tap motion mapping interface
 * @interface TapMotionMap
 */
export interface TapMotionMap {
  [key: string]: MotionWeightMap;
}

/**
 * Live2D model information interface
 * @interface ModelInfo
 */
export interface ModelInfo {
  /** Model name */
  name?: string;

  /** Model description */
  description?: string;

  /** Model URL */
  url: string;

  /** Scale factor */
  kScale: number;

  /** Initial X position shift */
  initialXshift: number;

  /** Initial Y position shift */
  initialYshift: number;

  /** Idle motion group name */
  idleMotionGroupName?: string;

  /** Default emotion */
  defaultEmotion?: number | string;

  /** Emotion mapping configuration */
  emotionMap: EmotionMap;

  /** Enable pointer interactivity */
  pointerInteractive?: boolean;

  /** Tap motion mapping configuration */
  tapMotions?: TapMotionMap;

  /** Enable scroll to resize */
  scrollToResize?: boolean;
}

/**
 * Live2D configuration context state interface
 * @interface Live2DConfigState
 */
interface Live2DConfigState {
  modelInfo?: ModelInfo;
  setModelInfo: (info: ModelInfo | undefined) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  updateModelScale: (newScale: number) => void;
}

/**
 * Default values and constants
 */
const DEFAULT_CONFIG = {
  modelInfo: {
    name: 'Mao',
    description: 'Cute assistant character',
    url: '/live2d-models/mao_pro_jp/runtime/mao_pro.model3.json',
    kScale: 0.15,
    initialXshift: 0,
    initialYshift: 0,
    idleMotionGroupName: 'idle',
    defaultEmotion: 0,
    emotionMap: {
      neutral: 0,
      happy: 1,
      sad: 2,
      surprised: 3,
      angry: 4,
    },
    pointerInteractive: true,
    scrollToResize: true,
    tapMotions: {},
  } as ModelInfo,
  isLoading: false,
};

/**
 * Create the Live2D configuration context
 */
export const Live2DConfigContext = createContext<Live2DConfigState | null>(null);

/**
 * Live2D Configuration Provider Component
 * @param {Object} props - Provider props
 * @param {React.ReactNode} props.children - Child components
 */
export function Live2DConfigProvider({ children }: { children: React.ReactNode }) {
  const { confUid } = useConfig();

  const [isPet, setIsPet] = useState(false);
  const [isLoading, setIsLoading] = useState(DEFAULT_CONFIG.isLoading);

  useEffect(() => {
    const unsubscribe = (window.api as any)?.onModeChanged((mode: string) => {
      setIsPet(mode === "pet");
    });
    return () => unsubscribe?.();
  }, []);

  const getStorageKey = (uid: string, isPetMode: boolean) => `${uid}_${isPetMode ? "pet" : "window"}`;

  const [modelInfo, setModelInfoState] = useLocalStorage<ModelInfo | undefined>(
    "modelInfo",
    DEFAULT_CONFIG.modelInfo,
    {
      filter: (value) => (value ? { ...value, url: "" } : value),
    },
  );

  const [scaleMemory, setScaleMemory] = useLocalStorage<Record<string, number>>(
    "scale_memory",
    {},
  );

  /**
   * Updates the Live2D model information and manages model scale persistence
   * @param info - The new model information to be set
   * @returns void
   */
  const setModelInfo = (info: ModelInfo | undefined) => {
    // Skip if no model URL is provided (avoid localStorage modelInfo remaining)
    if (!info?.url) {
      return;
    }

    // Validate configuration UID exists
    if (!confUid) {
      console.warn("Attempting to set model info without confUid");
      toaster.create({
        title: "Attempting to set model info without confUid",
        type: "error",
        duration: 2000,
      });
      return;
    }

    // Prevent unnecessary updates if model info hasn't changed
    if (JSON.stringify(info) === JSON.stringify(modelInfo)) {
      return;
    }

    if (info) {
      // Generate storage key based on confUid and mode
      const storageKey = getStorageKey(confUid, isPet);
      let finalScale: number;

      // Retrieve stored scale
      const storedScale = scaleMemory[storageKey];
      if (storedScale !== undefined) {
        finalScale = storedScale;
      } else {
        finalScale = Number(info.kScale || 0.001);
        // If no stored scale, store the initial scale in memory
        setScaleMemory((prev) => ({
          ...prev,
          [storageKey]: finalScale,
        }));
      }

      console.log("finalScale", finalScale);

      setModelInfoState({
        ...info,
        kScale: finalScale,
        // use new settings to updata the local storage, or still use the stored settings
        pointerInteractive:
          "pointerInteractive" in info
            ? info.pointerInteractive
            : (modelInfo?.pointerInteractive ?? false),
        scrollToResize:
          "scrollToResize" in info
            ? info.scrollToResize
            : (modelInfo?.scrollToResize ?? true),
      });
    } else {
      // Reset model info state when clearing (like switching character)
      setModelInfoState(undefined);
    }
  };
  const updateModelScale = useCallback(
    // Updates the Live2D model scale and persists it to local storage when scrolling in useLive2DResize
    (newScale: number) => {
      if (modelInfo) {
        const storageKey = getStorageKey(confUid, isPet);
        const fixedScale = Number(newScale.toFixed(8));
        setScaleMemory((prev) => ({
          ...prev,
          [storageKey]: fixedScale,
        })); // Update the scale in local storage

        setModelInfoState({
          ...modelInfo,
          kScale: fixedScale,
        }); // Update the modelInfo state
      }
    },
    [modelInfo, confUid, isPet, setScaleMemory, setModelInfoState],
  );

  useEffect(() => {
    // If modelInfo is updated, we need to use local storage to update some persistent user settings, like the scale.
    if (modelInfo) {
      const storageKey = getStorageKey(confUid, isPet);
      const memorizedScale = scaleMemory[storageKey];
      if (
        memorizedScale !== undefined &&
        memorizedScale !== Number(modelInfo.kScale)
      ) {
        setModelInfo({
          ...modelInfo,
          kScale: memorizedScale,
        });
      }
    }
  }, [isPet, modelInfo]);
  // Don't set confUid in the dependency beacause it will use old modelInfo to update.

  // Context value
  const contextValue = useMemo(
    () => ({
      modelInfo,
      setModelInfo,
      isLoading,
      setIsLoading,
      updateModelScale,
    }),
    [modelInfo, isLoading, updateModelScale],
  );

  return (
    <Live2DConfigContext.Provider value={contextValue}>
      {children}
    </Live2DConfigContext.Provider>
  );
}

/**
 * Custom hook to use the Live2D configuration context
 * @throws {Error} If used outside of Live2DConfigProvider
 */
export function useLive2DConfig() {
  const context = useContext(Live2DConfigContext);

  if (!context) {
    throw new Error('useLive2DConfig must be used within a Live2DConfigProvider');
  }

  return context;
}

// Export the provider as default
export default Live2DConfigProvider;
