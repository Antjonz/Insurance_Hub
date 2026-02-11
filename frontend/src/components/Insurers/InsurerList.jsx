import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Building2, RefreshCw, Wifi, WifiOff, Clock, ArrowRight } from 'lucide-react';
import { fetchInsurers, triggerSync } from '../../services/api';
import LoadingSpinner from '../Common/LoadingSpinner';
import StatusBadge from '../Common/StatusBadge';
import toast from 'react-hot-toast';

export default function InsurerList() {
  const [insurers, setInsurers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState({});

  useEffect(() => {
    loadInsurers();
  }, []);

  const loadInsurers = () => {
    fetchInsurers()
      .then(setInsurers)
      .catch(() => toast.error('Kan verzekeraars niet laden'))
      .finally(() => setLoading(false));
  };

  const handleSync = async (insurerId, name) => {
    setSyncing((prev) => ({ ...prev, [insurerId]: true }));
    try {
      const result = await triggerSync(insurerId);
      toast.success(`Synchronisatie ${name} voltooid`);
      loadInsurers();
    } catch {
      toast.error(`Synchronisatie ${name} mislukt`);
    } finally {
      setSyncing((prev) => ({ ...prev, [insurerId]: false }));
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Verzekeraars</h1>
          <p className="text-gray-500 text-sm">Beheer verbonden verzekeringsmaatschappijen</p>
        </div>
        <Link
          to="/insurers/sync"
          className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors text-sm"
        >
          <RefreshCw size={16} />
          Sync Monitor
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {insurers.map((insurer) => (
          <div key={insurer.id} className="bg-white rounded-lg shadow hover:shadow-md transition-shadow">
            <div className="p-6">
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${
                    insurer.api_status === 'active' ? 'bg-green-100' :
                    insurer.api_status === 'error' ? 'bg-red-100' : 'bg-gray-100'
                  }`}>
                    {insurer.api_status === 'active' ? (
                      <Wifi size={20} className="text-green-600" />
                    ) : (
                      <WifiOff size={20} className="text-red-500" />
                    )}
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-800">{insurer.name}</h3>
                    <p className="text-xs text-gray-400">{insurer.code}</p>
                  </div>
                </div>
                <StatusBadge status={insurer.api_status} />
              </div>

              {/* Details */}
              <div className="space-y-2 text-sm text-gray-600 mb-4">
                <div className="flex justify-between">
                  <span>Producten</span>
                  <span className="font-medium">{insurer.product_count}</span>
                </div>
                <div className="flex justify-between">
                  <span>API formaat</span>
                  <span className="font-medium uppercase">{insurer.api_format}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-1">
                    <Clock size={14} />
                    Laatste sync
                  </span>
                  <span className="font-medium">
                    {insurer.last_sync
                      ? new Date(insurer.last_sync).toLocaleString('nl-NL', {
                          day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit'
                        })
                      : 'Nooit'}
                  </span>
                </div>
                {insurer.last_sync_status && (
                  <div className="flex justify-between">
                    <span>Sync status</span>
                    <StatusBadge status={insurer.last_sync_status} />
                  </div>
                )}
              </div>

              {/* Contact */}
              <div className="text-xs text-gray-400 border-t border-gray-100 pt-3 mb-4">
                <p>{insurer.contact_email}</p>
                <p>{insurer.contact_phone}</p>
              </div>

              {/* Actions */}
              <button
                onClick={() => handleSync(insurer.id, insurer.name)}
                disabled={syncing[insurer.id]}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-primary-50 text-primary-600 rounded-lg hover:bg-primary-100 transition-colors text-sm font-medium disabled:opacity-50"
              >
                <RefreshCw size={14} className={syncing[insurer.id] ? 'animate-spin' : ''} />
                {syncing[insurer.id] ? 'Synchroniseren...' : 'Sync Starten'}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
