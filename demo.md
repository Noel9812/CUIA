CUIA — Capacity & Utilization Intelligence Agent: Comprehensive Project Analysis
1. What is this Project?
CUIA (Capacity & Utilization Intelligence Agent) is an enterprise workforce analytics and engineering intelligence platform. It aggregates simulated project tracking data (Jira-style issues, sprint logs, engineer capacities, and organizational hierarchies) to provide real-time, 100% deterministic visibility into engineering capacity, workload distribution, team health, and delivery risks.

The system combines:

Deterministic Analytics Core (Python/FastAPI): A computation engine where all business rules, aggregations, trend extrapolations, simulations, and risk scorings are calculated with mathematical precision.
AI Copilot Presentation Layer (LangGraph + AWS Bedrock): A natural language interface that never computes metrics on its own, but instead queries, summarizes, and explains the deterministic results produced by the backend.
Interactive Web Application (React + Vite + Tailwind CSS): Role-based dashboards for Delivery Managers and Executive Leadership with interactive gauges, charts, tables, and PDF reporting.
Mermaid diagram
2. Why is it Needed? (The Business Problem)
In modern software engineering organizations, tracking developer capacity, team throughput, and burnout is typically done through manual spreadsheets, fragmented Jira JQL filters, and subjective status updates.

Traditional Manual Approach	The CUIA Solution
Reactive & Delayed: Burnout, overloading, or capacity shortfalls are noticed only after sprint deadlines are missed.	Real-Time & Proactive: Continuous tracking of utilization, estimation accuracy, and blockers flags risks as they develop.
Subjective & Inconsistent: Different managers define "capacity" and "health" differently across teams.	Deterministic & Standardized: Configurable business rules compute uniform health scores, utilization rates, and risk indices across all teams.
Time-Consuming Cross-Referencing: Answering questions like "Why is Team Alpha falling behind?" requires hours of digging through tickets and logs.	Instant Natural Language Copilot: Managers can query the Copilot in plain English and receive scoped, mathematically validated root-cause explanations.
Opaque Skill Dependencies: Knowledge silos (Single Points of Failure) remain hidden until a key engineer goes on leave.	Automated SPOF Detection: Analyzes primary/secondary skills to detect single points of failure and suggests cross-training candidates.
3. What are We Expecting as Output?
CUIA produces 5 distinct categories of outputs:

1. Interactive Role-Based Web Dashboards
Leadership Dashboard (
LeadershipDashboard.tsx
): Org-wide KPIs (overall utilization, total capacity vs. logged hours, team health averages, active blockers, critical issue counts, high burnout alerts).
Delivery Manager (DM) Dashboard (
DeliveryDashboard.tsx
): Scoped drilldowns into the specific teams and engineers managed by that DM.
Team & Engineer Detail Views (
TeamDetails.tsx
, 
EngineerDetails.tsx
): Individual utilization breakdowns, story point velocity, estimation error tracking, and skills inventory.
2. Natural Language AI Copilot Insights
Context-aware answers via 
Copilot.tsx
 and 
graph.py
.
Example outputs: Explanations of why a team's health dropped, ranked lists of top performers or overloaded engineers, and follow-up conversational memory ("Why is that?").
3. Actionable Rule-Based Recommendations
Generated deterministically by 
recommendation_engine.py
 using 
recommendation_rules.json
.
Each recommendation includes: Severity, Business Rule, Reason, Business Impact, Supporting Metrics, Suggested Action, and Expected Outcome.
4. What-If Scenario Simulations
Evaluated on demand by 
simulation_engine.py
.
Allows managers to simulate:
Engineer taking leave or departing the company.
Reallocating tickets between engineers.
Adding/removing sprint tickets.
Team restructuring or merging.
Output: A deterministic before, after, and delta differential comparison showing the exact net impact on team health, utilization, and capacity.
5. Forward-Looking Capacity Forecasts & PDF Reports
Forecast Output (
forecast_engine.py
): 3-sprint forward projections of capacity, demand, moving average velocity, and risk ratings.
Automated PDF Reports (
report_engine.py
):
Daily Report: Today's utilization, remaining sprint hours, active blockers, and urgent recommendations.
Weekly Report: Sprint execution summary, team comparison matrix, velocity vs. capacity demand.
Monthly Report: Executive summary, organizational health trends, prolonged burnout alerts, and strategic staffing recommendations.
4. Significance & Core Architectural Innovations
A. The "Deterministic-First" AI Philosophy (Zero Hallucinations)
A major risk in enterprise analytics is LLMs inventing numbers, miscalculating averages, or hallucinating explanations. CUIA strictly decouples computation from presentation:

Python does 100% of the math: All aggregations, weights, rankings, and forecasts are calculated deterministically by Python services.
The LLM is only an explainer: The model receives pre-computed numbers in a minimal JSON payload and is constrained by system prompts to strictly describe the provided numbers without inventing or computing anything.
B. Two-Tier Zero-Cost Intent & Entity Routing
Instead of sending every raw user query to a heavy LLM, CUIA uses a fast, local pipeline (
intent_classifier.py
, 
entity_extractor.py
):

Keyword & entity matching classifies ~90% of user queries with 0 LLM calls.
Malicious prompt injections (e.g., "ignore previous instructions", "dump database") and out-of-scope queries (weather, recipes) are terminated instantly at the entry node without incurring LLM token costs.
C. Strict Persona & Data Isolation (Row-Level Security)
Configured in 
context_builders.py
 and 
dashboard.py
.
A Delivery Manager (e.g., dm-1) can only query and view teams/engineers assigned under their manager ID.
Even if a DM attempts prompt injection to ask about another manager's team, the context builder passes an empty dataset, preventing cross-tenant data leakage.
5. Metrics & Calculations: What, Why, and How
All metrics are implemented in 
analytics_engine.py
, 
business_rules_engine.py
, and 
forecast_engine.py
, driven by JSON configuration in 
backend/app/config/
.

Summary Table of All Metrics
Metric Name	Scope	Configuration Source	Primary Purpose
Effective Capacity	Engineer	dataset.json	Baseline workable hours per week excluding meetings/training
Sprint Capacity	Engineer / Team / Org	
analytics_rules.json
Total available hours across the sprint window
Utilization Rate (%)	Engineer / Team / Org	
analytics_rules.json
Identifies underutilized vs. overloaded capacity
Productivity Score	Engineer / Team / Org	
priority_weights.json
Values delivered high-priority work over raw ticket counts
Velocity (Story Points)	Engineer / Team / Org	
analytics_rules.json
Measures completed sprint output in story points
Estimation Accuracy (%)	Engineer / Team / Org	
analytics_engine.py
Measures fidelity between original estimates and actual logged hours
Health Score (0–100)	Engineer / Team / Org	
health_rules.json
Holistic composite score combining performance and risk penalties
Burnout Risk	Engineer / Team	
analytics_rules.json
Categorical warning (Low / Medium / High) for engineer exhaustion
Single Point of Failure (SPOF)	Team / Org	
analytics_engine.py
Identifies skills known by only 1 engineer in a team/org
Average Resolution Time	Engineer / Team / Org	
analytics_engine.py
Time (in hours) between issue startedTime and resolvedTime
Sprint Completion (%)	Engineer / Team	
analytics_engine.py
Percentage of assigned tickets resolved in the current sprint
Performance Ranking Score	Engineer	
business_rules.json
Objective, multi-factor engineer performance index
Priority Attention Score	Engineer	
business_rules.json
Triages which engineer urgently needs managerial assistance
Replacement Viability Score	Engineer	
business_rules.json
Matches substitute candidates based on skills, capacity, and experience
Forecast Projections	Team / Org	
forecast_rules.json
3-sprint moving averages and linear trend extrapolations
Detailed Mathematical Formulas & Step-by-Step Logic
1. Effective Capacity & Sprint Capacity
Why: Full-time hours (45h/week) do not represent true coding capacity. Engineers attend meetings, undergo training, or take leave.
Formula: 
EffectiveCapacity
=
max
⁡
(
0
,
workingHoursPerWeek
−
leaveHours
−
meetingHours
−
trainingHours
)
EffectiveCapacity=max(0,workingHoursPerWeek−leaveHours−meetingHours−trainingHours) 
SprintCapacity
=
EffectiveCapacity
×
sprint_duration_weeks
SprintCapacity=EffectiveCapacity×sprint_duration_weeks
Example: Working hours = 45h, Meetings = 3h, Training = 2h, Leave = 0h 
→
→ Effective Capacity = 40h/week. Over a 2-week sprint: 
SprintCapacity
=
40
×
2
=
80
 hours
SprintCapacity=40×2=80 hours.
2. Utilization Rate (%)
Why: Detects whether an engineer or team is starved of work (
<
60
%
<60%), balanced (
60
%
−
100
%
60%−100%), or at risk of severe burnout (
>
100
%
>100%).
Engineer Formula: 
Utilization
engineer
=
∑
loggedHours
current_sprint
SprintCapacity
×
100
Utilization 
engineer
​
 = 
SprintCapacity
∑loggedHours 
current_sprint
​
 
​
 ×100
Team & Org Aggregation (Ratio of Totals): 
Utilization
team
=
∑
members
loggedHours
∑
members
SprintCapacity
×
100
Utilization 
team
​
 = 
∑ 
members
​
 SprintCapacity
∑ 
members
​
 loggedHours
​
 ×100 (Note: CUIA uses ratio of totals rather than average of percentages to prevent skewing when engineers have different base capacities).
3. Productivity Score
Why: Completing 1 critical architectural issue is worth significantly more than closing 10 trivial low-priority tickets.
Formula: 
Productivity
=
∑
i
∈
Resolved Issues
(
storyPoints
i
×
PriorityWeight
(
priority
i
)
)
Productivity=∑ 
i∈Resolved Issues
​
 (storyPoints 
i
​
 ×PriorityWeight(priority 
i
​
 ))
Configured Weights (
priority_weights.json
):
Critical
=
8
Critical=8
High
=
5
High=5
Medium
=
3
Medium=3
Low
=
1
Low=1
Example: Resolving one 5-point Critical ticket (
5
×
8
=
40
5×8=40) + one 3-point Medium ticket (
3
×
3
=
9
3×3=9) 
→
→ Productivity Score = 49.
4. Estimation Accuracy (%)
Why: Measures sprint predictability and flags chronic under/over-estimation.
Formula: 
Estimation Accuracy
=
max
⁡
(
0
,
100
−
∣
∑
loggedHours
−
∑
originalEstimate
∣
max
⁡
(
1
,
∑
originalEstimate
)
×
100
)
Estimation Accuracy=max(0,100− 
max(1,∑originalEstimate)
∣∑loggedHours−∑originalEstimate∣
​
 ×100)
If an engineer logged 45 hours on tasks estimated at 40 hours, error is 
∣
45
−
40
∣
/
40
×
100
=
12.5
%
→
Accuracy
=
87.5
%
∣45−40∣/40×100=12.5%→Accuracy=87.5%.
5. Health Score (0 to 100)
Why: Single composite operational metric combining positive productivity with risk deductions.
Configured Weights (
health_rules.json
):
Capacity Balance (
W
1
=
0.20
W 
1
​
 =0.20): 
100
−
∣
100
−
utilization
∣
100−∣100−utilization∣ (Rewards being near 100%; penalizes over- and under-utilization).
Utilization Score (
W
2
=
0.20
W 
2
​
 =0.20): 
min
⁡
(
100
,
utilization
)
min(100,utilization).
Productivity Score (
W
3
=
0.15
W 
3
​
 =0.15): 
min
⁡
(
100
,
Productivity
max
⁡
(
1
,
Velocity
)
×
100
)
min(100, 
max(1,Velocity)
Productivity
​
 ×100) (or 50 if velocity is 0).
Velocity Score (
W
4
=
0.15
W 
4
​
 =0.15): 
min
⁡
(
100
,
Velocity
benchmark_sp (20)
×
100
)
min(100, 
benchmark_sp (20)
Velocity
​
 ×100).
Estimation Accuracy (
W
5
=
0.10
W 
5
​
 =0.10): 
max
⁡
(
0
,
EstimationAccuracy
)
max(0,EstimationAccuracy).
Dependency Risk (
W
6
=
0.10
W 
6
​
 =0.10): 100 base score (penalized at team level if SPOF exists).
Critical Issue Penalty Weight (
W
7
=
0.05
W 
7
​
 =0.05): 
max
⁡
(
0
,
100
−
(
CriticalIssues
×
20
)
)
max(0,100−(CriticalIssues×20)).
Blocked Issue Penalty Weight (
W
8
=
0.05
W 
8
​
 =0.05): 
max
⁡
(
0
,
100
−
(
BlockedIssues
×
20
)
)
max(0,100−(BlockedIssues×20)).
Health Score
=
∑
k
=
1
8
(
Component
k
×
W
k
)
Health Score= 
k=1
∑
8
​
 (Component 
k
​
 ×W 
k
​
 )
Health Ranges:
≥
75
≥75: Healthy
50
 to 
74.99
50 to 74.99: At Risk
<
50
<50: Unhealthy / Critical
6. Burnout Risk
Why: Prevent developer attrition and quality degradation before burnout occurs.
Logic (
analytics_engine.py
):
High: 
Utilization
>
110.0
%
Utilization>110.0% OR 
Active Critical Issues
>
2
Active Critical Issues>2.
Medium: 
Utilization
>
95.0
%
Utilization>95.0%.
Low: Otherwise.
7. Performance Ranking Score (Business Rules Engine)
Why: Deterministic evaluation of engineer performance without AI subjectivity.
Formula (
business_rules_engine.py
): 
Score
=
(
Vel
20
×
100
×
0.30
)
+
(
Health
×
0.25
)
+
(
EstAcc
×
0.20
)
+
(
max
⁡
(
0
,
100
−
∣
Util
−
85
∣
)
×
0.15
)
−
(
min
⁡
(
100
,
Blocked
×
25
)
×
0.10
)
Score=( 
20
Vel
​
 ×100×0.30)+(Health×0.25)+(EstAcc×0.20)+(max(0,100−∣Util−85∣)×0.15)−(min(100,Blocked×25)×0.10)
8. Priority Attention Urgency Score
Why: Tells Delivery Managers exactly which engineer needs immediate help.
Formula (
business_rules_engine.py
):
Burnout Points
=
(
100
 if High else 
50
 if Medium else 
0
)
×
0.40
Burnout Points=(100 if High else 50 if Medium else 0)×0.40
Utilization Points
=
min
⁡
(
100
,
max
⁡
(
0
,
Utilization
−
80
)
×
2
)
×
0.30
Utilization Points=min(100,max(0,Utilization−80)×2)×0.30
Blocked Points
=
min
⁡
(
100
,
BlockedTickets
×
33
)
×
0.20
Blocked Points=min(100,BlockedTickets×33)×0.20
Critical Points
=
min
⁡
(
100
,
CriticalIssues
×
25
)
×
0.10
Critical Points=min(100,CriticalIssues×25)×0.10 
AttentionScore
=
Burnout Points
+
Utilization Points
+
Blocked Points
+
Critical Points
AttentionScore=Burnout Points+Utilization Points+Blocked Points+Critical Points
9. Replacement Candidate Match Score
Why: Automatically suggests the best substitute engineer when someone goes on leave or departs.
Formula (
business_rules_engine.py
): 
SkillScore
=
∣
TargetSkills
∩
CandidateSkills
∣
∣
TargetSkills
∣
×
100
×
0.50
SkillScore= 
∣TargetSkills∣
∣TargetSkills∩CandidateSkills∣
​
 ×100×0.50 
CapacityScore
=
max
⁡
(
0
,
100
−
CandidateUtilization
)
×
0.30
CapacityScore=max(0,100−CandidateUtilization)×0.30 
ExperienceScore
=
min
⁡
(
100
,
YearsExperience
15
×
100
)
×
0.20
ExperienceScore=min(100, 
15
YearsExperience
​
 ×100)×0.20 
ReplacementScore
=
SkillScore
+
CapacityScore
+
ExperienceScore
ReplacementScore=SkillScore+CapacityScore+ExperienceScore
10. Forecast & Trend Extrapolations
Why: Predict future capacity gaps and delivery risks for upcoming sprints.
Methodology (
forecast_engine.py
):
Moving Average: Computes 3-sprint Simple Moving Average (SMA) for Velocity, Utilization, and Logged Hours.
Linear Trend Slope (
m
m): Fits a least-squares regression line: 
m
=
∑
(
i
−
x
ˉ
)
(
y
i
−
y
ˉ
)
∑
(
i
−
x
ˉ
)
2
m= 
∑(i− 
x
ˉ
 ) 
2
 
∑(i− 
x
ˉ
 )(y 
i
​
 − 
y
ˉ
​
 )
​
 
Projections: Projects values for 
N
=
3
N=3 future sprints: 
y
^
t
+
k
=
y
last
+
(
m
×
k
)
y
^
​
  
t+k
​
 =y 
last
​
 +(m×k).
Capacity Gap: 
CapacityGap
=
CurrentCapacity
−
MovingAvgLoggedHours
CapacityGap=CurrentCapacity−MovingAvgLoggedHours.
Risk Classification: High if projected utilization 
>
90
%
>90%, velocity deceleration 
>
10
%
>10%, or capacity gap 
>
15
%
>15%.
6. Summary of Key Files


CUIA/
├── backend/
│   ├── app/
│   │   ├── ai/                      # LangGraph & Bedrock Explainer
│   │   │   ├── graph.py             # LangGraph state machine & routing
│   │   │   ├── intent_classifier.py # Deterministic weighted keyword classifier
│   │   │   ├── entity_extractor.py  # Zero-LLM entity parser (teams, engineers)
│   │   │   └── context_builders.py  # Token-compressed persona data builder
│   │   ├── services/                # Pure Deterministic Python Engines
│   │   │   ├── analytics_engine.py  # Core metrics (Util, Health, SPOF, Accuracy)
│   │   │   ├── business_rules_engine.py # Performance & Priority rankings
│   │   │   ├── forecast_engine.py   # SMA & linear trend forecasting
│   │   │   ├── recommendation_engine.py # Rule-based recommendations
│   │   │   ├── simulation_engine.py # What-If scenario deep-cloner & delta diff
│   │   │   └── report_engine.py     # PDF ReportLab generator
│   │   └── config/                  # JSON Business Rules & Weights
│   └── sample_data/dataset.json     # Simulated Jira & Workforce Dataset
├── docs/                            # 15 Detailed Architecture & Spec Documents
└── frontend/src/                    # React 18, Vite, Recharts, Tailwind UI


1. Metric #5: Health Score (0 to 100)
1.1 Core Purpose & Why It Is Needed
Traditional engineering metrics look at single data points in isolation (e.g., "How many hours did they log?" or "How many story points did they finish?"). This creates dangerous blind spots:

An engineer working 120 hours on 5 tickets might look productive, but they are drowning in critical bugs and facing imminent burnout.
An engineer completing 20 story points might have completely missed their time estimates by 
300
%
300%, wrecking sprint delivery predictability.
The Health Score provides a single, balanced operational index (from 0 to 100) that balances positive productive output against operational risks and penalties.

1.2 Mathematical Mechanics & Implementation Trace
Implemented in 
AnalyticsEngine._compute_health_score()
 and configured in 
health_rules.json
.

Health Score
=
∑
k
=
1
8
(
Component
k
×
W
k
)
Health Score= 
k=1
∑
8
​
 (Component 
k
​
 ×W 
k
​
 )
The weights sum up to exactly 
1.00
1.00 (
100
%
100%):

Component (
k
k)	Weight (
W
k
W 
k
​
 )	Raw Formula / Code Calculation	Component Purpose
1. Capacity Balance	0.20	$\max(0, 100 -	100 - \text{utilization}
2. Utilization Score	0.20	
min
⁡
(
100
,
utilization
)
min(100,utilization)	Rewards active, logged contribution up to full capacity (capped at 
100
100).
3. Productivity Score	0.15	
min
⁡
(
100
,
Productivity
max
⁡
(
1
,
Velocity
)
×
100
)
min(100, 
max(1,Velocity)
Productivity
​
 ×100) (or 50 if velocity = 0)	Rewards resolving high-priority tickets (weighted by story points) relative to raw ticket volume.
4. Velocity Score	0.15	
min
⁡
(
100
,
Velocity
benchmark_sp (20)
×
100
)
min(100, 
benchmark_sp (20)
Velocity
​
 ×100)	Rewards throughput against the standard sprint throughput target (
20
 SP
20 SP).
5. Estimation Accuracy	0.10	
max
⁡
(
0
,
EstimationAccuracy
)
max(0,EstimationAccuracy)	Rewards reliable sprint estimates where logged hours match initial estimates.
6. Dependency Risk	0.10	Baseline 
100
100	Baseline health credit for skill distribution stability.
7. Critical Issue Factor	0.05	
max
⁡
(
0
,
100
−
(
CriticalIssues
×
20
)
)
max(0,100−(CriticalIssues×20))	Subtracts 
20
 points
20 points per open critical bug from this component's subscore.
8. Blocked Issue Factor	0.05	
max
⁡
(
0
,
100
−
(
BlockedIssues
×
20
)
)
max(0,100−(BlockedIssues×20))	Subtracts 
20
 points
20 points per blocked ticket from this component's subscore.
1.3 Why the Specific Config Values Matter
Why Capacity Balance (
0.20
0.20) vs. Utilization (
0.20
0.20)?
If we only had Utilization, an engineer utilized at 
140
%
140% would get maximum points, encouraging unhealthy overwork.
By adding Capacity Balance with equal weight (
0.20
0.20), an engineer at 
140
%
140% utilization gets 
100
100 on Utilization, but drops to 
100
−
∣
100
−
140
∣
=
60
100−∣100−140∣=60 on Capacity Balance. Overwork is mathematically penalized.
Why Velocity Benchmark is 
20
 SP
20 SP?
Configured via max_velocity_benchmark_sp: 20 in 
analytics_rules.json
. In a standard 2-week sprint for an individual contributor, delivering 
20
 SP
20 SP represents strong, top-tier throughput. Normalizing by 
20
20 scales the velocity component cleanly onto a 
0
–
100
0–100 scale.
Why 
20
 Point
20 Point Deduction per Critical / Blocked Issue?
Defined in critical_issue_deduction_per_issue: 20.
100
/
20
=
5
100/20=5 issues. Having 5 active critical bugs or 5 blocked tickets completely zeros out that entire subcomponent, immediately dragging the health score into the "At Risk" category.
1.4 Concrete Worked Example
Scenario: Engineer Charlie
Sprint Capacity: 
80
 hours
80 hours (2-week sprint)
Logged Hours: 
72
 hours
72 hours 
→
Utilization
=
72
80
×
100
=
90.0
%
→Utilization= 
80
72
​
 ×100=90.0%
Delivered Story Points (Velocity): 
15
 SP
15 SP
Productivity Points: 
60
60 (resolved one 5-SP Critical ticket 
[
5
×
8
=
40
]
[5×8=40] + one 4-SP High ticket 
[
4
×
5
=
20
]
[4×5=20])
Estimation Accuracy: 
85.0
%
85.0%
Open Critical Issues: 
1
1
Blocked Tickets: 
0
0
Step-by-Step Calculation:
Capacity Balance: 
(
100
−
∣
100
−
90
∣
)
×
0.20
=
90
×
0.20
=
18.0
(100−∣100−90∣)×0.20=90×0.20=18.0
Utilization Score: 
min
⁡
(
100
,
90
)
×
0.20
=
90
×
0.20
=
18.0
min(100,90)×0.20=90×0.20=18.0
Productivity Score: 
min
⁡
(
100
,
60
15
×
100
)
×
0.15
=
100
×
0.15
=
15.0
min(100, 
15
60
​
 ×100)×0.15=100×0.15=15.0
Velocity Score: 
min
⁡
(
100
,
15
20
×
100
)
×
0.15
=
75
×
0.15
=
11.25
min(100, 
20
15
​
 ×100)×0.15=75×0.15=11.25
Estimation Accuracy: 
85
×
0.10
=
8.50
85×0.10=8.50
Dependency Risk: 
100
×
0.10
=
10.0
100×0.10=10.0
Critical Issue Factor: 
max
⁡
(
0
,
100
−
(
1
×
20
)
)
×
0.05
=
80
×
0.05
=
4.0
max(0,100−(1×20))×0.05=80×0.05=4.0
Blocked Issue Factor: 
max
⁡
(
0
,
100
−
(
0
×
20
)
)
×
0.05
=
100
×
0.05
=
5.0
max(0,100−(0×20))×0.05=100×0.05=5.0
Final Health Score
=
18.0
+
18.0
+
15.0
+
11.25
+
8.50
+
10.0
+
4.0
+
5.0
=
89.75
(
Healthy
)
Final Health Score=18.0+18.0+15.0+11.25+8.50+10.0+4.0+5.0=89.75(Healthy)
2. Metric #6: Burnout Risk
2.1 Core Purpose & Why It Is Needed
Developer burnout leads directly to unannounced attrition, missed deadlines, and severe software bugs. However, burnout is not just about hours worked:

Working 
115
%
115% on straightforward feature tickets is exhausting.
Working 
85
%
85% capacity while carrying 3 production-critical P0 firefights causes cognitive stress and burnout just as fast.
Burnout Risk in CUIA captures both volume overload and cognitive crisis load.

2.2 Mathematical Mechanics & Implementation Trace
Implemented in 
AnalyticsEngine._compute_burnout_risk()
:

python


if utilization > burnout_cfg["high_utilization_percent"] or critical_count > burnout_cfg["high_critical_issues"]:
    return "High"
elif utilization > burnout_cfg["medium_utilization_percent"]:
    return "Medium"
return "Low"
Mermaid diagram
2.3 Why the Specific Config Values Matter
From 
analytics_rules.json
:

json


"burnout_thresholds": {
  "high_utilization_percent": 110,
  "medium_utilization_percent": 95,
  "high_critical_issues": 2
}
Why Strict Inequality (> 110 and > 2)?
An engineer at exactly 
100
%
100% or 
110.0
%
110.0% utilization is fully loaded or slightly stretched. Crossing into 
110.1
%
110.1% means the engineer is logging overtime hours that are unsustainable over multiple sprints.
Similarly, having 
2
2 critical issues is manageable by a senior engineer, but having 
3
3 or more forces constant context-switching and panic-driven development.
Why 
95
%
95% for Medium?
A buffer of 
5
%
5% (
95
–
100
%
95–100%) gives early warning to managers during sprint planning before an engineer becomes completely red-lined.
2.4 Concrete Worked Example
Case A: Engineer Diana logs 
92
 hours
92 hours on an 
80
h
80h sprint (
115.0
%
115.0% util) with 
0
0 critical issues 
→
→ High Burnout Risk (triggered by utilization 
>
110
%
>110%).
Case B: Engineer Evan logs 
65
 hours
65 hours on an 
80
h
80h sprint (
81.25
%
81.25% util) but is assigned 
3
3 Critical P0 issues 
→
→ High Burnout Risk (triggered by critical issues 
>
2
>2).
Case C: Engineer Frank logs 
78
 hours
78 hours on an 
80
h
80h sprint (
97.5
%
97.5% util) with 
1
1 Critical issue 
→
→ Medium Burnout Risk (utilization 
>
95
%
>95%).
3. Metric #7: Performance Ranking Score
3.1 Core Purpose & Why It Is Needed
In management reviews or AI-driven workforce assistants, asking "Who is our top performer?" can easily lead to biased, subjective, or hallucinated AI opinions.

The Performance Ranking Score is computed deterministically in 
BusinessRulesEngine.rank_engineers_by_performance()
. It synthesizes throughput, code quality/health, reliability, and work pacing into a unified mathematical rank.

3.2 Mathematical Mechanics & Formula
Configured in 
business_rules.json
:

Performance Score
=
Velocity Score
+
Health Score
+
Estimation Score
+
Utilization Balance
−
Blocked Penalty
Performance Score=Velocity Score+Health Score+Estimation Score+Utilization Balance−Blocked Penalty
Each component is calculated as follows:

Velocity Score
=
min
⁡
(
100
,
Velocity
20
×
100
)
×
0.30
Velocity Score=min(100, 
20
Velocity
​
 ×100)×0.30
Health Score
=
(
Health
100
×
100
)
×
0.25
Health Score=( 
100
Health
​
 ×100)×0.25
Estimation Score
=
(
EstimationAccuracy
100
×
100
)
×
0.20
Estimation Score=( 
100
EstimationAccuracy
​
 ×100)×0.20
Utilization Balance
=
max
⁡
(
0
,
100
−
∣
Utilization
−
85
∣
)
×
0.15
Utilization Balance=max(0,100−∣Utilization−85∣)×0.15
Blocked Penalty
=
min
⁡
(
100
,
BlockedTickets
×
25
)
×
0.10
Blocked Penalty=min(100,BlockedTickets×25)×0.10
3.3 Why the Specific Config Values Matter
Why is the Utilization Target set to 
85
%
85% (utilization_balance_target: 85)?
In queuing theory and agile delivery (Kingman's formula for waiting times), a system operating at 
100
%
100% capacity experiences exponential delays when any unexpected task arrives.
An engineer at 
85
%
85% utilization has the optimal blend of high throughput and sufficient buffer (
15
%
15%) to handle code reviews, incident triage, and design discussions without stalling.
Why the 
−
10
%
−10% Penalty on Blocked Tickets (blockedTickets * 25)?
Carrying 
4
4 blocked tickets means 
4
×
25
=
100
×
0.10
=
−
10
 points
4×25=100×0.10=−10 points. Top performers are expected to proactively raise impediments and unblock work rather than allowing multiple stale tickets to accumulate.
3.4 Concrete Worked Example
Scenario: Engineer Grace vs. Engineer Dave
Grace: Velocity = 
18
 SP
18 SP, Health = 
92.0
92.0, Estimation Accuracy = 
90
%
90%, Utilization = 
86
%
86%, Blocked Tickets = 
0
0.
Dave: Velocity = 
20
 SP
20 SP, Health = 
70.0
70.0, Estimation Accuracy = 
60
%
60%, Utilization = 
120
%
120%, Blocked Tickets = 
2
2.
Grace's Calculation:
Velocity Component: 
18
20
×
100
×
0.30
=
90
×
0.30
=
27.0
20
18
​
 ×100×0.30=90×0.30=27.0
Health Component: 
92
×
0.25
=
23.0
92×0.25=23.0
Estimation Component: 
90
×
0.20
=
18.0
90×0.20=18.0
Utilization Balance: 
(
100
−
∣
86
−
85
∣
)
×
0.15
=
99
×
0.15
=
14.85
(100−∣86−85∣)×0.15=99×0.15=14.85
Blocked Penalty: 
(
0
×
25
)
×
0.10
=
0.0
(0×25)×0.10=0.0
Total Performance Score: 
27.0
+
23.0
+
18.0
+
14.85
−
0.0
=
82.85
27.0+23.0+18.0+14.85−0.0=82.85
Dave's Calculation:
Velocity Component: 
20
20
×
100
×
0.30
=
100
×
0.30
=
30.0
20
20
​
 ×100×0.30=100×0.30=30.0
Health Component: 
70
×
0.25
=
17.5
70×0.25=17.5
Estimation Component: 
60
×
0.20
=
12.0
60×0.20=12.0
Utilization Balance: 
(
100
−
∣
120
−
85
∣
)
×
0.15
=
65
×
0.15
=
9.75
(100−∣120−85∣)×0.15=65×0.15=9.75
Blocked Penalty: 
(
2
×
25
)
×
0.10
=
50
×
0.10
=
−
5.0
(2×25)×0.10=50×0.10=−5.0
Total Performance Score: 
30.0
+
17.5
+
12.0
+
9.75
−
5.0
=
64.25
30.0+17.5+12.0+9.75−5.0=64.25
Result: Grace ranks significantly higher (
82.85
82.85 vs. 
64.25
64.25). Even though Dave delivered 
2
2 more story points, his high overwork (
120
%
120%), poor estimation, lower health, and blocked tickets pull his score down.

4. Metric #8: Priority Attention Urgency Score
4.1 Core Purpose & Why It Is Needed
Delivery Managers running multiple teams cannot inspect 30 engineers individually every morning. They need an automated triage queue that answers: "Who is currently in distress and requires my immediate intervention today?"

The Priority Attention Score ranks engineers in descending order of urgency.

4.2 Mathematical Mechanics & Formula
Implemented in 
BusinessRulesEngine.rank_by_attention_priority()
 and configured in 
business_rules.json
:

AttentionScore
=
(
BurnoutScore
×
40
100
)
+
(
UtilScore
×
30
100
)
+
(
BlockedScore
×
20
100
)
+
(
CriticalScore
×
10
100
)
AttentionScore=(BurnoutScore× 
100
40
​
 )+(UtilScore× 
100
30
​
 )+(BlockedScore× 
100
20
​
 )+(CriticalScore× 
100
10
​
 )
Where:

BurnoutScore
=
100
 (if High)
,
50
 (if Medium)
,
0
 (if Low)
BurnoutScore=100 (if High),50 (if Medium),0 (if Low).
UtilScore
=
min
⁡
(
100
,
max
⁡
(
0
,
Utilization
−
80
)
×
2
)
UtilScore=min(100,max(0,Utilization−80)×2). (Ramps up linearly from 
0
 pts
0 pts at 
80
%
80% utilization to 
100
 pts
100 pts at 
130
%
130% utilization).
BlockedScore
=
min
⁡
(
100
,
BlockedTickets
×
33
)
BlockedScore=min(100,BlockedTickets×33). (
3
3 blocked tickets maxes this out at 
99
–
100
 pts
99–100 pts).
CriticalScore
=
min
⁡
(
100
,
CriticalIssues
×
25
)
CriticalScore=min(100,CriticalIssues×25). (
4
4 critical issues maxes this out at 
100
 pts
100 pts).
4.3 Why the Specific Config Values Matter
json


"priority_attention": {
  "burnout_weight": 40,
  "utilization_weight": 30,
  "blocked_weight": 20,
  "critical_issues_weight": 10
}
Why Burnout Weight is 
40
%
40% (Highest Priority)?
Burnout represents an imminent human flight and health risk. Workload adjustments must happen before attrition occurs.
Why the Utilization Ramp starts at 
80
%
80% (
max
⁡
(
0
,
Util
−
80
)
×
2
max(0,Util−80)×2)?
Utilizations below 
80
%
80% do not require emergency managerial attention. Once utilization passes 
80
%
80%, each 
1
%
1% increase adds 
2
 raw points
2 raw points to the utilization factor, aggressively escalating attention as the engineer enters overtime territory.
4.4 Concrete Worked Example
Scenario: Engineer Mark
Burnout Risk: High (
100
 points
100 points)
Utilization: 
115
%
115%
Blocked Tickets: 
2
2
Critical Issues: 
3
3
Calculation:
Burnout Contribution
=
100
×
0.40
=
40.0
Burnout Contribution=100×0.40=40.0
Util Contribution
=
min
⁡
(
100
,
(
115
−
80
)
×
2
)
×
0.30
=
min
⁡
(
100
,
70
)
×
0.30
=
70
×
0.30
=
21.0
Util Contribution=min(100,(115−80)×2)×0.30=min(100,70)×0.30=70×0.30=21.0
Blocked Contribution
=
min
⁡
(
100
,
2
×
33
)
×
0.20
=
66
×
0.20
=
13.2
Blocked Contribution=min(100,2×33)×0.20=66×0.20=13.2
Critical Contribution
=
min
⁡
(
100
,
3
×
25
)
×
0.10
=
75
×
0.10
=
7.5
Critical Contribution=min(100,3×25)×0.10=75×0.10=7.5
Final Attention Score
=
40.0
+
21.0
+
13.2
+
7.5
=
81.7
(
Top Priority Triage
)
Final Attention Score=40.0+21.0+13.2+7.5=81.7(Top Priority Triage)
5. Metric #9: Replacement Candidate Match Score
5.1 Core Purpose & Why It Is Needed
When a key developer goes on unexpected medical leave, resigns, or is overwhelmed by high burnout, managers must find a replacement immediately.

A naive search for someone with "available capacity" often assigns complex Kafka or Kubernetes tasks to a junior frontend engineer who lacks the skills. The Replacement Match Score ranks candidate engineers by matching required skills, available capacity bandwidth, and domain seniority.

5.2 Mathematical Mechanics & Formula
Implemented in 
BusinessRulesEngine.find_replacement_candidates()
:

ReplacementScore
=
(
SkillScore
×
0.50
)
+
(
CapacityScore
×
0.30
)
+
(
ExperienceScore
×
0.20
)
ReplacementScore=(SkillScore×0.50)+(CapacityScore×0.30)+(ExperienceScore×0.20)
Where:

TargetSkills
=
TargetEngineer’s Primary
∪
Secondary Skills
TargetSkills=TargetEngineer’s Primary∪Secondary Skills.
CandidateSkills
=
Candidate’s Primary
∪
Secondary
∪
CrossTraining Skills
CandidateSkills=Candidate’s Primary∪Secondary∪CrossTraining Skills.
SkillScore
=
∣
TargetSkills
∩
CandidateSkills
∣
max
⁡
(
1
,
∣
TargetSkills
∣
)
×
100
SkillScore= 
max(1,∣TargetSkills∣)
∣TargetSkills∩CandidateSkills∣
​
 ×100.
CapacityScore
=
max
⁡
(
0
,
100
−
CandidateUtilization
)
CapacityScore=max(0,100−CandidateUtilization). (Lower utilization = higher available bandwidth).
ExperienceScore
=
min
⁡
(
100
,
CandidateYearsExperience
15
×
100
)
ExperienceScore=min(100, 
15
CandidateYearsExperience
​
 ×100). (Normalized against a 15-year ceiling).
5.3 Why the Specific Config Values Matter
Configured in 
business_rules.json
:

json


"replacement_scoring": {
  "skill_match_weight": 0.50,
  "capacity_weight": 0.30,
  "experience_weight": 0.20
}
Skill Match (
0.50
0.50): Without domain capability (e.g., Spring Boot, Go, AWS), assigning tasks is futile. Skill overlap carries half the entire score.
Available Capacity (
0.30
0.30): Assigning tickets to an engineer already running at 
105
%
105% utilization will trigger another burnout event. Engineers with lower utilization (e.g., 
50
%
50%) receive much higher capacity points (
100
−
50
=
50
 pts
100−50=50 pts).
Experience (
0.20
0.20): Senior engineers ramp up on unfamiliar codebases faster than juniors. Normalizing against 
15
 years
15 years assigns full experience points to staff/principal engineers while scaling juniors proportionately.
5.4 Concrete Worked Example
Target Engineer Being Replaced:
Target Skills: {"AWS", "Go", "Kubernetes", "PostgreSQL"} (
4
 skills
4 skills)
Candidate: Engineer Sarah
Sarah's Skills: {"AWS", "Go", "Python"} 
→
→ Overlap with Target: {"AWS", "Go"} (
2
 skills
2 skills).
Sarah's Utilization: 
40.0
%
40.0% (very high available bandwidth).
Sarah's Experience: 
6
 years
6 years.
Calculation:
Skill Overlap
=
2
4
×
100
=
50.0
→
Skill Component
=
50.0
×
0.50
=
25.0
Skill Overlap= 
4
2
​
 ×100=50.0→Skill Component=50.0×0.50=25.0
Capacity Component
=
(
100
−
40.0
)
×
0.30
=
60.0
×
0.30
=
18.0
Capacity Component=(100−40.0)×0.30=60.0×0.30=18.0
Experience Component
=
(
6
15
×
100
)
×
0.20
=
40.0
×
0.20
=
8.0
Experience Component=( 
15
6
​
 ×100)×0.20=40.0×0.20=8.0
Sarah’s Total Replacement Score
=
25.0
+
18.0
+
8.0
=
51.0
Sarah’s Total Replacement Score=25.0+18.0+8.0=51.0
6. Metric #10: Forecast & Trend Extrapolations
6.1 Core Purpose & Why It Is Needed
Software engineering projects fail gradually before they fail suddenly. Velocity decay and capacity creep happen over 2–3 sprints.

The Forecast Engine (
forecast_engine.py
) avoids heavy, non-explainable black-box ML models. It uses least-squares linear trend regression and simple moving averages over a trailing sprint window to give leadership forward projections for the next 
3
 sprints
3 sprints.

6.2 Mathematical Mechanics & Formulas
Configured in 
forecast_rules.json
:

Mermaid diagram
1. Simple Moving Average (SMA):
SMA
(
Y
)
=
1
W
∑
i
=
1
W
Y
recent_
i
(
where 
W
=
3
)
SMA(Y)= 
W
1
​
  
i=1
∑
W
​
 Y 
recent_i
​
 (where W=3)
2. Linear Trend Slope (
m
m) via Least-Squares Regression:
For historical series 
Y
=
[
y
0
,
y
1
,
…
,
y
n
−
1
]
Y=[y 
0
​
 ,y 
1
​
 ,…,y 
n−1
​
 ] indexed 
i
=
0
,
1
,
…
,
n
−
1
i=0,1,…,n−1:

x
ˉ
=
n
−
1
2
,
y
ˉ
=
1
n
∑
i
=
0
n
−
1
y
i
x
ˉ
 = 
2
n−1
​
 , 
y
ˉ
​
 = 
n
1
​
  
i=0
∑
n−1
​
 y 
i
​
 
m
=
∑
i
=
0
n
−
1
(
i
−
x
ˉ
)
(
y
i
−
y
ˉ
)
∑
i
=
0
n
−
1
(
i
−
x
ˉ
)
2
m= 
∑ 
i=0
n−1
​
 (i− 
x
ˉ
 ) 
2
 
∑ 
i=0
n−1
​
 (i− 
x
ˉ
 )(y 
i
​
 − 
y
ˉ
​
 )
​
 
m
>
0
→
m>0→ Velocity Accelerating (increasing throughput).
m
<
0
→
m<0→ Velocity Decelerating (delivery slowdown).
3. Future Projections:
y
^
future_
k
=
max
⁡
(
0
,
y
last
+
(
m
×
k
)
)
for 
k
=
1
,
2
,
3
y
^
​
  
future_k
​
 =max(0,y 
last
​
 +(m×k))for k=1,2,3
4. Capacity Gap:
Capacity Gap
=
Current Sprint Capacity
−
SMA
(
Logged Hours
)
Capacity Gap=Current Sprint Capacity−SMA(Logged Hours)
5. Composite Risk Assessment (
forecast_engine.py#L244-L271
):
Risk factor counters:

If 
Average Utilization
>
90
%
Average Utilization>90% 
→
+
2
 risk factors
→+2 risk factors.
If 
Velocity Trend 
(
m
)
<
0
Velocity Trend (m)<0 and decay 
>
10
%
>10% 
→
+
1
 risk factor
→+1 risk factor.
If 
∣
Capacity Gap
∣
/
Capacity
>
15
%
∣Capacity Gap∣/Capacity>15% 
→
+
1
 risk factor
→+1 risk factor.
Risk Level: 
≥
3
→
Critical
≥3→Critical, 
2
→
High
2→High, 
1
→
Medium
1→Medium, 
0
→
Low
0→Low.
6.3 Why the Specific Config Values Matter
json


{
  "forecast_horizon_sprints": 3,
  "trend_analysis_window_sprints": 3,
  "risk_thresholds": {
    "utilization_risk_percent": 90,
    "capacity_gap_risk_percent": 15,
    "velocity_decline_risk_percent": 10
  }
}
Why Window Size = 3 Sprints?
In 2-week sprint cycles, 3 sprints represent 6 weeks of actual history. This is long enough to smooth out temporary anomalies (such as a single engineer taking a 2-day holiday) while staying responsive to recent team staffing changes.
Why 3 Sprints Horizon?
3 future sprints (6 weeks) corresponds to the second half of a standard quarterly planning cycle (PI / Quarter), giving management actionable lead time to hire or redistribute scope.
Why Utilization Risk at 
90
%
90% (utilization_risk_percent: 90)?
Once an entire organization averages 
>
90
%
>90% utilization, any future scope addition will force the team past 
100
%
100% into delivery failure or burnout.
6.4 Concrete Worked Example
Historical Team Data (Last 3 Sprints):
Sprint 40: Velocity = 
60
 SP
60 SP, Logged = 
310
h
310h, Util = 
77.5
%
77.5%
Sprint 41: Velocity = 
55
 SP
55 SP, Logged = 
330
h
330h, Util = 
82.5
%
82.5%
Sprint 42 (Current): Velocity = 
50
 SP
50 SP, Logged = 
370
h
370h, Util = 
92.5
%
92.5%
Team Total Capacity: 
400
 hours
400 hours
Step 1: Moving Averages:
SMA
(
Velocity
)
=
60
+
55
+
50
3
=
55.0
 SP
SMA(Velocity)= 
3
60+55+50
​
 =55.0 SP
SMA
(
Utilization
)
=
77.5
+
82.5
+
92.5
3
=
84.17
%
SMA(Utilization)= 
3
77.5+82.5+92.5
​
 =84.17%
SMA
(
Logged Hours
)
=
310
+
330
+
370
3
=
336.67
 hours
SMA(Logged Hours)= 
3
310+330+370
​
 =336.67 hours
Step 2: Linear Trend of Velocity:
n
=
3
n=3, 
i
=
[
0
,
1
,
2
]
i=[0,1,2], 
x
ˉ
=
1.0
x
ˉ
 =1.0, 
y
ˉ
=
55.0
y
ˉ
​
 =55.0
i
=
0
:
(
0
−
1
)
(
60
−
55
)
=
−
1
×
5
=
−
5
i=0:(0−1)(60−55)=−1×5=−5
i
=
1
:
(
1
−
1
)
(
55
−
55
)
=
0
×
0
=
0
i=1:(1−1)(55−55)=0×0=0
i
=
2
:
(
2
−
1
)
(
50
−
55
)
=
1
×
−
5
=
−
5
i=2:(2−1)(50−55)=1×−5=−5
Numerator
=
−
5
+
0
+
−
5
=
−
10
Numerator=−5+0+−5=−10
Denominator
=
(
0
−
1
)
2
+
(
1
−
1
)
2
+
(
2
−
1
)
2
=
1
+
0
+
1
=
2
Denominator=(0−1) 
2
 +(1−1) 
2
 +(2−1) 
2
 =1+0+1=2
Velocity Slope (
m
m): 
−
10
2
=
−
5.0
 SP / sprint
2
−10
​
 =−5.0 SP / sprint (decelerating by 
5
 SP
5 SP per sprint).
Step 3: Projections for Next 3 Sprints:
Sprint 43 (
k
=
1
k=1): 
50
+
(
−
5.0
×
1
)
=
45.0
 SP
50+(−5.0×1)=45.0 SP
Sprint 44 (
k
=
2
k=2): 
50
+
(
−
5.0
×
2
)
=
40.0
 SP
50+(−5.0×2)=40.0 SP
Sprint 45 (
k
=
3
k=3): 
50
+
(
−
5.0
×
3
)
=
35.0
 SP
50+(−5.0×3)=35.0 SP
Step 4: Capacity Gap:
Capacity Gap
=
400
−
336.67
=
+
63.33
 hours of unused capacity
Capacity Gap=400−336.67=+63.33 hours of unused capacity
Step 5: Risk Evaluation:
Velocity is decelerating by 
−
5
 SP
−5 SP on a 
55
 SP
55 SP average (
9.1
%
9.1% drop, approaching the 
10
%
10% risk mark).
Current sprint utilization (
92.5
%
92.5%) exceeds the 
90
%
90% utilization threshold (
+
2
 risk factors
+2 risk factors).
Overall Forecast Status: Flagged as "High Delivery Risk" due to surging logged hours combined with diminishing story point output (a classic indicator of tech debt, severe blockers, or rework).
7. Comparative Summary of All 6 Metrics
Metric	Target Question Answered	Who Uses It?	Key Input Variables	Primary Failure Mode if Ignored
5. Health Score	"How holistically sound is this engineer or team?"	Executive Leadership & DMs	Utilization, Productivity, Velocity, Estimation Accuracy, Blockers, SPOF	Undetected quality decay and sudden project collapse.
6. Burnout Risk	"Who is working in an unsustainable state right now?"	Delivery Managers	Utilization 
>
110
%
>110%, Critical Issues 
>
2
>2	Developer resignation, illness, and high turnover.
7. Performance Score	"Who are our top contributors on a balanced scorecard?"	Leadership & HR	Velocity, Health, Estimation, 
85
%
85% Util Target, Blockers	Promoting heroes who burn out their teams while ignoring steady, accurate deliverers.
8. Priority Attention	"Who needs managerial unblocking or 1:1 triage today?"	Delivery Managers	Burnout (40%), Overtime (30%), Blocked (20%), Critical (10%)	Stalled sprints caused by unaddressed blockers.
9. Replacement Match	"If X is unavailable, who can best step in?"	Resource Managers	Skill Overlap (50%), Headroom (30%), Experience (20%)	Misallocating critical tasks to unqualified engineers.
10. Forecast & Trends	"Where will our capacity and velocity be in 6 weeks?"	VPs of Engineering & Directors	3-sprint SMA, Least-Squares Slope, Capacity Gap	Missing quarterly release commitments.
8:40 AM




