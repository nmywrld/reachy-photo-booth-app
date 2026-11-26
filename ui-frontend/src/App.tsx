/**
 * Copyright 2025 NVIDIA Corporation
 * SPDX-License-Identifier: Apache-2.0
 */

import { useCallback, useEffect, useState, useRef } from "react";
import useAppState from "./hooks/useAppState";
import useWebsocket from "./hooks/useWebsocket";
import useWebRTC from "./hooks/useWebRTC";
import ImageGeneration from "./ImageGeneration";
import Transcript from "./Transcript";
import BigMessage from "./BigMessage";
import type { BaseMessage, ShutterMessage } from "./types/api";
import FullScreen from "./FullScreen";
import UserTracking from "./UserTracking";
import Crosshair from "./Crosshair";
import LightBorder from "./LightBorder";
import CapturedImage from "./CapturedImage";
import QRCode from "./QRCode";
import Countdown from "./Countdown";
import WakeUpAnimation from "./WakeUpAnimation";
import VideoFeed from "./VideoFeed";
import ShutterButton from "./ShutterButton";
import MirrorPhotoCard from "./MirrorPhotoCard";

const WS_URL =
  import.meta.env.VITE_UI_SERVER_WS_URL || "ws://localhost:9000/ws";

function App() {
  const { lastMessage, sendMessage, readyState } =
    useWebsocket<BaseMessage>(WS_URL);
  const stream = useWebRTC({ lastMessage, sendMessage });
  const appState = useAppState(lastMessage);
  const [showWakeUp, setShowWakeUp] = useState(false);
  const prevToolTypeRef = useRef<string | null>(null);
  const pressShutter = useCallback(() => {
    const message: ShutterMessage = { message_type: "ShutterMessage" };
    sendMessage(message);
  }, [sendMessage]);

  useEffect(() => {
    if (!appState) return;

    const currentToolType = appState.tool?.type;
    const prevToolType = prevToolTypeRef.current;

    // Transition from falsy (no tool) to "AskHuman"
    if (!prevToolType && currentToolType === "AskHuman") {
      setShowWakeUp(true);
      // Remove the animation after it's done (roughly 2s based on animation duration)
      setTimeout(() => setShowWakeUp(false), 2000);
    }

    prevToolTypeRef.current = currentToolType || null;
  }, [appState]);

  if (readyState === WebSocket.CLOSED) {
    return (
      <FullScreen>
        <BigMessage>
          Websocket closed or failed to connect. Please reload the page.
        </BigMessage>
      </FullScreen>
    );
  }

  if (readyState === WebSocket.CONNECTING) {
    return (
      <FullScreen>
        <BigMessage>Connecting to server...</BigMessage>
      </FullScreen>
    );
  }

  if (!appState) {
    return (
      <FullScreen>
        <BigMessage>Waiting for app state...</BigMessage>
      </FullScreen>
    );
  }

  const {
    tool,
    transcript,
    animation,
    tracking_data,
    qr_code,
    countdown_started_at,
    countdown_duration,
    user_present,
    mirror_photo,
    shutter_busy
  } = appState;

  // The magic mirror is the default screen. The original prompt-driven flow
  // (look_at_human -> generate_image) still takes over the screen when used.
  const showImageGeneration = tool?.type === "GenerateImage";
  const capturedImageUrl =
    tool?.type === "LookAtHuman" ? tool.captured_image : null;
  const showMirror = !showImageGeneration && !capturedImageUrl;

  return (
    <FullScreen>
      {showMirror && (
        <>
          <VideoFeed className="h-full w-full" stream={stream} />
          <UserTracking
            className="absolute h-full w-full"
            circles={tracking_data}
          />
          {tool?.type === "LookAtHuman" && (
            <Crosshair className="absolute h-full w-full" />
          )}
          {showWakeUp && <WakeUpAnimation className="absolute h-full w-full" />}
          <Countdown
            className="absolute h-full w-full"
            timestamp={countdown_started_at}
            duration={countdown_duration ?? 0}
          />
          {!tool && !mirror_photo && (
            <p className="absolute top-[4vh] left-1/2 -translate-x-1/2 rounded-full bg-black/55 px-[3vh] py-[1.2vh] text-center text-[3vh] backdrop-blur-sm">
              {user_present
                ? "Tell Reachy a style, like “make me a pirate”, then press the shutter!"
                : "Step in front of the magic mirror"}
            </p>
          )}
          {mirror_photo && (
            <MirrorPhotoCard
              className="absolute right-[3vw] top-1/2 w-[30vw] -translate-y-1/2"
              photo={mirror_photo}
            />
          )}
          <ShutterButton
            className="absolute bottom-[5vh] right-[4vw] h-[13vh] w-[13vh]"
            disabled={shutter_busy || !user_present}
            onPress={pressShutter}
          />
        </>
      )}
      {showImageGeneration && (
        <ImageGeneration
          className="h-full w-full"
          capturedImageUrl={tool.captured_image}
          generatedImageUrl={tool.generated_image}
        />
      )}
      {capturedImageUrl && (
        <CapturedImage
          className="h-full w-full"
          capturedImageUrl={capturedImageUrl}
        />
      )}
      {animation && (
        // Decorative: must never take clicks meant for the shutter button.
        <LightBorder className="absolute inset-0 pointer-events-none" animation={animation} />
      )}
      {qr_code ? (
        <div className="absolute bottom-10 w-3/4 left-1/2 -translate-x-1/2 flex flex-row items-center gap-8">
          <Transcript className="w-full" transcript={transcript} />
          <QRCode className="w-1/5 shrink-0" url={qr_code} />
        </div>
      ) : (
        <Transcript
          className="absolute bottom-10 w-3/4 left-1/2 -translate-x-1/2"
          transcript={transcript}
        />
      )}
    </FullScreen>
  );
}

export default App;
