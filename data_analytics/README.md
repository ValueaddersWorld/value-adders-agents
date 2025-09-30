# Data & Analytics Documentation

## Overview
This directory contains all documentation and specifications for the Data & Analytics infrastructure of the AddValue App. The analytics system is designed to track user engagement, measure well-being impact, and provide actionable insights while maintaining strict privacy and data sovereignty standards aligned with the Living Constitution.

## Contents

### 1. [Metrics Definition](./metrics_definition.md)
Comprehensive definition of all key metrics tracked in the AddValue App:
- **User Activation Metrics**: DAU, WAU, MAU, Activation Day completion rates
- **Micro-Act Metrics**: Daily counts, per-user averages, category distribution
- **Mood & Well-being Metrics**: Mood Shift Index, Flourish Index, Add-Value Index
- **Community Engagement**: Wave participation, feed engagement, Captain activation
- **Retention Metrics**: 7-day and 30-day retention, activation streaks
- **Technical Metrics**: Data collection success rates, performance metrics

### 2. [Database Schema](./database_schema.sql)
Complete PostgreSQL/Supabase database schema including:
- **Core Tables**: Users, activation sessions, micro-acts, Wave events, community posts
- **Metrics Tables**: Daily user metrics, platform metrics, analytics events
- **Calculated Functions**: `calculate_flourish_index()`, `calculate_add_value_index()`
- **Views**: DAU/WAU/MAU views, activation stats, Wave participation stats
- **Security**: Row-level security (RLS) policies, encryption, privacy controls

### 3. [Dashboard Specifications](./dashboard_specifications.md)
Detailed specifications for five core dashboards:
- **Flourish Index Dashboard**: Monitor user well-being and mood improvements
- **Add-Value Index Dashboard**: Track value creation and community impact
- **Wave Participation Dashboard**: Measure Weekly Wave engagement and effectiveness
- **User Growth & Retention Dashboard**: Track acquisition, activation, and retention
- **Executive Summary Dashboard**: High-level metrics for leadership

### 4. [Data Collection & Pipeline](./data_collection_pipeline.md)
Architecture and processes for data collection and analytics:
- **Event Collection System**: Event types, schema, collection methods
- **Data Ingestion Pipeline**: Validation, enrichment, storage, processing
- **Metrics Calculation**: Real-time, hourly, daily, weekly, and monthly batch jobs
- **Data Quality & Monitoring**: Quality checks, alerting, pipeline health
- **Privacy & Compliance**: Consent management, encryption, data retention
- **Analytics API**: Endpoints for metrics retrieval and dashboard data

## Quick Start

### Prerequisites
- Supabase project set up
- PostgreSQL 14+ (via Supabase)
- React Native app for client-side tracking

### Setup Steps

1. **Deploy Database Schema**
   ```bash
   # Connect to your Supabase database
   psql -h your-project.supabase.co -U postgres
   
   # Run the schema file
   \i database_schema.sql
   ```

2. **Configure Event Collection**
   - Integrate event tracking SDK in React Native app
   - Set up Supabase Realtime subscriptions
   - Configure batch jobs for metric calculations

3. **Deploy Dashboards**
   - Build dashboard components using React/Next.js
   - Connect to Supabase for data fetching
   - Implement role-based access control

4. **Set Up Monitoring**
   - Configure pipeline health monitoring
   - Set up alerting for data quality issues
   - Create admin dashboard for system health

## Key Metrics Summary

### North Star Metrics
1. **Weekly Active Users (WAU)**: Target 1000 by Q1
2. **Average Flourish Index**: Target 70+ (healthy threshold)
3. **Wave Participation Rate**: Target 60% of WAU
4. **7-Day Retention**: Target 40%

### Composite Indices

**Flourish Index (0-100)**
- Mood improvement: 40% weight
- Micro-acts frequency: 30% weight
- Community engagement: 20% weight
- Activation Day consistency: 10% weight

**Add-Value Index (0-100)**
- Micro-acts benefiting others: 50% weight
- Community interactions: 30% weight
- Wave participation: 20% weight

## Privacy & Data Sovereignty

All analytics adhere to strict privacy principles:
- ✅ AES-256 encryption for data at rest
- ✅ Anonymization of personal data in aggregated reports
- ✅ User consent required for data collection
- ✅ Compliance with data sovereignty requirements
- ✅ Alignment with Living Constitution principles
- ✅ User right to access and delete their data

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
- Set up database tables
- Implement event collection
- Create basic pipeline

### Phase 2: Core Metrics (Week 3-4)
- Deploy metric calculations
- Set up batch jobs
- Create database views

### Phase 3: Dashboards (Week 5-6)
- Build Flourish Index dashboard
- Build Add-Value Index dashboard
- Build Wave Participation dashboard

### Phase 4: Advanced Features (Week 7-8)
- Implement retention analysis
- Create executive dashboard
- Set up automated reports

### Phase 5: Optimization (Week 9-10)
- Performance tuning
- Caching implementation
- Load testing

## API Examples

### Get Flourish Index
```javascript
// GET /api/metrics/flourish-index?user_id={id}&date={date}
const response = await fetch(`/api/metrics/flourish-index?user_id=${userId}&date=2024-01-15`);
const data = await response.json();
// Returns: { value: 75.5, breakdown: {...}, metadata: {...} }
```

### Get Platform Summary
```javascript
// GET /api/metrics/platform-summary?date={date}
const response = await fetch('/api/metrics/platform-summary?date=2024-01-15');
const data = await response.json();
// Returns: { dau: 542, wau: 1234, avg_flourish: 72.3, ... }
```

### Real-time Metrics via WebSocket
```javascript
const ws = new WebSocket('ws://api/realtime/metrics');
ws.onmessage = (event) => {
  const metrics = JSON.parse(event.data);
  updateDashboard(metrics);
};
```

## SQL Query Examples

### Calculate WAU
```sql
SELECT COUNT(DISTINCT user_id) as wau
FROM users
WHERE last_activity_date >= CURRENT_DATE - INTERVAL '7 days'
  AND is_active = true;
```

### Get Mood Shift Trends
```sql
SELECT 
  DATE(started_at) as date,
  AVG(mood_shift) as avg_mood_shift,
  COUNT(*) as sessions
FROM activation_sessions
WHERE is_completed = true
  AND started_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(started_at)
ORDER BY date;
```

### Top Value Adders
```sql
SELECT 
  u.username,
  dum.add_value_index,
  dum.micro_acts_count,
  dum.interactions_given
FROM daily_user_metrics dum
JOIN users u ON dum.user_id = u.id
WHERE dum.metric_date = CURRENT_DATE - INTERVAL '1 day'
ORDER BY dum.add_value_index DESC
LIMIT 10;
```

## Reporting Cadence

- **Real-time**: DAU, micro-acts count, live Wave participants
- **Daily**: All user metrics, Flourish/Add-Value indices, completion rates
- **Weekly**: Retention rates, Wave summaries, trend analysis
- **Monthly**: Growth metrics, cohort analysis, executive reports

## Support & Maintenance

### Monitoring
- Pipeline health dashboard at `/admin/analytics/health`
- Data quality scores updated hourly
- Automated alerts for anomalies

### Troubleshooting
- Check pipeline logs: `SELECT * FROM analytics_events WHERE created_at > NOW() - INTERVAL '1 hour' ORDER BY created_at DESC`
- Verify batch job status: `SELECT * FROM job_runs WHERE status = 'failed'`
- Monitor query performance: Use Supabase Dashboard → Performance tab

### Contact
- Data Team: data@valueadders.world
- Technical Issues: Submit issue to engineering team
- Privacy Concerns: privacy@valueadders.world

## Contributing

When adding new metrics or dashboards:
1. Update `metrics_definition.md` with new metric specifications
2. Add database schema changes to `database_schema.sql`
3. Document dashboard requirements in `dashboard_specifications.md`
4. Update pipeline documentation in `data_collection_pipeline.md`
5. Test thoroughly in development environment
6. Submit for review by Data Analytics Agent and Technical Architect

## License & Compliance

All analytics systems and documentation align with:
- Value Adders World Living Constitution
- Principle: Technology must serve humanity
- Data sovereignty and privacy requirements
- Ethical AI and data practices

---

**Last Updated**: 2024-01-15
**Maintained by**: Data Analytics Agent
**Version**: 1.0
