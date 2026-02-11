import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileJson, FileSpreadsheet, FileCode, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { importProducts } from '../../services/api';
import toast from 'react-hot-toast';

const FORMAT_CONFIG = {
  json: { icon: FileJson, color: 'text-yellow-500', label: 'JSON' },
  xml: { icon: FileCode, color: 'text-orange-500', label: 'XML' },
  xlsx: { icon: FileSpreadsheet, color: 'text-green-500', label: 'Excel' },
  xls: { icon: FileSpreadsheet, color: 'text-green-500', label: 'Excel' },
};

export default function ProductImport() {
  const [file, setFile] = useState(null);
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState(null);
  const [step, setStep] = useState(1); // 1: upload, 2: preview, 3: result

  const onDrop = useCallback((accepted) => {
    if (accepted.length > 0) {
      setFile(accepted[0]);
      setStep(2);
      setResult(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/json': ['.json'],
      'text/xml': ['.xml'],
      'application/xml': ['.xml'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
    },
    maxFiles: 1,
    maxSize: 16 * 1024 * 1024,
  });

  const handleImport = async () => {
    if (!file) return;

    setImporting(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const data = await importProducts(formData);
      setResult(data);
      setStep(3);
      toast.success(`Import voltooid: ${data.results.created} aangemaakt, ${data.results.updated} bijgewerkt`);
    } catch (err) {
      const msg = err.response?.data?.error || 'Import mislukt';
      toast.error(msg);
      setResult({ error: msg });
      setStep(3);
    } finally {
      setImporting(false);
    }
  };

  const resetImport = () => {
    setFile(null);
    setResult(null);
    setStep(1);
  };

  const ext = file?.name?.split('.').pop().toLowerCase();
  const formatInfo = FORMAT_CONFIG[ext] || FORMAT_CONFIG.json;
  const FormatIcon = formatInfo.icon;

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-800">Product Import</h1>
        <p className="text-gray-500 text-sm">Importeer producten vanuit JSON, XML of Excel bestanden</p>
      </div>

      {/* Progress steps */}
      <div className="flex items-center gap-4 mb-8">
        {[
          { num: 1, label: 'Bestand uploaden' },
          { num: 2, label: 'Controleren' },
          { num: 3, label: 'Resultaat' },
        ].map(({ num, label }) => (
          <div key={num} className="flex items-center gap-2">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
              step >= num ? 'bg-primary-500 text-white' : 'bg-gray-200 text-gray-500'
            }`}>
              {num}
            </div>
            <span className={`text-sm ${step >= num ? 'text-gray-700' : 'text-gray-400'}`}>{label}</span>
            {num < 3 && <div className={`w-12 h-0.5 ${step > num ? 'bg-primary-500' : 'bg-gray-200'}`} />}
          </div>
        ))}
      </div>

      {/* Step 1: File Upload */}
      {step === 1 && (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors ${
            isDragActive
              ? 'border-primary-400 bg-primary-50'
              : 'border-gray-300 bg-white hover:border-primary-300 hover:bg-blue-50'
          }`}
        >
          <input {...getInputProps()} />
          <Upload size={48} className="mx-auto mb-4 text-gray-400" />
          <p className="text-lg text-gray-600 mb-2">
            {isDragActive ? 'Laat het bestand hier los...' : 'Sleep een bestand hierheen'}
          </p>
          <p className="text-sm text-gray-400 mb-4">of klik om een bestand te selecteren</p>
          <div className="flex justify-center gap-6 text-xs text-gray-400">
            <span className="flex items-center gap-1"><FileJson size={14} /> JSON</span>
            <span className="flex items-center gap-1"><FileCode size={14} /> XML</span>
            <span className="flex items-center gap-1"><FileSpreadsheet size={14} /> Excel (.xlsx)</span>
          </div>
        </div>
      )}

      {/* Step 2: Preview */}
      {step === 2 && file && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center gap-4 mb-6">
            <div className={`p-3 rounded-lg bg-gray-100`}>
              <FormatIcon size={32} className={formatInfo.color} />
            </div>
            <div>
              <p className="font-medium text-gray-800">{file.name}</p>
              <p className="text-sm text-gray-400">
                {(file.size / 1024).toFixed(1)} KB - {formatInfo.label} formaat
              </p>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-blue-700">
              Het bestand wordt gevalideerd en geimporteerd. Bestaande producten (op basis van
              product_code) worden bijgewerkt, nieuwe producten worden aangemaakt.
            </p>
          </div>

          <div className="flex gap-3">
            <button
              onClick={handleImport}
              disabled={importing}
              className="flex items-center gap-2 px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 text-sm font-medium"
            >
              {importing ? (
                <><Loader2 size={16} className="animate-spin" /> Importeren...</>
              ) : (
                <><Upload size={16} /> Importeren</>
              )}
            </button>
            <button
              onClick={resetImport}
              disabled={importing}
              className="px-6 py-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 text-sm"
            >
              Annuleren
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Results */}
      {step === 3 && result && (
        <div className="bg-white rounded-lg shadow p-6">
          {result.error ? (
            <div className="text-center py-6">
              <XCircle size={48} className="mx-auto mb-4 text-red-400" />
              <p className="text-lg font-medium text-red-600">Import Mislukt</p>
              <p className="text-sm text-gray-500 mt-2">{result.error}</p>
            </div>
          ) : (
            <>
              <div className="text-center py-4 mb-6">
                <CheckCircle size={48} className="mx-auto mb-4 text-green-400" />
                <p className="text-lg font-medium text-gray-800">Import Voltooid</p>
              </div>

              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="bg-green-50 rounded-lg p-4 text-center">
                  <p className="text-2xl font-bold text-green-600">{result.results.created}</p>
                  <p className="text-sm text-green-700">Aangemaakt</p>
                </div>
                <div className="bg-blue-50 rounded-lg p-4 text-center">
                  <p className="text-2xl font-bold text-blue-600">{result.results.updated}</p>
                  <p className="text-sm text-blue-700">Bijgewerkt</p>
                </div>
                <div className="bg-red-50 rounded-lg p-4 text-center">
                  <p className="text-2xl font-bold text-red-600">{result.results.errors?.length || 0}</p>
                  <p className="text-sm text-red-700">Fouten</p>
                </div>
              </div>

              {result.results.errors?.length > 0 && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                  <p className="text-sm font-medium text-red-800 mb-2">Foutdetails:</p>
                  {result.results.errors.map((err, i) => (
                    <p key={i} className="text-xs text-red-600 py-0.5">
                      Rij {err.row}: {err.error}
                    </p>
                  ))}
                </div>
              )}
            </>
          )}

          <button
            onClick={resetImport}
            className="w-full px-4 py-2 bg-primary-50 text-primary-600 rounded-lg hover:bg-primary-100 text-sm font-medium"
          >
            Nieuwe Import
          </button>
        </div>
      )}
    </div>
  );
}
