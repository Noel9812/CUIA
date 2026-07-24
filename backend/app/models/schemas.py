from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Issue(BaseModel):
    issueKey: str
    summary: str
    description: str
    issueType: str
    priority: str
    storyPoints: Optional[int] = 0
    originalEstimate: Optional[float] = 0
    remainingEstimate: Optional[float] = 0
    loggedHours: Optional[float] = 0
    status: str
    reporter: str
    assignee: Optional[str] = None
    sprint: Optional[str] = None
    createdTime: str
    startedTime: Optional[str] = None
    resolvedTime: Optional[str] = None
    labels: List[str]
    blocked: bool
    dependencies: List[str]
    parentEpic: Optional[str] = None

class Engineer(BaseModel):
    id: str
    name: str
    designation: str
    experience: int
    employmentType: str
    managerId: str
    teamId: str
    workingHoursPerWeek: float
    leaveHours: float
    meetingHours: float
    trainingHours: float
    effectiveCapacity: float
    location: str
    availabilityStatus: str
    primarySkills: List[str]
    secondarySkills: List[str]
    learningSkills: List[str]
    technologyOwnership: List[str]
    crossTrainingCandidates: List[str]
    certifications: List[str]
    currentSprint: str
    roleLevel: str

class Team(BaseModel):
    id: str
    name: str
    managerId: str

class DeliveryManager(BaseModel):
    id: str
    name: str

class Organization(BaseModel):
    name: str

class Dataset(BaseModel):
    organization: Organization
    deliveryManagers: List[DeliveryManager]
    teams: List[Team]
    engineers: List[Engineer]
    issues: List[Issue]

class Recommendation(BaseModel):
    severity: str
    businessRule: str
    supportingMetrics: Dict[str, Any]
    reason: str
    businessImpact: str
    suggestedAction: str
    expectedOutcome: str
    confidence: str
    sourceAnalytics: str

class ChatRequest(BaseModel):
    question: str
    persona: str = "leadership"

class ChatResponse(BaseModel):
    answer: str
