import { Suspense } from 'react';
import WarehouseScene from './WarehouseScene';
export default function WarehouseSceneWrapper({ items }) {
    return (<Suspense fallback={<div className="w-full h-full flex items-center justify-center bg-slate-900/50 rounded-2xl">
        <div className="text-slate-400 animate-pulse">Loading 3D Warehouse...</div>
      </div>}>
      <WarehouseScene items={items}/>
    </Suspense>);
}
