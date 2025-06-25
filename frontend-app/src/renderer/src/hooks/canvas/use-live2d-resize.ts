import { useEffect, useCallback, useRef } from 'react';
import { Live2DModel } from 'pixi-live2d-display-lipsyncpatch';
import * as PIXI from 'pixi.js';
import { ModelInfo, useLive2DConfig } from '@/context/live2d-config-context';

// Speed of model scaling when using mouse wheel
const SCALE_SPEED = 0.01;

// Reset model to center of container with initial offset
export const resetModelPosition = (
  model: Live2DModel,
  width: number,
  height: number,
  initialXshift: number | undefined,
  initialYshift: number | undefined,
) => {
  if (!model) return;
  const initXshift = Number(initialXshift || 0);
  const initYshift = Number(initialYshift || 0);
  const targetX = (width - model.width) / 2 + initXshift;
  const targetY = (height - model.height) / 2 + initYshift;

  model.position.set(targetX, targetY);
};

// Handle model scaling with smooth interpolation
const handleModelScale = (
  model: Live2DModel,
  deltaY: number,
) => {
  const delta = deltaY > 0 ? -SCALE_SPEED : SCALE_SPEED;
  const currentScale = model.scale.x;
  const newScale = currentScale + delta;

  const lerpFactor = 0.3;
  const smoothScale = currentScale + (newScale - currentScale) * lerpFactor;

  model.scale.set(smoothScale);
  return smoothScale;
};

// Set model size based on device pixel ratio and kScale in modelInfo
export const setModelSize = (
  model: Live2DModel,
  kScale: string | number | undefined,
) => {
  if (!model || !kScale) return;
  const dpr = Number(window.devicePixelRatio || 1);
  model.scale.set(Number(kScale));

  // Update filter resolution for retina displays
  if (model.filters) {
    model.filters.forEach((filter) => {
      if ("resolution" in filter) {
        Object.defineProperty(filter, "resolution", { value: dpr });
      }
    });
  }
};

// Main hook for handling Live2D model resizing and scaling
export const useLive2DResize = (
  containerRef: React.RefObject<HTMLDivElement>,
  appRef: React.RefObject<PIXI.Application>,
  modelRef: React.RefObject<Live2DModel>,
  modelInfo: ModelInfo | undefined,
  isPet: boolean,
) => {
  const { updateModelScale } = useLive2DConfig();
  const scaleUpdateTimeout = useRef<NodeJS.Timeout | null>(null);
  const lastScaleRef = useRef<number | null>(null);

  // Handle mouse wheel scaling
  const handleWheel = useCallback((e: WheelEvent) => {
    if (!modelRef.current || !modelInfo?.scrollToResize) return;
    e.preventDefault();
    const smoothScale = handleModelScale(modelRef.current, e.deltaY);

    // Only update scale if change is significant
    const hasSignificantChange = !lastScaleRef.current ||
      Math.abs(smoothScale - lastScaleRef.current) > 0.0001;

    if (hasSignificantChange) {
      if (scaleUpdateTimeout.current) {
        clearTimeout(scaleUpdateTimeout.current);
      }

      // Debounce scale updates
      scaleUpdateTimeout.current = setTimeout(() => {
        updateModelScale(smoothScale);
        lastScaleRef.current = smoothScale;
      }, 500);
    }
  }, [modelRef, modelInfo?.scrollToResize, updateModelScale]);

  // Add wheel event listener
  useEffect(() => {
    const canvas = containerRef.current?.querySelector('canvas');
    if (canvas) {
      canvas.addEventListener('wheel', handleWheel, { passive: false });
      return () => canvas.removeEventListener('wheel', handleWheel);
    }
    return undefined;
  }, [handleWheel, containerRef]);

  // Handle container resize
  useEffect(() => {
    const observer = new ResizeObserver(() => {
      if (modelRef.current && appRef.current) {
        // Get container dimensions based on mode
        const { width, height } = isPet
          ? { width: window.innerWidth, height: window.innerHeight }
          : containerRef.current?.getBoundingClientRect() || {
            width: 0,
            height: 0,
          };

        // Resize renderer and reset model position
        appRef.current.renderer.resize(width, height);
        appRef.current.renderer.clear();
        resetModelPosition(modelRef.current, width, height, modelInfo?.initialXshift, modelInfo?.initialYshift);
      }
    });

    if (containerRef.current) {
      observer.observe(containerRef.current);
    }

    return () => {
      observer.disconnect();
    };
  }, [modelRef, containerRef, isPet, appRef]);

  // Cleanup timeout on unmount
  useEffect(() => () => {
    if (scaleUpdateTimeout.current) {
      clearTimeout(scaleUpdateTimeout.current);
    }
  }, []);
};
