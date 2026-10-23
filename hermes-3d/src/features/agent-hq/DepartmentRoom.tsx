"use client";

import React, { useRef, useState } from "react";
import { useFrame } from "@react-three/fiber";
import { Html } from "@react-three/drei";
import * as THREE from "three";
import { DepartmentConfig } from "./types";

interface AgentVisualData {
  id: string;
  name: string;
  role: string;
  status: "working" | "idle" | "in_progress";
  currentTask?: string;
  avatarColor?: string;
}

interface DepartmentRoomProps {
  dept: DepartmentConfig;
  agents: AgentVisualData[];
  onSelectAgent?: (agent: AgentVisualData) => void;
  onSelectDepartment?: (dept: DepartmentConfig) => void;
}

// Low-poly 3D Agent Avatar seated at desk
const SeatedAgent3D: React.FC<{
  agent: AgentVisualData;
  position: [number, number, number];
  rotationY?: number;
  deptColor: string;
  onClick?: () => void;
}> = ({ agent, position, rotationY = 0, deptColor, onClick }) => {
  const headRef = useRef<THREE.Group>(null);
  const leftArmRef = useRef<THREE.Mesh>(null);
  const rightArmRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  const isWorking = agent.status === "working" || agent.status === "in_progress";

  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    const speed = isWorking ? 12 : 2;

    // Typing arm motion
    if (isWorking) {
      if (leftArmRef.current) {
        leftArmRef.current.rotation.x = Math.sin(t * speed) * 0.15 - 0.4;
      }
      if (rightArmRef.current) {
        rightArmRef.current.rotation.x = Math.cos(t * speed) * 0.15 - 0.4;
      }
      if (headRef.current) {
        headRef.current.position.y = 1.05 + Math.sin(t * 4) * 0.02;
      }
    } else {
      if (headRef.current) {
        headRef.current.position.y = 1.05 + Math.sin(t * 1.5) * 0.015;
      }
    }
  });

  return (
    <group
      position={position}
      rotation={[0, rotationY, 0]}
      onClick={(e) => {
        e.stopPropagation();
        onClick?.();
      }}
      onPointerOver={(e) => {
        e.stopPropagation();
        setHovered(true);
      }}
      onPointerOut={() => setHovered(false)}
    >
      {/* Office Chair */}
      <group position={[0, 0, 0.45]}>
        {/* Seat cushion */}
        <mesh position={[0, 0.4, 0]} castShadow>
          <boxGeometry args={[0.55, 0.1, 0.5]} />
          <meshStandardMaterial color="#1e293b" roughness={0.7} />
        </mesh>
        {/* Chair backrest */}
        <mesh position={[0, 0.75, 0.22]} castShadow>
          <boxGeometry args={[0.5, 0.65, 0.08]} />
          <meshStandardMaterial color="#0f172a" roughness={0.7} />
        </mesh>
        {/* Chair stem */}
        <mesh position={[0, 0.2, 0]}>
          <cylinderGeometry args={[0.04, 0.04, 0.4, 12]} />
          <meshStandardMaterial color="#475569" metalness={0.9} roughness={0.2} />
        </mesh>
        {/* Wheel base */}
        <mesh position={[0, 0.02, 0]}>
          <cylinderGeometry args={[0.25, 0.25, 0.04, 8]} />
          <meshStandardMaterial color="#0f172a" metalness={0.8} />
        </mesh>
      </group>

      {/* Character Torso */}
      <mesh position={[0, 0.75, 0.4]} castShadow>
        <boxGeometry args={[0.42, 0.55, 0.28]} />
        <meshStandardMaterial
          color={agent.avatarColor || deptColor}
          roughness={0.5}
          metalness={0.2}
        />
      </mesh>

      {/* Head + Face */}
      <group position={[0, 1.15, 0.4]} ref={headRef}>
        <mesh castShadow>
          <boxGeometry args={[0.34, 0.34, 0.34]} />
          <meshStandardMaterial color="#fcd34d" roughness={0.4} />
        </mesh>
        {/* Hair block */}
        <mesh position={[0, 0.12, -0.04]} castShadow>
          <boxGeometry args={[0.36, 0.18, 0.36]} />
          <meshStandardMaterial color="#334155" roughness={0.9} />
        </mesh>
        {/* Eyes (front facing) */}
        <mesh position={[-0.08, 0.02, 0.18]}>
          <boxGeometry args={[0.05, 0.06, 0.02]} />
          <meshBasicMaterial color="#0f172a" />
        </mesh>
        <mesh position={[0.08, 0.02, 0.18]}>
          <boxGeometry args={[0.05, 0.06, 0.02]} />
          <meshBasicMaterial color="#0f172a" />
        </mesh>
      </group>

      {/* Left Arm */}
      <mesh position={[-0.26, 0.75, 0.32]} rotation={[-0.4, 0, 0.1]} ref={leftArmRef} castShadow>
        <boxGeometry args={[0.1, 0.38, 0.1]} />
        <meshStandardMaterial color={agent.avatarColor || deptColor} />
      </mesh>

      {/* Right Arm */}
      <mesh position={[0.26, 0.75, 0.32]} rotation={[-0.4, 0, -0.1]} ref={rightArmRef} castShadow>
        <boxGeometry args={[0.1, 0.38, 0.1]} />
        <meshStandardMaterial color={agent.avatarColor || deptColor} />
      </mesh>

      {/* Live Working Status Beacon */}
      <mesh position={[0, 1.5, 0.4]}>
        <sphereGeometry args={[0.07, 16, 16]} />
        <meshBasicMaterial
          color={isWorking ? "#10b981" : "#f59e0b"}
          transparent
          opacity={hovered ? 1.0 : 0.85}
        />
      </mesh>

      {/* Name tooltip on hover */}
      {hovered && (
        <Html position={[0, 1.7, 0.4]} center distanceFactor={20} zIndexRange={[120, 0]}>
          <div className="pointer-events-none select-none bg-slate-900/90 backdrop-blur-md px-2.5 py-1 rounded-lg border border-slate-700 shadow-xl whitespace-nowrap text-center">
            <p className="text-[10px] font-bold text-white leading-tight">{agent.name}</p>
            <p className="text-[8px] font-mono text-cyan-400 capitalize">{agent.status}</p>
            {agent.currentTask && (
              <p className="text-[8px] text-slate-300 max-w-[140px] truncate mt-0.5">
                {agent.currentTask}
              </p>
            )}
          </div>
        </Html>
      )}
    </group>
  );
};

export const DepartmentRoom: React.FC<DepartmentRoomProps> = ({
  dept,
  agents,
  onSelectAgent,
  onSelectDepartment,
}) => {
  const [hovered, setHovered] = useState(false);
  const runningCount = agents.filter(
    (a) => a.status === "working" || a.status === "in_progress"
  ).length;

  return (
    <group
      position={dept.position}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
      onClick={() => onSelectDepartment?.(dept)}
    >
      {/* Room Base Slab */}
      <mesh position={[0, -0.2, 0]} receiveShadow>
        <boxGeometry args={[9.5, 0.4, 9.5]} />
        <meshStandardMaterial
          color={hovered ? "#1e293b" : "#0f172a"}
          roughness={0.5}
          metalness={0.7}
        />
      </mesh>

      {/* Glowing Room Perimeter Line */}
      <lineSegments position={[0, 0.02, 0]}>
        <edgesGeometry args={[new THREE.BoxGeometry(9.5, 0.05, 9.5)]} />
        <meshBasicMaterial color={dept.color} />
      </lineSegments>

      {/* Glass Partition Back Wall */}
      <mesh position={[0, 1.2, -4.6]} castShadow>
        <boxGeometry args={[9.2, 2.0, 0.1]} />
        <meshStandardMaterial
          color={dept.color}
          transparent
          opacity={0.18}
          roughness={0.1}
          metalness={0.9}
        />
      </mesh>

      {/* Glass Partition Left Wall */}
      <mesh position={[-4.6, 1.2, 0]} castShadow>
        <boxGeometry args={[0.1, 2.0, 9.2]} />
        <meshStandardMaterial
          color={dept.color}
          transparent
          opacity={0.18}
          roughness={0.1}
          metalness={0.9}
        />
      </mesh>

      {/* Neon Top Railing for Back Wall */}
      <mesh position={[0, 2.22, -4.6]}>
        <boxGeometry args={[9.4, 0.06, 0.12]} />
        <meshBasicMaterial color={dept.glowColor} />
      </mesh>

      {/* Neon Top Railing for Left Wall */}
      <mesh position={[-4.6, 2.22, 0]}>
        <boxGeometry args={[0.12, 0.06, 9.4]} />
        <meshBasicMaterial color={dept.glowColor} />
      </mesh>

      {/* Desk 1 (Left desk) */}
      <group position={[-2.2, 0, -1.2]}>
        {/* Tabletop */}
        <mesh position={[0, 0.72, 0]} castShadow receiveShadow>
          <boxGeometry args={[2.8, 0.08, 1.4]} />
          <meshStandardMaterial color="#1e293b" roughness={0.3} metalness={0.6} />
        </mesh>
        {/* Desk legs */}
        <mesh position={[-1.3, 0.36, -0.6]}>
          <boxGeometry args={[0.08, 0.72, 0.08]} />
          <meshStandardMaterial color="#475569" metalness={0.8} />
        </mesh>
        <mesh position={[1.3, 0.36, -0.6]}>
          <boxGeometry args={[0.08, 0.72, 0.08]} />
          <meshStandardMaterial color="#475569" metalness={0.8} />
        </mesh>
        <mesh position={[-1.3, 0.36, 0.6]}>
          <boxGeometry args={[0.08, 0.72, 0.08]} />
          <meshStandardMaterial color="#475569" metalness={0.8} />
        </mesh>
        <mesh position={[1.3, 0.36, 0.6]}>
          <boxGeometry args={[0.08, 0.72, 0.08]} />
          <meshStandardMaterial color="#475569" metalness={0.8} />
        </mesh>
        {/* Monitor 1 */}
        <mesh position={[-0.45, 1.15, -0.35]} castShadow>
          <boxGeometry args={[0.9, 0.55, 0.05]} />
          <meshStandardMaterial color="#0f172a" roughness={0.4} />
        </mesh>
        {/* Glowing Screen 1 */}
        <mesh position={[-0.45, 1.15, -0.32]}>
          <boxGeometry args={[0.82, 0.48, 0.01]} />
          <meshBasicMaterial color="#38bdf8" />
        </mesh>
        {/* Monitor stand */}
        <mesh position={[-0.45, 0.85, -0.35]}>
          <cylinderGeometry args={[0.03, 0.03, 0.2, 8]} />
          <meshStandardMaterial color="#475569" metalness={0.8} />
        </mesh>
        {/* Keyboard */}
        <mesh position={[-0.45, 0.77, 0.05]}>
          <boxGeometry args={[0.55, 0.02, 0.2]} />
          <meshStandardMaterial color="#0f172a" />
        </mesh>
      </group>

      {/* Desk 2 (Right desk) */}
      <group position={[2.2, 0, -1.2]}>
        {/* Tabletop */}
        <mesh position={[0, 0.72, 0]} castShadow receiveShadow>
          <boxGeometry args={[2.8, 0.08, 1.4]} />
          <meshStandardMaterial color="#1e293b" roughness={0.3} metalness={0.6} />
        </mesh>
        {/* Desk legs */}
        <mesh position={[-1.3, 0.36, -0.6]}>
          <boxGeometry args={[0.08, 0.72, 0.08]} />
          <meshStandardMaterial color="#475569" metalness={0.8} />
        </mesh>
        <mesh position={[1.3, 0.36, -0.6]}>
          <boxGeometry args={[0.08, 0.72, 0.08]} />
          <meshStandardMaterial color="#475569" metalness={0.8} />
        </mesh>
        <mesh position={[-1.3, 0.36, 0.6]}>
          <boxGeometry args={[0.08, 0.72, 0.08]} />
          <meshStandardMaterial color="#475569" metalness={0.8} />
        </mesh>
        <mesh position={[1.3, 0.36, 0.6]}>
          <boxGeometry args={[0.08, 0.72, 0.08]} />
          <meshStandardMaterial color="#475569" metalness={0.8} />
        </mesh>
        {/* Monitor 2 */}
        <mesh position={[0.45, 1.15, -0.35]} castShadow>
          <boxGeometry args={[0.9, 0.55, 0.05]} />
          <meshStandardMaterial color="#0f172a" roughness={0.4} />
        </mesh>
        {/* Glowing Screen 2 */}
        <mesh position={[0.45, 1.15, -0.32]}>
          <boxGeometry args={[0.82, 0.48, 0.01]} />
          <meshBasicMaterial color={dept.color} />
        </mesh>
        {/* Monitor stand */}
        <mesh position={[0.45, 0.85, -0.35]}>
          <cylinderGeometry args={[0.03, 0.03, 0.2, 8]} />
          <meshStandardMaterial color="#475569" metalness={0.8} />
        </mesh>
        {/* Keyboard */}
        <mesh position={[0.45, 0.77, 0.05]}>
          <boxGeometry args={[0.55, 0.02, 0.2]} />
          <meshStandardMaterial color="#0f172a" />
        </mesh>
      </group>

      {/* Render Agents Seated at Desks */}
      {agents.slice(0, 2).map((agent, index) => {
        const xPos = index === 0 ? -2.65 : 2.65;
        return (
          <SeatedAgent3D
            key={agent.id}
            agent={agent}
            position={[xPos, 0, -1.2]}
            rotationY={0}
            deptColor={dept.color}
            onClick={() => onSelectAgent?.(agent)}
          />
        );
      })}

      {/* Extra standing agent if more than 2 */}
      {agents.length > 2 && (
        <SeatedAgent3D
          agent={agents[2]}
          position={[0, 0, 1.5]}
          rotationY={Math.PI}
          deptColor={dept.color}
          onClick={() => onSelectAgent?.(agents[2])}
        />
      )}

      {/* Room Accent Glow Light */}
      <pointLight position={[0, 3.2, 0]} color={dept.color} intensity={2.0} distance={12} />

      {/* Floating Overhead Billboard Label */}
      <Html position={[0, 4.4, 0]} center distanceFactor={26} zIndexRange={[100, 0]}>
        <div className="pointer-events-none select-none flex flex-col items-center">
          <div
            className="flex items-center gap-1.5 px-3 py-1 rounded-xl bg-slate-950/85 backdrop-blur-md border shadow-lg transition-transform duration-200"
            style={{
              borderColor: dept.color,
              boxShadow: `0 0 16px ${dept.color}40`,
            }}
          >
            <span
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: dept.glowColor }}
            ></span>
            <span className="font-bold text-[11px] text-white tracking-wide">
              {dept.name}
            </span>
          </div>
          <div className="mt-1 flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-900/80 border border-slate-700/60">
            <span className="text-[9px] font-mono text-slate-300">
              {agents.length} agent{agents.length === 1 ? "" : "s"}
            </span>
            <span className="text-[9px] text-slate-500">•</span>
            <span className="text-[9px] font-mono text-emerald-400 font-semibold">
              {runningCount} running
            </span>
          </div>
        </div>
      </Html>
    </group>
  );
};
