"use client";

import { useState, useEffect } from "react";
import {
  Shield,
  ShieldAlert,
  ShieldCheck,
  Activity,
  Target,
  AlertTriangle,
  Terminal,
  Cpu,
} from "lucide-react";

const SCAN_LOGS = [
  "Establishing secure API link...",
  "Tokenizing input sequence...",
  "Loading DistilBERT weights...",
  "Executing PyTorch tensor math...",
  "Evaluating contextual risk factors...",
  "Finalizing threat matrix...",
];

export default function SentinelDashboard() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");
  const [scanText, setScanText] = useState(SCAN_LOGS[0]);

  // Dynamic terminal text effect during loading
  useEffect(() => {
    if (!loading) return;
    let i = 0;
    const interval = setInterval(() => {
      i = (i + 1) % SCAN_LOGS.length;
      setScanText(SCAN_LOGS[i]);
    }, 400); // Changes text every 400ms for that high-tech scanning feel
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
        throw new Error("Failed to communicate with the Sentinel API");

      const data = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case "SAFE":
        return "text-emerald-400 border-emerald-500/30 bg-emerald-500/10 shadow-emerald-900/20";
      case "MODERATE":
        return "text-yellow-400 border-yellow-500/30 bg-yellow-500/10 shadow-yellow-900/20";
      case "HIGH":
        return "text-orange-500 border-orange-500/30 bg-orange-500/10 shadow-orange-900/20";
      case "CRITICAL":
        return "text-red-500 border-red-500/30 bg-red-500/10 shadow-red-900/20";
      default:
        return "text-gray-400 border-gray-500/30 bg-gray-500/10 shadow-gray-900/20";
    }
  };

  return (
    <div className="p-4 md:p-8 font-sans">
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Header - Glassmorphism */}
        <header className="flex items-center space-x-4 border border-slate-800/60 bg-slate-900/50 backdrop-blur-md p-6 rounded-2xl shadow-2xl">
          <div className="relative">
            <div className="absolute inset-0 bg-indigo-500 blur-lg opacity-40 animate-pulse"></div>
            <Shield className="w-12 h-12 text-indigo-400 relative z-10" />
          </div>
          <div>
            <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
              SENTINEL CORE{" "}
              <span className="px-2 py-1 bg-indigo-500/20 text-indigo-300 text-xs rounded-full border border-indigo-500/30 uppercase tracking-widest font-mono">
                v1.0 Live
              </span>
            </h1>
            <p className="text-slate-400 text-sm mt-1 flex items-center gap-2">
              <Cpu className="w-4 h-4" /> Native PyTorch CPU Inference Engine
            </p>
          </div>
        </header>

        {/* Input Section */}
        <div className="bg-slate-900/60 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6 shadow-2xl transition-all duration-300 focus-within:border-indigo-500/50 focus-within:shadow-[0_0_30px_-5px_rgba(99,102,241,0.15)]">
          <label className="flex items-center gap-2 text-sm font-semibold text-indigo-300 mb-3 uppercase tracking-wider">
            <Terminal className="w-4 h-4" /> Target Payload
          </label>
          <textarea
            className="w-full bg-slate-950/80 border border-slate-800 rounded-xl p-4 text-slate-200 placeholder-slate-600 focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition-all outline-none resize-none font-mono text-sm leading-relaxed"
            rows={4}
            placeholder="> Input communication intercept for real-time risk evaluation... (English/Hinglish supported)"
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                analyzeText();
              }
            }}
          />
          <div className="mt-4 flex items-center justify-between">
            {/* Dynamic Loading Terminal */}
            <div className="text-indigo-400 font-mono text-xs flex items-center gap-2 h-6">
              {loading && (
                <>
                  <div className="w-2 h-4 bg-indigo-400 animate-pulse"></div>
                  {scanText}
                </>
              )}
            </div>

            <button
              onClick={analyzeText}
              disabled={loading || !text.trim()}
              className="bg-indigo-600 hover:bg-indigo-500 text-white px-8 py-3 rounded-xl font-bold transition-all duration-200 disabled:opacity-50 flex items-center space-x-2 shadow-lg hover:shadow-indigo-500/25 border border-indigo-400/20 hover:-translate-y-0.5"
            >
              {loading ? (
                <>
                  <Activity className="w-5 h-5 animate-spin" />
                  <span>ANALYZING...</span>
                </>
              ) : (
                <>
                  <ShieldAlert className="w-5 h-5" />
                  <span>SCAN PAYLOAD</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-red-950/50 border border-red-500/30 text-red-400 p-4 rounded-xl flex items-center space-x-3 backdrop-blur-sm animate-in fade-in zoom-in duration-300">
            <AlertTriangle className="w-6 h-6 flex-shrink-0" />
            <p className="font-mono text-sm">{error}</p>
          </div>
        )}

        {/* Results Section */}
        {result && (
          <div className="space-y-6 animate-in slide-in-from-bottom-8 fade-in duration-700 ease-out">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Main Risk Level Card */}
              <div
                className={`col-span-1 md:col-span-3 rounded-2xl p-8 border flex items-center justify-between backdrop-blur-md transition-all hover:scale-[1.01] ${getRiskColor(result.risk_level)}`}
              >
                <div className="space-y-1">
                  <p className="text-xs font-bold uppercase tracking-[0.2em] opacity-80 flex items-center gap-2">
                    <Activity className="w-4 h-4" /> Threat Classification
                  </p>
                  <h3 className="text-5xl font-black tracking-tight drop-shadow-md">
                    {result.risk_level}
                  </h3>
                </div>
                <div className="relative">
                  {/* Glowing background behind icon */}
                  <div className="absolute inset-0 bg-current blur-2xl opacity-20"></div>
                  {result.risk_level === "SAFE" ? (
                    <ShieldCheck className="w-16 h-16 opacity-90 animate-pulse relative z-10" />
                  ) : (
                    <AlertTriangle className="w-16 h-16 opacity-90 animate-pulse relative z-10" />
                  )}
                </div>
              </div>

              {/* Threat Probability */}
              <div className="bg-slate-900/60 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6 shadow-xl hover:-translate-y-1 hover:border-indigo-500/30 transition-all duration-300 group">
                <div className="flex items-center space-x-2 mb-4 text-slate-400 group-hover:text-indigo-300 transition-colors">
                  <Activity className="w-5 h-5" />
                  <span className="text-xs font-bold uppercase tracking-wider">
                    Model Probability
                  </span>
                </div>
                <div className="text-4xl font-black text-slate-100 flex items-baseline gap-1">
                  {(result.threat_probability * 100).toFixed(1)}
                  <span className="text-lg text-slate-500 font-medium">%</span>
                </div>
              </div>

              {/* Immediacy */}
              <div className="bg-slate-900/60 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6 shadow-xl hover:-translate-y-1 hover:border-orange-500/30 transition-all duration-300 group">
                <div className="flex items-center space-x-2 mb-4 text-slate-400 group-hover:text-orange-300 transition-colors">
                  <AlertTriangle className="w-5 h-5" />
                  <span className="text-xs font-bold uppercase tracking-wider">
                    Immediacy
                  </span>
                </div>
                <div className="text-4xl font-black text-slate-100">
                  {result.immediacy}
                </div>
              </div>

              {/* Target Identified */}
              <div className="bg-slate-900/60 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6 shadow-xl hover:-translate-y-1 hover:border-red-500/30 transition-all duration-300 group">
                <div className="flex items-center space-x-2 mb-4 text-slate-400 group-hover:text-red-300 transition-colors">
                  <Target className="w-5 h-5" />
                  <span className="text-xs font-bold uppercase tracking-wider">
                    Targeted Attack
                  </span>
                </div>
                <div className="text-4xl font-black text-slate-100">
                  {result.target_identified ? "DETECTED" : "NONE"}
                </div>
              </div>
            </div>

            {/* AI Reasoning Log - Terminal Style */}
            <div className="bg-black/80 backdrop-blur-md border border-slate-800 rounded-2xl p-1 shadow-2xl overflow-hidden">
              <div className="bg-slate-900 px-4 py-2 flex items-center gap-2 border-b border-slate-800">
                <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
                <div className="w-3 h-3 rounded-full bg-green-500/80"></div>
                <span className="text-xs font-mono text-slate-500 ml-2">
                  sys_log_output.sh
                </span>
              </div>
              <div className="p-6">
                <h4 className="text-xs font-bold text-slate-500 mb-3 uppercase tracking-widest flex items-center gap-2">
                  <Terminal className="w-4 h-4" /> AI Engine Reasoning Log
                </h4>
                <p className="text-green-400 leading-relaxed font-mono text-sm">
                  <span className="text-slate-600 select-none mr-2">
                    root@sentinel:~#
                  </span>
                  {result.reason}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
