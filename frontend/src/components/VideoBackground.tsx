"use client";

import Hls from "hls.js";
import { useEffect, useRef } from "react";

const SOURCE = "https://stream.mux.com/Aa02T7oM1wH5Mk5EEVDYhbZ1ChcdhRsS2m1NYyx4Ua1g.m3u8";

export function VideoBackground({ flip = false }: { flip?: boolean }) {
  const ref = useRef<HTMLVideoElement>(null);
  useEffect(() => {
    const video = ref.current;
    if (!video) return;
    let hls: Hls | null = null;
    if (Hls.isSupported()) {
      hls = new Hls();
      hls.loadSource(SOURCE);
      hls.attachMedia(video);
    } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
      video.src = SOURCE;
    }
    return () => hls?.destroy();
  }, []);
  return <video ref={ref} autoPlay muted loop playsInline className={`absolute inset-0 h-full w-full object-cover ${flip ? "scale-y-[-1]" : ""}`} />;
}
