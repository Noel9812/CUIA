import axios from 'axios';
import { LeadershipDashboardData, DeliveryDashboardData, TeamDetailsData, EngineerDetailsData } from '../types';

const api = axios.create({
  baseURL: '/api',
});

export const fetchLeadershipDashboard = async (): Promise<LeadershipDashboardData> => {
  const response = await api.get<LeadershipDashboardData>('/dashboard/leadership');
  return response.data;
};

export const fetchDeliveryDashboard = async (managerId: string): Promise<DeliveryDashboardData> => {
  const response = await api.get<DeliveryDashboardData>(`/dashboard/delivery?managerId=${managerId}`);
  return response.data;
};

export const fetchTeamDetails = async (teamId: string): Promise<TeamDetailsData> => {
  const response = await api.get<TeamDetailsData>(`/dashboard/team/${teamId}`);
  return response.data;
};

export const fetchEngineerDetails = async (engineerId: string): Promise<EngineerDetailsData> => {
  const response = await api.get<EngineerDetailsData>(`/dashboard/engineer/${engineerId}`);
  return response.data;
};

export const chatWithCopilot = async (
  question: string,
  persona: string = 'leadership',
  conversationContext?: Record<string, unknown>
) => {
  const response = await api.post('/copilot/chat', {
    question,
    persona,
    conversation_context: conversationContext ?? null,
  });
  return response.data;
};

export const downloadReport = async (type: string, persona: string) => {
  const response = await api.get(`/reports/download/${type}?persona=${persona}`, { responseType: 'blob' });
  return response.data;
};
