import React, { useEffect, useMemo, useRef, useState } from "react";
import { Streamlit, ComponentProps } from "streamlit-component-lib";
import { Canvas, ThreeEvent } from "@react-three/fiber";
import { OrbitControls, Grid } from "@react-three/drei";
import * as THREE from "three";

type CatalogItem =
  | { id: string; label: string; shape: "box"; size: [number, number, number] }
  | { id: string; label: string; shape: "cylinder"; radius: number; height: number };

type Command = { token: number; type: "insert"; definitionId: string | null };

type Instance = {
  id: string;
  definitionId: string;
  position: [number, number, number];
  rotationY: number; // radians
};

type SceneState = { instances: Instance[]; selectedId: string | null };

function uuid() {
  return crypto.randomUUID ? crypto.randomUUID() : `id_${Math.random().toString(16).slice(2)}`;
}

function clamp(n: number, a: number, b: number) {
  return Math.max(a, Math.min(b, n));
}

export function ThreeBuilder(props: ComponentProps) {
  const catalog: CatalogItem[] = props.args["catalog"] ?? [];
  const command: Command = props.args["command"] ?? { token: 0, type: "insert", definitionId: null };

  const [instances, setInstances] = useState<Instance[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const lastTokenRef = useRef<number>(-1);

  // Tell Streamlit our height
  useEffect(() => {
    Streamlit.setFrameHeight(props.args["height"] ?? 640);
  }, [props.args]);

  // Emit state back to Streamlit (throttled-ish via RAF)
  const emitRef = useRef<number | null>(null);
  const emitState = (next: SceneState) => {
    if (emitRef.current) cancelAnimationFrame(emitRef.current);
    emitRef.current = requestAnimationFrame(() => {
      Streamlit.setComponentValue(next);
    });
  };

  // Whenever state changes, emit to Streamlit
  useEffect(() => {
    emitState({ instances, selectedId });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [instances, selectedId]);

  // Handle insert/clear commands from Streamlit
  useEffect(() => {
    if (command.token === lastTokenRef.current) return;
    lastTokenRef.current = command.token;

    const defId = command.definitionId;
    if (!defId) return;

    if (defId === "__CLEAR__") {
      setInstances([]);
      setSelectedId(null);
      return;
    }

    // Place new instance near origin with small offset
    const i: Instance = {
      id: uuid(),
      definitionId: defId,
      position: [0, 0.05, 0],
      rotationY: 0
    };

    setInstances((prev) => [...prev, i]);
    setSelectedId(i.id);
  }, [command]);

  // Rotation hotkey: R rotates selected by 15 degrees
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (!selectedId) return;
      if (e.key.toLowerCase() === "r") {
        setInstances((prev) =>
          prev.map((x) =>
            x.id === selectedId ? { ...x, rotationY: x.rotationY + THREE.MathUtils.degToRad(15) } : x
          )
        );
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [selectedId]);

  const catalogMap = useMemo(() => {
    const m = new Map<string, CatalogItem>();
    for (const c of catalog) m.set(c.id, c);
    return m;
  }, [catalog]);

  return (
    <div style={{ width: "100%", height: props.args["height"] ?? 640 }}>
      <Canvas camera={{ position: [4, 4, 4], fov: 50 }}>
        <ambientLight intensity={0.8} />
        <directionalLight position={[5, 8, 5]} intensity={1.0} />

        {/* Ground */}
        <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
          <planeGeometry args={[50, 50]} />
          <meshStandardMaterial color="#f2f2f2" />
        </mesh>
        <Grid
          infiniteGrid
          cellSize={0.5}
          cellThickness={0.5}
          sectionSize={2}
          sectionThickness={1}
          fadeDistance={20}
        />

        <OrbitControls makeDefault />

        <InstancesLayer
          instances={instances}
          setInstances={setInstances}
          selectedId={selectedId}
          setSelectedId={setSelectedId}
          catalogMap={catalogMap}
        />
      </Canvas>
    </div>
  );
}

function InstancesLayer(props: {
  instances: Instance[];
  setInstances: React.Dispatch<React.SetStateAction<Instance[]>>;
  selectedId: string | null;
  setSelectedId: (id: string | null) => void;
  catalogMap: Map<string, CatalogItem>;
}) {
  const { instances, setInstances, selectedId, setSelectedId, catalogMap } = props;

  // Drag on plane using raycasting
  const plane = useMemo(() => new THREE.Plane(new THREE.Vector3(0, 1, 0), 0), []);
  const raycaster = useMemo(() => new THREE.Raycaster(), []);
  const pointer = useMemo(() => new THREE.Vector2(), []);
  const draggingRef = useRef<{ id: string } | null>(null);

  const onPointerDown = (e: ThreeEvent<PointerEvent>, id: string) => {
    e.stopPropagation();
    setSelectedId(id);
    draggingRef.current = { id };
  };

  const onPointerUp = () => {
    draggingRef.current = null;
  };

  const onPointerMove = (e: ThreeEvent<PointerEvent>) => {
    if (!draggingRef.current) return;

    // Compute intersection with ground plane
    const { camera, gl } = e;
    const rect = gl.domElement.getBoundingClientRect();
    pointer.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    pointer.y = -(((e.clientY - rect.top) / rect.height) * 2 - 1);

    raycaster.setFromCamera(pointer, camera);
    const hit = new THREE.Vector3();
    raycaster.ray.intersectPlane(plane, hit);

    // Limit to a reasonable area
    hit.x = clamp(hit.x, -20, 20);
    hit.z = clamp(hit.z, -20, 20);

    const id = draggingRef.current.id;
    setInstances((prev) =>
      prev.map((inst) =>
        inst.id === id ? { ...inst, position: [hit.x, inst.position[1], hit.z] } : inst
      )
    );
  };

  return (
    <group onPointerMove={onPointerMove} onPointerUp={onPointerUp} onPointerMissed={() => setSelectedId(null)}>
      {instances.map((inst) => {
        const def = catalogMap.get(inst.definitionId);
        const isSel = inst.id === selectedId;

        return (
          <group
            key={inst.id}
            position={inst.position}
            rotation={[0, inst.rotationY, 0]}
            onPointerDown={(e) => onPointerDown(e, inst.id)}
          >
            <mesh castShadow receiveShadow>
              {def?.shape === "cylinder" ? (
                <cylinderGeometry args={[def.radius, def.radius, def.height, 24]} />
              ) : (
                // default box
                <boxGeometry args={(def && def.shape === "box" ? def.size : [1, 1, 1]) as [number, number, number]} />
              )}

              <meshStandardMaterial color={isSel ? "#ffd54f" : "#90caf9"} />
            </mesh>
          </group>
        );
      })}
    </group>
  );
}
