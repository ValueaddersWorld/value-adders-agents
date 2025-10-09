# Data Collection Processes and Analytics Pipeline

## Overview
This document defines the data collection processes and analytics pipeline architecture for the AddValue App. The system is designed with privacy-first principles, data sovereignty, and alignment with the Living Constitution.

## Data Collection Architecture

### 1. Event Collection System

#### 1.1 Event Types
Events are categorized into the following types:

**User Events:**
- `user_signup` - User creates account
- `user_login` - User authenticates
- `user_profile_update` - Profile information changed
- `user_consent_update` - Data collection consent modified

**Activation Events:**
- `activation_started` - User begins Activation Day
- `activation_round_completed` - User completes a round (1-8)
- `activation_affirmation_selected` - User selects an affirmation
- `activation_mood_logged` - User logs mood (start/end)
- `activation_completed` - User completes full Activation Day
- `activation_breathwork_completed` - Breathwork session finished

**Micro-Act Events:**
- `microact_created` - User logs a micro-act
- `microact_updated` - Micro-act edited
- `microact_shared` - Micro-act shared to community feed
- `microact_category_selected` - Category chosen for micro-act

**Community Events:**
- `post_created` - User creates community post
- `post_liked` - User likes a post
- `post_commented` - User comments on post
- `post_shared` - User shares a post
- `user_followed` - User follows another user

**Wave Events:**
- `wave_registered` - User registers for Wave
- `wave_joined` - User joins Wave session
- `wave_left` - User leaves Wave
- `wave_interaction` - User participates in discussion
- `wave_microact_shared` - User shares micro-act during Wave
- `wave_feedback_submitted` - User provides Wave feedback

#### 1.2 Event Schema
All events follow a consistent schema:

```json
{
  "event_id": "uuid",
  "event_name": "string",
  "event_category": "string",
  "user_id": "uuid",
  "session_id": "string",
  "timestamp": "ISO 8601 datetime",
  "properties": {
    // Event-specific properties
  },
  "context": {
    "device_type": "mobile|tablet|desktop",
    "platform": "ios|android|web",
    "app_version": "string",
    "locale": "string",
    "timezone": "string"
  },
  "privacy": {
    "consent_given": "boolean",
    "ip_anonymized": "boolean"
  }
}
```

#### 1.3 Collection Methods

**Client-Side Collection (React Native App):**
- SDK integration for automatic event tracking
- Manual event logging for user actions
- Offline queue with sync when online
- Batch sending to reduce network calls

**Server-Side Collection (Supabase):**
- Database triggers for certain events
- API endpoint events
- Background job events
- System events (errors, performance)

**Privacy Controls:**
- User consent check before collection
- IP address anonymization
- Optional device ID anonymization
- User right to delete all data

### 2. Data Ingestion Pipeline

#### 2.1 Pipeline Stages

```
Client App → Event Queue → Validation → Enrichment → Storage → Processing
```

**Stage 1: Event Queue**
- Technology: Supabase Realtime or message queue (Redis/RabbitMQ)
- Purpose: Buffer incoming events
- Capacity: Handle 10,000 events/minute
- Retry logic: Exponential backoff for failed sends

**Stage 2: Validation**
- Schema validation against event definitions
- Data type checking
- Required field verification
- Consent verification
- Rate limiting and abuse detection

**Stage 3: Enrichment**
- Add server timestamp
- Geo-location (country/region only, if consented)
- User segment classification
- Session stitching
- Anomaly detection flags

**Stage 4: Storage**
- Primary: Write to `analytics_events` table
- Secondary: Archive to cold storage after 90 days
- Encryption: AES-256 for data at rest
- Backup: Daily snapshots

**Stage 5: Processing**
- Real-time aggregation for dashboards
- Batch processing for complex metrics
- ML model input preparation (future)

#### 2.2 Data Flow Diagram

```
┌─────────────┐
│ React Native│
│     App     │
└──────┬──────┘
       │
       │ HTTPS/TLS
       ↓
┌─────────────────┐
│  Event API      │
│  (Supabase)     │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Validation     │
│  Service        │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  analytics_     │
│  events table   │
└────────┬────────┘
         │
         ↓
┌─────────────────┐     ┌──────────────┐
│  Stream         │────→│  Real-time   │
│  Processor      │     │  Dashboards  │
└────────┬────────┘     └──────────────┘
         │
         ↓
┌─────────────────┐
│  Batch Jobs     │
│  (Metrics Calc) │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Aggregated     │
│  Metrics Tables │
└─────────────────┘
```

### 3. Metrics Calculation Pipeline

#### 3.1 Real-Time Metrics
Calculated on event ingestion for immediate dashboard updates:

- Daily Active Users (DAU)
- Current online users
- Micro-acts logged today
- Wave participants (live count)
- Activation sessions in progress

**Implementation:**
- Use Supabase Realtime subscriptions
- Maintain in-memory counters (Redis)
- Update frequency: Every event
- Dashboard refresh: 2-5 minutes

#### 3.2 Hourly Batch Jobs
Run every hour for near-real-time metrics:

```sql
-- Example: Update hourly user activity
INSERT INTO hourly_metrics (metric_hour, dau, activations, microacts)
SELECT 
  DATE_TRUNC('hour', CURRENT_TIMESTAMP) as metric_hour,
  COUNT(DISTINCT CASE WHEN last_activity_date = CURRENT_DATE THEN user_id END) as dau,
  COUNT(DISTINCT CASE WHEN activation_sessions.started_at >= DATE_TRUNC('hour', CURRENT_TIMESTAMP - INTERVAL '1 hour') THEN activation_sessions.id END) as activations,
  COUNT(DISTINCT CASE WHEN micro_acts.created_at >= DATE_TRUNC('hour', CURRENT_TIMESTAMP - INTERVAL '1 hour') THEN micro_acts.id END) as microacts
FROM users
LEFT JOIN activation_sessions ON users.id = activation_sessions.user_id
LEFT JOIN micro_acts ON users.id = micro_acts.user_id;
```

**Hourly Metrics:**
- Activation completion rates
- Micro-acts by category
- Community engagement
- Wave participation trends

#### 3.3 Daily Batch Jobs
Run at 2 AM UTC for comprehensive daily metrics:

```sql
-- Calculate daily user metrics and indices
INSERT INTO daily_user_metrics (
  user_id, 
  metric_date, 
  flourish_index, 
  add_value_index,
  -- other fields
)
SELECT 
  u.id as user_id,
  CURRENT_DATE - INTERVAL '1 day' as metric_date,
  calculate_flourish_index(u.id, CURRENT_DATE - INTERVAL '1 day') as flourish_index,
  calculate_add_value_index(u.id, CURRENT_DATE - INTERVAL '1 day') as add_value_index,
  -- calculate other metrics
FROM users u
WHERE u.is_active = true;

-- Calculate platform-wide metrics
INSERT INTO platform_metrics (metric_date, dau, new_users, ...)
SELECT 
  CURRENT_DATE - INTERVAL '1 day' as metric_date,
  COUNT(DISTINCT CASE WHEN last_activity_date = CURRENT_DATE - INTERVAL '1 day' THEN id END) as dau,
  COUNT(DISTINCT CASE WHEN created_at::date = CURRENT_DATE - INTERVAL '1 day' THEN id END) as new_users,
  -- other aggregations
FROM users;
```

**Daily Metrics:**
- Flourish Index per user
- Add-Value Index per user
- Retention cohorts update
- Streak calculations
- Platform-wide aggregations

#### 3.4 Weekly Batch Jobs
Run on Mondays at 3 AM UTC:

- Weekly Active Users (WAU) calculation
- Wave participation summaries
- Retention cohort analysis
- Trend analysis and forecasting
- Data quality checks

#### 3.5 Monthly Batch Jobs
Run on 1st of month at 4 AM UTC:

- Monthly Active Users (MAU)
- Churn analysis
- Long-term trend analysis
- Executive reports generation
- Data archival to cold storage

### 4. Data Quality & Monitoring

#### 4.1 Data Quality Checks

**Completeness:**
- Check for missing required fields
- Verify event flow (no gaps in critical events)
- Alert on low event volume

**Accuracy:**
- Cross-validate related events (e.g., activation_started should precede activation_completed)
- Range checks on numeric values
- Timestamp consistency checks

**Timeliness:**
- Monitor event lag (time between event occurrence and storage)
- Alert on pipeline delays > 5 minutes
- Track batch job completion times

**Consistency:**
- Check for duplicate events
- Verify referential integrity
- Validate metric calculations against raw events

#### 4.2 Monitoring & Alerting

**Pipeline Health Metrics:**
- Event ingestion rate
- Processing latency
- Error rate
- Queue depth
- Database performance

**Alert Conditions:**
```yaml
alerts:
  - name: "High Event Error Rate"
    condition: "error_rate > 1%"
    severity: "critical"
    notification: ["data_team", "engineering_team"]
  
  - name: "Pipeline Lag"
    condition: "processing_lag > 5 minutes"
    severity: "warning"
    notification: ["data_team"]
  
  - name: "Batch Job Failure"
    condition: "daily_job_failed = true"
    severity: "critical"
    notification: ["data_team", "on_call"]
  
  - name: "Data Quality Issue"
    condition: "null_rate > 5% OR duplicate_rate > 1%"
    severity: "warning"
    notification: ["data_team"]
```

**Monitoring Dashboard:**
- Pipeline throughput graph
- Error rate trends
- Job execution status
- Data quality scores
- System resource utilization

### 5. Privacy & Compliance

#### 5.1 Data Privacy Measures

**Consent Management:**
- Explicit user consent for data collection
- Granular consent options (analytics, personalization, marketing)
- Easy consent withdrawal
- No collection without consent

**Data Minimization:**
- Collect only necessary data
- Anonymize where possible
- Aggregate early, discard raw data when appropriate
- No collection of unnecessary PII

**Encryption:**
- TLS/HTTPS for data in transit
- AES-256 for data at rest
- Encryption keys managed via Supabase Vault
- Regular key rotation

**Anonymization:**
- IP address anonymization (last octet removed)
- User ID hashing in reports
- No PII in exported data
- Aggregated data only in public dashboards

#### 5.2 Data Retention & Deletion

**Retention Periods:**
- Raw events: 90 days in hot storage, then archive
- Aggregated metrics: 2 years
- User data: Until account deletion + 30 days
- Backups: 90 days

**User Data Deletion:**
```sql
-- Complete user data deletion process
CREATE OR REPLACE FUNCTION delete_user_data(p_user_id UUID)
RETURNS void AS $$
BEGIN
  -- Soft delete user
  UPDATE users SET deleted_at = NOW() WHERE id = p_user_id;
  
  -- Anonymize analytics events
  UPDATE analytics_events 
  SET user_id = NULL, 
      event_properties = jsonb_set(event_properties, '{user_id}', '"anonymized"')
  WHERE user_id = p_user_id;
  
  -- Delete personal data after 30 days (run via scheduled job)
  -- DELETE FROM users WHERE deleted_at < NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;
```

#### 5.3 Compliance Requirements

**Living Constitution Alignment:**
- Technology serves humanity principle
- Data sovereignty respected
- User empowerment over their data
- Transparent data practices

**Regulatory Compliance:**
- GDPR-ready (if applicable)
- Right to access data
- Right to deletion
- Data portability
- Privacy by design

### 6. Analytics API

#### 6.1 API Endpoints

**Metrics Retrieval:**
```
GET /api/metrics/flourish-index?user_id={id}&date={date}
GET /api/metrics/add-value-index?user_id={id}&date={date}
GET /api/metrics/platform-summary?date={date}
GET /api/metrics/user-activity?user_id={id}&from={date}&to={date}
```

**Dashboard Data:**
```
GET /api/dashboard/flourish?from={date}&to={date}
GET /api/dashboard/add-value?from={date}&to={date}
GET /api/dashboard/wave-participation?from={date}&to={date}
GET /api/dashboard/executive-summary
```

**Real-time Metrics:**
```
GET /api/realtime/dau
GET /api/realtime/active-sessions
GET /api/realtime/live-waves
WebSocket: ws://api/realtime/metrics
```

#### 6.2 API Authentication & Authorization

- JWT-based authentication
- Role-based access control (RBAC)
- API rate limiting: 1000 requests/hour per user
- Audit logging of all API access

#### 6.3 API Response Format

```json
{
  "status": "success",
  "data": {
    "metric": "flourish_index",
    "value": 75.5,
    "date": "2024-01-15",
    "breakdown": {
      "mood_score": 80,
      "microact_score": 75,
      "community_score": 70,
      "consistency_score": 75
    }
  },
  "metadata": {
    "calculated_at": "2024-01-15T10:30:00Z",
    "data_points": 1543,
    "confidence": "high"
  }
}
```

### 7. Implementation Checklist

#### Phase 1: Foundation (Week 1-2)
- [ ] Set up analytics_events table
- [ ] Implement event validation service
- [ ] Create event collection SDK for React Native
- [ ] Set up basic pipeline monitoring
- [ ] Implement consent management

#### Phase 2: Core Metrics (Week 3-4)
- [ ] Create daily/platform metrics tables
- [ ] Implement batch jobs for metric calculation
- [ ] Set up Flourish Index calculation
- [ ] Set up Add-Value Index calculation
- [ ] Create database views for common queries

#### Phase 3: Dashboards (Week 5-6)
- [ ] Implement Flourish Index dashboard
- [ ] Implement Add-Value Index dashboard
- [ ] Implement Wave Participation dashboard
- [ ] Set up real-time data subscriptions
- [ ] Create API endpoints for dashboard data

#### Phase 4: Advanced Features (Week 7-8)
- [ ] Implement retention cohort analysis
- [ ] Set up anomaly detection
- [ ] Create executive summary dashboard
- [ ] Implement data export functionality
- [ ] Set up automated reports

#### Phase 5: Optimization & Scale (Week 9-10)
- [ ] Performance optimization
- [ ] Implement caching strategy
- [ ] Set up data archival process
- [ ] Load testing and scaling
- [ ] Documentation and training

### 8. Success Metrics for Analytics System

- **Availability**: 99.9% uptime
- **Latency**: < 200ms API response time (95th percentile)
- **Accuracy**: < 0.1% error rate in calculations
- **Completeness**: > 99% event capture rate
- **Compliance**: 100% compliance with privacy policies
- **User Trust**: > 80% user satisfaction with data transparency

## Tools & Technologies

**Data Collection:**
- Supabase Realtime for event streaming
- React Native SDK for client-side tracking
- PostgreSQL for event storage

**Processing:**
- PostgreSQL functions for calculations
- Supabase Edge Functions for processing
- Cron jobs for batch processing

**Monitoring:**
- Supabase Dashboard for database monitoring
- Custom monitoring dashboard for pipeline health
- Error tracking (Sentry or similar)

**Dashboards:**
- React/Next.js for dashboard UI
- Recharts/D3.js for visualizations
- Redis for caching

## Next Steps

1. Review and approve this architecture
2. Set up development environment
3. Begin Phase 1 implementation
4. Regular check-ins with Product and Technical teams
5. Iterate based on feedback and requirements
