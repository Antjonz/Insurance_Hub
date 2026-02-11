import React, { useState, useEffect } from 'react';
import { RefreshCw, CheckCircle, XCircle, AlertCircle, Clock, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import { fetchSyncStatus, triggerSync } from '../../services/api';
import LoadingSpinner from '../Common/LoadingSpinner';
import toast from 'react-hot-toast';

const HEALTH_CONFIG = {
  green: { icon: CheckCircle, color: 'text-green-500', bg: 'bg-green-100', label: 'Gezond' },
  yellow: { icon: AlertCircle, color: 'text-yellow-500', bg: 'bg-yellow-100', label: 'Waarschuwing' },
  red: { icon: XCircle, color: 'text-red-500', bg: 'bg-red-100', label: 'Fout' },
};

export default function SyncMonitor() {
  const [statusData, setStatusData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState({});

  useEffect(() => {
    loadStatus();
    const interval = setInterval(loadStatus, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const loadStatus = () => {
    fetchSyncStatus()
      .then(setStatusData)
      .catch(() => toast.error('Kan sync status niet laden'))
      .finally(() => setLoading(false));
  };

  const handleSync = async (id, name) => {
    setSyncing((prev) => ({ ...prev, [id]: true }));
    try {
      await triggerSync(id);
      toast.success(`${name} gesynchroniseerd`);
      loadStatus();
    } catch {
      toast.error(`Sync mislukt voor ${name}`);
      loadStatus();
    } finally {
      setSyncing((prev) => ({ ...prev, [id]: false }));
    }
  };

  if (loading) return <LoadingSpinner message="Sync status laden..." />;

  return (
    <div className="p-8">
      <div className="flex items-center gap-4 mb-8">
        <Link to="/insurers" className="text-gray-400 hover:text-gray-600">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Sync Monitor</h1>
          <p className="text-gray-500 text-sm">Real-time synchronisatie status van alle verzekeraars</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full">
          <thead className="bg-primary-700">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-white uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-white uppercase">Verzekeraar</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-white uppercase">API Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-white uppercase">Formaat</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-white uppercase">Laatste Sync</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-white uppercase">Records</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-white uppercase">Duur</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-white uppercase">Fouten (24u)</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-white uppercase">Actie</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {statusData.map((item) => {
              const health = HEALTH_CONFIG[item.health] || HEALTH_CONFIG.green;
              const HealthIcon = health.icon;

              return (
                <tr key={item.insurer_id} className="hover:bg-blue-50">
                  <td className="px-6 py-4">
                    <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium ${health.bg}`}>
                      <HealthIcon size={14} className={health.color} />
                      <span className={health.color}>{health.label}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div>
                      <p className="font-medium text-gray-800">{item.insurer_name}</p>
                      <p className="text-xs text-gray-400">{item.insurer_code}</p>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`capitalize text-sm ${
                      item.api_status === 'active' ? 'text-green-600' : 'text-red-500'
                    }`}>
                      {item.api_status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600 uppercase">{item.api_format}</td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-1 text-sm text-gray-600">
                      <Clock size={14} />
                      {item.last_sync
                        ? new Date(item.last_sync).toLocaleString('nl-NL')
                        : 'Nooit'}
                    </div>
                    {item.last_sync_status && (
                      <span className={`text-xs ${
                        item.last_sync_status === 'success' ? 'text-green-500' : 'text-red-500'
                      }`}>
                        {item.last_sync_status}
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">{item.last_sync_records || '-'}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {item.last_sync_duration_ms ? `${item.last_sync_duration_ms}ms` : '-'}
                  </td>
                  <td className="px-6 py-4">
                    {item.recent_failures > 0 ? (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700">
                        <XCircle size={12} />
                        {item.recent_failures}
                      </span>
                    ) : (
                      <span className="text-sm text-green-500">0</span>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <button
                      onClick={() => handleSync(item.insurer_id, item.insurer_name)}
                      disabled={syncing[item.insurer_id]}
                      className="flex items-center gap-1 px-3 py-1.5 bg-primary-50 text-primary-600 rounded hover:bg-primary-100 text-xs font-medium disabled:opacity-50"
                    >
                      <RefreshCw size={12} className={syncing[item.insurer_id] ? 'animate-spin' : ''} />
                      Sync
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Error details */}
      {statusData.some((s) => s.last_sync_errors) && (
        <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-red-800 mb-2">Recente Fouten</h3>
          {statusData
            .filter((s) => s.last_sync_errors)
            .map((s) => (
              <div key={s.insurer_id} className="text-sm text-red-600 py-1">
                <span className="font-medium">{s.insurer_name}:</span> {s.last_sync_errors}
              </div>
            ))}
        </div>
      )}
    </div>
  );
}
