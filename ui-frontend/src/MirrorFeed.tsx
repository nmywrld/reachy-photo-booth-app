/**
 * SPDX-License-Identifier: Apache-2.0
 */

import classNames from "classnames";
import { useEffect, useRef } from "react";

interface MirrorFeedProps {
  className?: string;
  stream: MediaStream | null;
}

/**
 * The magic mirror: the square stylized feed, shown whole in the middle of the
 * screen, over a blurred, enlarged copy of itself that fills the sides.
 */
export default function MirrorFeed({ className, stream }: MirrorFeedProps) {
  const backRef = useRef<HTMLVideoElement>(null);
  const frontRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    for (const video of [backRef.current, frontRef.current]) {
      if (video && stream) video.srcObject = stream;
    }
  }, [stream]);

  return (
    <div className={classNames("relative overflow-hidden", className)}>
      <video
        autoPlay
        playsInline
        muted
        ref={backRef}
        className="absolute inset-0 h-full w-full object-cover scale-110 blur-2xl opacity-60"
      />
      <video
        autoPlay
        playsInline
        muted
        ref={frontRef}
        className="absolute inset-0 h-full w-full object-contain"
      />
    </div>
  );
}
