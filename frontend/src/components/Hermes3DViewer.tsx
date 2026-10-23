import React, { useState } from 'react';
import { ExternalLink, RefreshCw, Maximize2, Sparkles, Box } from 'lucide-react';

interface Hermes3DViewerProps {
  onSelectAgent?: (agent: any) => void;
}

export const Hermes3DViewer: React.FC<Hermes3DViewerProps> = () => {
  const [iframeKey, setIframeKey] = useState<number>(1);
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);
  const [isLoaded, setIsLoaded] = useState<boolean>(false);

  const hermes3dUrl = (import.meta as any).env?.VITE_HERMES3D_URL || (typeof window !== "undefined" ? `${window.location.protocol}//${window.location.hostname}:3000/office` : "http://localhost:3000/office");

  const handleReload = () => {
    setIsLoaded(false);
    setIframeKey(prev => prev + 1);
  };

  const toggleFullscreen = () => {
    setIsFullscreen(prev => !prev);
  };

  return (
    <div className={`bg-white rounded-3xl border border-purple-100 shadow-soft overflow-hidden transition-all ${
      isFullscreen ? 'fixed inset-4 z-50 flex flex-col' : 'space-y-0'
    }`}>
      {/* Header Controls Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 bg-white border-b border-purple-50">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-2xl bg-purple-100 text-purple-600 flex items-center justify-center flex-shrink-0 shadow-sm">
            <Box className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-2">
              Hermes 3D Virtual Office
              <span className="flex items-center gap-1 text-[10px] text-emerald-600 font-bold bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-100">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                Port 3000 Live
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              Lingkungan 3D interaktif native dari Hermes3D (Three.js & Phaser).
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleReload}
            title="Reload 3D Office"
            className="p-2 text-slate-500 hover:text-purple-600 hover:bg-purple-50 rounded-xl border border-purple-100 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>

          <button
            onClick={toggleFullscreen}
            title={isFullscreen ? "Exit Fullscreen" : "Fullscreen View"}
            className="p-2 text-slate-500 hover:text-purple-600 hover:bg-purple-50 rounded-xl border border-purple-100 transition-colors"
          >
            <Maximize2 className="w-4 h-4" />
          </button>

          <a
            href={hermes3dUrl}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1.5 px-3 py-1.5 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-xs font-bold shadow-sm transition-all"
          >
            <span>Buka Tab Terpisah</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>

      {/* 3D Frame Viewport */}
      <div className={`relative bg-slate-950 w-full ${isFullscreen ? 'flex-1' : 'h-[540px]'}`}>
        {!isLoaded && (
          <div className="absolute inset-0 flex flex-col items-center justify-center text-white space-y-3 z-10 bg-slate-900/90 backdrop-blur-sm">
            <Sparkles className="w-8 h-8 text-purple-400 animate-spin" />
            <div className="text-center">
              <p className="text-xs font-bold text-slate-200">Memuat Hermes 3D Virtual Office...</p>
              <p className="text-[10px] text-slate-400 mt-1">Menghubungkan ke {hermes3dUrl}</p>
            </div>
          </div>
        )}

        <iframe
          key={iframeKey}
          src={hermes3dUrl}
          title="Hermes 3D Office"
          onLoad={() => setIsLoaded(true)}
          className="w-full h-full border-0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        />
      </div>
    </div>
  );
};
