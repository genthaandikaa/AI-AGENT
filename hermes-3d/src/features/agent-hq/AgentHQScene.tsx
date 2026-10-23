"use client";

import React, { useMemo } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import * as THREE from "three";
import { BrainCenterHub } from "./BrainCenterHub";
import { DepartmentRoom } from "./DepartmentRoom";
import { DataStreamParticles } from "./DataStreamParticles";
import { DEPARTMENTS, DepartmentConfig } from "./types";

interface AgentVisualData {
  id: string;
  name: string;
  role: string;
  status: "working" | "idle" | "in_progress";
  currentTask?: string;
  avatarColor?: string;
}

interface AgentHQSceneProps {
  agents: AgentVisualData[];
  memoryCount?: number;
  onSelectAgent?: (agent: AgentVisualData) => void;
  onSelectDepartment?: (dept: DepartmentConfig) => void;
  cameraControlRef?: React.MutableRefObject<any>;
}

// Background Starfield & Subtle Grid Floor
const BackgroundGrid: React.FC = () => {
  return (
    <group position={[0, -0.6, 0]}>
      {/* Dark Ambient Floor Plate */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[140, 140]} />
        <meshStandardMaterial color="#090d16" roughness={0.95} metalness={0.1} />
      </mesh>

      {/* Grid Helper with subtle cyan/purple grid lines */}
      <gridHelper args={[120, 60, "#1e293b", "#0f172a"]} position={[0, 0.02, 0]} />
    </group>
  );
};

export const AgentHQScene: React.FC<AgentHQSceneProps> = ({
  agents,
  memoryCount = 1245,
  onSelectAgent,
  onSelectDepartment,
  cameraControlRef,
}) => {
  // Map agents to departments dynamically based on roles/id
  const agentsByDept = useMemo(() => {
    const map = new Map<string, AgentVisualData[]>();
    DEPARTMENTS.forEach((d) => map.set(d.id, []));

    agents.forEach((agent) => {
      const roleLower = (agent.role || "").toLowerCase();
      const idLower = (agent.id || "").toLowerCase();

      let assigned = false;
      for (const dept of DEPARTMENTS) {
        if (
          dept.roles.some(
            (r) => roleLower.includes(r.toLowerCase()) || idLower.includes(r.toLowerCase())
          )
        ) {
          map.get(dept.id)?.push(agent);
          assigned = true;
          break;
        }
      }
      // Fallback to Scripts & Coding if unmatched
      if (!assigned) {
        map.get("scripts_coding")?.push(agent);
      }
    });

    return map;
  }, [agents]);

  return (
    <div className="absolute inset-0 w-full h-full bg-[#090d16]">
      <Canvas
        shadows
        camera={{
          position: [34, 34, 34],
          fov: 38,
          near: 0.5,
          far: 500,
        }}
        gl={{
          antialias: true,
          alpha: false,
          powerPreference: "high-performance",
          toneMapping: THREE.ACESFilmicToneMapping,
          toneMappingExposure: 1.15,
        }}
        style={{ width: "100%", height: "100%" }}
        onCreated={({ gl, camera }) => {
          gl.setClearColor("#090d16", 1);
          camera.lookAt(0, 0, 0);
        }}
      >
        {/* OrbitControls Clamped to Keep Isometric Angle */}
        <OrbitControls
          ref={cameraControlRef}
          enableDamping
          dampingFactor={0.08}
          minDistance={15}
          maxDistance={120}
          minPolarAngle={Math.PI / 6}
          maxPolarAngle={Math.PI / 2.2}
          target={[0, 0, 0]}
        />

        {/* Scene Lighting */}
        <ambientLight color="#ffffff" intensity={0.8} />
        <directionalLight
          position={[30, 50, 30]}
          intensity={1.5}
          castShadow
          shadow-mapSize-width={2048}
          shadow-mapSize-height={2048}
        />
        <directionalLight position={[-25, 25, -25]} intensity={0.6} color="#38bdf8" />
        <hemisphereLight args={["#1e293b", "#090d16", 0.6]} />

        {/* Starfield & Background Grid */}
        <BackgroundGrid />

        {/* Central Hub: The Brain */}
        <BrainCenterHub
          memoryCount={memoryCount}
          activeAgentsCount={agents.length}
        />

        {/* Animated Connecting Pathways & Data Particles */}
        <DataStreamParticles />

        {/* 8 Department Rooms Arranged in a Circular Ring */}
        {DEPARTMENTS.map((dept) => {
          const deptAgents = agentsByDept.get(dept.id) || [];
          return (
            <DepartmentRoom
              key={dept.id}
              dept={dept}
              agents={deptAgents}
              onSelectAgent={onSelectAgent}
              onSelectDepartment={onSelectDepartment}
            />
          );
        })}
      </Canvas>
    </div>
  );
};
