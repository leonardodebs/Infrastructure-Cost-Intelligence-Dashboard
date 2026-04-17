import React from 'react';

export default function StatCard({ title, value, subtitle, icon, trend }) {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6 transition-all hover:shadow-md">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{title}</p>
          <p className="text-2xl font-bold text-slate-900 dark:text-white mt-2">{value}</p>
          {subtitle && (
            <div className="flex items-center gap-1 mt-2">
              {trend && (
                <span className={`text-xs font-medium ${trend > 0 ? 'text-red-500' : 'text-green-500'}`}>
                  {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}%
                </span>
              )}
              <p className="text-xs text-slate-400">{subtitle}</p>
            </div>
          )}
        </div>
        <div className="p-3 bg-slate-50 dark:bg-slate-700 rounded-lg text-2xl">
          {icon}
        </div>
      </div>
    </div>
  );
}
