"use client";

import React, { useCallback, useEffect, useRef, useState } from "react";
import { AgentHQScene } from "./AgentHQScene";
import { AgentHQHud } from "./AgentHQHud";
import { DEPARTMENTS, DepartmentConfig } from "./types";
import type { OfficeRenderMode } from "@/features/office/renderMode";

interface AgentHQ3DProps {
  agents?: any[];
  renderMode?: OfficeRenderMode;
  onRenderModeChange?: (mode: OfficeRenderMode) => void;
  onAgentChatSelect?: (agentId: string) => void;
  officeTitle?: string;
}

export const AgentHQ3D: React.FC<AgentHQ3DProps> = ({
  agents = [],
  renderMode = "agent-hq" as any,
  onRenderModeChange = () => {},
  onAgentChatSelect = () => {},
  officeTitle = "Harmage Agent HQ",
}) => {
  const [activeTab, setActiveTab] = useState<string>("office");
  const [memoryCount, setMemoryCount] = useState<number>(1245);
  const [totalTasksCount, setTotalTasksCount] = useState<number>(22);
  const [selectedAgent, setSelectedAgent] = useState<any | null>(null);

  const cameraControlRef = useRef<any>(null);

  // Fetch live metrics from Harmage backend if available
  useEffect(() => {
    let mounted = true;
    const fetchMetrics = async () => {
      try {
        const [brainRes, taskRes] = await Promise.all([
          fetch("http://127.0.0.1:9200/api/npc/brain/state", { signal: AbortSignal.timeout(3000) }).catch(() => null),
          fetch("http://127.0.0.1:9200/api/tasks", { signal: AbortSignal.timeout(3000) }).catch(() => null),
        ]);

        if (brainRes && brainRes.ok) {
          const brainData = await brainRes.json();
          if (mounted && brainData?.memories_count) {
            setMemoryCount(brainData.memories_count);
          }
        }

        if (taskRes && taskRes.ok) {
          const taskData = await taskRes.json();
          if (mounted && Array.isArray(taskData)) {
            setTotalTasksCount(taskData.length);
          }
        }
      } catch {
        // Use default fallback metrics if backend is busy
      }
    };

    void fetchMetrics();
    const interval = setInterval(fetchMetrics, 15000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  // Format incoming agents to visual format
  const formattedAgents = React.useMemo(() => {
    if (!agents || agents.length === 0) {
      // Default standard 10 Harmage Agents if store is initializing
      return [
        { id: "alex_vance", name: "Alex Vance", role: "Long-form Video Editor", status: "working", currentTask: "Rendering Explainer 16:9" },
        { id: "maya_lin", name: "Maya Lin", role: "Scriptwriter & Viral Hook", status: "working", currentTask: "8-Stage Edu Script v2" },
        { id: "ethan_cole", name: "Ethan Cole", role: "Market & Trend Researcher", status: "working", currentTask: "AI Agent Market Audit" },
        { id: "victor_sterling", name: "Victor Sterling", role: "Affiliate TikTok Lead", status: "working", currentTask: "Keranjang Kuning Conversion" },
        { id: "sarah_chen", name: "Sarah Chen", role: "Executive Manager", status: "working", currentTask: "Operations & Daily Standup" },
        { id: "marcus_vance", name: "Marcus Vance", role: "Treasurer & Token Budget", status: "working", currentTask: "Token Burn Rate Reconciliation" },
        { id: "zackary_cross", name: "Zackary Cross", role: "QA Sentinel", status: "working", currentTask: "Continuous Integration Testing" },
        { id: "antigravity_engineer", name: "Antigravity Engineer", role: "Autonomous Software Engineer", status: "working", currentTask: "Agent HQ 3D Scene Architecture" },
        { id: "social_specialist", name: "Riley Rivera", role: "Social Publisher", status: "working", currentTask: "TikTok Viral Sound Tracking" },
        { id: "secretary", name: "Elena Rostova", role: "Corporate Secretary", status: "working", currentTask: "Calendar & Meeting Schedules" },
      ];
    }

    return agents.map((a: any) => ({
      id: a.id || a.agentId,
      name: a.name || a.agentId,
      role: a.role || a.title || "Agent",
      status: a.status === "idle" ? "idle" : "working",
      currentTask: a.currentTask || a.taskTitle || "Processing operational queue",
      avatarColor: a.avatarColor,
    }));
  }, [agents]);

  const runningCount = formattedAgents.filter(
    (a) => a.status === "working" || a.status === "in_progress"
  ).length;

  const handleResetCamera = useCallback(() => {
    if (cameraControlRef.current) {
      cameraControlRef.current.reset();
    }
  }, []);

  const handleZoomIn = useCallback(() => {
    if (cameraControlRef.current) {
      cameraControlRef.current.dollyIn(1.2);
      cameraControlRef.current.update();
    }
  }, []);

  const handleZoomOut = useCallback(() => {
    if (cameraControlRef.current) {
      cameraControlRef.current.dollyOut(1.2);
      cameraControlRef.current.update();
    }
  }, []);

  const handleSelectAgent = useCallback(
    (agent: any) => {
      setSelectedAgent(agent);
      onAgentChatSelect(agent.id);
    },
    [onAgentChatSelect]
  );

  return (
    <div className="absolute inset-0 w-full h-full overflow-hidden bg-[#090d16]">
      {/* 3D Scene Canvas */}
      <AgentHQScene
        agents={formattedAgents as any}
        memoryCount={memoryCount}
        cameraControlRef={cameraControlRef}
        onSelectAgent={handleSelectAgent}
      />

      {/* Floating HUD Overlay */}
      <AgentHQHud
        totalAgents={formattedAgents.length}
        runningAgents={runningCount}
        totalTasks={totalTasksCount}
        activeTab={activeTab}
        onTabChange={setActiveTab}
        renderMode={renderMode}
        onRenderModeChange={onRenderModeChange}
        onResetCamera={handleResetCamera}
        onZoomIn={handleZoomIn}
        onZoomOut={handleZoomOut}
        selectedAgent={selectedAgent}
        onCloseSelectedAgent={() => setSelectedAgent(null)}
      />
    </div>
  );
};
