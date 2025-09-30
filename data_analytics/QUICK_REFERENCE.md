# Data Analytics Quick Reference

## Key Metrics At-a-Glance

| Metric | Target | Current Status | How to Check |
|--------|--------|----------------|--------------|
| Weekly Active Users (WAU) | 1,000 | TBD | `SELECT * FROM weekly_active_users;` |
| Avg Flourish Index | 70+ | TBD | `SELECT AVG(flourish_index) FROM daily_user_metrics WHERE metric_date = CURRENT_DATE - 1;` |
| Wave Participation Rate | 60% | TBD | `SELECT (wave_participants::float / wau) * 100 FROM platform_metrics;` |
| 7-Day Retention | 40% | TBD | Calculate from users table |
| Activation Completion | 80% | TBD | `SELECT * FROM activation_completion_stats;` |

## Essential SQL Queries

### Daily Active Users (DAU)
```sql
SELECT COUNT(DISTINCT user_id) as dau
FROM users
WHERE last_activity_date = CURRENT_DATE
  AND is_active = true;
```

### User Flourish Index
```sql
SELECT 
  user_id,
  flourish_index,
  metric_date
FROM daily_user_metrics
WHERE metric_date = CURRENT_DATE - INTERVAL '1 day'
ORDER BY flourish_index DESC
LIMIT 10;
```

### Wave Participation Summary
```sql
SELECT 
  w.title,
  w.scheduled_at,
  COUNT(p.id) as participants,
  AVG(p.rating) as avg_rating
FROM wave_events w
LEFT JOIN wave_participation p ON w.id = p.wave_id
WHERE w.status = 'completed'
GROUP BY w.id
ORDER BY w.scheduled_at DESC
LIMIT 5;
```

### Mood Shift Trends
```sql
SELECT 
  DATE(started_at) as date,
  AVG(mood_shift) as avg_shift,
  COUNT(*) as sessions
FROM activation_sessions
WHERE is_completed = true
  AND started_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE(started_at)
ORDER BY date;
```

### Micro-Acts by Category
```sql
SELECT 
  category,
  COUNT(*) as count,
  AVG(value_added_score) as avg_value
FROM micro_acts
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY category
ORDER BY count DESC;
```

## Index Calculations

### Flourish Index Formula
```
Flourish Index = (mood_score × 0.4) + (microact_score × 0.3) + (community_score × 0.2) + (consistency_score × 0.1)
```

Components:
- **Mood Score (40%)**: Based on mood shift from Activation Day
- **Micro-act Score (30%)**: Based on number of micro-acts logged
- **Community Score (20%)**: Based on community interactions and posts
- **Consistency Score (10%)**: Based on activation streak

### Add-Value Index Formula
```
Add-Value Index = (microact_value × 0.5) + (community_interactions × 0.3) + (wave_participation × 0.2)
```

Components:
- **Micro-act Value (50%)**: Based on micro-acts benefiting others
- **Community Interactions (30%)**: Based on posts and interactions
- **Wave Participation (20%)**: Based on Wave attendance and engagement

## API Endpoints

### Metrics
- `GET /api/metrics/flourish-index?user_id={id}&date={date}`
- `GET /api/metrics/add-value-index?user_id={id}&date={date}`
- `GET /api/metrics/platform-summary?date={date}`

### Dashboards
- `GET /api/dashboard/flourish?from={date}&to={date}`
- `GET /api/dashboard/add-value?from={date}&to={date}`
- `GET /api/dashboard/wave-participation?from={date}&to={date}`

### Real-time
- `GET /api/realtime/dau`
- `WebSocket: ws://api/realtime/metrics`

## Database Tables Reference

### Core Tables
- `users` - User profiles and activity tracking
- `activation_sessions` - Activation Day sessions
- `micro_acts` - User-logged micro-acts
- `wave_events` - Weekly Wave events
- `wave_participation` - Wave attendance tracking
- `community_posts` - Community feed posts
- `community_interactions` - Likes, comments, shares

### Metrics Tables
- `daily_user_metrics` - Daily user-level metrics
- `platform_metrics` - Daily platform-wide metrics
- `analytics_events` - Raw event log

### Helper Tables
- `user_streaks` - Activation streaks
- `hourly_metrics` - Hourly aggregations (optional)

## Event Types

### Activation Events
- `activation_started`
- `activation_round_completed`
- `activation_affirmation_selected`
- `activation_mood_logged`
- `activation_completed`

### Micro-Act Events
- `microact_created`
- `microact_updated`
- `microact_shared`

### Wave Events
- `wave_registered`
- `wave_joined`
- `wave_left`
- `wave_feedback_submitted`

### Community Events
- `post_created`
- `post_liked`
- `post_commented`

## Batch Jobs Schedule

| Job | Frequency | Time (UTC) | Purpose |
|-----|-----------|------------|---------|
| Real-time metrics | Continuous | - | DAU, events count |
| Hourly aggregation | Every hour | :00 | Hourly metrics |
| Daily metrics | Daily | 02:00 | User & platform metrics |
| Weekly summary | Weekly | Mon 03:00 | WAU, retention |
| Monthly report | Monthly | 1st, 04:00 | MAU, cohorts |

## Common Tasks

### Add New Metric
1. Define in `metrics_definition.md`
2. Add column to relevant table
3. Update calculation function
4. Add to dashboard specification
5. Update API endpoints

### Debug Missing Data
```sql
-- Check event flow
SELECT event_name, COUNT(*), MAX(created_at)
FROM analytics_events
WHERE created_at >= CURRENT_DATE - INTERVAL '24 hours'
GROUP BY event_name;

-- Check batch job status
SELECT * FROM cron.job_run_details 
WHERE end_time >= NOW() - INTERVAL '24 hours'
ORDER BY end_time DESC;

-- Verify RLS policies
SELECT * FROM pg_policies WHERE tablename = 'users';
```

### Check Data Quality
```sql
-- Completeness check
SELECT 
  COUNT(*) as total_users,
  COUNT(last_activity_date) as with_activity,
  COUNT(*) - COUNT(last_activity_date) as missing
FROM users
WHERE is_active = true;

-- Range validation
SELECT 
  'Flourish Index out of range' as issue,
  COUNT(*) as count
FROM daily_user_metrics
WHERE flourish_index < 0 OR flourish_index > 100;
```

## Performance Optimization

### Index Usage
```sql
-- Check index usage
SELECT 
  schemaname,
  tablename,
  indexname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

### Query Optimization
```sql
-- Use EXPLAIN ANALYZE for slow queries
EXPLAIN ANALYZE
SELECT * FROM daily_user_metrics
WHERE metric_date >= CURRENT_DATE - INTERVAL '30 days';
```

### Caching Strategy
- Cache dashboard data for 5 minutes
- Cache real-time metrics for 1 minute
- Cache platform summary for 10 minutes

## Monitoring Alerts

### Critical Alerts
- No events in last hour
- Batch job failure
- Error rate > 1%
- Pipeline lag > 5 minutes

### Warning Alerts
- Event volume drop > 30%
- Data quality issues
- API response time > 200ms
- Dashboard load time > 2s

## Privacy Controls

### User Data Access
```sql
-- User can access their own data
SELECT * FROM users WHERE id = auth.uid();
SELECT * FROM daily_user_metrics WHERE user_id = auth.uid();
```

### Data Deletion
```sql
-- Delete user data (admin only)
SELECT delete_user_data('[USER_ID]');
```

### Anonymization
```sql
-- Anonymize for reporting
SELECT 
  'user_' || ROW_NUMBER() OVER (ORDER BY add_value_index DESC) as anonymous_id,
  add_value_index,
  micro_acts_count
FROM daily_user_metrics
WHERE metric_date = CURRENT_DATE - 1
ORDER BY add_value_index DESC
LIMIT 10;
```

## Troubleshooting Quick Fixes

### Issue: Events not tracking
```bash
# Check Edge Function logs
supabase functions logs track-event

# Test event API
curl -X POST https://[project].supabase.co/functions/v1/track-event \
  -H "Authorization: Bearer [token]" \
  -H "Content-Type: application/json" \
  -d '{"event_name":"test","event_category":"test"}'
```

### Issue: Dashboard no data
```sql
-- Verify data exists
SELECT COUNT(*) FROM daily_user_metrics WHERE metric_date >= CURRENT_DATE - 7;

-- Check RLS policies allow access
SET ROLE authenticated;
SELECT * FROM daily_user_metrics LIMIT 1;
```

### Issue: Batch job not running
```sql
-- Check scheduled jobs
SELECT * FROM cron.job;

-- Manual trigger
SELECT calculate_daily_metrics();
```

## File Structure

```
data_analytics/
├── README.md                        # Overview and quick start
├── QUICK_REFERENCE.md              # This file
├── IMPLEMENTATION_GUIDE.md         # Step-by-step implementation
├── metrics_definition.md           # All metrics defined
├── database_schema.sql             # Database schema
├── dashboard_specifications.md     # Dashboard specs
└── data_collection_pipeline.md     # Pipeline architecture
```

## Key Contacts

- **Technical Issues**: engineering@valueadders.world
- **Data Questions**: data@valueadders.world  
- **Privacy Concerns**: privacy@valueadders.world
- **General Support**: support@valueadders.world

## Useful Links

- Supabase Dashboard: https://app.supabase.com/project/[project-id]
- Analytics Dashboard: https://analytics.valueadders.world
- API Documentation: https://api.valueadders.world/docs
- GitHub Repository: https://github.com/ValueaddersWorld/value-adders-agents

## Version Information

- **Schema Version**: 1.0
- **Last Updated**: 2024-01-15
- **Maintained By**: Data Analytics Agent
