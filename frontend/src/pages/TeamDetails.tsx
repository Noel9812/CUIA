import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchTeamDetails } from '../services/api';
import { TeamDetailsData } from '../types';
import { ArrowLeft, Users, Activity, Target, Shield, Clock } from 'lucide-react';
import RecommendationsList from '../components/Recommendations';

const TeamDetails: React.FC = () => {
  const { teamId } = useParams<{ teamId: string }>();
  const [data, setData] = useState<TeamDetailsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        if (teamId) {
          const result = await fetchTeamDetails(teamId);
          setData(result);
        }
      } catch (err) {
        setError('Failed to load team details');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [teamId]);

  if (loading) return <div className="p-8 text-center text-gray-500">Loading team details...</div>;
  if (error || !data) return <div className="p-8 text-center text-red-500">{error}</div>;

  const t = data.team;

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      
      {/* Header */}
      <div className="flex items-center space-x-4">
        <Link to="/" className="p-2 bg-white border rounded-lg hover:bg-gray-50">
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t.name}</h1>
          <p className="text-gray-500">{t.members} Engineers • Managed by {t.managerId}</p>
        </div>
      </div>

      {/* Team Summary — all values from backend team analytics */}
      <section className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Team Summary</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <StatBox label="Health Score" value={`${Math.round(t.healthScore)}%`} />
          <StatBox label="Utilization" value={`${Math.round(t.utilization)}%`} />
          <StatBox label="Velocity (SP)" value={t.velocity} />
          <StatBox label="Avg Resolution Time" value={`${Math.round(t.averageResolutionTime)}h`} />
          <StatBox label="Burnout Risk" value={t.burnoutRisk} isAlert={t.burnoutRisk > 0} />
          <StatBox label="Dependency Risk" value={t.dependencyRisk} isAlert={t.dependencyRisk > 0} />
          <StatBox label="Critical Issues" value={t.criticalIssues} isAlert={t.criticalIssues > 0} />
          <StatBox label="Blocked Issues" value={t.blockedIssues} isAlert={t.blockedIssues > 0} />
        </div>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Team Skills */}
        <section className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Team Skills Coverage</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm whitespace-nowrap">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  <th className="px-4 py-3 font-semibold text-gray-600">Technology</th>
                  <th className="px-4 py-3 font-semibold text-gray-600">Coverage</th>
                  <th className="px-4 py-3 font-semibold text-gray-600">Risk</th>
                  <th className="px-4 py-3 font-semibold text-gray-600">Cross-Train</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {data.skills.map((s, i) => (
                  <tr key={i} className="hover:bg-gray-50/50">
                    <td className="px-4 py-3 font-medium text-gray-900">{s.technology}</td>
                    <td className="px-4 py-3">{s.coverage} Eng</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${s.risk === 'Critical' ? 'bg-red-100 text-red-800' : s.risk === 'Medium' ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'}`}>
                        {s.risk}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-500">{s.candidate}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Forecast — using correct backend field names */}
        <section className="bg-indigo-900 text-white rounded-xl shadow-sm p-6">
          <h2 className="text-xl font-bold mb-4">Forecast & Capacity</h2>
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                 <p className="text-indigo-200 text-sm">Forecasted Capacity</p>
                 <p className="text-2xl font-bold">{Math.round(data.forecast.currentCapacity)}h</p>
               </div>
               <div>
                 <p className="text-indigo-200 text-sm">Avg Velocity</p>
                 <p className="text-2xl font-bold">{Math.round(data.forecast.averageVelocity)} SP</p>
               </div>
            </div>
            <div>
              <p className="text-indigo-200 text-sm">Capacity Gap</p>
              <p className="text-2xl font-bold">{Math.round(data.forecast.capacityGap)}h</p>
            </div>
            <div className="pt-4 border-t border-indigo-800">
               <p className="text-indigo-200 text-sm mb-2">Risk Assessment</p>
               <div className="flex items-center space-x-2">
                 <span className={`px-3 py-1 rounded-full text-sm font-medium ${data.forecast.forecastRisk === 'High' || data.forecast.forecastRisk === 'Critical' ? 'bg-red-500/20 text-red-200' : 'bg-emerald-500/20 text-emerald-200'}`}>
                   {data.forecast.forecastRisk} Risk
                 </span>
               </div>
            </div>
          </div>
        </section>
      </div>

      {/* Team Members */}
      <section>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Team Members</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {data.engineers.map((eng) => (
            <div key={eng.id} className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex flex-col">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-bold text-gray-900">{eng.name}</h3>
                  <p className="text-sm text-gray-500">{eng.designation}</p>
                </div>
                <div className={`px-2 py-1 rounded-full text-xs font-medium ${eng.utilization > 95 ? 'bg-red-100 text-red-800' : eng.utilization < 60 ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'}`}>
                  {Math.round(eng.utilization)}% Util
                </div>
              </div>

              <div className="space-y-3 mb-6 flex-grow">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Effective Cap</span>
                  <span className="font-medium">{eng.availableHours}h/wk</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Sprint Capacity</span>
                  <span className="font-medium">{eng.sprintCapacity}h</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Productivity</span>
                  <span className="font-medium">{Math.round(eng.productivity)} wSP</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Critical Tickets</span>
                  <span className={`font-medium ${eng.criticalIssues > 0 ? 'text-red-600' : ''}`}>{eng.criticalIssues}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Burnout Risk</span>
                  <span className={`font-medium ${eng.burnoutRisk === 'High' ? 'text-red-600' : ''}`}>{eng.burnoutRisk}</span>
                </div>
                <div className="pt-3 border-t">
                  <p className="text-xs text-gray-500 mb-2">Primary Skills</p>
                  <div className="flex flex-wrap gap-2">
                    {eng.primarySkills.map((s, i) => (
                      <span key={i} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-md">{s}</span>
                    ))}
                  </div>
                </div>
              </div>

              <Link to={`/engineer/${eng.id}`} className="mt-auto w-full py-2 border border-gray-200 hover:bg-gray-50 text-gray-700 font-medium rounded-lg text-center transition-colors">
                View Engineer
              </Link>
            </div>
          ))}
        </div>
      </section>

      {/* Insights */}
      <section>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Team Recommendations</h2>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <RecommendationsList recommendations={data.recommendations} />
        </div>
      </section>

    </div>
  );
};

const StatBox = ({ label, value, isAlert = false }: { label: string; value: string | number; isAlert?: boolean }) => (
  <div>
    <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">{label}</p>
    <p className={`text-2xl font-bold ${isAlert ? 'text-red-600' : 'text-gray-900'}`}>{value}</p>
  </div>
);

export default TeamDetails;
