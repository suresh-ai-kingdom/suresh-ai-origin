# SURESH AI ORIGIN — Execution Intelligence Platform

## Vision
**Rare execution strategies that improve with your data. Uncopable. 1%.**

Transform from: ZIP delivery → to: Personalized execution intelligence

---

## Architecture

### Core Data Models

#### 1. User Profile (New)
```python
class UserProfile:
    id = String (PK)
    email = String
    goal = String  # "earn_money", "save_time", "scale_business"
    market = String  # "freelancer", "shop_owner", "content_creator", "agency"
    skill_level = String  # "beginner", "intermediate", "advanced"
    country = String  # "IN", "US", etc
    created_at = Float
    updated_at = Float
```

#### 2. Workflow Execution (New)
```python
class WorkflowExecution:
    id = String (PK)
    user_id = String (FK → UserProfile)
    workflow_name = String  # "resume_generator", "whatsapp_bot", "prompt_selling"
    status = String  # "started", "in_progress", "completed", "abandoned"
    steps_completed = Integer  # 1/5, 2/5, 3/5
    started_at = Float
    completed_at = Float
    execution_notes = Text  # User's notes during execution
```

#### 3. Outcome (New)
```python
class Outcome:
    id = String (PK)
    execution_id = String (FK → WorkflowExecution)
    user_id = String (FK → UserProfile)
    metric_type = String  # "revenue", "time_saved", "customers", "custom"
    value = Float  # ₹5000, 10 hours, 3 customers
    currency = String  # "INR", "USD"
    proof_type = String  # "screenshot", "invoice", "text", "none"
    proof_url = String  # link to uploaded proof
    timestamp = Float
    verified = Boolean  # Admin verified or auto-verified
```

#### 4. Workflow Performance (New)
```python
class WorkflowPerformance:
    id = String (PK)
    workflow_name = String
    market = String  # "freelancer", "shop_owner", etc
    skill_level = String
    success_rate = Float  # % of users who completed
    avg_outcome_value = Float  # Average ₹ earned or time saved
    completion_time_hours = Float  # Avg hours to complete
    data_points = Integer  # How many executions tracked
    updated_at = Float
```

#### 5. Recommendation (New)
```python
class Recommendation:
    id = String (PK)
    user_id = String (FK → UserProfile)
    workflow_name = String
    reason = String  # "73% success rate for your market", "peer recommendation", etc
    rank = Integer  # 1 = top recommendation
    created_at = Float
    clicked = Boolean
    outcome = String  # "completed", "abandoned", "in_progress"
```

---

## Core Features (MVP)

### 1. Interactive Executor
**Where execution happens (not PDFs)**

- Step-by-step workflow guide (replaces PDF)
- Timer for each step (45-min routine tracking)
- Notes capture (what worked, what failed)
- Screenshots/proofs embedded
- Real-time guidance (context-aware tips)

**Entry point:** `/executor/<workflow_id>`

### 2. Outcome Logger
**Capture real results**

- "What was the result of this workflow?"
- Revenue: ₹X earned
- Time: Y hours saved
- Customers: Z acquired
- Custom: Text/screenshot proof
- Automatic calculation of workflow ROI

**Entry point:** `/outcome/log/<execution_id>`

### 3. Personalized Recommendations
**Suggest next workflow based on data**

Algorithm:
```
For each workflow:
  success_rate_in_your_market = (completed / started) where market matches
  peer_outcome = avg outcome for users like you
  difficulty_match = (your_skill_level, workflow_required_level)
  
ranking = success_rate * 0.4 + peer_outcome * 0.4 + difficulty_match * 0.2
```

**Entry point:** `/dashboard/next`

### 4. Proof Dashboard
**Your execution history + proof of outcomes**

Shows:
- Total revenue earned (sum of outcomes)
- Workflows completed
- Workflows with highest ROI
- Proof gallery (screenshots, invoices)
- Peer comparison (anonymized: "You're in top 25% for your market")

**Entry point:** `/dashboard/proof`

### 5. Rare Workflows Discovery
**Find workflows working for 1% (not templates)**

Filter by:
- Your market + skill level + goal
- Success rate ≥ 60%
- Average outcome ≥ ₹5000
- Completion time ≤ 20 hours

Shows:
- "Only 127 people in India have completed this"
- "88% earned ₹10k+"
- "Requires: intermediate prompt engineering"

**Entry point:** `/workflows/rare`

---

## Database Schema (SQL)

```sql
-- User Profile
CREATE TABLE user_profiles (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE,
  goal TEXT,
  market TEXT,
  skill_level TEXT,
  country TEXT,
  created_at FLOAT,
  updated_at FLOAT
);

-- Workflow Execution
CREATE TABLE workflow_executions (
  id TEXT PRIMARY KEY,
  user_id TEXT REFERENCES user_profiles(id),
  workflow_name TEXT,
  status TEXT,
  steps_completed INTEGER,
  started_at FLOAT,
  completed_at FLOAT,
  execution_notes TEXT
);

-- Outcomes
CREATE TABLE outcomes (
  id TEXT PRIMARY KEY,
  execution_id TEXT REFERENCES workflow_executions(id),
  user_id TEXT REFERENCES user_profiles(id),
  metric_type TEXT,
  value FLOAT,
  currency TEXT,
  proof_type TEXT,
  proof_url TEXT,
  timestamp FLOAT,
  verified INTEGER DEFAULT 0
);

-- Workflow Performance (Aggregated)
CREATE TABLE workflow_performance (
  id TEXT PRIMARY KEY,
  workflow_name TEXT,
  market TEXT,
  skill_level TEXT,
  success_rate FLOAT,
  avg_outcome_value FLOAT,
  completion_time_hours FLOAT,
  data_points INTEGER,
  updated_at FLOAT
);

-- Recommendations
CREATE TABLE recommendations (
  id TEXT PRIMARY KEY,
  user_id TEXT REFERENCES user_profiles(id),
  workflow_name TEXT,
  reason TEXT,
  rank INTEGER,
  created_at FLOAT,
  clicked INTEGER DEFAULT 0,
  outcome TEXT
);
```

---

## Transition Strategy

### Phase 1: Keep Old System (Week 1-2)
- Old ZIP downloads still work
- But new users onboard into new platform
- Track: old system ≈ 0 revenue, prove new system works

### Phase 2: New Platform MVP (Week 3-4)
- Build Executor + Outcome Logger
- First 50 users get free access (invite-only)
- Collect execution + outcome data
- Calculate workflow performance metrics

### Phase 3: Turn On Recommendations (Week 5-6)
- Once data reaches 100+ executions
- Show personalized recommendations
- Users can see peer success rates
- Prove platform creates better execution

### Phase 4: Monetization (Week 7+)
- Free tier: 1 workflow execution + basic tracking
- Pro (₹99/mo): Unlimited executions + recommendations + rare workflows + proof dashboard
- Scale (₹299/mo): Everything + white-label for coaches + API access

---

## Revenue Flywheel

1. **Users execute workflows inside platform** (not external)
2. **Outcomes get logged** (real data captured)
3. **Recommendations improve** (better data = better suggestions)
4. **Success rate visible** ("Your workflow had 73% success in India")
5. **Switching cost increases** (can't get this intelligence elsewhere)
6. **Pricing power increases** (pay for intelligence, not prompts)
7. **Peer data becomes moat** (100+ completed outcomes makes system unique)

---

## Metrics to Track

### Daily
- New executions started
- Executions completed
- Outcomes logged
- Recommendations clicked

### Weekly
- Workflow performance changes (success rate)
- User retention (Day 7)
- Average outcome value
- Proof submissions

### Monthly
- MRR from Pro tier
- CAC (if ads)
- Churn rate
- Peer network size (100 executions?)

---

## Kill List (Old System)
- ❌ ZIP downloads from `/download/<product>`
- ❌ One-time purchase model
- ❌ Razorpay orders/payments (old system)
- ❌ Admin reconciliation (unnecessary)
- ❌ Entitlements gating (replaced by tier system)
- ❌ Stripe checkout (rebuild for new model)

---

## Build Plan

### Week 1: Data Foundation
- [ ] Add 5 new tables (UserProfile, WorkflowExecution, Outcome, WorkflowPerformance, Recommendation)
- [ ] Migration script
- [ ] Basic CRUD endpoints

### Week 2: Executor + Logger
- [ ] `/executor/<workflow>` page (step-by-step guide)
- [ ] `/outcome/log` form (capture results)
- [ ] Workflow performance aggregation job

### Week 3: Dashboard + Recommendations
- [ ] `/dashboard/proof` (outcome history)
- [ ] Recommendation algorithm
- [ ] `/workflows/rare` (filtered discovery)

### Week 4: Monetization
- [ ] Stripe Checkout for Pro (₹99/mo)
- [ ] Feature gating (rare workflows = Pro only)
- [ ] Proof dashboard = Pro only

---

**Start building Week 1 immediately?**
