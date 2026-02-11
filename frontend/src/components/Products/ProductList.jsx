import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, Filter, Upload, Package } from 'lucide-react';
import { fetchProducts, fetchProductTypes } from '../../services/api';
import DataTable from '../Common/DataTable';
import StatusBadge from '../Common/StatusBadge';
import LoadingSpinner from '../Common/LoadingSpinner';

const TYPE_LABELS = {
  property: 'Woning',
  life: 'Leven',
  health: 'Zorg',
  auto: 'Auto',
  liability: 'Aansprakelijkheid',
  travel: 'Reis',
};

export default function ProductList() {
  const [products, setProducts] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [types, setTypes] = useState([]);
  const [filters, setFilters] = useState({
    search: '',
    type: '',
    page: 1,
    per_page: 15,
    sort: 'name',
    order: 'asc',
  });

  useEffect(() => {
    fetchProductTypes().then(setTypes).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    fetchProducts(filters)
      .then((data) => {
        setProducts(data.items);
        setTotal(data.total);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [filters]);

  const columns = [
    { key: 'product_code', label: 'Code', sortable: true, width: '130px' },
    { key: 'name', label: 'Product Naam', sortable: true },
    { key: 'insurer_name', label: 'Verzekeraar', sortable: false },
    {
      key: 'product_type', label: 'Type', sortable: true, width: '120px',
      render: (val) => (
        <span className="px-2 py-0.5 rounded bg-primary-50 text-primary-700 text-xs font-medium">
          {TYPE_LABELS[val] || val}
        </span>
      ),
    },
    {
      key: 'base_premium', label: 'Basispremie', sortable: true, width: '120px',
      render: (val) => `\u20AC${val?.toFixed(2) || '0.00'}`,
    },
    {
      key: 'coverage_amount', label: 'Dekking', sortable: true, width: '130px',
      render: (val) => val ? `\u20AC${val.toLocaleString('nl-NL')}` : '-',
    },
    {
      key: 'deductible', label: 'Eigen Risico', width: '100px',
      render: (val) => val ? `\u20AC${val.toFixed(2)}` : '\u20AC0.00',
    },
    {
      key: 'status', label: 'Status', width: '100px',
      render: (val) => <StatusBadge status={val} />,
    },
    {
      key: 'policy_count', label: 'Polissen', width: '80px',
      render: (val) => <span className="font-medium">{val}</span>,
    },
  ];

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Productcatalogus</h1>
          <p className="text-gray-500 text-sm">{total} producten van alle verzekeraars</p>
        </div>
        <Link
          to="/products/import"
          className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors text-sm"
        >
          <Upload size={16} />
          Importeren
        </Link>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6 flex flex-wrap gap-4 items-center">
        <div className="flex-1 min-w-[200px] relative">
          <Search size={16} className="absolute left-3 top-2.5 text-gray-400" />
          <input
            type="text"
            placeholder="Zoek producten..."
            value={filters.search}
            onChange={(e) => setFilters({ ...filters, search: e.target.value, page: 1 })}
            className="w-full pl-9 pr-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-300 focus:border-primary-300"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter size={16} className="text-gray-400" />
          <select
            value={filters.type}
            onChange={(e) => setFilters({ ...filters, type: e.target.value, page: 1 })}
            className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-300"
          >
            <option value="">Alle types</option>
            {types.map((t) => (
              <option key={t} value={t}>{TYPE_LABELS[t] || t}</option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <LoadingSpinner />
      ) : (
        <DataTable
          columns={columns}
          data={products}
          totalItems={total}
          page={filters.page}
          perPage={filters.per_page}
          sortBy={filters.sort}
          sortOrder={filters.order}
          onPageChange={(page) => setFilters({ ...filters, page })}
          onSort={(key) =>
            setFilters({
              ...filters,
              sort: key,
              order: filters.sort === key && filters.order === 'asc' ? 'desc' : 'asc',
            })
          }
          emptyMessage="Geen producten gevonden"
        />
      )}
    </div>
  );
}
