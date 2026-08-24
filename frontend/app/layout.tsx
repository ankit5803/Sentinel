import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Sentinel Threat Engine",
  description: "Real-Time AI NLP Threat Detection Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased min-h-screen bg-slate-950 text-slate-200 selection:bg-indigo-500/40 relative">
        {/* High-tech dynamic grid background */}
        <div className="fixed inset-0 z-[-1] bg-[linear-gradient(to_right,#4f4f4f2e_1px,transparent_1px),linear-gradient(to_bottom,#4f4f4f2e_1px,transparent_1px)] bg-[size:24px_24px] [mask-image:radial-gradient(ellipse_80%_60%_at_50%_0%,#000_70%,transparent_100%)]" />

        {/* Subtle ambient glow at the top */}
        <div className="fixed top-0 inset-x-0 h-[500px] pointer-events-none z-[-1] bg-gradient-to-b from-indigo-900/20 to-transparent blur-3xl" />

        {children}
      </body>
    </html>
  );
}
