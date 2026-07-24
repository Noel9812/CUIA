import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchLeadershipDashboard } from '../services/api';
import { LeadershipDashboardData } from '../types';
import { KPICard } from '../components/KPICards';
import { Users, Activity, TrendingUp, AlertTriangle, Bug, Target, Briefcase } from 'lucide-react';
import { TeamComparisonChart } from '../components/Charts';
import RecommendationsList from '../components/Recommendations';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function LeadershipDashboard() {
  const [data, setData] = useState<LeadershipDashboardData | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchLeadershipDashboard().then(setData);
  }, []);

  if (!data) return <div className="p-8">Loading dashboard...</div>;

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Executive Overview</h2>
        <p className="text-gray-500 mt-1">Organization-wide analytics and health metrics.</p>
      </div>

      {/* 1. Executive KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard title="Total Engineers" value={data.kpis.totalEngineers} icon={<Users />} status="info" desc={`${data.kpis.teams} Teams`} />
        <KPICard title="Avg Utilization" value={`${data.kpis.overallUtilization.toFixed(1)}%`} icon={<Activity />} status={data.kpis.overallUtilization > 95 ? 'critical' : 'healthy'} desc="Target: 80%" />
        <KPICard title="Estimation Accuracy" value={`${data.kpis.overallEstimationAccuracy.toFixed(1)}%`} icon={<Target />} status="info" />
        <KPICard title="Burnout Risks" value={data.kpis.burnoutRiskCount} icon={<AlertTriangle />} status={data.kpis.burnoutRiskCount > 0 ? 'critical' : 'healthy'} desc="Engineers > 95% util" />
        <KPICard title="Active Sprints" value={data.kpis.activeSprints} icon={<Briefcase />} status="info" />
        <KPICard title="Critical Issues" value={data.kpis.criticalJiraIssues} icon={<Bug />} status={data.kpis.criticalJiraIssues > 10 ? 'warning' : 'healthy'} />
        <KPICard title="Org Health Score" value={data.kpis.overallTeamHealth.toFixed(0)} icon={<TrendingUp />} status="healthy" />
        <KPICard title="Underutilized" value={data.kpis.idleEngineers} icon={<Users />} status="warning" desc="Engineers < 60% util" />
      </div>

      {/* 2. Organization Trend Graphs */}
      <div>
        <h3 className="text-xl font-bold mb-4 text-gray-800">Organization Historical Trends</h3>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h4 className="text-sm font-semibold text-gray-500 mb-4">Organization Capacity vs Utilization</h4>
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
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h4 className="text-sm font-semibold text-gray-500 mb-4">Organization Productivity Trend</h4>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data.historicalTrends}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="sprint" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                  <Tooltip cursor={{ fill: '#f8fafc' }} />
                  <Line type="monotone" dataKey="productivity" name="Weighted Productivity" stroke="#10b981" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Organization Health Graph & 5. Strategic Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold mb-4">Organization Health</h3>
          <TeamComparisonChart teams={data.teams} />
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 max-h-96 overflow-y-auto">
          <h3 className="text-lg font-semibold mb-4">Strategic Recommendations</h3>
          <RecommendationsList recommendations={data.recommendations} />
        </div>
      </div>

      {/* 4. Team Overview */}
      <div className="mt-8">
        <h3 className="text-xl font-bold mb-4 text-gray-800">Team Overview</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
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
                  {team.healthScore < 70 ? 'Critical' : 'Healthy'}
                </div>
              </div>
              <div className="space-y-2 mt-4 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Utilization</span>
                  <span className="font-semibold">{team.utilization.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Est. Accuracy</span>
                  <span className="font-semibold">{team.estimationAccuracy.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between text-red-600">
                  <span>Burnout Risk</span>
                  <span className="font-semibold">{team.burnoutRisk} engineers</span>
                </div>
                <div className="flex justify-between text-orange-600">
                  <span>Critical Issues</span>
                  <span className="font-semibold">{team.criticalIssues}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
