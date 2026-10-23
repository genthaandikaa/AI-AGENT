"use client";

import React, { useState } from "react";
import {
  Search,
  Calendar,
  Layers,
  Brain,
  Bell,
  ZoomIn,
  ZoomOut,
  Maximize2,
  ChevronDown,
  Sparkles,
  Compass,
  Monitor,
  Activity,
  CheckCircle2,
  X,
  ExternalLink,
} from "lucide-react";
import { DEPARTMENTS } from "./types";
import type { OfficeRenderMode } from "@/features/office/renderMode";

interface AgentHQHudProps {
  totalAgents: number;
  runningAgents: number;
  totalTasks?: number;
  activeTab: string;
  onTabChange: (tab: string) => void;
  renderMode: OfficeRenderMode;
  onRenderModeChange: (mode: OfficeRenderMode) => void;
  onResetCamera?: () => void;
  onZoomIn?: () => void;
  onZoomOut?: () => void;
  selectedAgent?: any;
  onCloseSelectedAgent?: () => void;
}

export const AgentHQHud: React.FC<AgentHQHudProps> = ({
  totalAgents,
  runningAgents,
  totalTasks = 22,
  activeTab,
  onTabChange,
  renderMode,
  onRenderModeChange,
  onResetCamera,
  onZoomIn,
  onZoomOut,
  selectedAgent,
  onCloseSelectedAgent,
}) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [showNotification, setShowNotification] = useState(true);

  return (
    <div className="absolute inset-0 pointer-events-none select-none z-20 flex flex-col justify-between p-4 overflow-hidden font-sans">
      {/* ========================================================================= */}
      {/* TOP NAVIGATION BAR                                                        */}
      {/* ========================================================================= */}
      <header className="flex items-center justify-between gap-4 pointer-events-auto">
        {/* Left: Branding & Organization Dropdown */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-2xl bg-slate-900/80 backdrop-blur-xl border border-slate-700/60 shadow-xl">
            <div className="w-6 h-6 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center text-white shadow-[0_0_12px_rgba(6,182,212,0.5)]">
              <Sparkles className="w-3.5 h-3.5" />
            </div>
            <div className="flex flex-col">
              <span className="text-xs font-black tracking-wide text-white flex items-center gap-1.5">
                Agent HQ
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              </span>
            </div>
            <span className="text-[10px] font-semibold text-slate-400 bg-slate-800/80 px-2 py-0.5 rounded-md border border-slate-700/40">
              Harmage AI
            </span>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400 ml-0.5" />
          </div>

          {/* Render Mode Switcher Pill */}
          <div className="flex items-center gap-1 p-1 rounded-xl bg-slate-900/80 backdrop-blur-xl border border-slate-700/60 shadow-lg">
            <button
              onClick={() => onRenderModeChange("agent-hq" as any)}
              className={`px-2.5 py-1 rounded-lg text-[10px] font-bold transition-all ${
                renderMode === ("agent-hq" as any)
                  ? "bg-cyan-500 text-slate-950 shadow-[0_0_10px_rgba(6,182,212,0.4)]"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              3D Agent HQ
            </button>
            <button
              onClick={() => onRenderModeChange("2d")}
              className={`px-2.5 py-1 rounded-lg text-[10px] font-bold transition-all ${
                renderMode === "2d"
                  ? "bg-purple-600 text-white shadow-[0_0_10px_rgba(147,51,234,0.4)]"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              2D Pixel
            </button>
            <button
              onClick={() => onRenderModeChange("3d")}
              className={`px-2.5 py-1 rounded-lg text-[10px] font-bold transition-all ${
                renderMode === "3d"
                  ? "bg-amber-600 text-white shadow-[0_0_10px_rgba(217,119,6,0.4)]"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              Retro 3D
            </button>
          </div>
        </div>

        {/* Center: Tabs & Search Input */}
        <div className="flex items-center gap-3">
          {/* Main Tabs */}
          <div className="flex items-center gap-1 p-1 rounded-2xl bg-slate-900/80 backdrop-blur-xl border border-slate-700/60 shadow-xl">
            <button
              onClick={() => onTabChange("office")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                activeTab === "office"
                  ? "bg-slate-800 text-white shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Compass className="w-3.5 h-3.5 text-cyan-400" />
              <span>Office</span>
            </button>

            <button
              onClick={() => onTabChange("tasks")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                activeTab === "tasks"
                  ? "bg-slate-800 text-white shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Layers className="w-3.5 h-3.5 text-indigo-400" />
              <span>Tasks</span>
              <span className="px-1.5 py-0.2 rounded-full bg-indigo-500/20 text-indigo-300 text-[10px]">
                {totalTasks}
              </span>
            </button>

            <button
              onClick={() => onTabChange("calendar")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                activeTab === "calendar"
                  ? "bg-slate-800 text-white shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Calendar className="w-3.5 h-3.5 text-amber-400" />
              <span>Calendar</span>
            </button>

            <button
              onClick={() => onTabChange("brain")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                activeTab === "brain"
                  ? "bg-slate-800 text-white shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Brain className="w-3.5 h-3.5 text-pink-400" />
              <span>Brain</span>
            </button>
          </div>

          {/* Quick Search Agent / AI Command */}
          <div className="relative">
            <div className="flex items-center gap-2 w-56 px-3 py-1.5 rounded-2xl bg-slate-900/80 backdrop-blur-xl border border-slate-700/60 shadow-xl focus-within:border-cyan-500 transition-colors">
              <Search className="w-3.5 h-3.5 text-slate-400" />
              <input
                type="text"
                placeholder="Ask any agent..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-transparent border-none outline-none text-xs text-white placeholder-slate-500"
              />
              <span className="font-mono text-[9px] text-slate-500 border border-slate-700 px-1.5 py-0.5 rounded">
                /
              </span>
            </div>
          </div>
        </div>

        {/* Right: Agent Status Pill & User Profile */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-2xl bg-slate-900/80 backdrop-blur-xl border border-slate-700/60 shadow-xl">
            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></div>
            <span className="text-xs font-bold text-white tracking-wide">
              {totalAgents} agents
            </span>
            <span className="text-slate-500">•</span>
            <span className="text-xs font-bold text-emerald-400">
              {runningAgents} running
            </span>
          </div>

          <div className="w-9 h-9 rounded-2xl bg-gradient-to-tr from-purple-500 to-indigo-600 p-[1px] shadow-lg">
            <div className="w-full h-full rounded-[15px] bg-slate-950 flex items-center justify-center text-xs font-bold text-white overflow-hidden">
              <img
                src="https://api.dicebear.com/7.x/bottts/svg?seed=Gentha"
                alt="Profile"
                className="w-7 h-7 object-cover"
              />
            </div>
          </div>
        </div>
      </header>

      {/* ========================================================================= */}
      {/* FLOATING NOTIFICATION CARD                                                */}
      {/* ========================================================================= */}
      {showNotification && (
        <div className="self-end mr-2 mt-4 pointer-events-auto max-w-sm animate-in fade-in slide-in-from-top-4 duration-300">
          <div className="flex items-start gap-3 p-3.5 rounded-2xl bg-slate-900/90 backdrop-blur-2xl border border-teal-500/40 shadow-[0_0_20px_rgba(20,184,166,0.25)]">
            <div className="w-8 h-8 rounded-xl bg-teal-500/20 border border-teal-500/50 flex items-center justify-center text-teal-400 flex-shrink-0">
              <Activity className="w-4 h-4" />
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold text-teal-300">Analytics</span>
                <button
                  onClick={() => setShowNotification(false)}
                  className="text-slate-400 hover:text-white"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
              <p className="text-xs text-slate-200 font-medium mt-0.5">
                Weekly token & operations report is ready.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Center Spacer */}
      <div className="flex-1"></div>

      {/* ========================================================================= */}
      {/* BOTTOM FOOTER HUD (Captions + Minimap Radar Controls)                     */}
      {/* ========================================================================= */}
      <footer className="flex items-end justify-between pointer-events-auto">
        {/* Subtitle / Tour Tour Guide Pill */}
        <div className="flex items-center gap-2 px-4 py-2 rounded-2xl bg-slate-950/85 backdrop-blur-2xl border border-slate-700/60 shadow-2xl">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
          <span className="text-xs font-bold text-white tracking-wide">
            Today, I&apos;m giving you the full tour...
          </span>
          <span className="text-[10px] text-slate-400 font-mono ml-2 border-l border-slate-700 pl-2">
            Isometric 3D Agent HQ • Three.js
          </span>
        </div>

        {/* Minimap Radar Widget */}
        <div className="flex flex-col items-end gap-2">
          {/* Radar Container */}
          <div className="relative w-40 h-40 rounded-3xl bg-slate-950/90 backdrop-blur-2xl border border-slate-700/70 shadow-2xl overflow-hidden p-2 flex flex-col justify-between">
            {/* Radar Grid Graphic */}
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-30">
              <div className="w-32 h-32 rounded-full border border-cyan-500/50"></div>
              <div className="absolute w-20 h-20 rounded-full border border-cyan-500/40"></div>
              <div className="absolute w-full h-[1px] bg-cyan-500/30"></div>
              <div className="absolute h-full w-[1px] bg-cyan-500/30"></div>
            </div>

            {/* Radar Hub Dot */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-3.5 h-3.5 rounded-full bg-cyan-400 shadow-[0_0_10px_#06b6d4] z-10"></div>

            {/* Minimap Department Nodes */}
            {DEPARTMENTS.map((dept) => {
              // Convert 3D [x, 0, z] coordinates to 2D radar [x, y]
              const radX = 80 + (dept.position[0] / 24) * 58;
              const radY = 80 + (dept.position[2] / 24) * 58;
              return (
                <div
                  key={dept.id}
                  className="absolute w-2.5 h-2.5 rounded-full -translate-x-1/2 -translate-y-1/2 transition-transform hover:scale-150 cursor-pointer shadow-md"
                  style={{
                    left: `${radX}px`,
                    top: `${radY}px`,
                    backgroundColor: dept.color,
                  }}
                  title={dept.name}
                />
              );
            })}

            {/* Radar Header */}
            <div className="relative z-10 flex items-center justify-between text-[9px] font-mono text-slate-400">
              <span className="font-bold text-cyan-300">RADAR</span>
              <span>8 ROOMS</span>
            </div>

            {/* Radar Controls */}
            <div className="relative z-10 flex items-center justify-end gap-1">
              <button
                onClick={onZoomIn}
                className="p-1 rounded-lg bg-slate-800/80 text-slate-300 hover:text-white transition-colors"
                title="Zoom In"
              >
                <ZoomIn className="w-3 h-3" />
              </button>
              <button
                onClick={onZoomOut}
                className="p-1 rounded-lg bg-slate-800/80 text-slate-300 hover:text-white transition-colors"
                title="Zoom Out"
              >
                <ZoomOut className="w-3 h-3" />
              </button>
              <button
                onClick={onResetCamera}
                className="p-1 rounded-lg bg-slate-800/80 text-slate-300 hover:text-white transition-colors"
                title="Reset Camera"
              >
                <Maximize2 className="w-3 h-3" />
              </button>
            </div>
          </div>
        </div>
      </footer>

      {/* Selected Agent Modal / Side Drawer */}
      {selectedAgent && (
        <div className="fixed inset-y-4 right-4 w-80 bg-slate-900/95 backdrop-blur-2xl border border-slate-700/80 shadow-2xl rounded-3xl p-5 pointer-events-auto flex flex-col justify-between animate-in slide-in-from-right duration-300 z-50">
          <div>
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-xl bg-cyan-500/20 text-cyan-400 flex items-center justify-center font-bold">
                  {selectedAgent.name[0]}
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white">{selectedAgent.name}</h4>
                  <p className="text-[10px] text-slate-400 capitalize">{selectedAgent.role}</p>
                </div>
              </div>
              <button
                onClick={onCloseSelectedAgent}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="mt-4 space-y-3">
              <div>
                <span className="text-[10px] font-mono text-slate-500 uppercase">Status</span>
                <div className="flex items-center gap-2 mt-1">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                  <span className="text-xs font-bold text-emerald-400 capitalize">
                    {selectedAgent.status}
                  </span>
                </div>
              </div>

              {selectedAgent.currentTask && (
                <div>
                  <span className="text-[10px] font-mono text-slate-500 uppercase">Active Task</span>
                  <p className="text-xs text-slate-200 bg-slate-950/70 p-2.5 rounded-xl border border-slate-800 mt-1">
                    {selectedAgent.currentTask}
                  </p>
                </div>
              )}
            </div>
          </div>

          <div className="border-t border-slate-800 pt-3 flex items-center gap-2">
            <button
              onClick={onCloseSelectedAgent}
              className="flex-1 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-600 text-slate-950 font-bold text-xs shadow-lg transition-all"
            >
              Tutup
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
