"use client";

import { useState, useEffect } from "react";
import {
  Activity,
  Target,
  AlertTriangle,
  Zap,
  Radar,
  CheckCircle2,
  AlertOctagon,
  Eye,
  Shield,
} from "lucide-react";

const SCAN_LOGS = [
  "ESTABLISHING SECURE UPLINK...",
  "TOKENIZING SEQUENCE PATTERNS...",
  "EXTRACTING LINGUISTIC CONTEXT...",
  "CALCULATING THREAT VECTORS...",
  "EVALUATING RISK MATRIX...",
  "SYNTHESIZING VERDICT...",
];

export default function SentinelDashboard() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");
  const [scanText, setScanText] = useState(SCAN_LOGS[0]);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!loading) return;
    let i = 0;
    const interval = setInterval(() => {
      i = (i + 1) % SCAN_LOGS.length;
      setScanText(SCAN_LOGS[i]);
    }, 400);
    return () => clearInterval(interval);
  }, [loading]);

  const analyzeText = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(
        "https://ankit03-sentinel-api.hf.space/api/v1/analyze",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text }),
        },
      );

      if (!response.ok)
        throw new Error("Neural link severed. API unavailable.");

      const data = await response.json();
      setTimeout(() => setResult(data), 600);
    } catch (err: any) {
      setError(err.message || "Anomalous error detected.");
    } finally {
      setTimeout(() => setLoading(false), 600);
    }
  };

  // Fluid Liquid Theme Engine
  const getTheme = (level: string | null) => {
    switch (level) {
      case "SAFE":
        return {
          blob1: "bg-emerald-600",
          blob2: "bg-teal-500",
          blob3: "bg-green-700",
          accent: "text-emerald-400",
          border: "border-emerald-500/30",
          bg: "bg-emerald-950/10",
          icon: <CheckCircle2 className="w-12 h-12 text-emerald-400" />,
        };
      case "MODERATE":
      case "REVIEW":
        return {
          blob1: "bg-amber-600",
          blob2: "bg-yellow-500",
          blob3: "bg-orange-600",
          accent: "text-amber-400",
          border: "border-amber-500/30",
          bg: "bg-amber-950/10",
          icon: <Eye className="w-12 h-12 text-amber-400" />,
        };
      case "HIGH_RISK":
      case "HIGH":
      case "VIOLENT_THREAT":
        return {
          blob1: "bg-rose-700",
          blob2: "bg-red-600",
          blob3: "bg-orange-700",
          accent: "text-rose-500",
          border: "border-rose-500/40",
          bg: "bg-rose-950/20",
          icon: <AlertOctagon className="w-12 h-12 text-rose-500" />,
        };
      default:
        // Idle State
        return {
          blob1: "bg-indigo-700",
          blob2: "bg-purple-600",
          blob3: "bg-blue-800",
          accent: "text-indigo-400",
          border: "border-white/10",
          bg: "bg-white/[0.02]",
          icon: <Radar className="w-12 h-12 text-indigo-400" />,
        };
    }
  };

  const theme = getTheme(result?.risk_level || null);

  if (!mounted) return null;

  return (
    <div className="min-h-screen bg-[#030305] text-white selection:bg-indigo-500/30 font-sans overflow-hidden relative flex flex-col items-center justify-center py-20 px-4 md:px-12">
      {/* --- FLUID AURORA BACKGROUND ENGINE --- */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* Deep background color to anchor the blobs */}
        <div className="absolute inset-0 bg-[#030305] z-0"></div>

        {/* Layer 1: The Blobs */}
        <div className="absolute inset-0 z-0 opacity-40 mix-blend-screen filter blur-[100px]">
          <div
            className={`absolute top-0 left-[-10%] w-[60vw] h-[60vw] rounded-full mix-blend-multiply transition-colors duration-[2000ms] ease-in-out wavy-blob-1 ${theme.blob1}`}
          ></div>
          <div
            className={`absolute top-[-20%] right-[-10%] w-[50vw] h-[50vw] rounded-full mix-blend-multiply transition-colors duration-[2000ms] ease-in-out wavy-blob-2 ${theme.blob2}`}
          ></div>
          <div
            className={`absolute bottom-[-10%] left-[20%] w-[70vw] h-[70vw] rounded-full mix-blend-multiply transition-colors duration-[2000ms] ease-in-out wavy-blob-3 ${theme.blob3}`}
          ></div>
        </div>

        {/* Layer 2: Noise Texture overlay for that premium matte glass look */}
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 brightness-100 contrast-150 mix-blend-overlay z-0"></div>
      </div>

      {/* --- MAIN CONTENT (Glassmorphism UI) --- */}
      <div className="w-full max-w-6xl relative z-10 flex flex-col gap-12">
        {/* Header */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
          <div className="space-y-2">
            <h1 className="text-6xl md:text-8xl font-black tracking-tighter text-white drop-shadow-lg">
              SENTINEL
            </h1>
            <p className="text-sm md:text-base font-mono tracking-[0.3em] text-white/70 uppercase">
              Autonomous Threat Intelligence v2.0
            </p>
          </div>
          <div className="flex items-center gap-3 px-5 py-3 rounded-full border border-white/20 bg-black/40 backdrop-blur-xl shadow-2xl">
            <div className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </div>
            <span className="text-xs font-bold tracking-widest uppercase text-white/90">
              Engine Online
            </span>
          </div>
        </header>

        {/* Input Stage */}
        <div
          className={`relative group transition-all duration-1000 ${result ? "opacity-90 scale-[0.99]" : "scale-100"}`}
        >
          <div className="relative bg-[#050508]/60 backdrop-blur-3xl rounded-[32px] border border-white/10 overflow-hidden shadow-[0_8px_32px_0_rgba(0,0,0,0.5)]">
            {/* Loading laser beam effect */}
            {loading && (
              <div
                className="absolute top-0 left-0 h-[2px] bg-white shadow-[0_0_20px_#fff] animate-[sweep_2s_ease-in-out_infinite]"
                style={{ width: "30%" }}
              ></div>
            )}

            <textarea
              className="w-full min-h-[180px] bg-transparent p-10 text-xl md:text-2xl font-light text-white/90 placeholder-white/30 focus:outline-none resize-none transition-all leading-relaxed"
              placeholder="Intercept data stream... (Type English or Hinglish)"
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  analyzeText();
                }
              }}
            />

            <div className="flex flex-col md:flex-row items-center justify-between p-6 border-t border-white/10 bg-black/20">
              <div className="h-8 flex items-center font-mono text-xs tracking-[0.2em] mb-4 md:mb-0">
                {loading ? (
                  <span className="flex items-center gap-3 text-white">
                    <Activity className="w-4 h-4 animate-spin" /> {scanText}
                  </span>
                ) : (
                  <span className="text-white/40">
                    AWAITING PAYLOAD INGESTION
                  </span>
                )}
              </div>

              <button
                onClick={analyzeText}
                disabled={loading || !text.trim()}
                className="w-full md:w-auto relative px-10 py-4 bg-white text-black font-bold tracking-[0.2em] text-sm uppercase rounded-2xl overflow-hidden transition-all hover:scale-[1.02] active:scale-95 disabled:opacity-50 disabled:hover:scale-100 group/btn shadow-[0_0_40px_-10px_rgba(255,255,255,0.5)] hover:shadow-[0_0_60px_-15px_rgba(255,255,255,0.8)]"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-gray-200 to-white opacity-0 group-hover/btn:opacity-100 transition-opacity"></div>
                <span className="relative flex items-center justify-center gap-3">
                  <Zap className="w-4 h-4" /> Initialize Scan
                </span>
              </button>
            </div>
          </div>
        </div>

        {/* Results Dashboard */}
        {result && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 transition-all duration-1000 ease-out animate-in slide-in-from-bottom-24 fade-in">
            {/* Main Verdict */}
            <div
              className={`col-span-1 lg:col-span-8 rounded-[32px] p-8 md:p-12 border backdrop-blur-3xl flex flex-col justify-between relative overflow-hidden transition-all duration-700 shadow-[0_8px_32px_0_rgba(0,0,0,0.4)] ${theme.bg} ${theme.border}`}
            >
              <div className="absolute top-0 right-0 p-12 opacity-20 scale-150 transform -translate-y-1/4 translate-x-1/4">
                {theme.icon}
              </div>

              <div className="relative z-10">
                <p className="font-mono text-xs tracking-[0.3em] uppercase opacity-70 mb-4 flex items-center gap-3 text-white">
                  Primary Classification{" "}
                  <span className="w-16 h-[1px] bg-white/30"></span>
                </p>
                <h2
                  className={`text-5xl md:text-7xl font-black tracking-tighter ${theme.accent} drop-shadow-2xl`}
                >
                  {result.risk_level.replace("_", " ")}
                </h2>
              </div>

              <div className="mt-12 flex flex-col md:flex-row gap-10 relative z-10">
                <div>
                  <p className="font-mono text-[10px] tracking-[0.2em] text-white/50 mb-2">
                    PROBABILITY INDEX
                  </p>
                  <p className="text-5xl font-light tracking-tight text-white">
                    {(result.threat_probability * 100).toFixed(1)}
                    <span className="text-2xl text-white/40 ml-1">%</span>
                  </p>
                </div>
                <div className="hidden md:block w-[1px] bg-white/10"></div>
                <div>
                  <p className="font-mono text-[10px] tracking-[0.2em] text-white/50 mb-2">
                    IMMEDIACY
                  </p>
                  <p className="text-5xl font-light tracking-tight text-white">
                    {result.immediacy}
                  </p>
                </div>
              </div>
            </div>

            {/* Target Card */}
            <div className="col-span-1 lg:col-span-4 rounded-[32px] p-8 border border-white/10 bg-black/40 backdrop-blur-3xl flex flex-col justify-center items-center text-center group hover:bg-black/60 transition-colors shadow-[0_8px_32px_0_rgba(0,0,0,0.4)]">
              <div
                className={`p-5 rounded-full mb-6 transition-all duration-500 group-hover:scale-110 ${result.target_identified ? "bg-red-500/20 text-red-400 shadow-[0_0_30px_rgba(239,68,68,0.3)]" : "bg-emerald-500/20 text-emerald-400 shadow-[0_0_30px_rgba(16,185,129,0.3)]"}`}
              >
                <Target className="w-10 h-10" />
              </div>
              <p className="font-mono text-xs tracking-[0.3em] text-white/50 mb-3">
                TARGET LOCK
              </p>
              <h3 className="text-3xl font-semibold tracking-tight text-white">
                {result.target_identified ? "Confirmed" : "Negative"}
              </h3>
            </div>

            {/* AI Reasoning Block */}
            <div className="col-span-1 lg:col-span-12 rounded-[32px] p-8 md:p-10 border border-white/10 bg-black/40 backdrop-blur-3xl relative overflow-hidden shadow-[0_8px_32px_0_rgba(0,0,0,0.4)]">
              <div className="absolute left-0 top-0 bottom-0 w-2 bg-gradient-to-b from-white to-white/10"></div>
              <div className="flex items-start gap-8">
                <div className="mt-1 hidden md:block">
                  <div className="w-12 h-12 rounded-full border border-white/20 flex items-center justify-center bg-white/5 backdrop-blur-md">
                    <Shield className="w-5 h-5 text-white/80" />
                  </div>
                </div>
                <div>
                  <p className="font-mono text-[10px] tracking-[0.3em] text-white/50 mb-4">
                    RISK ENGINE SYNTHESIS LOG
                  </p>
                  <p className="text-lg md:text-2xl font-light text-white/90 leading-relaxed">
                    {result.reason}
                  </p>
                  <div className="mt-6 flex flex-wrap items-center gap-4">
                    <span className="px-3 py-1 rounded-full border border-white/10 bg-white/5 text-[10px] font-mono text-white/60 tracking-widest uppercase">
                      LANG:{" "}
                      {result.language_detected?.toUpperCase() || "UNKNOWN"}
                    </span>
                    <span className="px-3 py-1 rounded-full border border-white/10 bg-white/5 text-[10px] font-mono text-white/60 tracking-widest uppercase">
                      MODEL: DISTILBERT_V2
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* --- INJECTED CSS FOR FLUID AURORA ANIMATIONS --- */}
      <style
        dangerouslySetInnerHTML={{
          __html: `
        @keyframes sweep {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(400%); }
        }

        /* Organic shape shifting */
        @keyframes shapeShift {
          0% { border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%; }
          25% { border-radius: 50% 50% 30% 70% / 70% 30% 70% 30%; }
          50% { border-radius: 70% 30% 50% 50% / 30% 70% 30% 70%; }
          75% { border-radius: 30% 70% 30% 70% / 50% 50% 70% 30%; }
          100% { border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%; }
        }

        /* Floating and rotating */
        @keyframes float1 {
          0% { transform: translate(0, 0) rotate(0deg) scale(1); }
          33% { transform: translate(10vw, -10vh) rotate(120deg) scale(1.1); }
          66% { transform: translate(-10vw, 15vh) rotate(240deg) scale(0.9); }
          100% { transform: translate(0, 0) rotate(360deg) scale(1); }
        }

        @keyframes float2 {
          0% { transform: translate(0, 0) rotate(0deg) scale(1); }
          33% { transform: translate(-15vw, 10vh) rotate(-120deg) scale(0.9); }
          66% { transform: translate(10vw, -15vh) rotate(-240deg) scale(1.2); }
          100% { transform: translate(0, 0) rotate(-360deg) scale(1); }
        }

        @keyframes float3 {
          0% { transform: translate(0, 0) rotate(0deg) scale(1); }
          50% { transform: translate(15vw, 5vh) rotate(180deg) scale(1.1); }
          100% { transform: translate(0, 0) rotate(360deg) scale(1); }
        }

        /* Combine animations on the blobs */
        .wavy-blob-1 {
          animation: shapeShift 20s infinite alternate, float1 25s infinite ease-in-out;
        }
        .wavy-blob-2 {
          animation: shapeShift 25s infinite alternate-reverse, float2 30s infinite ease-in-out;
        }
        .wavy-blob-3 {
          animation: shapeShift 15s infinite alternate, float3 35s infinite ease-in-out;
        }
      `,
        }}
      />
    </div>
  );
}
