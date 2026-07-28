import React, { useEffect, useState } from 'react';
import { fetchDeliveryDashboard } from '../services/api';
import { DeliveryDashboardData } from '../types';
import { Activity, AlertTriangle, CheckCircle, Clock, Users, ArrowRight, Target, PieChart } from 'lucide-react';
import { Link } from 'react-router-dom';
import RecommendationsList from '../components/Recommendations';
import { KPICard, MiniKPI } from '../components/KPICards';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart as RechartsPieChart, Pie, Cell, LineChart, Line, Legend } from 'recharts';

const DeliveryDashboard: React.FC<{ managerId: string }> = ({ managerId }) => {
  const [data, setData] = useState<DeliveryDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const result = await fetchDeliveryDashboard(managerId);
        setData(result);
        setError(null);
      } catch (err) {
        setError('Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [managerId]);

  if (loading) return <SkeletonDashboard />;
  if (error || !data) return <div className="p-8 text-center text-red-500">{error}</div>;

  // Compute issue status distribution from backend-provided issues (presentation-only grouping)
  const statusGroups = [
    { name: 'To Do', value: data.issues.filter(i => i.status === 'To Do' || i.status === 'Selected for Development').length },
    { name: 'In Progress', value: data.issues.filter(i => i.status === 'In Progress' || i.status === 'Code Review' || i.status === 'Testing' || i.status === 'Ready For QA').length },
    { name: 'Done', value: data.issues.filter(i => i.status === 'Done' || i.status === 'Released').length },
    { name: 'Blocked', value: data.issues.filter(i => i.status === 'Blocked').length },
  ].filter(g => g.value > 0);

  const PIE_COLORS = ['#cbd5e1', '#3b82f6', '#10b981', '#ef4444'];

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      
      {/* Executive Health KPIs — all values from backend kpis */}
      <section>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Executive Health</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard title="Team Health Score" value={`${Math.round(data.kpis.healthScore)}%`} status={data.kpis.healthScore > 80 ? 'healthy' : data.kpis.healthScore > 60 ? 'warning' : 'critical'} desc="Average across managed teams" icon={<Activity />} />
          <KPICard title="Average Utilization" value={`${Math.round(data.kpis.utilization)}%`} status={data.kpis.utilization > 95 ? 'critical' : data.kpis.utilization > 80 ? 'warning' : 'healthy'} desc="Across all engineers" icon={<PieChart />} />
          <KPICard title="Remaining Capacity" value={`${Math.round(data.kpis.remainingCapacity)}h`} status={data.kpis.remainingCapacity < 0 ? 'critical' : 'healthy'} desc="Available hours this sprint" icon={<Clock />} />
          <KPICard title="Dependency Risks" value={data.kpis.dependencyRisks.toString()} status={data.kpis.dependencyRisks > 0 ? 'critical' : 'healthy'} desc="Single points of failure" icon={<AlertTriangle />} />
        </div>
      </section>

      {/* Operational Charts */}
      <section>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Operational Analytics</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Issue Distribution — derived from backend issues list (presentation grouping only) */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 className="text-sm font-semibold text-gray-500 mb-4">Jira Status Distribution</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <RechartsPieChart>
                  <Pie
                    data={statusGroups}
                    cx="50%" cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${value}`}
                  >
                    {statusGroups.map((_entry, index) => (
                      <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </RechartsPieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-center gap-4 text-xs text-gray-500 mt-2">
              <span className="flex items-center"><div className="w-3 h-3 bg-slate-300 rounded-full mr-1"></div>To Do</span>
              <span className="flex items-center"><div className="w-3 h-3 bg-blue-500 rounded-full mr-1"></div>In Progress</span>
              <span className="flex items-center"><div className="w-3 h-3 bg-emerald-500 rounded-full mr-1"></div>Done</span>
              <span className="flex items-center"><div className="w-3 h-3 bg-red-500 rounded-full mr-1"></div>Blocked</span>
            </div>
          </div>

          {/* Historical Capacity vs Logged Hours Trend */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 className="text-sm font-semibold text-gray-500 mb-4">Capacity vs Logged Hours Trend</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data.historicalTrends}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="sprint" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                  <Tooltip cursor={{ fill: '#f8fafc' }} />
                  <Legend />
                  <Line type="monotone" dataKey="capacity" name="Total Capacity (h)" stroke="#8b5cf6" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                  <Line type="monotone" dataKey="loggedHours" name="Logged Hours (h)" stroke="#3b82f6" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Mini KPIs from backend */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <MiniKPI title="Critical Issues" value={data.kpis.criticalIssues} isAlert={data.kpis.criticalIssues > 0} />
          <MiniKPI title="Blocked Issues" value={data.kpis.blockedIssues} isAlert={data.kpis.blockedIssues > 0} />
          <MiniKPI title="Burnout Risk" value={data.kpis.burnoutRiskCount} isAlert={data.kpis.burnoutRiskCount > 0} />
          <MiniKPI title="Dependency Risks" value={data.kpis.dependencyRisks} isAlert={data.kpis.dependencyRisks > 0} />
        </div>
      </section>

      {/* Team Overview */}
      <section>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Team Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {data.teams.map((team) => (
            <div key={team.id} className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex flex-col">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h3 className="text-lg font-bold text-gray-900">{team.name}</h3>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${team.healthScore > 80 ? 'bg-emerald-100 text-emerald-800' : team.healthScore > 60 ? 'bg-amber-100 text-amber-800' : 'bg-red-100 text-red-800'}`}>
                      {team.healthScore > 80 ? 'Healthy' : team.healthScore > 60 ? 'Needs Attention' : 'Critical'}
                    </span>
                    <span className="text-sm text-gray-500">{team.members} Members</span>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-y-4 gap-x-8 mb-6 flex-grow">
                <div><p className="text-xs text-gray-500 uppercase">Health</p><p className="font-semibold text-gray-900">{Math.round(team.healthScore)}%</p></div>
                <div><p className="text-xs text-gray-500 uppercase">Utilization</p><p className="font-semibold text-gray-900">{Math.round(team.utilization)}%</p></div>
                <div><p className="text-xs text-gray-500 uppercase">Velocity</p><p className="font-semibold text-gray-900">{team.velocity} SP</p></div>
                <div><p className="text-xs text-gray-500 uppercase">Critical/Blocked</p><p className="font-semibold text-gray-900">{team.criticalIssues} / {team.blockedIssues}</p></div>
                <div><p className="text-xs text-gray-500 uppercase">Burnout Risk</p><p className="font-semibold text-gray-900">{team.burnoutRisk}</p></div>
                <div><p className="text-xs text-gray-500 uppercase">Forecast</p><p className="font-semibold text-gray-900">{team.forecastStatus}</p></div>
              </div>

              <Link to={`/team/${team.id}`} className="mt-auto w-full py-2 bg-gray-50 hover:bg-gray-100 text-indigo-600 font-medium rounded-lg text-center transition-colors flex items-center justify-center space-x-2">
                <span>View Team Details</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          ))}
        </div>
      </section>

      {/* Forecast & Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
           <h2 className="text-xl font-bold text-gray-900 mb-4">Executive Briefing</h2>
           <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
             <RecommendationsList recommendations={data.recommendations} />
           </div>
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-900 mb-4">Forecast & Capacity</h2>
          <div className="bg-indigo-900 text-white rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-semibold mb-4">Next Sprint Prediction</h3>
            <div className="space-y-4">
               <div>
                 <p className="text-indigo-200 text-sm">Forecasted Capacity</p>
                 <p className="text-2xl font-bold">{Math.round(data.forecast.currentCapacity)}h</p>
               </div>
               <div>
                 <p className="text-indigo-200 text-sm">Avg Velocity</p>
                 <p className="text-2xl font-bold">{Math.round(data.forecast.averageVelocity)} SP</p>
               </div>
               <div>
                 <p className="text-indigo-200 text-sm">Capacity Gap</p>
                 <p className="text-2xl font-bold">{Math.round(data.forecast.capacityGap)}h</p>
               </div>
               <div className="pt-4 border-t border-indigo-800">
                 <p className="text-indigo-200 text-sm">Risk Assessment</p>
                 <div className="flex items-center space-x-2 mt-1">
                   {data.forecast.forecastRisk === 'High' || data.forecast.forecastRisk === 'Critical' ? <AlertTriangle className="w-5 h-5 text-red-400" /> : <CheckCircle className="w-5 h-5 text-emerald-400" />}
                   <span className="font-medium text-lg">{data.forecast.forecastRisk}</span>
                 </div>
               </div>
            </div>
          </div>
        </div>
      </div>
      
    </div>
  );
};

// Helper Components

const SkeletonDashboard = () => (
  <div className="space-y-8 animate-pulse">
    <section>
      <div className="h-6 w-48 bg-gray-200 rounded mb-4"></div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-32 bg-gray-200 rounded-xl"></div>
        ))}
      </div>
    </section>
    <section>
      <div className="h-6 w-48 bg-gray-200 rounded mb-4"></div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-20 bg-gray-200 rounded-lg"></div>
        ))}
      </div>
    </section>
  </div>
);

export default DeliveryDashboard;
