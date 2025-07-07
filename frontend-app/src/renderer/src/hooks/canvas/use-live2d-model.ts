/* eslint-disable no-use-before-define */
/* eslint-disable no-param-reassign */
import { useEffect, useRef, useCallback, useState } from "react";
import * as PIXI from "pixi.js";
import {
  Live2DModel,
  MotionPreloadStrategy,
  MotionPriority,
} from "pixi-live2d-display-lipsyncpatch";
import {
  ModelInfo,
  useLive2DConfig,
  MotionWeightMap,
  TapMotionMap,
} from "@/context/live2d-config-context";
import { useLive2DModel as useModelContext } from "@/context/live2d-model-context";
import { setModelSize, resetModelPosition } from "./use-live2d-resize";
import { audioTaskQueue } from "@/utils/task-queue";
import { AiStateEnum, useAiState } from "@/context/ai-state-context";
import { toaster } from "@/components/ui/toaster";
import { useForceIgnoreMouse } from "../utils/use-force-ignore-mouse";
import { debugLive2D } from "@/utils/live2d-debug";

interface UseLive2DModelProps {
  isPet: boolean; // Whether the model is in pet mode
  modelInfo: ModelInfo | undefined; // Live2D model configuration information
}

export const useLive2DModel = ({
  isPet,
  modelInfo,
}: UseLive2DModelProps) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const appRef = useRef<PIXI.Application | null>(null);
  const modelRef = useRef<Live2DModel | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const kScaleRef = useRef<string | number | undefined>(undefined);
  const lastLoadedUrlRef = useRef<string | null>(null);
  const { setCurrentModel } = useModelContext();
  const { setIsLoading } = useLive2DConfig();
  const loadingRef = useRef(false);
  const { setAiState, aiState } = useAiState();
  const [isModelReady, setIsModelReady] = useState(false);
  const { forceIgnoreMouse } = useForceIgnoreMouse();

  // Cleanup function for Live2D model
  const cleanupModel = useCallback(() => {
    if (modelRef.current) {
      modelRef.current.removeAllListeners();
      setCurrentModel(null);
      if (appRef.current) {
        appRef.current.stage.removeChild(modelRef.current);
        modelRef.current.destroy({
          children: true,
          texture: true,
          baseTexture: true,
        });
        PIXI.utils.clearTextureCache();
        modelRef.current = null;
      }
    }
    lastLoadedUrlRef.current = null; // Reset the last loaded URL
    setIsModelReady(false);
  }, [setCurrentModel]);

  // Initialize PIXI application with canvas (only once)
  useEffect(() => {
    let app: PIXI.Application | null = null;
    
    const initializeApp = () => {
      if (!canvasRef.current || appRef.current) {
        debugLive2D.log("Skipping PIXI app initialization", {
          hasCanvas: !!canvasRef.current,
          hasExistingApp: !!appRef.current
        });
        return;
      }
      
      try {
        debugLive2D.log("Initializing PIXI Application");
        app = new PIXI.Application({
          view: canvasRef.current, // canvas element to render on
          autoStart: true,
          width: window.innerWidth,
          height: window.innerHeight,
          backgroundAlpha: 0, // transparent background
          antialias: true, // antialiasing
          clearBeforeRender: true, // clear before render
          preserveDrawingBuffer: false, // don't preserve drawing buffer
          powerPreference: "high-performance", // high performance, use GPU if available
          resolution: window.devicePixelRatio || 1,
          autoDensity: true, // auto adjust resolution to fit the screen
        });

        // Render on every frame
        app.ticker.add(() => {
          if (app?.renderer && appRef.current) {
            app.renderer.render(app.stage);
          }
        });

        appRef.current = app;
        debugLive2D.log("PIXI Application initialized successfully");
      } catch (error) {
        debugLive2D.error("Failed to initialize PIXI Application", error);
      }
    };

    // Initialize with a small delay to ensure canvas is ready
    const timeoutId = setTimeout(initializeApp, 10);

    return () => {
      clearTimeout(timeoutId);
      // Only cleanup if this is the final unmount
      if (app && appRef.current) {
        try {
          debugLive2D.log("Destroying PIXI Application");
          app.destroy(true, {
            children: true,
            texture: true,
            baseTexture: true,
          });
          PIXI.utils.destroyTextureCache();
          debugLive2D.log("PIXI Application destroyed");
        } catch (error) {
          debugLive2D.error("Error destroying PIXI Application", error);
        }
      }
      appRef.current = null;
    };
  }, []); // Empty dependency array - only run once

  const setupModel = useCallback(
    async (model: Live2DModel) => {
      if (!appRef.current) {
        debugLive2D.warn("No PIXI app available for model setup");
        return;
      }

      if (modelRef.current) {
        modelRef.current.removeAllListeners();
        appRef.current.stage.removeChild(modelRef.current);
        modelRef.current.destroy({
          children: true,
          texture: true,
          baseTexture: true,
        });
        PIXI.utils.clearTextureCache();
      }

      modelRef.current = model;
      setCurrentModel(model);
      appRef.current.stage.addChild(model);

      model.interactive = true;
      model.cursor = "pointer";
      
      // Set the anchor point to center for proper centering
      model.anchor.set(0.5, 0.5);
      
      setIsModelReady(true);
      debugLive2D.log("Model setup completed successfully");
    },
    [setCurrentModel], // Only depend on setCurrentModel
  );

  const setupModelSizeAndPosition = useCallback(() => {
    if (!modelRef.current) return;
    setModelSize(modelRef.current, kScaleRef.current);

    const { width, height } = isPet
      ? { width: window.innerWidth, height: window.innerHeight }
      : containerRef.current?.getBoundingClientRect() || {
        width: 0,
        height: 0,
      };

    resetModelPosition(modelRef.current, width, height, modelInfo?.initialXshift, modelInfo?.initialYshift);
  }, [isPet, modelInfo?.initialXshift, modelInfo?.initialYshift]);

  // Load Live2D model with configuration
  const loadModel = useCallback(async () => {
    if (!modelInfo?.url || !appRef.current) {
      debugLive2D.log("Cannot load model: missing URL or PIXI app", { 
        hasUrl: !!modelInfo?.url, 
        hasApp: !!appRef.current 
      });
      return;
    }

    if (loadingRef.current) {
      debugLive2D.log("Model loading already in progress, skipping...");
      return; // Prevent multiple simultaneous loads
    }

    debugLive2D.log("Starting model load", modelInfo.url);

    // Check if model URL is accessible
    const urlExists = await debugLive2D.checkModelUrl(modelInfo.url);
    if (!urlExists) {
      debugLive2D.error("Model URL is not accessible", modelInfo.url);
      return;
    }

    try {
      loadingRef.current = true;
      setIsLoading(true);
      setAiState(AiStateEnum.LOADING);

      // Clean up existing model first
      if (modelRef.current) {
        debugLive2D.log("Cleaning up existing model");
        cleanupModel();
      }

      debugLive2D.log("Creating Live2D model from URL", {
        url: modelInfo.url,
        idleMotionGroup: modelInfo.idleMotionGroupName,
        pointerInteractive: modelInfo.pointerInteractive
      });

      // Initialize Live2D model with settings
      const model = await Live2DModel.from(modelInfo.url, {
        autoHitTest: true,
        autoFocus: modelInfo.pointerInteractive ?? false,
        autoUpdate: true,
        ticker: PIXI.Ticker.shared,
        motionPreload: MotionPreloadStrategy.IDLE,
        idleMotionGroup: modelInfo.idleMotionGroupName,
      });

      debugLive2D.log("Live2D model created successfully");

      // Only setup if the app still exists (component not unmounted)
      if (appRef.current) {
        await setupModel(model);
        debugLive2D.log("Model loaded and setup successfully");
      } else {
        debugLive2D.warn("App was destroyed during model loading, cleaning up model");
        model.destroy();
      }
    } catch (error) {
      debugLive2D.error("Failed to load Live2D model", error);
      toaster.create({
        title: `Failed to load Live2D model: ${error}`,
        type: "error",
        duration: 2000,
      });
    } finally {
      loadingRef.current = false;
      setIsLoading(false);
      setAiState(AiStateEnum.IDLE);
    }
  }, [
    modelInfo?.url,
    modelInfo?.pointerInteractive,
    modelInfo?.idleMotionGroupName,
    setIsLoading,
    setAiState,
    setupModel,
    cleanupModel,
  ]);

  const setupModelInteractions = useCallback(
    (model: Live2DModel) => {
      if (!model) return;

      // Clear all previous listeners
      model.removeAllListeners("pointerenter");
      model.removeAllListeners("pointerleave");
      model.removeAllListeners("rightdown");
      model.removeAllListeners("pointerdown");
      model.removeAllListeners("pointermove");
      model.removeAllListeners("pointerup");
      model.removeAllListeners("pointerupoutside");

      // If force ignore mouse is enabled, disable interaction
      if (forceIgnoreMouse && isPet) {
        model.interactive = false;
        model.cursor = "default";
        return;
      }

      // Enable interactions
      model.interactive = true;
      model.cursor = "pointer";

      let dragging = false;
      let pointerX = 0;
      let pointerY = 0;
      let isTap = false;
      const dragThreshold = 5;

      if (isPet) {
        model.on("pointerenter", () => {
          (window.api as any)?.updateComponentHover("live2d-model", true);
        });

        model.on("pointerleave", () => {
          if (!dragging) {
            (window.api as any)?.updateComponentHover("live2d-model", false);
          }
        });

        model.on("rightdown", (e: any) => {
          e.data.originalEvent.preventDefault();
          (window.api as any).showContextMenu();
        });
      }

      model.on("pointerdown", (e) => {
        if (e.button === 0) {
          dragging = true;
          isTap = true;
          pointerX = e.global.x - model.x;
          pointerY = e.global.y - model.y;
        }
      });

      model.on("pointermove", (e) => {
        if (dragging) {
          const newX = e.global.x - pointerX;
          const newY = e.global.y - pointerY;
          const dx = newX - model.x;
          const dy = newY - model.y;

          if (Math.hypot(dx, dy) > dragThreshold) {
            isTap = false;
          }

          model.position.x = newX;
          model.position.y = newY;
        }
      });

      model.on("pointerup", (e) => {
        if (dragging) {
          dragging = false;
          if (isTap) {
            handleTapMotion(model, e.global.x, e.global.y);
          }
        }
      });

      model.on("pointerupoutside", () => {
        dragging = false;
      });
    },
    [isPet, forceIgnoreMouse],
  );

  const handleTapMotion = useCallback(
    (model: Live2DModel, x: number, y: number) => {
      if (!modelInfo?.tapMotions) return;

      console.log("handleTapMotion", modelInfo?.tapMotions);
      // Convert global coordinates to model's local coordinates
      const localPos = model.toLocal(new PIXI.Point(x, y));
      const hitAreas = model.hitTest(localPos.x, localPos.y);

      const foundMotion = hitAreas.find((area) => {
        const motionGroup = modelInfo?.tapMotions?.[area];
        if (motionGroup) {
          console.log(`Found motion group for area ${area}:`, motionGroup);
          playRandomMotion(model, motionGroup);
          return true;
        }
        return false;
      });

      if (!foundMotion && Object.keys(modelInfo.tapMotions).length > 0) {
        const mergedMotions = getMergedMotionGroup(modelInfo.tapMotions);
        playRandomMotion(model, mergedMotions);
      }
    },
    [modelInfo?.tapMotions],
  );

  // Reset expression when AI state changes to IDLE (like finishing a conversation)
  useEffect(() => {
    if (aiState === AiStateEnum.IDLE) {
      console.log("defaultEmotion: ", modelInfo?.defaultEmotion);
      if (modelInfo?.defaultEmotion) {
        modelRef.current?.internalModel.motionManager.expressionManager?.setExpression(
          modelInfo.defaultEmotion,
        );
      } else {
        modelRef.current?.internalModel.motionManager.expressionManager?.resetExpression();
      }
    }
  }, [modelRef.current, aiState, modelInfo?.defaultEmotion]);

  // Load model when URL changes and cleanup on unmount
  useEffect(() => {
    if (!modelInfo?.url) return;
    
    // Skip if we've already loaded this URL and model exists
    if (modelInfo.url === lastLoadedUrlRef.current && modelRef.current) {
      debugLive2D.log("Model already loaded for this URL, skipping", modelInfo.url);
      return;
    }
    
    debugLive2D.log("Model URL effect triggered", modelInfo.url);
    
    // Avoid loading if already in progress
    if (loadingRef.current) {
      debugLive2D.log("Model already loading, skipping...");
      return;
    }
    
    // Add a small delay to ensure PIXI app is ready
    const timeoutId = setTimeout(() => {
      if (appRef.current && !loadingRef.current) {
        debugLive2D.log("PIXI app ready, loading model");
        lastLoadedUrlRef.current = modelInfo.url;
        loadModel();
      } else if (!appRef.current) {
        debugLive2D.warn("PIXI app not ready yet, retrying...");
        // Retry after another delay if app is not ready
        setTimeout(() => {
          if (appRef.current && !loadingRef.current) {
            debugLive2D.log("PIXI app ready on retry, loading model");
            lastLoadedUrlRef.current = modelInfo.url;
            loadModel();
          } else {
            debugLive2D.error("PIXI app still not ready after retry");
          }
        }, 100);
      }
    }, 50);
    
    return () => clearTimeout(timeoutId);
  }, [modelInfo?.url]); // Only depend on URL

  // Separate effect for cleanup on unmount
  useEffect(() => {
    return () => {
      debugLive2D.log("Component unmounting, cleaning up model");
      cleanupModel();
    };
  }, [cleanupModel]);

  useEffect(() => {
    kScaleRef.current = modelInfo?.kScale;
  }, [modelInfo?.kScale]);

  useEffect(() => {
    setupModelSizeAndPosition();
  }, [isModelReady, setupModelSizeAndPosition]);

  useEffect(() => {
    if (modelRef.current && isModelReady) {
      setupModelInteractions(modelRef.current);
    }
  }, [isModelReady, setupModelInteractions, forceIgnoreMouse]);

  return {
    canvasRef,
    appRef,
    modelRef,
    containerRef,
  };
};

const playRandomMotion = (model: Live2DModel, motionGroup: MotionWeightMap) => {
  if (!motionGroup || Object.keys(motionGroup).length === 0) return;

  const totalWeight = Object.values(motionGroup).reduce((sum, weight) => sum + weight, 0);
  let random = Math.random() * totalWeight;

  Object.entries(motionGroup).find(([motion, weight]) => {
    random -= weight;
    if (random <= 0) {
      const priority = audioTaskQueue.hasTask()
        ? MotionPriority.NORMAL
        : MotionPriority.FORCE;

      console.log(
        `Playing weighted motion: ${motion} (weight: ${weight}/${totalWeight}, priority: ${priority})`,
      );
      model.motion(motion, undefined, priority);
      return true;
    }
    return false;
  });
};

const getMergedMotionGroup = (
  tapMotions: TapMotionMap,
): MotionWeightMap => {
  const mergedMotions: {
    [key: string]: { total: number; count: number };
  } = {};

  Object.values(tapMotions)
    .flatMap((motionGroup) => Object.entries(motionGroup))
    .reduce((acc, [motion, weight]) => {
      if (!acc[motion]) {
        acc[motion] = { total: 0, count: 0 };
      }
      acc[motion].total += weight;
      acc[motion].count += 1;
      return acc;
    }, mergedMotions);

  return Object.entries(mergedMotions).reduce(
    (acc, [motion, { total, count }]) => ({
      ...acc,
      [motion]: total / count,
    }),
    {} as MotionWeightMap,
  );
};
