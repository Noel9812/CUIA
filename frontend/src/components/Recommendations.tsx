import React, { useState } from 'react';
import { Recommendation } from '../types';
import { AlertTriangle, Info, ShieldAlert, ChevronDown, ChevronUp } from 'lucide-react';

const RecommendationsList: React.FC<{ recommendations: Recommendation[] }> = ({ recommendations }) => {
  if (recommendations.length === 0) {
    return <div className="text-gray-500 text-sm">No action required at this time.</div>;
  }

  return (
    <div className="space-y-4">
      {recommendations.map((rec, idx) => (
        <RecommendationCard key={idx} recommendation={rec} />
      ))}
    </div>
  );
};

const RecommendationCard = ({ recommendation: r }: { recommendation: Recommendation }) => {
  const [expanded, setExpanded] = useState(false);

  const icons = {
    Critical: <ShieldAlert className="w-5 h-5 text-red-500" />,
    High: <AlertTriangle className="w-5 h-5 text-amber-500" />,
    Medium: <Info className="w-5 h-5 text-blue-500" />,
    Low: <Info className="w-5 h-5 text-gray-400" />
  };

  const bgs = {
    Critical: 'bg-red-50 border-red-100',
    High: 'bg-amber-50 border-amber-100',
    Medium: 'bg-blue-50 border-blue-100',
    Low: 'bg-gray-50 border-gray-100'
  };

  return (
    <div className={`rounded-xl border p-4 transition-all ${bgs[r.severity as keyof typeof bgs] || bgs.Medium}`}>
      <div className="flex items-start justify-between cursor-pointer" onClick={() => setExpanded(!expanded)}>
        <div className="flex items-start space-x-3">
          <div className="mt-0.5">{icons[r.severity as keyof typeof icons]}</div>
          <div>
            <h4 className="font-semibold text-gray-900">{r.businessRule}</h4>
            <p className="text-sm text-gray-700 mt-1">{r.reason}</p>
          </div>
        </div>
        <button className="text-gray-400 hover:text-gray-600">
          {expanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
        </button>
      </div>

      {expanded && (
        <div className="mt-4 pt-4 border-t border-black/5 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <span className="text-xs font-semibold uppercase text-gray-500 block mb-1">Business Impact</span>
            <p className="text-sm text-gray-800">{r.businessImpact}</p>
          </div>
          <div>
            <span className="text-xs font-semibold uppercase text-gray-500 block mb-1">Suggested Action</span>
            <p className="text-sm text-gray-800 font-medium">{r.suggestedAction}</p>
          </div>
          <div className="md:col-span-2">
            <span className="text-xs font-semibold uppercase text-gray-500 block mb-1">Expected Outcome</span>
            <p className="text-sm text-emerald-700 bg-emerald-50/50 p-2 rounded border border-emerald-100">{r.expectedOutcome}</p>
          </div>
          <div className="md:col-span-2 flex items-center space-x-4 text-xs text-gray-500">
             <span>Confidence: <strong className="text-gray-700">{r.confidence}</strong></span>
             <span>Source: {r.sourceAnalytics}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default RecommendationsList;
