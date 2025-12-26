import React, { useEffect, useMemo, useRef, useState } from "react";
import {
  Streamlit,
  ComponentProps,
  withStreamlitConnection,
} from "streamlit-component-lib";
import { Canvas, ThreeEvent, useThree } from "@react-three/fiber";
import { OrbitControls, Grid } from "@react-three/drei";
import * as THREE from "three";

type CatalogItem = {
  id: string;
  label: string;
  category?: string;
  shape?: "box" | "cylinder";
  size?: [number, number, number]; // [width, height, depth] for box
  radius?: number; // for cylinder
  height?: number; // for cylinder
  color?: string;
};

type Command = {
  token: number;
  type: "insert" | "delete" | "clear";
  definitionId: string | null;
};

type Instance = {
  id: string;
  definitionId: string;
  position: [number, number, number];
  rotationY: number; // radians
};

type SceneState = {
  instances: Instance[];
  selectedId: string | null;
  lastChange?: { type: string; instanceId?: string; timestamp: number };
};

function uuid() {
  return crypto.randomUUID
    ? crypto.randomUUID()
    : `id_${Math.random().toString(16).slice(2)}`;
}

function clamp(n: number, a: number, b: number) {
  return Math.max(a, Math.min(b, n));
}

// Default sizes for component types
const DEFAULT_SIZES: Record<string, [number, number, number]> = {
  wall: [3, 2.8, 0.3],
  floor: [4, 0.2, 4],
  roof: [5, 0.3, 5],
  window: [1.2, 1.5, 0.1],
  door: [1, 2.2, 0.1],
};

const DEFAULT_COLORS: Record<string, string> = {
  wall: "#b0bec5",
  floor: "#8d6e63",
  roof: "#d84315",
  window: "#81d4fa",
  door: "#5d4037",
};

function ThreeBuilderInner(props: ComponentProps) {
  const catalog: CatalogItem[] = props.args["catalog"] ?? [];
  const command: Command =
    props.args["command"] ?? { token: 0, type: "insert", definitionId: null };
  const initialInstances: Instance[] = props.args["initialInstances"] ?? [];
  const projectId: string | null = props.args["projectId"] ?? null;
  const height: number = props.args["height"] ?? 640;

  const [instances, setInstances] = useState<Instance[]>(initialInstances);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const lastTokenRef = useRef<number>(-1);
  const readyRef = useRef(false);

  // Streamlit component ready + height
  useEffect(() => {
    if (!readyRef.current) {
      Streamlit.setComponentReady();
      readyRef.current = true;
    }
    Streamlit.setFrameHeight(height);
  }, [height]);

  // Initialize from props ONCE (even if empty)
  const initializedRef = useRef<boolean>(false);
  useEffect(() => {
    if (!initializedRef.current) {
      setInstances(initialInstances);
      initializedRef.current = true;
    }
  }, [initialInstances]);

  // Reset when project changes (also reset instances to the passed initialInstances)
  useEffect(() => {
    if (projectId !== null) {
      setInstances(initialInstances);
      setSelectedId(null);
      initializedRef.current = true;
    }
  }, [projectId, initialInstances]);

  // Emit state back to Streamlit (throttled-ish via RAF)
  const emitRef = useRef<number | null>(null);
  const emitState = (next: SceneState) => {
    if (emitRef.current) cancelAnimationFrame(emitRef.current);
    emitRef.current = requestAnimationFrame(() => {
      Streamlit.setComponentValue(next);
    });
  };

  useEffect(() => {
    emitState({ instances, selectedId });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [instances, selectedId]);

  // Handle insert/delete/clear commands from Streamlit
  useEffect(() => {
    if (command.token === lastTokenRef.current) return;
    lastTokenRef.current = command.token;

    const defId = command.definitionId;

    if (command.type === "clear") {
      setInstances([]);
      setSelectedId(null);
      return;
    }

    if (command.type === "delete") {
      setInstances((prev) => prev.filter((x) => x.id !== selectedId));
      setSelectedId(null);
      return;
    }

    if (command.type === "insert" && defId) {
      const catalogItem = catalog.find((c) => c.id === defId);
      const size = catalogItem?.size || DEFAULT_SIZES[defId] || [1, 1, 1];

      const i: Instance = {
        id: uuid(),
        definitionId: defId,
        position: [0, size[1] / 2, 0],
        rotationY: 0,
      };

      setInstances((prev) => [...prev, i]);
      setSelectedId(i.id);
    }
  }, [command, catalog, selectedId]);

  // Keyboard shortcuts
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (!selectedId) return;

      if (e.key.toLowerCase() === "r") {
        setInstances((prev) =>
          prev.map((x) =>
            x.id === selectedId
              ? { ...x, rotationY: x.rotationY + THREE.MathUtils.degToRad(15) }
              : x
          )
        );
      }

      if (e.key === "Delete" || e.key === "Backspace") {
        setInstances((prev) => prev.filter((x) => x.id !== selectedId));
        setSelectedId(null);
      }

      const moveStep = e.shiftKey ? 0.1 : 0.5;

      const move = (dx: number, dz: number) => {
        setInstances((prev) =>
          prev.map((x) =>
            x.id === selectedId
              ? {
                  ...x,
                  position: [x.position[0] + dx, x.position[1], x.position[2] + dz],
                }
              : x
          )
        );
      };

      if (e.key === "ArrowUp") {
        e.preventDefault();
        move(0, -moveStep);
      }
      if (e.key === "ArrowDown") {
        e.preventDefault();
        move(0, moveStep);
      }
      if (e.key === "ArrowLeft") {
        e.preventDefault();
        move(-moveStep, 0);
      }
      if (e.key === "ArrowRight") {
        e.preventDefault();
        move(moveStep, 0);
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
    <div style={{ width: "100%", height, position: "relative" }}>
      <div
        style={{
          position: "absolute",
          top: 8,
          left: 8,
          background: "rgba(0,0,0,0.6)",
          color: "white",
          padding: "8px 12px",
          borderRadius: 4,
          fontSize: 12,
          zIndex: 10,
          pointerEvents: "none",
        }}
      >
        <div>
          <b>Controls:</b> Drag to move • R to rotate • Delete to remove
        </div>
        <div>Arrow keys: move (Shift for smaller steps)</div>
      </div>

      <Canvas camera={{ position: [8, 8, 8], fov: 50 }} shadows>
        <ambientLight intensity={0.6} />
        <directionalLight position={[10, 15, 10]} intensity={1.0} castShadow />
        <directionalLight position={[-5, 5, -5]} intensity={0.3} />

        <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow position={[0, -0.01, 0]}>
          <planeGeometry args={[100, 100]} />
          <meshStandardMaterial color="#e8e8e8" />
        </mesh>

        <Grid
          infiniteGrid
          cellSize={1}
          cellThickness={1}
          cellColor="#aaaaaa"
          sectionSize={5}
          sectionThickness={2}
          sectionColor="#666666"
          fadeDistance={50}
          fadeStrength={1}
          position={[0, 0.01, 0]}
        />

        <OrbitControls
          makeDefault
          enabled={!isDragging}
          minPolarAngle={0.1}
          maxPolarAngle={Math.PI / 2 - 0.1}
        />

        <InstancesLayer
          instances={instances}
          setInstances={setInstances}
          selectedId={selectedId}
          setSelectedId={setSelectedId}
          catalogMap={catalogMap}
          setIsDragging={setIsDragging}
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
  setIsDragging: (dragging: boolean) => void;
}) {
  const { instances, setInstances, selectedId, setSelectedId, catalogMap, setIsDragging } = props;

  const { camera, gl } = useThree();

  const plane = useMemo(() => new THREE.Plane(new THREE.Vector3(0, 1, 0), 0), []);
  const raycaster = useMemo(() => new THREE.Raycaster(), []);
  const pointer = useMemo(() => new THREE.Vector2(), []);
  const draggingRef = useRef<{ id: string; offsetX: number; offsetZ: number } | null>(null);

  const getHitOnGround = (e: ThreeEvent<PointerEvent>) => {
    const rect = gl.domElement.getBoundingClientRect();
    const { clientX, clientY } = e.nativeEvent;

    pointer.x = ((clientX - rect.left) / rect.width) * 2 - 1;
    pointer.y = -(((clientY - rect.top) / rect.height) * 2 - 1);

    raycaster.setFromCamera(pointer, camera);

    const hit = new THREE.Vector3();
    raycaster.ray.intersectPlane(plane, hit);
    return hit;
  };

  const onPointerDown = (e: ThreeEvent<PointerEvent>, id: string, inst: Instance) => {
    e.stopPropagation();
    setSelectedId(id);

    const hit = getHitOnGround(e);

    draggingRef.current = {
      id,
      offsetX: inst.position[0] - hit.x,
      offsetZ: inst.position[2] - hit.z,
    };
    setIsDragging(true);
  };

  const onPointerUp = () => {
    draggingRef.current = null;
    setIsDragging(false);
  };

  const onPointerMove = (e: ThreeEvent<PointerEvent>) => {
    if (!draggingRef.current) return;

    const hit = getHitOnGround(e);

    const newX = clamp(hit.x + draggingRef.current.offsetX, -25, 25);
    const newZ = clamp(hit.z + draggingRef.current.offsetZ, -25, 25);

    const id = draggingRef.current.id;
    setInstances((prev) =>
      prev.map((inst) => (inst.id === id ? { ...inst, position: [newX, inst.position[1], newZ] } : inst))
    );
  };

  return (
    <group
      onPointerMove={onPointerMove}
      onPointerUp={onPointerUp}
      onPointerLeave={onPointerUp}
      onPointerMissed={() => setSelectedId(null)}
    >
      {instances.map((inst) => {
        const def = catalogMap.get(inst.definitionId);
        const isSel = inst.id === selectedId;

        const size: [number, number, number] =
          def?.size || DEFAULT_SIZES[inst.definitionId] || [1, 1, 1];

        const color = def?.color || DEFAULT_COLORS[inst.definitionId] || "#90caf9";
        const shape = def?.shape || "box";

        const isWindow = inst.definitionId === "window";

        return (
          <group
            key={inst.id}
            position={inst.position}
            rotation={[0, inst.rotationY, 0]}
            onPointerDown={(e) => onPointerDown(e, inst.id, inst)}
          >
            {isSel && (
              <mesh>
                {shape === "cylinder" && def?.radius && def?.height ? (
                  <cylinderGeometry args={[def.radius + 0.05, def.radius + 0.05, def.height + 0.1, 24]} />
                ) : (
                  <boxGeometry args={[size[0] + 0.1, size[1] + 0.1, size[2] + 0.1]} />
                )}
                <meshBasicMaterial color="#ffd54f" wireframe />
              </mesh>
            )}

            <mesh castShadow receiveShadow>
              {shape === "cylinder" && def?.radius && def?.height ? (
                <cylinderGeometry args={[def.radius, def.radius, def.height, 24]} />
              ) : (
                <boxGeometry args={size} />
              )}
              <meshStandardMaterial
                color={isSel ? "#ffd54f" : color}
                transparent={isWindow}
                opacity={isWindow ? 0.6 : 1}
              />
            </mesh>

            {isSel && (
              <mesh position={[0, size[1] / 2 + 0.3, 0]}>
                <sphereGeometry args={[0.1, 8, 8]} />
                <meshBasicMaterial color="#ff5722" />
              </mesh>
            )}
          </group>
        );
      })}
    </group>
  );
}

// Streamlit expects a default export wrapped with the connection HOC
export default withStreamlitConnection(ThreeBuilderInner);
export { ThreeBuilderInner as ThreeBuilder };
