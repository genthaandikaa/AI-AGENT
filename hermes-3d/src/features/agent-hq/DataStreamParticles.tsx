"use client";

import React, { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { DEPARTMENTS } from "./types";

export const DataStreamParticles: React.FC = () => {
  const particlesRef = useRef<THREE.Points>(null);

  // Pathways: Line conduits from each department room to the brain hub
  const pathways = useMemo(() => {
    return DEPARTMENTS.map((dept) => {
      const [x, , z] = dept.position;
      // Start from room edge towards hub edge
      const dir = new THREE.Vector3(x, 0, z).normalize();
      const start = new THREE.Vector3(x - dir.x * 3.5, 0.05, z - dir.z * 3.5);
      const end = new THREE.Vector3(dir.x * 6.5, 0.05, dir.z * 6.5);
      return {
        dept,
        points: [start, end],
        color: dept.color,
      };
    });
  }, []);

  // Moving particle stream
  const countPerLine = 10;
  const totalParticles = DEPARTMENTS.length * countPerLine;

  const { positions, lineIndices, progress } = useMemo(() => {
    const pos = new Float32Array(totalParticles * 3);
    const indices = new Float32Array(totalParticles);
    const prog = new Float32Array(totalParticles);

    for (let i = 0; i < totalParticles; i++) {
      const lineIdx = Math.floor(i / countPerLine);
      indices[i] = lineIdx;
      prog[i] = (i % countPerLine) / countPerLine;
    }
    return { positions: pos, lineIndices: indices, progress: prog };
  }, [totalParticles]);

  useFrame((state, delta) => {
    if (!particlesRef.current) return;
    const posAttr = particlesRef.current.geometry.attributes.position;

    for (let i = 0; i < totalParticles; i++) {
      progress[i] += delta * 0.35;
      if (progress[i] > 1.0) progress[i] -= 1.0;

      const lineIdx = lineIndices[i];
      const p = pathways[lineIdx];
      const start = p.points[0];
      const end = p.points[1];

      const curX = start.x + (end.x - start.x) * progress[i];
      const curY = 0.12 + Math.sin(progress[i] * Math.PI) * 0.15;
      const curZ = start.z + (end.z - start.z) * progress[i];

      posAttr.setXYZ(i, curX, curY, curZ);
    }
    posAttr.needsUpdate = true;
  });

  return (
    <group>
      {/* Static Glowing Cable Pathways */}
      {pathways.map((path, idx) => {
        const geom = new THREE.BufferGeometry().setFromPoints(path.points);
        return (
          <group key={idx}>
            {/* Primary Glowing Conduit */}
            {/* @ts-ignore */}
            <line geometry={geom}>
              <lineBasicMaterial color={path.color} transparent opacity={0.65} linewidth={2} />
            </line>
            {/* Pathway Base Plate */}
            <mesh
              position={[
                (path.points[0].x + path.points[1].x) / 2,
                -0.02,
                (path.points[0].z + path.points[1].z) / 2,
              ]}
              rotation={[
                0,
                Math.atan2(
                  path.points[0].x - path.points[1].x,
                  path.points[0].z - path.points[1].z
                ),
                0,
              ]}
            >
              <boxGeometry
                args={[
                  0.35,
                  0.04,
                  path.points[0].distanceTo(path.points[1]),
                ]}
              />
              <meshStandardMaterial color="#111827" roughness={0.7} metalness={0.6} />
            </mesh>
          </group>
        );
      })}

      {/* Dynamic Animated Pulse Particles */}
      <points ref={particlesRef}>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            args={[positions, 3]}
          />
        </bufferGeometry>
        <pointsMaterial
          size={0.35}
          color="#38bdf8"
          transparent
          opacity={0.9}
          blending={THREE.AdditiveBlending}
        />
      </points>
    </group>
  );
};
