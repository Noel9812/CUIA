import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchLeadershipDashboard } from '../services/api';
import { LeadershipDashboardData } from '../types';
import { KPICard } from '../components/KPICards';
import { Users, Activity, TrendingUp, AlertTriangle, Bug, Target, Briefcase, ShieldAlert } from 'lucide-react';
import { TeamComparisonChart } from '../components/Charts';
import RecommendationsList from '../components/Recommendations';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

export default function LeadershipDashboard() {
  const [data, setData] = useState<LeadershipDashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchLeadershipDashboard()
      .then(setData)
      .catch(() => setError('Failed to load leadership dashboard.'));
  }, []);

  if (error) return <div className="p-8 text-center text-red-500">{error}</div>;
  if (!data) return <div className="p-8">Loading dashboard...</div>;

  const k = data.kpis;

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Executive Overview</h2>
        <p className="text-gray-500 mt-1">{k.name} — Organization-wide analytics and health metrics.</p>
      </div>

      {/* Executive KPIs — all values from backend */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard title="Total Engineers" value={k.totalEngineers} icon={<Users />} status="info" desc={`${k.teams} Teams • ${k.deliveryManagers} DMs`} />
        <KPICard title="Avg Utilization" value={`${k.overallUtilization.toFixed(1)}%`} icon={<Activity />} status={k.overallUtilization > 95 ? 'critical' : k.overallUtilization > 80 ? 'warning' : 'healthy'} desc="Organization-wide average" />
        <KPICard title="Estimation Accuracy" value={`${k.overallEstimationAccuracy.toFixed(1)}%`} icon={<Target />} status={k.overallEstimationAccuracy < 70 ? 'warning' : 'healthy'} />
        <KPICard title="Burnout Risks" value={k.burnoutRiskCount} icon={<AlertTriangle />} status={k.burnoutRiskCount > 0 ? 'critical' : 'healthy'} desc="Engineers at high risk" />
        <KPICard title="Active Sprints" value={k.activeSprints} icon={<Briefcase />} status="info" />
        <KPICard title="Critical Issues" value={k.criticalJiraIssues} icon={<Bug />} status={k.criticalJiraIssues > 5 ? 'critical' : k.criticalJiraIssues > 0 ? 'warning' : 'healthy'} />
        <KPICard title="Org Health Score" value={k.overallTeamHealth.toFixed(0)} icon={<TrendingUp />} status={k.overallTeamHealth < 70 ? 'warning' : 'healthy'} desc="Avg team health /100" />
        <KPICard title="Underutilized" value={k.idleEngineers} icon={<Users />} status={k.idleEngineers > 0 ? 'warning' : 'healthy'} desc="Engineers < 60% util" />
      </div>

      {/* Historical Trend Graphs — data from sprintAggregates */}
      <div>
        <h3 className="text-xl font-bold mb-4 text-gray-800">Organization Historical Trends</h3>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Capacity vs Logged Hours */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h4 className="text-sm font-semibold text-gray-500 mb-4">Capacity vs Logged Hours (per Sprint)</h4>
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

          {/* Velocity Trend */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h4 className="text-sm font-semibold text-gray-500 mb-4">Velocity Trend (Story Points per Sprint)</h4>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data.historicalTrends}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="sprint" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                  <Tooltip cursor={{ fill: '#f8fafc' }} />
                  <Legend />
                  <Line type="monotone" dataKey="velocity" name="Velocity (SP)" stroke="#10b981" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>

      {/* Utilization % Trend + Completion Rate */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h4 className="text-sm font-semibold text-gray-500 mb-4">Utilization % Trend</h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.historicalTrends}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="sprint" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} domain={[0, 'auto']} />
                <Tooltip cursor={{ fill: '#f8fafc' }} />
                <Legend />
                <Line type="monotone" dataKey="utilization" name="Utilization %" stroke="#f59e0b" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                <Line type="monotone" dataKey="completionRate" name="Completion Rate %" stroke="#06b6d4" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Forecast Summary */}
        <div className="bg-indigo-900 text-white rounded-xl shadow-sm p-6">
          <h4 className="text-lg font-semibold mb-4">Forecast Outlook</h4>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-indigo-200 text-sm">Current Capacity</p>
                <p className="text-2xl font-bold">{Math.round(data.forecast.currentCapacity)}h</p>
              </div>
              <div>
                <p className="text-indigo-200 text-sm">Avg Velocity</p>
                <p className="text-2xl font-bold">{data.forecast.averageVelocity} SP</p>
              </div>
              <div>
                <p className="text-indigo-200 text-sm">Velocity Trend</p>
                <p className="text-lg font-semibold capitalize">{data.forecast.trendAnalysis.velocityDirection}</p>
              </div>
              <div>
                <p className="text-indigo-200 text-sm">Capacity Gap</p>
                <p className="text-lg font-semibold">{Math.round(data.forecast.capacityGap)}h</p>
              </div>
            </div>
            <div className="pt-4 border-t border-indigo-800">
              <p className="text-indigo-200 text-sm mb-1">Forecast Risk</p>
              <div className="flex items-center space-x-2">
                {data.forecast.forecastRisk === 'Low' ? (
                  <span className="px-3 py-1 rounded-full text-sm font-medium bg-emerald-500/20 text-emerald-200">{data.forecast.forecastRisk}</span>
                ) : (
                  <span className="px-3 py-1 rounded-full text-sm font-medium bg-red-500/20 text-red-200">{data.forecast.forecastRisk}</span>
                )}
                <span className="text-indigo-300 text-sm">({data.forecast.trendAnalysis.sprintsAnalyzed} sprints analyzed)</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Team Health Comparison & Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold mb-4">Team Health Comparison</h3>
          <TeamComparisonChart teams={data.teams} />
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 max-h-96 overflow-y-auto">
          <h3 className="text-lg font-semibold mb-4">Strategic Recommendations</h3>
          <RecommendationsList recommendations={data.recommendations} />
        </div>
      </div>

      {/* Team Overview Cards */}
      <div>
        <h3 className="text-xl font-bold mb-4 text-gray-800">Team Overview</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {data.teams.map(team => (
            <div
              key={team.id}
              onClick={() => navigate(`/team/${team.id}`)}
              className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:border-indigo-500 cursor-pointer transition-all hover:shadow-md"
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h4 className="text-lg font-bold text-gray-900">{team.name}</h4>
                  <p className="text-sm text-gray-500">{team.members} Members</p>
                </div>
                <div className={`px-3 py-1 rounded-full text-xs font-bold ${team.healthScore < 70 ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
                  {team.healthScore < 70 ? 'At Risk' : 'Healthy'}
                </div>
              </div>
              <div className="space-y-2 mt-4 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Utilization</span>
                  <span className="font-semibold">{team.utilization.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Velocity</span>
                  <span className="font-semibold">{team.velocity} SP</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Est. Accuracy</span>
                  <span className="font-semibold">{team.estimationAccuracy.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between text-red-600">
                  <span>Burnout Risk</span>
                  <span className="font-semibold">{team.burnoutRisk} engineers</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
