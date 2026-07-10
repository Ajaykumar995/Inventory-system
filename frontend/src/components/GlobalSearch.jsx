import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { searchService } from '../services/searchService';
const typeIcon = {
    product: '🏷️',
    category: '📁',
    supplier: '🏭',
};
export default function GlobalSearch() {
    const [q, setQ] = useState('');
    const [results, setResults] = useState([]);
    const [open, setOpen] = useState(false);
    const ref = useRef(null);
    const navigate = useNavigate();
    useEffect(() => {
        if (q.trim().length < 2) {
            setResults([]);
            return;
        }
        const t = setTimeout(() => {
            searchService.search(q.trim())
                .then((r) => { setResults(r.data.results); setOpen(true); })
                .catch(() => setResults([]));
        }, 300);
        return () => clearTimeout(t);
    }, [q]);
    useEffect(() => {
        const handler = (e) => {
            if (ref.current && !ref.current.contains(e.target))
                setOpen(false);
        };
        document.addEventListener('mousedown', handler);
        return () => document.removeEventListener('mousedown', handler);
    }, []);
    const pick = (hit) => {
        setOpen(false);
        setQ('');
        navigate(hit.path);
    };
    return (<div ref={ref} className="relative w-full max-w-md">
      <input className="w-full px-4 py-2 rounded-xl glass border border-white/10 text-sm text-white placeholder-slate-500" placeholder="Search products, categories, suppliers..." value={q} onChange={(e) => setQ(e.target.value)} onFocus={() => results.length > 0 && setOpen(true)}/>
      {open && results.length > 0 && (<div className="absolute top-full mt-2 w-full glass rounded-xl border border-white/10 shadow-2xl z-50 overflow-hidden">
          {results.map((hit) => (<button key={`${hit.type}-${hit.id}`} onClick={() => pick(hit)} className="w-full px-4 py-3 flex items-center gap-3 text-left hover:bg-white/10 transition">
              <span>{typeIcon[hit.type] ?? '🔍'}</span>
              <div>
                <div className="text-sm text-white">{hit.label}</div>
                {hit.sublabel && <div className="text-xs text-slate-400">{hit.sublabel}</div>}
              </div>
              <span className="ml-auto text-[10px] text-slate-500 uppercase">{hit.type}</span>
            </button>))}
        </div>)}
    </div>);
}
