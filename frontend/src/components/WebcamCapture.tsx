import { forwardRef, useEffect, useImperativeHandle, useRef, useState } from "react";

export type WebcamCaptureRef = {
  captureSequence: (opts: { frames: number; fps: number; quality: number }) => Promise<string[]>;
};

type Props = {
  className?: string;
};

function stripDataUrlPrefix(dataUrl: string) {
  const idx = dataUrl.indexOf(",");
  return idx >= 0 ? dataUrl.slice(idx + 1) : dataUrl;
}

export const WebcamCapture = forwardRef<WebcamCaptureRef, Props>(function WebcamCaptureInner({ className }, ref) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [cameraReady, setCameraReady] = useState(false);
  const captureInFlight = useRef(false);
  const [isCapturing, setIsCapturing] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function start() {
      setCameraError(null);
      setCameraReady(false);
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { width: { ideal: 480 }, height: { ideal: 360 }, facingMode: "user" },
          audio: false
        });
        if (cancelled) return;
        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          await videoRef.current.play();
          setCameraReady(true);
        }
      } catch (e: any) {
        setCameraError(e?.message || "Camera permission denied");
      }
    }

    start();
    return () => {
      cancelled = true;
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((t) => t.stop());
        streamRef.current = null;
      }
    };
  }, []);

  useImperativeHandle(ref, () => ({
    async captureSequence({ frames, fps, quality }) {
      if (captureInFlight.current) throw new Error("Capture already in progress");
      if (!cameraReady || !videoRef.current) throw new Error("Camera not ready");

      captureInFlight.current = true;
      setIsCapturing(true);
      try {
        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d");
        if (!ctx) throw new Error("No canvas context");

        const targetW = 320;
        const targetH = 240;
        canvas.width = targetW;
        canvas.height = targetH;

        const intervalMs = Math.max(1, Math.floor(1000 / fps));
        const out: string[] = [];

        for (let i = 0; i < frames; i++) {
          ctx.drawImage(videoRef.current, 0, 0, targetW, targetH);
          const dataUrl = canvas.toDataURL("image/jpeg", quality);
          out.push(stripDataUrlPrefix(dataUrl));
          if (i < frames - 1) {
            await new Promise((r) => setTimeout(r, intervalMs));
          }
        }
        return out;
      } finally {
        captureInFlight.current = false;
        setIsCapturing(false);
      }
    }
  }));

  return (
    <div className={`relative ${className || ""}`}>
      {/* Decorative Outer Glow */}
      <div className={`absolute -inset-1 rounded-2xl blur-lg transition-all duration-1000 ${isCapturing ? 'bg-indigo-500/50 opacity-100' : 'bg-transparent opacity-0'}`} />
      
      <div className="relative w-full aspect-[4/3] overflow-hidden rounded-xl border border-white/10 bg-slate-900/50 backdrop-blur-sm shadow-inner group">
        <video
          ref={videoRef}
          playsInline
          muted
          className={`absolute inset-0 h-full w-full object-cover transition-opacity duration-700 ${cameraReady ? "opacity-100" : "opacity-0"}`}
        />
        
        {/* Loading Overlay */}
        {!cameraReady && !cameraError && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-900/80 backdrop-blur-md z-10 transition-opacity">
            <div className="w-8 h-8 rounded-full border-2 border-indigo-500/30 border-t-indigo-500 animate-spin mb-3" />
            <p className="text-slate-300 text-sm font-medium animate-pulse">Initializing Camera…</p>
          </div>
        )}

        {/* Error Overlay */}
        {cameraError && (
          <div className="absolute inset-0 flex items-center justify-center p-4 bg-slate-900/90 backdrop-blur-md z-10">
            <p className="text-center text-sm font-medium text-rose-400 bg-rose-500/10 px-4 py-3 rounded-lg border border-rose-500/20">
              {cameraError}
            </p>
          </div>
        )}

        {/* Scanning Overlay Effect when Capturing */}
        {isCapturing && (
          <>
            <div className="absolute inset-0 bg-indigo-500/10 mix-blend-overlay pointer-events-none z-20" />
            <div className="absolute top-0 left-0 right-0 h-1 bg-indigo-400/80 shadow-[0_0_10px_rgba(99,102,241,0.8)] z-20 animate-[scan_2s_ease-in-out_infinite]" />
            <style>{`
              @keyframes scan {
                0% { transform: translateY(0); opacity: 0.8; }
                50% { transform: translateY(100cqh); opacity: 1; }
                100% { transform: translateY(0); opacity: 0.8; }
              }
            `}</style>
          </>
        )}
        
        {/* Overlay guides */}
        {cameraReady && !isCapturing && (
          <div className="absolute inset-0 pointer-events-none border-2 border-transparent group-hover:border-white/10 transition-colors duration-300 rounded-xl" />
        )}
      </div>

    </div>
  );
});
