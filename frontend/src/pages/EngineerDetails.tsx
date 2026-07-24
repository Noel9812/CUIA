import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchEngineerDetails } from '../services/api';
import { EngineerDetailsData } from '../types';
import { ArrowLeft, User, Briefcase, Clock, Calendar, CheckCircle, AlertTriangle } from 'lucide-react';
import RecommendationsList from '../components/Recommendations';

const EngineerDetails: React.FC = () => {
  const { engineerId } = useParams<{ engineerId: string }>();
  const [data, setData] = useState<EngineerDetailsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        if (engineerId) {
          const result = await fetchEngineerDetails(engineerId);
          setData(result);
        }
      } catch (err) {
        setError('Failed to load engineer details');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [engineerId]);

  if (loading) return <div className="p-8 text-center text-gray-500">Loading engineer details...</div>;
  if (error || !data) return <div className="p-8 text-center text-red-500">{error}</div>;

  const e = data.engineer;

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      
      {/* Header Profile */}
      <div className="flex items-center space-x-4">
        <Link to={`/team/${e.teamId}`} className="p-2 bg-white border rounded-lg hover:bg-gray-50">
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </Link>
        <div className="flex-grow">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{e.name}</h1>
              <p className="text-gray-500 flex items-center space-x-2 mt-1">
                <Briefcase className="w-4 h-4" /> <span>{e.designation}</span>
                <span className="text-gray-300">•</span>
                <span>{e.experience} Yrs Exp</span>
              </p>
            </div>
            <div className={`px-4 py-2 rounded-lg border ${e.utilization > 95 ? 'bg-red-50 border-red-200 text-red-700' : 'bg-emerald-50 border-emerald-200 text-emerald-700'}`}>
              <div className="text-sm font-semibold uppercase tracking-wider mb-1">Utilization</div>
              <div className="text-xl font-bold">{Math.round(e.utilization)}%</div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        
        {/* Capacity */}
        <section className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-6 flex items-center"><Clock className="w-5 h-5 mr-2 text-indigo-500" /> Capacity Breakdown</h2>
          <div className="space-y-4">
             <CapRow label="Gross Working Hours" value="45h" />
             <CapRow label="Leave / PTO" value={`-${45 - e.availableHours}h`} isDeduction />
             <div className="pt-4 border-t border-gray-100 flex justify-between font-bold text-gray-900 text-lg">
               <span>Effective Capacity</span>
               <span>{e.availableHours}h</span>
             </div>
             <div className="pt-2 flex justify-between text-indigo-700 font-medium">
               <span>Actual Logged Hours</span>
               <span>{e.loggedHours}h</span>
             </div>
          </div>
        </section>

        {/* Productivity */}
        <section className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-6 flex items-center"><CheckCircle className="w-5 h-5 mr-2 text-emerald-500" /> Productivity</h2>
          <div className="grid grid-cols-2 gap-y-6 gap-x-4">
             <div><p className="text-sm text-gray-500">Weighted Productivity</p><p className="text-xl font-bold text-gray-900">{Math.round(e.productivity)}</p></div>
             <div><p className="text-sm text-gray-500">Story Points Delivered</p><p className="text-xl font-bold text-gray-900">{e.storyPoints}</p></div>
             <div><p className="text-sm text-gray-500">Avg Resolution Time</p><p className="text-xl font-bold text-gray-900">{Math.round(e.averageResolutionTime)}h</p></div>
             <div><p className="text-sm text-gray-500">Estimation Accuracy</p><p className="text-xl font-bold text-gray-900">{Math.round(e.estimationAccuracy)}%</p></div>
          </div>
        </section>

      </div>

      {/* Skills */}
      <section className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h2 className="text-lg font-bold text-gray-900 mb-6">Skills & Ownership</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
           <div>
             <h3 className="text-sm font-semibold uppercase text-gray-500 mb-3">Primary Skills</h3>
             <div className="flex flex-wrap gap-2">
               {e.primarySkills.map((s, i) => <span key={i} className="px-3 py-1 bg-indigo-50 text-indigo-700 rounded-lg text-sm">{s}</span>)}
             </div>
           </div>
           <div>
             <h3 className="text-sm font-semibold uppercase text-gray-500 mb-3">Secondary Skills</h3>
             <div className="flex flex-wrap gap-2">
               {e.secondarySkills.map((s, i) => <span key={i} className="px-3 py-1 bg-gray-50 text-gray-700 rounded-lg text-sm">{s}</span>)}
             </div>
           </div>
           <div>
             <h3 className="text-sm font-semibold uppercase text-gray-500 mb-3">Cross-Train Candidates</h3>
             <div className="flex flex-wrap gap-2">
               {e.crossTrainingSkills && e.crossTrainingSkills.length > 0 ? e.crossTrainingSkills.map((s, i) => <span key={i} className="px-3 py-1 bg-amber-50 text-amber-700 rounded-lg text-sm">{s}</span>) : <span className="text-sm text-gray-400">None assigned</span>}
             </div>
           </div>
        </div>
      </section>

      {/* Jira Work */}
      <section className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-6 border-b border-gray-100">
          <h2 className="text-lg font-bold text-gray-900">Current Jira Workload</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-sm whitespace-nowrap">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 font-semibold text-gray-600">Key</th>
                <th className="px-6 py-3 font-semibold text-gray-600">Summary</th>
                <th className="px-6 py-3 font-semibold text-gray-600">Priority</th>
                <th className="px-6 py-3 font-semibold text-gray-600">SP</th>
                <th className="px-6 py-3 font-semibold text-gray-600">Logged</th>
                <th className="px-6 py-3 font-semibold text-gray-600">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {data.issues.map((i, idx) => (
                <tr key={idx} className="hover:bg-gray-50/50">
                  <td className="px-6 py-4 font-medium text-indigo-600">{i.issueKey}</td>
                  <td className="px-6 py-4 truncate max-w-xs">{i.summary}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${i.priority === 'Critical' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'}`}>
                      {i.priority}
                    </span>
                  </td>
                  <td className="px-6 py-4">{i.storyPoints}</td>
                  <td className="px-6 py-4">{i.loggedHours}h</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${i.status === 'Done' ? 'bg-emerald-100 text-emerald-800' : (i.blocked ? 'bg-amber-100 text-amber-800' : 'bg-blue-100 text-blue-800')}`}>
                      {i.blocked ? 'Blocked' : i.status}
                    </span>
                  </td>
                </tr>
              ))}
              {data.issues.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-gray-500">No Jira issues assigned.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      {/* Insights */}
      <section>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Engineer Insights</h2>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <RecommendationsList recommendations={data.recommendations} />
        </div>
      </section>

    </div>
  );
};

const CapRow = ({ label, value, isDeduction = false }: any) => (
  <div className="flex justify-between text-sm">
    <span className="text-gray-500">{label}</span>
    <span className={`font-medium ${isDeduction ? 'text-red-500' : 'text-gray-900'}`}>{value}</span>
  </div>
);

export default EngineerDetails;
