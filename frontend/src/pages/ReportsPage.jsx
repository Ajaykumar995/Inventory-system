import { useEffect, useState } from 'react';
import { catalogService } from '../services/catalogService';
import { inventoryService } from '../services/inventoryService';
import { saleService } from '../services/saleService';
import { purchaseService } from '../services/purchaseService';
import { MAX_PAGE_SIZE } from '../utils/constants';
import { downloadCsv } from '../utils/csv';
export default function ReportsPage() {
    const [stats, setStats] = useState({ products: 0, stock: 0, sales: 0, suppliers: 0, categories: 0 });
    const [exporting, setExporting] = useState('');
    const [error, setError] = useState('');
    useEffect(() => {
        Promise.all([
            catalogService.listProducts({ page_size: 1 }),
            catalogService.listCategories({ page_size: 1 }),
            inventoryService.listStock({ page_size: 1 }),
            saleService.list({ page_size: 1 }),
            purchaseService.listSuppliers({ page_size: 1 }),
        ]).then(([p, cat, s, sa, sup]) => {
            setStats({
                products: p.data.total,
                categories: cat.data.total,
                stock: s.data.total,
                sales: sa.data.total,
                suppliers: sup.data.total,
            });
        }).catch(() => { });
    }, []);
    const exportProducts = async () => {
        setExporting('products');
        setError('');
        try {
            const { data } = await catalogService.listProducts({ page_size: MAX_PAGE_SIZE });
            downloadCsv('products.csv', data.items.map((p) => ({
                id: p.id, name: p.name, sku: p.sku, barcode: p.barcode ?? '',
                brand: p.brand ?? '', category: p.category?.name, unit: p.unit,
                cost_price: p.cost_price ?? '', selling_price: p.selling_price ?? '', active: p.is_active,
            })));
        }
        catch {
            setError('Export failed');
        }
        finally {
            setExporting('');
        }
    };
    const exportStock = async () => {
        setExporting('stock');
        setError('');
        try {
            const { data } = await inventoryService.listStock({ page_size: MAX_PAGE_SIZE });
            downloadCsv('inventory-stock.csv', data.items.map((i) => ({
                product: i.product.name, sku: i.product.sku, category: i.product.category?.name,
                current_stock: i.current_stock, min_stock: i.min_stock, max_stock: i.max_stock,
                status: i.stock_status, location: i.location ?? '',
            })));
        }
        catch {
            setError('Export failed');
        }
        finally {
            setExporting('');
        }
    };
    const exportSales = async () => {
        setExporting('sales');
        setError('');
        try {
            const { data } = await saleService.list({ page_size: MAX_PAGE_SIZE });
            downloadCsv('sales.csv', data.items.map((s) => ({
                invoice: s.invoice_number, date: s.sale_date, customer: s.customer_name ?? '',
                payment: s.payment_method, subtotal: s.subtotal, tax: s.tax_amount,
                total: s.total_amount, status: s.status,
            })));
        }
        catch {
            setError('Export failed');
        }
        finally {
            setExporting('');
        }
    };
    const exportCategories = async () => {
        setExporting('categories');
        setError('');
        try {
            const { data } = await catalogService.listCategories({ page_size: MAX_PAGE_SIZE });
            downloadCsv('categories.csv', data.items.map((c) => ({
                id: c.id, name: c.name, description: c.description ?? '',
            })));
        }
        catch {
            setError('Export failed');
        }
        finally {
            setExporting('');
        }
    };
    const exportSuppliers = async () => {
        setExporting('suppliers');
        setError('');
        try {
            const { data } = await purchaseService.listSuppliers({ page_size: MAX_PAGE_SIZE });
            downloadCsv('suppliers.csv', data.items.map((s) => ({
                id: s.id, name: s.name, contact: s.contact_person ?? '', phone: s.phone ?? '',
                email: s.email ?? '', rating: s.rating,
            })));
        }
        catch {
            setError('Export failed');
        }
        finally {
            setExporting('');
        }
    };
    const cards = [
        { key: 'products', label: 'Products', count: stats.products, icon: '🏷️', action: exportProducts },
        { key: 'stock', label: 'Stock Levels', count: stats.stock, icon: '📦', action: exportStock },
        { key: 'sales', label: 'Sales History', count: stats.sales, icon: '💳', action: exportSales },
        { key: 'categories', label: 'Categories', count: stats.categories, icon: '📁', action: exportCategories },
        { key: 'suppliers', label: 'Suppliers', count: stats.suppliers, icon: '🏭', action: exportSuppliers },
    ];
    return (<div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-green-400 to-emerald-400 bg-clip-text text-transparent">Reports & Export</h1>
        <p className="text-slate-400 mt-1">Download CSV reports for accounting, audits, and backups</p>
      </div>

      {error && <p className="text-sm text-red-400 bg-red-500/10 rounded-lg px-4 py-2">{error}</p>}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {cards.map((c) => (<div key={c.key} className="glass rounded-2xl border border-white/10 p-5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-2xl">{c.icon}</span>
              <span className="text-2xl font-bold text-white">{c.count}</span>
            </div>
            <h3 className="font-semibold text-white">{c.label}</h3>
            <button onClick={c.action} disabled={exporting === c.key} className="w-full py-2 rounded-xl bg-emerald-600/80 hover:bg-emerald-500 text-white text-sm disabled:opacity-50 transition">
              {exporting === c.key ? 'Exporting…' : 'Download CSV'}
            </button>
          </div>))}
      </div>
    </div>);
}
