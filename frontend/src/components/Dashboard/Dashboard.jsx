import React, { useState, useEffect } from 'react';
import {
  PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, BarChart, Bar,
} from 'recharts';
import { FileText, AlertTriangle, Euro, Building2, TrendingUp, Activity } from 'lucide-react';
import { fetchDashboardStats } from '../../services/api';
import LoadingSpinner from '../Common/LoadingSpinner';
import StatusBadge from '../Common/StatusBadge';

const CHART_COLORS = ['#1B4F72', '#2E86C1', '#5DADE2', '#85C1E9', '#AED6F1', '#D6EAF8'];

function KpiCard({ title, value, icon: Icon, color, subtitle }) {
  return (
    <div className="bg-white rounded-lg shadow p-6 flex items-start gap-4">
      <div className={`p-3 rounded-lg ${color}`}>
        <Icon size={24} className="text-white" />
      </div>
      <div>
        <p className="text-sm text-gray-500">{title}</p>
        <p className="text-2xl font-bold text-gray-800">{value}</p>
        {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardStats()
      .then(setStats)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner message="Dashboard laden..." />;

  if (error) {
    return (
      <div className="p-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <AlertTriangle className="mx-auto mb-2 text-red-400" size={32} />
          <p className="text-red-600">Kan dashboard niet laden: {error}</p>
          <p className="text-sm text-red-400 mt-2">
            Controleer of de backend API draait op http://localhost:5000
          </p>
        </div>
      </div>
    );
  }

  const { kpis, policies_by_insurer, premium_trends, policies_by_type, claims_by_status, recent_activity } = stats;

  return (
    <div className="p-8">
      {/* Page header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>
        <p className="text-gray-500 text-sm">Overzicht van het InsuranceHub platform</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <KpiCard
          title="Actieve Polissen"
          value={kpis.total_policies}
          icon={FileText}
          color="bg-primary-500"
          subtitle="Totaal actieve polissen"
        />
        <KpiCard
          title="Openstaande Claims"
          value={kpis.active_claims}
          icon={AlertTriangle}
          color="bg-amber-500"
          subtitle="In behandeling / ingediend"
        />
        <KpiCard
          title="Maandelijkse Premie"
          value={`\u20AC${kpis.monthly_premium.toLocaleString('nl-NL', { minimumFractionDigits: 2 })}`}
          icon={Euro}
          color="bg-green-500"
          subtitle="Totale maandpremie"
        />
        <KpiCard
          title="Verzekeraars"
          value={`${kpis.connected_insurers}/${kpis.total_insurers}`}
          icon={Building2}
          color="bg-primary-700"
          subtitle="Verbonden / totaal"
        />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Policies by Insurer - Pie Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <Building2 size={18} className="text-primary-500" />
            Polissen per Verzekeraar
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={policies_by_insurer}
                cx="50%"
                cy="50%"
                outerRadius={100}
                dataKey="value"
                nameKey="name"
                label={({ name, value }) => `${name}: ${value}`}
              >
                {policies_by_insurer.map((_, idx) => (
                  <Cell key={idx} fill={CHART_COLORS[idx % CHART_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => [`${value} polissen`, 'Aantal']} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Premium Trends - Line Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <TrendingUp size={18} className="text-primary-500" />
            Premie Trend (12 maanden)
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={premium_trends}>
              <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
              <XAxis dataKey="month" tick={{ fontSize: 11 }} />
              <YAxis
                tick={{ fontSize: 11 }}
                tickFormatter={(v) => `\u20AC${v}`}
              />
              <Tooltip
                formatter={(value) => [`\u20AC${value.toFixed(2)}`, 'Premie']}
              />
              <Line
                type="monotone"
                dataKey="premium"
                stroke="#2E86C1"
                strokeWidth={2}
                dot={{ fill: '#1B4F72', r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Bottom row: Product types + Recent activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Policies by Type - Bar Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Polissen per Producttype</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={policies_by_type}>
              <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
              <XAxis dataKey="type" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="count" fill="#2E86C1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <Activity size={18} className="text-primary-500" />
            Recente Activiteit
          </h3>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {recent_activity.map((item, idx) => (
              <div key={idx} className="flex items-start gap-3 py-2 border-b border-gray-50 last:border-0">
                <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${
                  item.type === 'sync' ? 'bg-blue-400' : 'bg-amber-400'
                }`} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium text-gray-700 truncate">{item.message}</p>
                    <StatusBadge status={item.status} />
                  </div>
                  <p className="text-xs text-gray-400 truncate">{item.detail}</p>
                </div>
                <span className="text-xs text-gray-400 flex-shrink-0">
                  {item.timestamp ? new Date(item.timestamp).toLocaleDateString('nl-NL') : ''}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
