export interface Organization {
  name: string;
}

export interface Engineer {
  id: string;
  name: string;
  designation: string;
  experience: number;
  teamId: string;
  employmentType: string;
  location: string;
  availabilityStatus: string;
  primarySkills: string[];
  secondarySkills: string[];
  crossTrainingSkills: string[];
  availableHours: number;
  sprintCapacity: number;
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
  burnoutRisk: string;
  sprintCompletion: number;
  historicalUtilization: number;
  historicalVelocity: number;
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
  blockedIssues: number;
  members: number;
  velocity: number;
  averageResolutionTime: number;
  sprintCompletion: number;
  forecastStatus: string;
}

export interface Issue {
  issueKey: string;
  summary: string;
  description: string;
  issueType: string;
  priority: string;
  status: string;
  sprint: string | null;
  assignee: string | null;
  reporter: string;
  originalEstimate: number;
  remainingEstimate: number;
  loggedHours: number;
  storyPoints: number;
  createdTime: string;
  startedTime: string | null;
  resolvedTime: string | null;
  blocked: boolean;
  dependencies: string[];
  labels: string[];
  parentEpic: string | null;
}

export interface Recommendation {
  severity: string;
  businessRule: string;
  reason: string;
  supportingMetrics: Record<string, any>;
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

/** Matches backend ForecastEngine org forecast response */
export interface OrgForecast {
  currentCapacity: number;
  averageVelocity: number;
  averageUtilization: number;
  velocityTrend: number;
  utilizationTrend: number;
  capacityGap: number;
  forecastRisk: string;
  futureSprints: FutureSprint[];
  trendAnalysis: {
    velocityDirection: string;
    utilizationDirection: string;
    sprintsAnalyzed: number;
  };
}

export interface FutureSprint {
  sprint: string;
  projectedVelocity: number;
  projectedUtilization: number;
  projectedCapacity: number;
  risk: string;
}

/** Matches backend ForecastEngine manager/team forecast response */
export interface ScopedForecast {
  teamId?: string;
  managerId?: string;
  currentCapacity: number;
  averageVelocity: number;
  averageUtilization: number;
  capacityGap: number;
  forecastRisk: string;
  forecastDemand?: number;
}

/** Matches backend sprintAggregates structure */
export interface SprintAggregate {
  sprint: string;
  capacity: number;
  loggedHours: number;
  utilization: number;
  velocity: number;
  totalIssues: number;
  resolvedIssues: number;
  activeIssues: number;
  completionRate: number;
}

export interface LeadershipDashboardData {
  kpis: {
    name: string;
    totalEngineers: number;
    deliveryManagers: number;
    teams: number;
    activeJiraIssues: number;
    activeSprints: number;
    overallUtilization: number;
    overallProductivity: number;
    overallEstimationAccuracy: number;
    overallTeamHealth: number;
    burnoutRiskCount: number;
    idleEngineers: number;
    criticalJiraIssues: number;
    blockedIssues: number;
    dependencyRisks: number;
    averageResolutionTime?: number;
  };
  historicalTrends: SprintAggregate[];
  teams: Team[];
  forecast: OrgForecast;
  recommendations: Recommendation[];
}

export interface DeliveryDashboardData {
  kpis: DeliveryManagerKPIs;
  forecast: ScopedForecast;
  historicalTrends: SprintAggregate[];
  teams: Team[];
  engineers: Engineer[];
  recommendations: Recommendation[];
  issues: Issue[];
}

export interface TeamDetailsData {
  team: Team;
  engineers: Engineer[];
  issues: Issue[];
  recommendations: Recommendation[];
  forecast: ScopedForecast;
  skills: SkillCoverage[];
}

export interface SkillCoverage {
  technology: string;
  coverage: number;
  risk: string;
  candidate: string;
  owner: string;
}

export interface EngineerDetailsData {
  engineer: Engineer;
  issues: Issue[];
  recommendations: Recommendation[];
}

export type Persona = 'leadership' | 'dm-1' | 'dm-2';
