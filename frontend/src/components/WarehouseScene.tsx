import { useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Grid, Text, Float, Environment } from '@react-three/drei'
import * as THREE from 'three'
import type { WarehouseItem } from '../types/inventory'

const STATUS_COLORS: Record<string, string> = {
  healthy: '#22c55e',
  low_stock: '#eab308',
  out_of_stock: '#ef4444',
  overstock: '#3b82f6',
}

function StockBox({ item, position }: { item: WarehouseItem; position: [number, number, number] }) {
  const meshRef = useRef<THREE.Mesh>(null)
  const height = Math.max(0.3, Math.min(3, item.stock / Math.max(item.max_stock, 1) * 3))
  const color = STATUS_COLORS[item.status] ?? '#64748b'

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.position.y = height / 2 + Math.sin(state.clock.elapsedTime * 1.5 + position[0]) * 0.02
    }
  })

  return (
    <group position={position}>
      <Float speed={1.5} rotationIntensity={0.1} floatIntensity={0.3}>
        <mesh ref={meshRef} position={[0, height / 2, 0]} castShadow>
          <boxGeometry args={[0.8, height, 0.8]} />
          <meshStandardMaterial color={color} metalness={0.3} roughness={0.4} emissive={color} emissiveIntensity={0.15} />
        </mesh>
      </Float>
      <Text position={[0, height + 0.4, 0]} fontSize={0.18} color="#e2e8f0" anchorX="center" maxWidth={1.2}>
        {item.sku}
      </Text>
      <Text position={[0, -0.15, 0]} fontSize={0.14} color={color} anchorX="center">
        {item.stock}
      </Text>
    </group>
  )
}

function WarehouseFloor() {
  return (
    <>
      <Grid
        position={[0, 0, 0]}
        args={[20, 20]}
        cellSize={0.5}
        cellThickness={0.5}
        cellColor="#1e3a5f"
        sectionSize={2}
        sectionThickness={1}
        sectionColor="#3b82f6"
        fadeDistance={25}
        infiniteGrid
      />
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.01, 0]} receiveShadow>
        <planeGeometry args={[30, 30]} />
        <meshStandardMaterial color="#0f172a" metalness={0.8} roughness={0.2} />
      </mesh>
    </>
  )
}

function ShelvingUnit({ items, offsetX }: { items: WarehouseItem[]; offsetX: number }) {
  return (
    <group position={[offsetX, 0, 0]}>
      {/* Shelf frame */}
      <mesh position={[0, 1.5, 0]}>
        <boxGeometry args={[4.5, 0.05, 1.5]} />
        <meshStandardMaterial color="#334155" metalness={0.6} roughness={0.3} />
      </mesh>
      {items.map((item, i) => (
        <StockBox key={item.product_id} item={item} position={[(i - items.length / 2 + 0.5) * 1.1, 0, 0]} />
      ))}
    </group>
  )
}

function Scene({ items }: { items: WarehouseItem[] }) {
  const rows = useMemo(() => {
    const chunk = 6
    const result: WarehouseItem[][] = []
    const data = items.length ? items : generateDemoItems()
    for (let i = 0; i < data.length; i += chunk) {
      result.push(data.slice(i, i + chunk))
    }
    return result.slice(0, 4)
  }, [items])

  return (
    <>
      <ambientLight intensity={0.3} />
      <directionalLight position={[10, 15, 5]} intensity={1.2} castShadow shadow-mapSize={[1024, 1024]} />
      <pointLight position={[-5, 8, -5]} intensity={0.5} color="#3b82f6" />
      <pointLight position={[5, 8, 5]} intensity={0.3} color="#8b5cf6" />
      <Environment preset="night" />
      <WarehouseFloor />
      {rows.map((row, i) => (
        <ShelvingUnit key={i} items={row} offsetX={(i - rows.length / 2 + 0.5) * 5.5} />
      ))}
      <OrbitControls
        enablePan={false}
        minPolarAngle={Math.PI / 6}
        maxPolarAngle={Math.PI / 2.2}
        minDistance={8}
        maxDistance={20}
        autoRotate
        autoRotateSpeed={0.5}
      />
    </>
  )
}

function generateDemoItems(): WarehouseItem[] {
  const statuses: WarehouseItem['status'][] = ['healthy', 'low_stock', 'out_of_stock', 'overstock']
  return Array.from({ length: 18 }, (_, i) => ({
    product_id: i + 1,
    name: `Product ${i + 1}`,
    sku: `SKU-${String(i + 1).padStart(3, '0')}`,
    stock: [0, 5, 45, 120, 200][i % 5],
    min_stock: 20,
    max_stock: 150,
    status: statuses[i % 4],
  }))
}

export default function WarehouseScene({ items }: { items: WarehouseItem[] }) {
  return (
    <div className="w-full h-full rounded-2xl overflow-hidden">
      <Canvas shadows camera={{ position: [12, 10, 12], fov: 45 }} gl={{ antialias: true, alpha: true }}>
        <fog attach="fog" args={['#0f172a', 15, 35]} />
        <Scene items={items} />
      </Canvas>
    </div>
  )
}
