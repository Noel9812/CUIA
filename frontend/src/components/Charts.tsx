import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer, LineChart, Line
} from 'recharts';
import { Team, Engineer } from '../types';

export function TeamComparisonChart({ teams }: { teams: Team[] }) {
  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={teams} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
          <XAxis dataKey="name" axisLine={false} tickLine={false} />
          <YAxis axisLine={false} tickLine={false} />
          <RechartsTooltip cursor={{fill: 'transparent'}} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
          <Legend />
          <Bar dataKey="utilization" name="Utilization %" fill="#4f46e5" radius={[4, 4, 0, 0]} />
          <Bar dataKey="productivity" name="Productivity %" fill="#10b981" radius={[4, 4, 0, 0]} />
          <Bar dataKey="healthScore" name="Health Score" fill="#f59e0b" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function EngineerUtilizationChart({ engineers }: { engineers: Engineer[] }) {
  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={engineers} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
          <XAxis dataKey="name" axisLine={false} tickLine={false} />
          <YAxis axisLine={false} tickLine={false} />
          <RechartsTooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
          <Legend />
          <Line type="monotone" dataKey="utilization" name="Utilization %" stroke="#ef4444" strokeWidth={3} activeDot={{ r: 8 }} />
          <Line type="monotone" dataKey="productivity" name="Productivity %" stroke="#3b82f6" strokeWidth={3} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
