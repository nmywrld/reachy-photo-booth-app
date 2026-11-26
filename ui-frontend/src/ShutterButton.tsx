/**
 * SPDX-License-Identifier: Apache-2.0
 */

import classNames from "classnames";
import { useEffect } from "react";

interface ShutterButtonProps {
  className?: string;
  disabled: boolean;
  onPress: () => void;
}

/**
 * Round camera-style shutter. Enter also presses it, so a keyboard or a USB
 * presenter clicker works when the kiosk has no touchscreen.
 */
export default function ShutterButton({
  className,
  disabled,
  onPress
}: ShutterButtonProps) {
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.code === "Enter" || event.code === "NumpadEnter") {
        event.preventDefault();
        if (!disabled) onPress();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [disabled, onPress]);

  return (
    <button
      type="button"
      aria-label="Take a photo"
      disabled={disabled}
      onClick={onPress}
      className={classNames(
        // Above every overlay (light border, countdown, photo card).
        "z-50 rounded-full border-[0.8vh] border-white bg-white/25 backdrop-blur-sm",
        "flex items-center justify-center transition-transform",
        "active:scale-90 disabled:opacity-40 disabled:active:scale-100",
        className
      )}
    >
      <span className="block h-[78%] w-[78%] rounded-full bg-white" />
    </button>
  );
}
