import React from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import {
  LayoutDashboard,
  Building2,
  Package,
  FileText,
  BarChart3,
  Upload,
  PlusCircle,
} from 'lucide-react';
import Dashboard from './components/Dashboard/Dashboard';
import InsurerList from './components/Insurers/InsurerList';
import SyncMonitor from './components/Insurers/SyncMonitor';
import ProductList from './components/Products/ProductList';
import ProductImport from './components/Products/ProductImport';
import PolicyList from './components/Policies/PolicyList';
import PolicyForm from './components/Policies/PolicyForm';
import ReportBuilder from './components/Reports/ReportBuilder';

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/insurers', icon: Building2, label: 'Verzekeraars' },
  { path: '/products', icon: Package, label: 'Producten' },
  { path: '/policies', icon: FileText, label: 'Polissen' },
  { path: '/reports', icon: BarChart3, label: 'Rapporten' },
];

function App() {
  return (
    <Router>
      <div className="flex h-screen bg-gray-50">
        {/* Sidebar */}
        <aside className="w-64 bg-primary-700 text-white flex flex-col shadow-xl">
          <div className="p-6 border-b border-primary-600">
            <h1 className="text-xl font-bold tracking-wide">InsuranceHub</h1>
            <p className="text-primary-200 text-xs mt-1">Multi-Insurer Platform</p>
          </div>
          <nav className="flex-1 py-4">
            {navItems.map(({ path, icon: Icon, label }) => (
              <NavLink
                key={path}
                to={path}
                end={path === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-6 py-3 text-sm transition-colors ${
                    isActive
                      ? 'bg-primary-600 text-white border-r-4 border-accent-400'
                      : 'text-primary-200 hover:bg-primary-600 hover:text-white'
                  }`
                }
              >
                <Icon size={18} />
                {label}
              </NavLink>
            ))}
            <div className="border-t border-primary-600 mt-4 pt-4">
              <NavLink
                to="/products/import"
                className={({ isActive }) =>
                  `flex items-center gap-3 px-6 py-3 text-sm transition-colors ${
                    isActive
                      ? 'bg-primary-600 text-white border-r-4 border-accent-400'
                      : 'text-primary-200 hover:bg-primary-600 hover:text-white'
                  }`
                }
              >
                <Upload size={18} />
                Import
              </NavLink>
              <NavLink
                to="/policies/new"
                className={({ isActive }) =>
                  `flex items-center gap-3 px-6 py-3 text-sm transition-colors ${
                    isActive
                      ? 'bg-primary-600 text-white border-r-4 border-accent-400'
                      : 'text-primary-200 hover:bg-primary-600 hover:text-white'
                  }`
                }
              >
                <PlusCircle size={18} />
                Nieuwe Polis
              </NavLink>
            </div>
          </nav>
          <div className="p-4 border-t border-primary-600 text-xs text-primary-300">
            <p>InsuranceHub v1.0</p>
            <p>Portfolio Project</p>
          </div>
        </aside>

        {/* Main content */}
        <main className="flex-1 overflow-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/insurers" element={<InsurerList />} />
            <Route path="/insurers/sync" element={<SyncMonitor />} />
            <Route path="/products" element={<ProductList />} />
            <Route path="/products/import" element={<ProductImport />} />
            <Route path="/policies" element={<PolicyList />} />
            <Route path="/policies/new" element={<PolicyForm />} />
            <Route path="/reports" element={<ReportBuilder />} />
          </Routes>
        </main>
      </div>
      <Toaster position="top-right" />
    </Router>
  );
}

export default App;
