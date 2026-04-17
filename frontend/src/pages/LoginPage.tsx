import { useMemo, useRef, useState } from "react";
import { WebcamCapture, type WebcamCaptureRef } from "../components/WebcamCapture";
import { useFaceAuth } from "../hooks/useFaceAuth";

type Props = { onAuthenticated: (userId: string, token: string) => void };

export function LoginPage({ onAuthenticated }: Props) {
  const [userId, setUserId] = useState("");
  const [challenge, setChallenge] = useState("blink");
  const [status, setStatus] = useState("");
  const [mode, setMode] = useState<"login" | "enroll">("login");
  const captureRef = useRef<WebcamCaptureRef | null>(null);
  const { loading, enroll, verify } = useFaceAuth();

  const enrollFrames = 15;
  const enrollFps = 10;
  const verifyFrames = 20;
  const verifyFps = 10;

  const captureQuality = useMemo(() => 0.65, []);

  return (
    <main className="min-h-screen flex items-center justify-center p-6 bg-transparent relative z-10">
      <div className="w-full max-w-md animate-fade-in-up">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-400">
            Nexus: Character Design Architect
          </h1>
          <p className="mt-2 text-sm text-slate-400 font-medium tracking-wide">
            {mode === "login" ? "Biometric Secure Access" : "Identity Enrollment"}
          </p>
        </div>

        <div className="glass-panel rounded-2xl p-6 sm:p-8">
          <div className="flex gap-1 p-1 bg-slate-900/50 rounded-xl mb-6 border border-white/5">
            <button
              onClick={() => setMode("login")}
              className={`flex-1 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                mode === "login"
                  ? "bg-indigo-500/20 text-indigo-400 border border-indigo-500/30"
                  : "text-slate-500 hover:text-slate-300"
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => setMode("enroll")}
              className={`flex-1 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                mode === "enroll"
                  ? "bg-indigo-500/20 text-indigo-400 border border-indigo-500/30"
                  : "text-slate-500 hover:text-slate-300"
              }`}
            >
              Register
            </button>
          </div>

          <div className="space-y-5">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                User Identifier
              </label>
              <input
                className="glass-input rounded-xl px-4 py-3 text-sm text-slate-100 placeholder:text-slate-500"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                placeholder="e.g., designer_01"
              />
            </div>

            <div className="relative">
              <WebcamCapture className="w-full" ref={captureRef} />
              
              {/* Status Indicator */}
              {status && (
                <div className="absolute -bottom-4 left-1/2 -translate-x-1/2 whitespace-nowrap bg-indigo-600 text-white text-[11px] font-bold px-4 py-2 rounded-full border border-white/20 shadow-2xl backdrop-blur-lg animate-fade-in z-20">
                  {status}
                </div>
              )}
            </div>

            {/* Liveness Challenge - Hardcoded to Blink as requested */}

            <div className="pt-4">
              {mode === "enroll" ? (
                <button
                  disabled={loading || !userId}
                  className="premium-btn w-full rounded-xl py-3 font-semibold text-sm text-white bg-gradient-to-r from-indigo-500 to-purple-600 shadow-[0_0_20px_rgba(99,102,241,0.4)] hover:shadow-[0_0_25px_rgba(99,102,241,0.6)] border border-indigo-400/50"
                  onClick={async () => {
                    try {
                      if (!captureRef.current) throw new Error("Camera not ready");
                      setStatus("Acquiring biometric signature...");
                      const seq = await captureRef.current.captureSequence({
                        frames: enrollFrames,
                        fps: enrollFps,
                        quality: captureQuality
                      });
                      await enroll(userId, seq);
                      setStatus("Enrollment success. Please Login.");
                      setTimeout(() => setMode("login"), 1500);
                    } catch (e: any) {
                      setStatus(e?.message || "Enrollment failed");
                    }
                  }}
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-2">
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"/> Processing
                    </span>
                  ) : "Register Biology"}
                </button>
              ) : (
                <button
                  disabled={loading || !userId}
                  className="premium-btn w-full rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 shadow-[0_0_20px_rgba(16,185,129,0.3)] hover:shadow-[0_0_25px_rgba(16,185,129,0.5)] border border-emerald-400/50 py-3 font-semibold text-sm text-white disabled:from-slate-700 disabled:to-slate-800 disabled:shadow-none disabled:border-slate-600/50"
                  onClick={async () => {
                    try {
                      if (!captureRef.current) throw new Error("Camera not ready");
                      setStatus(`Authenticating via challenge: ${challenge}...`);
                      const seq = await captureRef.current.captureSequence({
                        frames: verifyFrames,
                        fps: verifyFps,
                        quality: captureQuality
                      });
                      const token = await verify(userId, seq, challenge);
                      setStatus("Identity Verified.");
                      setTimeout(() => onAuthenticated(userId, token), 500);
                    } catch (e: any) {
                      setStatus(e?.message || "Verification failed");
                    }
                  }}
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-2">
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"/> Verifying
                    </span>
                  ) : "Verify Identity"}
                </button>
              )}
            </div>
            
            <p className="text-center text-xs text-slate-500 mt-2">
              {mode === "login" 
                ? "Secure facial authentication required." 
                : "A short head-motion sequence will be captured."}
            </p>
          </div>
        </div>
      </div>
      
      {/* Tailwind specific custom animations inline for quick deployment */}
      <style>{`
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in-up {
          animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
      `}</style>
    </main>
  );
}
