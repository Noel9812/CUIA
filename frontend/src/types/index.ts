export interface Organization {
  name: string;
}

export interface Engineer {
  id: string;
  name: string;
  designation: string;
  experience: number;
  teamId: string;
  primarySkills: string[];
  secondarySkills: string[];
  crossTrainingSkills: string[];
  availableHours: number;
  utilization: number;
  productivity: number;
  activeTickets: number;
  criticalIssues: number;
  blockedTickets: number;
  storyPoints: number;
  velocity: number;
  estimationAccuracy: number;
  loggedHours: number;
  health: number;
  averageResolutionTime: number;
}

export interface Team {
  id: string;
  name: string;
  managerId: string;
  utilization: number;
  productivity: number;
  healthScore: number;
  estimationAccuracy: number;
  criticalIssues: number;
  burnoutRisk: number;
  dependencyRisk: number;
  openIssues: number;
  members: number;
  velocity: number;
  averageResolutionTime: number;
  forecastStatus: string;
}

export interface Issue {
  issueKey: string;
  summary: string;
  issueType: string;
  priority: string;
  status: string;
  sprint: string | null;
  assignee: string;
  originalEstimate: number;
  remainingEstimate: number;
  loggedHours: number;
  storyPoints: number;
  createdTime: string;
  resolvedTime: string | null;
  blocked: boolean;
}

export interface Recommendation {
  severity: string;
  businessRule: string;
  reason: string;
  supportingMetrics: any;
  businessImpact: string;
  suggestedAction: string;
  expectedOutcome: string;
  confidence: string;
  sourceAnalytics: string;
}

export interface DeliveryManagerKPIs {
  healthScore: number;
  utilization: number;
  remainingCapacity: number;
  forecastCapacityGap: number;
  burnoutRiskCount: number;
  dependencyRisks: number;
  productivity: number;
  velocity: number;
  storyPoints: number;
  sprintCompletion: number;
  estimationAccuracy: number;
  averageResolutionTime: number;
  criticalIssues: number;
  blockedIssues: number;
}

export interface Forecast {
  averageCapacity: number;
  averageVelocity: number;
  forecastRisk: string;
  forecastDemand?: number; // adding this for ui mock
}

export interface HistoricalTrend {
  sprint: string;
  capacity: number;
  utilization: number;
}

export interface DeliveryDashboardData {
  kpis: DeliveryManagerKPIs;
  forecast: Forecast;
  historicalTrends: HistoricalTrend[];
  teams: Team[];
  engineers: Engineer[];
  recommendations: Recommendation[];
  issues: Issue[];
}

export interface LeadershipDashboardData {
  kpis: any;
  historicalTrends: HistoricalTrend[];
  teams: Team[];
  recommendations: Recommendation[];
}

export interface TeamDetailsData {
  team: Team;
  engineers: Engineer[];
  issues: Issue[];
  recommendations: Recommendation[];
  forecast: Forecast;
  skills: any[];
}

export interface EngineerDetailsData {
  engineer: Engineer;
  issues: Issue[];
  recommendations: Recommendation[];
}

export type Persona = 'leadership' | 'dm-1' | 'dm-2';
