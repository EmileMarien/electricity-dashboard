import React, { useEffect, useMemo, useRef, useState } from "react";
import {
  Streamlit,
  ComponentProps,
  withStreamlitConnection,
} from "streamlit-component-lib";
import { Canvas, ThreeEvent, useThree } from "@react-three/fiber";
import { OrbitControls, Grid, Line } from "@react-three/drei";
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
  emoji?: string;
  description?: string;
};

type Command = {
  token: number;
  type: "insert" | "delete" | "clear";
  definitionId: string | null;
  floor?: number; // floor level to place the component on
};

type Instance = {
  id: string;
  definitionId: string;
  position: [number, number, number];
  rotationY: number; // radians
  floor: number; // floor level (0 = ground, 1 = first floor, etc.)
};

type SceneState = {
  instances: Instance[];
  selectedId: string | null;
  lastChange?: { type: string; instanceId?: string; timestamp: number };
};

type GridSize = [number, number] | null; // [width, depth] in meters

function uuid() {
  return crypto.randomUUID
    ? crypto.randomUUID()
    : `id_${Math.random().toString(16).slice(2)}`;
}

function clamp(n: number, a: number, b: number) {
  return Math.max(a, Math.min(b, n));
}

// Grid module size (60cm)
const GRID_MODULE = 0.6;

// Snap threshold for component-to-component snapping
const SNAP_THRESHOLD = 0.3;

// Snap a value to the nearest grid line
function snapToGrid(value: number): number {
  return Math.round(value / GRID_MODULE) * GRID_MODULE;
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

// Standard floor height in meters
const FLOOR_HEIGHT = 2.8;

function ThreeBuilderInner(props: ComponentProps) {
  const catalog: CatalogItem[] = props.args["catalog"] ?? [];
  const command: Command =
    props.args["command"] ?? { token: 0, type: "insert", definitionId: null };
  const initialInstances: Instance[] = props.args["initialInstances"] ?? [];
  const projectId: string | null = props.args["projectId"] ?? null;
  const height: number = props.args["height"] ?? 640;
  const gridSize: GridSize = props.args["gridSize"] ?? null;
  const activeFloor: number | null = props.args["activeFloor"] ?? null; // null = show all floors
  const totalFloors: number = props.args["totalFloors"] ?? 1;

  const [instances, setInstances] = useState<Instance[]>(initialInstances);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const lastTokenRef = useRef<number>(-1);
  const readyRef = useRef(false);
  const lastProjectIdRef = useRef<string | null>(null);

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
    // Only run once on mount - do NOT include initialInstances in deps
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Reset when project changes (only when projectId actually changes)
  useEffect(() => {
    if (projectId !== null && projectId !== lastProjectIdRef.current) {
      lastProjectIdRef.current = projectId;
      setInstances(initialInstances);
      setSelectedId(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId]);

  // Emit state back to Streamlit (debounced to prevent excessive updates)
  const emitRef = useRef<number | null>(null);
  const lastEmittedRef = useRef<string>("");
  
  const emitState = (next: SceneState) => {
    // Serialize state to compare - only emit if actually changed
    const serialized = JSON.stringify({ instances: next.instances, selectedId: next.selectedId });
    if (serialized === lastEmittedRef.current) return;
    
    if (emitRef.current) cancelAnimationFrame(emitRef.current);
    emitRef.current = requestAnimationFrame(() => {
      lastEmittedRef.current = serialized;
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
      
      // Determine which floor to place on (use command.floor, then activeFloor, then 0)
      const targetFloor = command.floor ?? (activeFloor !== null ? activeFloor : 0);
      // Calculate base Y position for this floor
      const floorBaseY = targetFloor * FLOOR_HEIGHT;

      const i: Instance = {
        id: uuid(),
        definitionId: defId,
        position: [0, floorBaseY + size[1] / 2, 0],
        rotationY: 0,
        floor: targetFloor,
      };

      setInstances((prev) => [...prev, i]);
      setSelectedId(i.id);
    }
  }, [command, catalog, selectedId, activeFloor]);

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

      const moveStep = e.shiftKey ? 0.1 : 0.6;

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

  // Building footprint outline points
  const footprintPoints = useMemo(() => {
    if (!gridSize) return null;
    const [width, depth] = gridSize;
    const halfW = width / 2;
    const halfD = depth / 2;
    // Create a closed rectangle at ground level
    return [
      new THREE.Vector3(-halfW, 0.02, -halfD),
      new THREE.Vector3(halfW, 0.02, -halfD),
      new THREE.Vector3(halfW, 0.02, halfD),
      new THREE.Vector3(-halfW, 0.02, halfD),
      new THREE.Vector3(-halfW, 0.02, -halfD), // Close the loop
    ];
  }, [gridSize]);

  // Grid lines for the building footprint
  const footprintGridLines = useMemo(() => {
    if (!gridSize) return [];
    const [width, depth] = gridSize;
    const halfW = width / 2;
    const halfD = depth / 2;
    const lines: THREE.Vector3[][] = [];
    const gridStep = GRID_MODULE; // 60cm grid

    // Vertical lines (along Z axis)
    for (let x = -halfW; x <= halfW + 0.01; x += gridStep) {
      lines.push([
        new THREE.Vector3(x, 0.015, -halfD),
        new THREE.Vector3(x, 0.015, halfD),
      ]);
    }
    // Horizontal lines (along X axis)
    for (let z = -halfD; z <= halfD + 0.01; z += gridStep) {
      lines.push([
        new THREE.Vector3(-halfW, 0.015, z),
        new THREE.Vector3(halfW, 0.015, z),
      ]);
    }
    return lines;
  }, [gridSize]);

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

        {/* Building footprint area - filled */}
        {gridSize && (
          <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.005, 0]}>
            <planeGeometry args={gridSize} />
            <meshStandardMaterial color="#d4edda" transparent opacity={0.4} />
          </mesh>
        )}

        {/* Building footprint grid lines */}
        {footprintGridLines.map((points, i) => (
          <Line
            key={`grid-line-${i}`}
            points={points}
            color="#90caf9"
            lineWidth={1}
            transparent
            opacity={0.5}
          />
        ))}

        {/* Building footprint outline */}
        {footprintPoints && (
          <Line
            points={footprintPoints}
            color="#2e7d32"
            lineWidth={3}
          />
        )}

        {/* Floor level indicators */}
        {Array.from({ length: totalFloors }, (_, floorNum) => (
          <group key={`floor-indicator-${floorNum}`}>
            {/* Floor plane indicator (semi-transparent) */}
            {floorNum > 0 && (
              <mesh
                rotation={[-Math.PI / 2, 0, 0]}
                position={[0, floorNum * FLOOR_HEIGHT + 0.01, 0]}
              >
                <planeGeometry args={[gridSize ? gridSize[0] : 20, gridSize ? gridSize[1] : 20]} />
                <meshStandardMaterial
                  color={activeFloor === floorNum ? "#bbdefb" : "#e3f2fd"}
                  transparent
                  opacity={activeFloor === null || activeFloor === floorNum ? 0.3 : 0.1}
                />
              </mesh>
            )}
            {/* Floor label */}
            {gridSize && (
              <mesh position={[-(gridSize[0] / 2) - 0.5, floorNum * FLOOR_HEIGHT + 0.1, 0]}>
                <boxGeometry args={[0.8, 0.3, 0.05]} />
                <meshStandardMaterial color={activeFloor === floorNum ? "#1976d2" : "#90a4ae"} />
              </mesh>
            )}
          </group>
        ))}

        <Grid
          infiniteGrid
          cellSize={0.6}
          cellThickness={1}
          cellColor="#cccccc"
          sectionSize={3}
          sectionThickness={2}
          sectionColor="#888888"
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
          activeFloor={activeFloor}
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
  activeFloor: number | null;
}) {
  const { instances, setInstances, selectedId, setSelectedId, catalogMap, setIsDragging, activeFloor } = props;

  const { camera, gl } = useThree();

  // Dynamic plane height based on active floor
  const planeHeight = activeFloor !== null ? activeFloor * FLOOR_HEIGHT : 0;
  const plane = useMemo(() => new THREE.Plane(new THREE.Vector3(0, 1, 0), -planeHeight), [planeHeight]);
  const raycaster = useMemo(() => new THREE.Raycaster(), []);
  const pointer = useMemo(() => new THREE.Vector2(), []);
  const draggingRef = useRef<{ id: string; offsetX: number; offsetZ: number; startY: number } | null>(null);

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
      startY: inst.position[1],
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
    const id = draggingRef.current.id;

    // Raw position from drag
    let newX = clamp(hit.x + draggingRef.current.offsetX, -25, 25);
    let newZ = clamp(hit.z + draggingRef.current.offsetZ, -25, 25);

    // Snap to grid first
    newX = snapToGrid(newX);
    newZ = snapToGrid(newZ);

    // Get the dragged instance's size for edge snapping
    const draggedInst = instances.find((i) => i.id === id);
    const draggedDef = draggedInst ? catalogMap.get(draggedInst.definitionId) : null;
    const draggedSize = draggedDef?.size || DEFAULT_SIZES[draggedInst?.definitionId || ""] || [1, 1, 1];
    const draggedHalfW = draggedSize[0] / 2;
    const draggedHalfD = draggedSize[2] / 2;

    // Try to snap to other components (edge-to-edge)
    for (const other of instances) {
      if (other.id === id) continue;

      const otherDef = catalogMap.get(other.definitionId);
      const otherSize = otherDef?.size || DEFAULT_SIZES[other.definitionId] || [1, 1, 1];
      const otherHalfW = otherSize[0] / 2;
      const otherHalfD = otherSize[2] / 2;

      const ox = other.position[0];
      const oz = other.position[2];

      // Check X-axis edge snapping (left/right edges)
      const leftEdge = ox - otherHalfW;
      const rightEdge = ox + otherHalfW;
      const myLeftEdge = newX - draggedHalfW;
      const myRightEdge = newX + draggedHalfW;

      // Snap my right edge to other's left edge
      if (Math.abs(myRightEdge - leftEdge) < SNAP_THRESHOLD) {
        newX = leftEdge - draggedHalfW;
      }
      // Snap my left edge to other's right edge
      else if (Math.abs(myLeftEdge - rightEdge) < SNAP_THRESHOLD) {
        newX = rightEdge + draggedHalfW;
      }

      // Check Z-axis edge snapping (front/back edges)
      const frontEdge = oz - otherHalfD;
      const backEdge = oz + otherHalfD;
      const myFrontEdge = newZ - draggedHalfD;
      const myBackEdge = newZ + draggedHalfD;

      // Snap my back edge to other's front edge
      if (Math.abs(myBackEdge - frontEdge) < SNAP_THRESHOLD) {
        newZ = frontEdge - draggedHalfD;
      }
      // Snap my front edge to other's back edge
      else if (Math.abs(myFrontEdge - backEdge) < SNAP_THRESHOLD) {
        newZ = backEdge + draggedHalfD;
      }
    }

    setInstances((prev) =>
      prev.map((inst) => (inst.id === id ? { ...inst, position: [newX, inst.position[1], newZ] } : inst))
    );
  };

  // Filter instances by floor if activeFloor is set
  const visibleInstances = activeFloor !== null
    ? instances.filter((inst) => inst.floor === activeFloor)
    : instances;
  
  // Get instances on other floors for ghost rendering
  const ghostInstances = activeFloor !== null
    ? instances.filter((inst) => inst.floor !== activeFloor)
    : [];

  return (
    <group
      onPointerMove={onPointerMove}
      onPointerUp={onPointerUp}
      onPointerLeave={onPointerUp}
      onPointerMissed={() => setSelectedId(null)}
    >
      {/* Ghost instances (other floors) - shown semi-transparent */}
      {ghostInstances.map((inst) => {
        const def = catalogMap.get(inst.definitionId);
        const size: [number, number, number] =
          def?.size || DEFAULT_SIZES[inst.definitionId] || [1, 1, 1];
        const shape = def?.shape || "box";

        return (
          <group
            key={`ghost-${inst.id}`}
            position={inst.position}
            rotation={[0, inst.rotationY, 0]}
          >
            <mesh>
              {shape === "cylinder" && def?.radius && def?.height ? (
                <cylinderGeometry args={[def.radius, def.radius, def.height, 24]} />
              ) : (
                <boxGeometry args={size} />
              )}
              <meshStandardMaterial
                color="#b0bec5"
                transparent
                opacity={0.2}
              />
            </mesh>
          </group>
        );
      })}

      {/* Active floor instances */}
      {visibleInstances.map((inst) => {
        const def = catalogMap.get(inst.definitionId);
        const isSel = inst.id === selectedId;

        const size: [number, number, number] =
          def?.size || DEFAULT_SIZES[inst.definitionId] || [1, 1, 1];

        const color = def?.color || DEFAULT_COLORS[inst.definitionId] || "#90caf9";
        const shape = def?.shape || "box";

        const isWindow = inst.definitionId?.includes("window");

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
