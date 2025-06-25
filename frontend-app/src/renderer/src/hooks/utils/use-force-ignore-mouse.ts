import { create } from "zustand";

// Define the state store interface
interface ForceIgnoreMouseState {
  // Whether mouse events are forcibly ignored
  forceIgnoreMouse: boolean;
  // Set the force ignore mouse state
  setForceIgnoreMouse: (forceIgnore: boolean) => void;
}

// Create a global store for force ignore mouse state
const useForceIgnoreMouseStore = create<ForceIgnoreMouseState>((set) => ({
  forceIgnoreMouse: false,
  setForceIgnoreMouse: (forceIgnore) => set({ forceIgnoreMouse: forceIgnore }),
}));

/**
 * Hook to access and manage force ignore mouse state
 * This is used to enable/disable mouse interaction with the model in pet mode
 */
export function useForceIgnoreMouse() {
  const { forceIgnoreMouse, setForceIgnoreMouse } = useForceIgnoreMouseStore();

  return {
    forceIgnoreMouse,
    setForceIgnoreMouse,
  };
}
