import { useState } from 'react';
import { downloadReport } from '../services/api';
import { FileText, Download } from 'lucide-react';
import { Persona } from '../types';

export default function Reports({ persona }: { persona: Persona }) {
  const [loading, setLoading] = useState<string | null>(null);

  const handleDownload = async (type: string) => {
    setLoading(type);
    try {
      const blob = await downloadReport(type, persona);
      
      const url = window.URL.createObjectURL(blob);
      const downloadAnchorNode = document.createElement('a');
      downloadAnchorNode.href = url;
      downloadAnchorNode.download = `cuia-${persona}-${type}-report.pdf`;
      document.body.appendChild(downloadAnchorNode); 
      downloadAnchorNode.click();
      window.URL.revokeObjectURL(url);
      downloadAnchorNode.remove();
      
    } catch (error) {
      alert(`Failed to download ${type} report.`);
    } finally {
      setLoading(null);
    }
  };

  const reports = [
    { type: 'daily', name: 'Daily Standup Report', desc: 'Summary of yesterday\'s performance and today\'s capacity.' },
    { type: 'weekly', name: 'Weekly Sprint Report', desc: 'Comprehensive sprint analytics and utilization trends.' },
    { type: 'monthly', name: 'Monthly Executive Report', desc: 'Organization-wide health, capacity, and recommendations.' }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Reports</h2>
        <p className="text-gray-500">Generate and download pre-computed intelligence reports as PDF for {persona === 'leadership' ? 'Leadership' : 'Delivery Manager'}.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {reports.map((report) => (
          <div key={report.type} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col h-full">
            <div className="flex items-center mb-4">
              <div className="p-3 rounded-lg bg-indigo-50 mr-4">
                <FileText className="w-6 h-6 text-indigo-600" />
              </div>
              <h3 className="text-lg font-semibold">{report.name}</h3>
            </div>
            <p className="text-gray-500 mb-6 flex-1 text-sm">{report.desc}</p>
            <button
              onClick={() => handleDownload(report.type)}
              disabled={loading === report.type}
              className="w-full flex items-center justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 transition-colors"
            >
              <Download className="w-4 h-4 mr-2" />
              {loading === report.type ? 'Generating...' : 'Download PDF'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
