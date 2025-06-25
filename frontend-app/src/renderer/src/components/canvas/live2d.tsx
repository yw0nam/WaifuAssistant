/* eslint-disable @typescript-eslint/ban-ts-comment */
import { memo, useEffect } from "react";
import { useLive2DConfig } from "@/context/live2d-config-context";
import { useIpcHandlers } from "@/hooks/utils/use-ipc-handlers";
import { useLive2DModel } from "@/hooks/canvas/use-live2d-model";
import { useLive2DResize } from "@/hooks/canvas/use-live2d-resize";
import { useInterrupt } from "@/hooks/utils/use-interrupt";
import { useAudioTask } from "@/hooks/utils/use-audio-task";
import { useForceIgnoreMouse } from "@/hooks/utils/use-force-ignore-mouse";

interface Live2DProps {
  isPet: boolean;
}

export const Live2D = memo(({ isPet }: Live2DProps): JSX.Element => {
  const { modelInfo, isLoading } = useLive2DConfig();
  const { forceIgnoreMouse } = useForceIgnoreMouse();

  // Register IPC handlers here as Live2D is a persistent component in the pet mode
  useIpcHandlers({ isPet });

  const { canvasRef, appRef, modelRef, containerRef } = useLive2DModel({
    isPet,
    modelInfo,
  });

  useLive2DResize(containerRef, appRef, modelRef, modelInfo, isPet);

  // Export these hooks for global use
  useInterrupt();
  useAudioTask();

  useEffect(() => {
    if (modelRef.current) {
      // @ts-ignore
      window.live2d = {
        expression: (name?: string | number) => modelRef.current?.expression(name),
        setExpression: (name?: string | number) => {
          if (name !== undefined) {
            modelRef.current?.internalModel.motionManager.expressionManager?.setExpression(name);
          }
        },
        setRandomExpression: () => modelRef.current?.internalModel.motionManager.expressionManager?.setRandomExpression(),
        getExpressions: () => modelRef.current?.internalModel.motionManager.expressionManager?.definitions.map((d) => d.name),
      };
    }
    return () => {
      // @ts-ignore
      delete window.live2d;
    };
  }, [modelRef.current]); // window.live2d.expression() / getExpressions() / setRandomExpression()

  return (
    <div
      ref={containerRef}
      style={{
        width: isPet ? "100vw" : "100%",
        height: isPet ? "100vh" : "100%",
        pointerEvents: isPet && forceIgnoreMouse ? "none" : "auto",
        overflow: "hidden",
        opacity: isLoading ? 0 : 1,
        transition: "opacity 0.3s ease-in-out",
      }}
    >
      <canvas
        id="canvas"
        ref={canvasRef}
        style={{
          width: "100%",
          height: "100%",
          pointerEvents: isPet && forceIgnoreMouse ? "none" : "auto",
          display: "block",
        }}
      />
    </div>
  );
});

Live2D.displayName = "Live2D";

export { useInterrupt, useAudioTask };
