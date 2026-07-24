import React, { useEffect, useState } from 'react';
import { fetchDeliveryDashboard } from '../services/api';
import { DeliveryDashboardData } from '../types';
import { Activity, AlertTriangle, CheckCircle, Clock, Users, ArrowRight, Zap, Target, PieChart } from 'lucide-react';
import { Link } from 'react-router-dom';
import RecommendationsList from '../components/Recommendations';
import { KPICard, MiniKPI } from '../components/KPICards';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart as RechartsPieChart, Pie, Cell, LineChart, Line } from 'recharts';

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

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      
      {/* Executive Health KPIs */}
      <section>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Executive Health</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard title="Team Health Score" value={`${Math.round(data.kpis.healthScore)}%`} status={data.kpis.healthScore > 80 ? 'healthy' : 'warning'} trend="↑ +2%" desc="Overall team health improved from previous sprint." icon={<Activity />} />
          <KPICard title="Average Utilization" value={`${Math.round(data.kpis.utilization)}%`} status="healthy" trend="→" desc="Balanced workload distribution." icon={<PieChart />} />
          <KPICard title="Remaining Capacity" value={`${Math.round(data.kpis.remainingCapacity)}h`} status="healthy" trend="" desc="Available hours this sprint." icon={<Clock />} />
          <KPICard title="Dependency Risks" value={data.kpis.dependencyRisks.toString()} status={data.kpis.dependencyRisks > 0 ? 'critical' : 'healthy'} trend="" desc="Single points of failure in skills." icon={<AlertTriangle />} />
        </div>
      </section>

      {/* Operational Charts */}
      <section>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Operational Analytics</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 className="text-sm font-semibold text-gray-500 mb-4">Jira Status Distribution (Current Sprint)</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <RechartsPieChart>
                  <Pie
                    data={[
                      { name: 'To Do', value: data.issues.filter(i => i.status === 'To Do' || i.status === 'Selected for Development').length },
                      { name: 'In Progress', value: data.issues.filter(i => i.status === 'In Progress' || i.status === 'Code Review').length },
                      { name: 'Done', value: data.issues.filter(i => i.status === 'Done' || i.status === 'Released').length },
                      { name: 'Blocked', value: data.issues.filter(i => i.status === 'Blocked').length },
                    ]}
                    cx="50%" cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    { [0, 1, 2, 3].map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={['#cbd5e1', '#3b82f6', '#10b981', '#ef4444'][index % 4]} />
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

          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 className="text-sm font-semibold text-gray-500 mb-4">Capacity vs Utilization Trend</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data.historicalTrends}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="sprint" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                  <Tooltip cursor={{ fill: '#f8fafc' }} />
                  <Line type="monotone" dataKey="capacity" name="Effective Capacity" stroke="#8b5cf6" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                  <Line type="monotone" dataKey="utilization" name="Utilized Capacity" stroke="#3b82f6" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-center gap-4 text-xs text-gray-500 mt-2">
              <span className="flex items-center"><div className="w-3 h-3 bg-purple-500 rounded-full mr-1"></div>Effective Capacity</span>
              <span className="flex items-center"><div className="w-3 h-3 bg-blue-500 rounded-full mr-1"></div>Utilized Capacity</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <MiniKPI title="Critical Issues" value={data.kpis.criticalIssues} isAlert={data.kpis.criticalIssues > 5} />
          <MiniKPI title="Blocked Issues" value={data.kpis.blockedIssues} isAlert={data.kpis.blockedIssues > 2} />
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
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${team.healthScore > 80 ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}`}>
                      {team.healthScore > 80 ? 'Healthy' : 'Needs Attention'}
                    </span>
                    <span className="text-sm text-gray-500">{team.members} Members</span>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-y-4 gap-x-8 mb-6 flex-grow">
                <div><p className="text-xs text-gray-500 uppercase">Health</p><p className="font-semibold text-gray-900">{Math.round(team.healthScore)}%</p></div>
                <div><p className="text-xs text-gray-500 uppercase">Utilization</p><p className="font-semibold text-gray-900">{Math.round(team.utilization)}%</p></div>
                <div><p className="text-xs text-gray-500 uppercase">Velocity</p><p className="font-semibold text-gray-900">{team.velocity}</p></div>
                <div><p className="text-xs text-gray-500 uppercase">Critical/Blocked</p><p className="font-semibold text-gray-900">{team.criticalIssues} / {team.openIssues}</p></div>
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
                 <p className="text-2xl font-bold">{Math.round(data.forecast.averageCapacity)}h</p>
               </div>
               <div>
                 <p className="text-indigo-200 text-sm">Forecasted Demand</p>
                 <p className="text-2xl font-bold">{Math.round(data.forecast.averageVelocity)} SP</p>
               </div>
               <div className="pt-4 border-t border-indigo-800">
                 <p className="text-indigo-200 text-sm">Risk Assessment</p>
                 <div className="flex items-center space-x-2 mt-1">
                   {data.forecast.forecastRisk === 'High' ? <AlertTriangle className="w-5 h-5 text-red-400" /> : <CheckCircle className="w-5 h-5 text-emerald-400" />}
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
        {[...Array(8)].map((_, i) => (
          <div key={i} className="h-20 bg-gray-200 rounded-lg"></div>
        ))}
      </div>
    </section>
    <section>
      <div className="h-6 w-48 bg-gray-200 rounded mb-4"></div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {[...Array(2)].map((_, i) => (
          <div key={i} className="h-64 bg-gray-200 rounded-xl"></div>
        ))}
      </div>
    </section>
  </div>
);

export default DeliveryDashboard;
