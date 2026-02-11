import React from 'react';

const STATUS_STYLES = {
  active: 'bg-green-100 text-green-700',
  success: 'bg-green-100 text-green-700',
  paid: 'bg-green-100 text-green-700',
  approved: 'bg-emerald-100 text-emerald-700',
  pending: 'bg-yellow-100 text-yellow-700',
  under_review: 'bg-amber-100 text-amber-700',
  submitted: 'bg-blue-100 text-blue-700',
  error: 'bg-red-100 text-red-700',
  failed: 'bg-red-100 text-red-700',
  rejected: 'bg-red-100 text-red-700',
  inactive: 'bg-gray-100 text-gray-600',
  expired: 'bg-gray-100 text-gray-600',
  cancelled: 'bg-gray-100 text-gray-600',
  discontinued: 'bg-gray-100 text-gray-600',
  partial: 'bg-orange-100 text-orange-700',
};

export default function StatusBadge({ status }) {
  const style = STATUS_STYLES[status] || 'bg-gray-100 text-gray-600';
  const label = status ? status.replace(/_/g, ' ') : 'unknown';

  return (
    <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium capitalize ${style}`}>
      {label}
    </span>
  );
}
