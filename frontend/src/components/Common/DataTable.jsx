import React, { useState } from 'react';
import { ChevronUp, ChevronDown, ChevronLeft, ChevronRight } from 'lucide-react';

/**
 * Reusable data table with sorting, filtering, and pagination.
 * Used across Products, Policies, and Reports pages.
 */
export default function DataTable({
  columns,
  data,
  totalItems,
  page = 1,
  perPage = 20,
  onPageChange,
  onSort,
  sortBy,
  sortOrder,
  onRowClick,
  emptyMessage = 'Geen gegevens gevonden',
}) {
  const totalPages = Math.ceil((totalItems || data.length) / perPage);

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-primary-700">
            <tr>
              {columns.map((col) => (
                <th
                  key={col.key}
                  className={`px-4 py-3 text-left text-xs font-medium text-white uppercase tracking-wider ${
                    col.sortable ? 'cursor-pointer hover:bg-primary-600 select-none' : ''
                  }`}
                  onClick={() => col.sortable && onSort?.(col.key)}
                  style={col.width ? { width: col.width } : {}}
                >
                  <div className="flex items-center gap-1">
                    {col.label}
                    {col.sortable && sortBy === col.key && (
                      sortOrder === 'asc' ? <ChevronUp size={14} /> : <ChevronDown size={14} />
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-100">
            {data.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="px-4 py-8 text-center text-gray-400">
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              data.map((row, idx) => (
                <tr
                  key={row.id || idx}
                  className={`hover:bg-blue-50 transition-colors ${
                    onRowClick ? 'cursor-pointer' : ''
                  }`}
                  onClick={() => onRowClick?.(row)}
                >
                  {columns.map((col) => (
                    <td key={col.key} className="px-4 py-3 text-sm text-gray-700">
                      {col.render ? col.render(row[col.key], row) : row[col.key]}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="bg-gray-50 px-4 py-3 flex items-center justify-between border-t border-gray-200">
          <p className="text-sm text-gray-500">
            Pagina {page} van {totalPages} ({totalItems || data.length} items)
          </p>
          <div className="flex gap-1">
            <button
              onClick={() => onPageChange?.(page - 1)}
              disabled={page <= 1}
              className="px-3 py-1 rounded text-sm bg-white border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeft size={16} />
            </button>
            {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
              const p = page <= 3 ? i + 1 : page - 2 + i;
              if (p > totalPages) return null;
              return (
                <button
                  key={p}
                  onClick={() => onPageChange?.(p)}
                  className={`px-3 py-1 rounded text-sm border ${
                    p === page
                      ? 'bg-primary-500 text-white border-primary-500'
                      : 'bg-white border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  {p}
                </button>
              );
            })}
            <button
              onClick={() => onPageChange?.(page + 1)}
              disabled={page >= totalPages}
              className="px-3 py-1 rounded text-sm bg-white border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
