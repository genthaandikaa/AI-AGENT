"use client";

import React, { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Html } from "@react-three/drei";
import * as THREE from "three";

interface BrainCenterHubProps {
  memoryCount?: number;
  activeAgentsCount?: number;
}

export const BrainCenterHub: React.FC<BrainCenterHubProps> = ({
  memoryCount = 1245,
  activeAgentsCount = 10,
}) => {
  const outerRingRef = useRef<THREE.Mesh>(null);
  const innerRingRef = useRef<THREE.Mesh>(null);
  const coreRef = useRef<THREE.Mesh>(null);
  const beamRef = useRef<THREE.Mesh>(null);

  useFrame((state, delta) => {
    const t = state.clock.getElapsedTime();

    if (outerRingRef.current) {
      outerRingRef.current.rotation.z = t * 0.4;
    }
    if (innerRingRef.current) {
      innerRingRef.current.rotation.z = -t * 0.6;
    }
    if (coreRef.current) {
      const scale = 1 + Math.sin(t * 2) * 0.08;
      coreRef.current.scale.set(scale, scale, scale);
    }
    if (beamRef.current) {
      const mat = beamRef.current.material as THREE.MeshBasicMaterial;
      if (mat) {
        mat.opacity = 0.35 + Math.sin(t * 3) * 0.15;
      }
    }
  });

  return (
    <group position={[0, 0, 0]}>
      {/* Base Tier 1: Large circular platform */}
      <mesh position={[0, -0.4, 0]} receiveShadow>
        <cylinderGeometry args={[7.5, 8.0, 0.4, 64]} />
        <meshStandardMaterial color="#0d1117" roughness={0.6} metalness={0.8} />
      </mesh>

      {/* Base Tier 2: Stepped inner circular platform */}
      <mesh position={[0, -0.1, 0]} receiveShadow>
        <cylinderGeometry args={[6.2, 6.5, 0.3, 64]} />
        <meshStandardMaterial color="#161b22" roughness={0.4} metalness={0.9} />
      </mesh>

      {/* Glowing Neon Cyan Outer Perimeter Ring */}
      <mesh position={[0, 0.06, 0]} rotation={[-Math.PI / 2, 0, 0]} ref={outerRingRef}>
        <ringGeometry args={[6.8, 7.1, 64]} />
        <meshBasicMaterial color="#06b6d4" side={THREE.DoubleSide} transparent opacity={0.85} />
      </mesh>

      {/* Decorative Segmented Tech Ring */}
      <mesh position={[0, 0.07, 0]} rotation={[-Math.PI / 2, 0, 0]} ref={innerRingRef}>
        <ringGeometry args={[5.2, 5.4, 32]} />
        <meshBasicMaterial color="#3b82f6" side={THREE.DoubleSide} transparent opacity={0.7} />
      </mesh>

      {/* Inner Pedestal with Circuit Pattern Look */}
      <mesh position={[0, 0.2, 0]}>
        <cylinderGeometry args={[3.2, 3.6, 0.4, 48]} />
        <meshStandardMaterial color="#0f172a" roughness={0.3} metalness={0.8} />
      </mesh>

      {/* Hologram Central Core Sphere */}
      <mesh position={[0, 1.8, 0]} ref={coreRef}>
        <sphereGeometry args={[1.2, 32, 32]} />
        <meshStandardMaterial
          color="#38bdf8"
          emissive="#0284c7"
          emissiveIntensity={0.8}
          roughness={0.1}
          metalness={0.9}
          transparent
          opacity={0.85}
        />
      </mesh>

      {/* Holographic Vertical Light Beam */}
      <mesh position={[0, 4.5, 0]} ref={beamRef}>
        <cylinderGeometry args={[0.3, 1.8, 7, 32, 1, true]} />
        <meshBasicMaterial color="#38bdf8" transparent opacity={0.3} side={THREE.DoubleSide} />
      </mesh>

      {/* Light Source emanating from The Brain */}
      <pointLight position={[0, 2.5, 0]} color="#38bdf8" intensity={3.5} distance={20} />

      {/* Floating Billboard Label: THE BRAIN */}
      <Html position={[0, 3.8, 0]} center distanceFactor={28} zIndexRange={[100, 0]}>
        <div className="pointer-events-none select-none flex flex-col items-center">
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-950/80 backdrop-blur-md border border-cyan-500/50 shadow-[0_0_15px_rgba(6,182,212,0.4)]">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
            <span className="font-mono text-[11px] font-black tracking-wider text-cyan-300">
              THE BRAIN
            </span>
          </div>
          <span className="mt-1 font-mono text-[9px] text-cyan-400/80 font-medium tracking-tight bg-slate-900/60 px-2 py-0.5 rounded-md border border-cyan-900/40">
            {memoryCount.toLocaleString()} shared memories
          </span>
        </div>
      </Html>
    </group>
  );
};
