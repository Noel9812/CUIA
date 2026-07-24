import React, { ReactNode } from 'react';

export const KPICard = ({ title, value, status, trend, desc, icon }: any) => {
  const colors = {
    healthy: 'text-emerald-600 bg-emerald-50',
    warning: 'text-amber-600 bg-amber-50',
    critical: 'text-red-600 bg-red-50',
    info: 'text-indigo-600 bg-indigo-50',
    neutral: 'text-slate-600 bg-slate-50'
  };
  
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
      <div className="flex justify-between items-start mb-2">
        <div className={`p-2 rounded-lg ${colors[status as keyof typeof colors] || colors.info}`}>
          {React.cloneElement(icon, { className: "w-5 h-5" })}
        </div>
        {trend && <span className="text-sm font-medium text-emerald-600">{trend}</span>}
      </div>
      <h3 className="text-gray-500 text-sm font-medium">{title}</h3>
      <p className="text-2xl font-bold text-gray-900 my-1">{value}</p>
      <p className="text-xs text-gray-400">{desc}</p>
    </div>
  );
};

export const MiniKPI = ({ title, value, isAlert = false }: any) => (
  <div className={`bg-white rounded-lg border p-4 transition-all duration-300 hover:shadow-md ${isAlert ? 'border-red-200 bg-red-50/30' : 'border-gray-100'}`}>
    <p className="text-xs text-gray-500 mb-1">{title}</p>
    <p className={`text-xl font-bold ${isAlert ? 'text-red-600' : 'text-gray-900'}`}>{value}</p>
  </div>
);
