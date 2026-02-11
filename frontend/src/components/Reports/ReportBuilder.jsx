import React, { useState } from 'react';
import { BarChart3, Download, FileSpreadsheet, Calendar, Loader2 } from 'lucide-react';
import { fetchPremiumReport, fetchClaimsReport, fetchProductsReport, exportReport } from '../../services/api';
import DataTable from '../Common/DataTable';
import LoadingSpinner from '../Common/LoadingSpinner';
import toast from 'react-hot-toast';

const REPORT_TYPES = [
  { value: 'premiums', label: 'Premium Overzicht', description: 'Maandelijkse premie-inkomsten per verzekeraar en producttype' },
  { value: 'claims', label: 'Schade Analyse', description: 'Overzicht van claims, goedkeuringen en afwijzingen' },
  { value: 'products', label: 'Product Prestaties', description: 'Vergelijking van producten: verkopen, omzet en dekking' },
];

const REPORT_COLUMNS = {
  premiums: [
    { key: 'insurer_name', label: 'Verzekeraar', sortable: true },
    { key: 'product_type', label: 'Producttype' },
    { key: 'policy_count', label: 'Polissen', render: (v) => v },
    { key: 'total_premium', label: 'Totale Premie', render: (v) => `\u20AC${v?.toFixed(2)}` },
    { key: 'avg_premium', label: 'Gem. Premie', render: (v) => `\u20AC${v?.toFixed(2)}` },
    { key: 'min_premium', label: 'Min.', render: (v) => `\u20AC${v?.toFixed(2)}` },
    { key: 'max_premium', label: 'Max.', render: (v) => `\u20AC${v?.toFixed(2)}` },
  ],
  claims: [
    { key: 'insurer_name', label: 'Verzekeraar' },
    { key: 'status', label: 'Status' },
    { key: 'category', label: 'Categorie' },
    { key: 'claim_count', label: 'Aantal' },
    { key: 'total_claimed', label: 'Geclaimd', render: (v) => `\u20AC${v?.toFixed(2)}` },
    { key: 'total_approved', label: 'Goedgekeurd', render: (v) => `\u20AC${v?.toFixed(2)}` },
  ],
  products: [
    { key: 'insurer_name', label: 'Verzekeraar' },
    { key: 'product_name', label: 'Product' },
    { key: 'product_type', label: 'Type' },
    { key: 'base_premium', label: 'Basispremie', render: (v) => `\u20AC${v?.toFixed(2)}` },
    { key: 'coverage_amount', label: 'Dekking', render: (v) => v ? `\u20AC${v.toLocaleString('nl-NL')}` : '-' },
    { key: 'policies_sold', label: 'Verkocht' },
    { key: 'revenue', label: 'Omzet', render: (v) => `\u20AC${v?.toFixed(2)}` },
  ],
};

export default function ReportBuilder() {
  const [reportType, setReportType] = useState('premiums');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);

  const generateReport = async () => {
    setLoading(true);
    try {
      let data;
      switch (reportType) {
        case 'premiums':
          data = await fetchPremiumReport({ start_date: startDate || undefined, end_date: endDate || undefined });
          break;
        case 'claims':
          data = await fetchClaimsReport();
          break;
        case 'products':
          data = await fetchProductsReport();
          break;
        default:
          return;
      }
      setReportData(data);
      toast.success('Rapport gegenereerd');
    } catch {
      toast.error('Rapport genereren mislukt');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      const blob = await exportReport({ report_type: reportType });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `insurancehub_${reportType}_${new Date().toISOString().split('T')[0]}.xlsx`;
      a.click();
      window.URL.revokeObjectURL(url);
      toast.success('Excel bestand gedownload');
    } catch {
      toast.error('Export mislukt');
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-800">Rapport Builder</h1>
        <p className="text-gray-500 text-sm">Genereer en exporteer verzekeringsrapporten</p>
      </div>

      {/* Report configuration */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-700 mb-4">Rapport Configuratie</h2>

        {/* Report type selection */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {REPORT_TYPES.map((type) => (
            <label
              key={type.value}
              className={`flex flex-col p-4 border rounded-lg cursor-pointer transition-colors ${
                reportType === type.value
                  ? 'border-primary-400 bg-primary-50'
                  : 'border-gray-200 hover:border-primary-200'
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                <input
                  type="radio" name="reportType" value={type.value}
                  checked={reportType === type.value}
                  onChange={() => { setReportType(type.value); setReportData(null); }}
                />
                <span className="font-medium text-gray-800 text-sm">{type.label}</span>
              </div>
              <p className="text-xs text-gray-500 ml-5">{type.description}</p>
            </label>
          ))}
        </div>

        {/* Date filters (for premium report) */}
        {reportType === 'premiums' && (
          <div className="flex gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">
                <Calendar size={14} className="inline mr-1" />
                Van
              </label>
              <input
                type="date" value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-300"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">
                <Calendar size={14} className="inline mr-1" />
                Tot
              </label>
              <input
                type="date" value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-300"
              />
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-3">
          <button
            onClick={generateReport}
            disabled={loading}
            className="flex items-center gap-2 px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 text-sm font-medium"
          >
            {loading ? (
              <><Loader2 size={16} className="animate-spin" /> Genereren...</>
            ) : (
              <><BarChart3 size={16} /> Rapport Genereren</>
            )}
          </button>
          {reportData && (
            <button
              onClick={handleExport}
              disabled={exporting}
              className="flex items-center gap-2 px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50 text-sm font-medium"
            >
              {exporting ? (
                <><Loader2 size={16} className="animate-spin" /> Exporteren...</>
              ) : (
                <><FileSpreadsheet size={16} /> Export Excel</>
              )}
            </button>
          )}
        </div>
      </div>

      {/* Report results */}
      {loading && <LoadingSpinner message="Rapport genereren..." />}

      {reportData && !loading && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-700">
                {REPORT_TYPES.find((t) => t.value === reportType)?.label}
              </h3>
              <p className="text-xs text-gray-400">
                Gegenereerd: {new Date(reportData.generated_at).toLocaleString('nl-NL')}
                {' - '}{reportData.data.length} rijen
              </p>
            </div>
          </div>
          <DataTable
            columns={REPORT_COLUMNS[reportType]}
            data={reportData.data}
            totalItems={reportData.data.length}
            perPage={50}
            emptyMessage="Geen gegevens voor dit rapport"
          />
        </div>
      )}
    </div>
  );
}
