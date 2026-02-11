import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, Package, Calculator, CheckCircle } from 'lucide-react';
import { fetchProducts, calculatePremium, createPolicy } from '../../services/api';
import toast from 'react-hot-toast';

const STEPS = [
  { num: 1, label: 'Klantgegevens', icon: User },
  { num: 2, label: 'Product kiezen', icon: Package },
  { num: 3, label: 'Premie berekenen', icon: Calculator },
  { num: 4, label: 'Bevestiging', icon: CheckCircle },
];

export default function PolicyForm() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [products, setProducts] = useState([]);
  const [calcResult, setCalcResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const [form, setForm] = useState({
    customer_name: '',
    customer_email: '',
    customer_phone: '',
    date_of_birth: '',
    address: '',
    postcode: '',
    product_id: '',
    start_date: new Date().toISOString().split('T')[0],
    end_date: '',
    payment_freq: 'monthly',
    notes: '',
  });

  useEffect(() => {
    fetchProducts({ per_page: 100, status: 'active' })
      .then((data) => setProducts(data.items))
      .catch(() => {});
  }, []);

  const updateField = (field, value) => setForm({ ...form, [field]: value });

  const handleCalculate = async () => {
    if (!form.product_id) {
      toast.error('Selecteer een product');
      return;
    }
    try {
      const result = await calculatePremium({
        product_id: parseInt(form.product_id),
        date_of_birth: form.date_of_birth || undefined,
        postcode: form.postcode || undefined,
      });
      setCalcResult(result);
      setStep(3);
    } catch {
      toast.error('Premie berekening mislukt');
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const policyData = {
        ...form,
        product_id: parseInt(form.product_id),
        premium_amount: calcResult?.calculated_premium || undefined,
      };
      const result = await createPolicy(policyData);
      toast.success(`Polis ${result.policy.policy_number} aangemaakt!`);
      setStep(4);
    } catch (err) {
      toast.error(err.response?.data?.error || 'Polis aanmaken mislukt');
    } finally {
      setSubmitting(false);
    }
  };

  const selectedProduct = products.find((p) => p.id === parseInt(form.product_id));

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-800">Nieuwe Polis Aanmaken</h1>
        <p className="text-gray-500 text-sm">Doorloop de stappen om een nieuwe polis aan te maken</p>
      </div>

      {/* Steps indicator */}
      <div className="flex items-center gap-2 mb-8 bg-white rounded-lg shadow p-4">
        {STEPS.map(({ num, label, icon: Icon }) => (
          <React.Fragment key={num}>
            <div
              className={`flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer ${
                step === num ? 'bg-primary-50 text-primary-700' :
                step > num ? 'text-green-600' : 'text-gray-400'
              }`}
              onClick={() => num < step && setStep(num)}
            >
              <Icon size={16} />
              <span className="text-sm font-medium hidden sm:inline">{label}</span>
            </div>
            {num < 4 && <div className={`flex-1 h-0.5 ${step > num ? 'bg-green-400' : 'bg-gray-200'}`} />}
          </React.Fragment>
        ))}
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        {/* Step 1: Customer info */}
        {step === 1 && (
          <>
            <h2 className="text-lg font-semibold text-gray-700 mb-4">Klantgegevens</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">Naam *</label>
                <input
                  type="text" value={form.customer_name}
                  onChange={(e) => updateField('customer_name', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-300"
                  placeholder="Jan de Vries"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">E-mail</label>
                <input
                  type="email" value={form.customer_email}
                  onChange={(e) => updateField('customer_email', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-300"
                  placeholder="j.devries@email.nl"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">Telefoon</label>
                <input
                  type="tel" value={form.customer_phone}
                  onChange={(e) => updateField('customer_phone', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-300"
                  placeholder="06-12345678"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">Geboortedatum</label>
                <input
                  type="date" value={form.date_of_birth}
                  onChange={(e) => updateField('date_of_birth', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-300"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-600 mb-1">Adres</label>
                <input
                  type="text" value={form.address}
                  onChange={(e) => updateField('address', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-300"
                  placeholder="Keizersgracht 123"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">Postcode</label>
                <input
                  type="text" value={form.postcode}
                  onChange={(e) => updateField('postcode', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-300"
                  placeholder="1015 CJ"
                  maxLength={7}
                />
              </div>
            </div>
            <div className="mt-6 flex justify-end">
              <button
                onClick={() => {
                  if (!form.customer_name) { toast.error('Naam is verplicht'); return; }
                  setStep(2);
                }}
                className="px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 text-sm font-medium"
              >
                Volgende
              </button>
            </div>
          </>
        )}

        {/* Step 2: Product selection */}
        {step === 2 && (
          <>
            <h2 className="text-lg font-semibold text-gray-700 mb-4">Product Kiezen</h2>
            <div className="space-y-3 max-h-96 overflow-y-auto mb-4">
              {products.map((product) => (
                <label
                  key={product.id}
                  className={`flex items-start gap-3 p-4 border rounded-lg cursor-pointer transition-colors ${
                    parseInt(form.product_id) === product.id
                      ? 'border-primary-400 bg-primary-50'
                      : 'border-gray-200 hover:border-primary-200 hover:bg-blue-50'
                  }`}
                >
                  <input
                    type="radio" name="product" value={product.id}
                    checked={parseInt(form.product_id) === product.id}
                    onChange={() => updateField('product_id', product.id.toString())}
                    className="mt-1"
                  />
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-gray-800">{product.name}</span>
                      <span className="text-primary-600 font-bold">{'\u20AC'}{product.base_premium.toFixed(2)}/mnd</span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">{product.insurer_name} - {product.product_code}</p>
                    {product.description && (
                      <p className="text-xs text-gray-400 mt-1">{product.description}</p>
                    )}
                    <div className="flex gap-4 mt-2 text-xs text-gray-500">
                      {product.coverage_amount && <span>Dekking: {'\u20AC'}{product.coverage_amount.toLocaleString('nl-NL')}</span>}
                      <span>Eigen risico: {'\u20AC'}{product.deductible?.toFixed(2) || '0.00'}</span>
                    </div>
                  </div>
                </label>
              ))}
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">Startdatum *</label>
                <input
                  type="date" value={form.start_date}
                  onChange={(e) => updateField('start_date', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-300"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">Betaalfrequentie</label>
                <select
                  value={form.payment_freq}
                  onChange={(e) => updateField('payment_freq', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-300"
                >
                  <option value="monthly">Maandelijks</option>
                  <option value="quarterly">Kwartaal</option>
                  <option value="yearly">Jaarlijks</option>
                </select>
              </div>
            </div>

            <div className="flex justify-between">
              <button onClick={() => setStep(1)} className="px-6 py-2 text-gray-600 hover:text-gray-800 text-sm">
                Terug
              </button>
              <button onClick={handleCalculate} className="px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 text-sm font-medium">
                Premie Berekenen
              </button>
            </div>
          </>
        )}

        {/* Step 3: Premium calculation result */}
        {step === 3 && calcResult && (
          <>
            <h2 className="text-lg font-semibold text-gray-700 mb-4">Premie Berekening</h2>
            <div className="bg-gray-50 rounded-lg p-6 mb-6">
              <div className="flex items-center justify-between mb-4">
                <span className="text-gray-600">Product</span>
                <span className="font-medium">{calcResult.product.name}</span>
              </div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-600">Basispremie</span>
                <span>{'\u20AC'}{calcResult.base_premium.toFixed(2)}</span>
              </div>
              {calcResult.factors.map((factor, i) => (
                <div key={i} className="flex items-center justify-between mb-2 text-sm">
                  <span className="text-gray-500">{factor.name}</span>
                  <span className="text-gray-500">x {factor.factor}</span>
                </div>
              ))}
              <div className="border-t border-gray-200 mt-3 pt-3">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-gray-700">Berekende Premie</span>
                  <span className="text-2xl font-bold text-primary-600">
                    {'\u20AC'}{calcResult.calculated_premium.toFixed(2)}
                    <span className="text-sm font-normal text-gray-400">/mnd</span>
                  </span>
                </div>
              </div>
              {calcResult.coverage_amount && (
                <div className="flex items-center justify-between mt-2 text-sm text-gray-500">
                  <span>Dekking</span>
                  <span>{'\u20AC'}{calcResult.coverage_amount.toLocaleString('nl-NL')}</span>
                </div>
              )}
              <div className="flex items-center justify-between mt-1 text-sm text-gray-500">
                <span>Eigen risico</span>
                <span>{'\u20AC'}{calcResult.deductible?.toFixed(2) || '0.00'}</span>
              </div>
            </div>

            {/* Summary */}
            <div className="bg-blue-50 rounded-lg p-4 mb-6">
              <p className="text-sm font-medium text-blue-800 mb-2">Overzicht</p>
              <div className="text-sm text-blue-700 space-y-1">
                <p>Klant: {form.customer_name}</p>
                <p>Product: {calcResult.product.name} ({calcResult.product.product_code})</p>
                <p>Startdatum: {new Date(form.start_date).toLocaleDateString('nl-NL')}</p>
              </div>
            </div>

            <div className="flex justify-between">
              <button onClick={() => setStep(2)} className="px-6 py-2 text-gray-600 hover:text-gray-800 text-sm">
                Terug
              </button>
              <button
                onClick={handleSubmit}
                disabled={submitting}
                className="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50 text-sm font-medium"
              >
                {submitting ? 'Aanmaken...' : 'Polis Aanmaken'}
              </button>
            </div>
          </>
        )}

        {/* Step 4: Confirmation */}
        {step === 4 && (
          <div className="text-center py-8">
            <CheckCircle size={64} className="mx-auto mb-4 text-green-400" />
            <h2 className="text-xl font-bold text-gray-800 mb-2">Polis Aangemaakt!</h2>
            <p className="text-gray-500 mb-6">De polis is succesvol aangemaakt in het systeem.</p>
            <div className="flex justify-center gap-3">
              <button
                onClick={() => navigate('/policies')}
                className="px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 text-sm"
              >
                Naar Polissen
              </button>
              <button
                onClick={() => { setStep(1); setForm({ ...form, customer_name: '', customer_email: '', customer_phone: '', product_id: '' }); setCalcResult(null); }}
                className="px-6 py-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 text-sm"
              >
                Nieuwe Polis
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
