import { useNavigate } from 'react-router-dom';
import { Engineer } from '../types';

export function EngineersTable({ engineers }: { engineers: Engineer[] }) {
  const navigate = useNavigate();

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name / Role</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Primary Skills</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Utilization</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Productivity</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Est. Accuracy</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Issues</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {engineers.map((e) => (
            <tr 
              key={e.id} 
              onClick={() => navigate(`/engineer/${e.id}`)}
              className="hover:bg-gray-50 cursor-pointer transition-colors"
            >
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm font-bold text-indigo-600">{e.name}</div>
                <div className="text-xs text-gray-500">{e.designation}</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <div className="flex space-x-1">
                  {e.primarySkills.map(s => <span key={s} className="px-2 py-0.5 bg-gray-100 rounded text-xs">{s}</span>)}
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${e.utilization > 95 ? 'bg-red-100 text-red-800' : e.utilization < 60 ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}`}>
                  {e.utilization.toFixed(1)}%
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{e.productivity.toFixed(1)}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{e.estimationAccuracy.toFixed(1)}%</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <div>Active: {e.activeTickets}</div>
                <div className="text-red-500">Critical: {e.criticalIssues}</div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
