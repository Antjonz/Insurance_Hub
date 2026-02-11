import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, PlusCircle } from 'lucide-react';
import { fetchPolicies } from '../../services/api';
import DataTable from '../Common/DataTable';
import StatusBadge from '../Common/StatusBadge';
import LoadingSpinner from '../Common/LoadingSpinner';

export default function PolicyList() {
  const [policies, setPolicies] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    search: '',
    status: '',
    page: 1,
    per_page: 15,
    sort: 'created_at',
    order: 'desc',
  });

  useEffect(() => {
    setLoading(true);
    fetchPolicies(filters)
      .then((data) => {
        setPolicies(data.items);
        setTotal(data.total);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [filters]);

  const columns = [
    { key: 'policy_number', label: 'Polis Nr.', sortable: true, width: '140px' },
    { key: 'customer_name', label: 'Klant', sortable: true },
    { key: 'product_name', label: 'Product', sortable: false },
    { key: 'insurer_name', label: 'Verzekeraar', sortable: false },
    {
      key: 'premium_amount', label: 'Premie', sortable: true, width: '100px',
      render: (val) => `\u20AC${val?.toFixed(2) || '0.00'}`,
    },
    {
      key: 'payment_freq', label: 'Frequentie', width: '100px',
      render: (val) => {
        const labels = { monthly: 'Maandelijks', quarterly: 'Kwartaal', yearly: 'Jaarlijks' };
        return labels[val] || val;
      },
    },
    {
      key: 'start_date', label: 'Startdatum', sortable: true, width: '110px',
      render: (val) => val ? new Date(val).toLocaleDateString('nl-NL') : '-',
    },
    {
      key: 'end_date', label: 'Einddatum', width: '110px',
      render: (val) => val ? new Date(val).toLocaleDateString('nl-NL') : 'Doorlopend',
    },
    {
      key: 'status', label: 'Status', width: '100px',
      render: (val) => <StatusBadge status={val} />,
    },
    {
      key: 'claims_count', label: 'Claims', width: '70px',
      render: (val) => val > 0 ? (
        <span className="px-2 py-0.5 rounded-full bg-amber-100 text-amber-700 text-xs font-medium">{val}</span>
      ) : <span className="text-gray-400">0</span>,
    },
  ];

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Polissen</h1>
          <p className="text-gray-500 text-sm">{total} polissen in het systeem</p>
        </div>
        <Link
          to="/policies/new"
          className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors text-sm"
        >
          <PlusCircle size={16} />
          Nieuwe Polis
        </Link>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6 flex flex-wrap gap-4 items-center">
        <div className="flex-1 min-w-[200px] relative">
          <Search size={16} className="absolute left-3 top-2.5 text-gray-400" />
          <input
            type="text"
            placeholder="Zoek op klant of polisnummer..."
            value={filters.search}
            onChange={(e) => setFilters({ ...filters, search: e.target.value, page: 1 })}
            className="w-full pl-9 pr-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-300"
          />
        </div>
        <select
          value={filters.status}
          onChange={(e) => setFilters({ ...filters, status: e.target.value, page: 1 })}
          className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-300"
        >
          <option value="">Alle statussen</option>
          <option value="active">Actief</option>
          <option value="expired">Verlopen</option>
          <option value="cancelled">Geannuleerd</option>
          <option value="pending">In afwachting</option>
        </select>
      </div>

      {loading ? (
        <LoadingSpinner />
      ) : (
        <DataTable
          columns={columns}
          data={policies}
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
          emptyMessage="Geen polissen gevonden"
        />
      )}
    </div>
  );
}
