import { Suspense } from 'react'
import WarehouseScene from './WarehouseScene'
import type { WarehouseItem } from '../types/inventory'

export default function WarehouseSceneWrapper({ items }: { items: WarehouseItem[] }) {
  return (
    <Suspense fallback={
      <div className="w-full h-full flex items-center justify-center bg-slate-900/50 rounded-2xl">
        <div className="text-slate-400 animate-pulse">Loading 3D Warehouse...</div>
      </div>
    }>
      <WarehouseScene items={items} />
    </Suspense>
  )
}
