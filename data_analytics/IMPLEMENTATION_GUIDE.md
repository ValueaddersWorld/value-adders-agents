# Implementation Guide for Data Analytics System

## Overview
This guide provides step-by-step instructions for implementing the Data & Analytics infrastructure for the AddValue App. Follow these steps in order to ensure a successful deployment.

## Prerequisites

### Required Access & Tools
- [ ] Supabase project access with admin privileges
- [ ] PostgreSQL client (psql or GUI like pgAdmin)
- [ ] Git repository access
- [ ] Node.js 18+ for dashboard development
- [ ] React Native development environment

### Required Knowledge
- PostgreSQL/SQL
- React/Next.js
- REST API development
- Data visualization libraries (Recharts, D3.js)

## Phase 1: Database Setup (Week 1)

### Step 1.1: Deploy Database Schema

1. Connect to your Supabase database:
   ```bash
   # Get connection string from Supabase dashboard
   # Settings → Database → Connection string
   
   psql "postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-ID].supabase.co:5432/postgres"
   ```

2. Review the schema file:
   ```bash
   cat data_analytics/database_schema.sql
   ```

3. Deploy the schema:
   ```sql
   \i data_analytics/database_schema.sql
   ```

4. Verify tables were created:
   ```sql
   \dt
   
   -- Should show:
   -- users
   -- activation_sessions
   -- user_streaks
   -- micro_acts
   -- wave_events
   -- wave_participation
   -- community_posts
   -- community_interactions
   -- daily_user_metrics
   -- platform_metrics
   -- analytics_events
   ```

5. Test the functions:
   ```sql
   -- Test Flourish Index calculation
   SELECT calculate_flourish_index(
     (SELECT id FROM users LIMIT 1),
     CURRENT_DATE
   );
   
   -- Test Add-Value Index calculation
   SELECT calculate_add_value_index(
     (SELECT id FROM users LIMIT 1),
     CURRENT_DATE
   );
   ```

### Step 1.2: Set Up Row Level Security (RLS)

The schema includes RLS policies. Verify they are enabled:

```sql
-- Check RLS is enabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
  AND tablename IN ('users', 'activation_sessions', 'micro_acts');
```

### Step 1.3: Create Initial Test Data

```sql
-- Insert a test user
INSERT INTO users (email, username, full_name, data_collection_consent)
VALUES ('test@example.com', 'test_user', 'Test User', true)
RETURNING id;

-- Save the returned UUID for next steps

-- Insert test activation session
INSERT INTO activation_sessions (
  user_id, 
  started_at, 
  completed_at,
  is_completed,
  rounds_completed,
  start_mood_score,
  end_mood_score,
  affirmations_completed
) VALUES (
  '[USER_ID_FROM_ABOVE]',
  NOW() - INTERVAL '1 hour',
  NOW(),
  true,
  8,
  4,
  8,
  18
);

-- Insert test micro-acts
INSERT INTO micro_acts (user_id, category, title, impact_scope, value_added_score)
VALUES 
  ('[USER_ID]', 'compassion', 'Helped neighbor', 'one_person', 8),
  ('[USER_ID]', 'service', 'Volunteered at food bank', 'community', 9),
  ('[USER_ID]', 'gratitude', 'Thanked a friend', 'one_person', 7);

-- Verify data
SELECT * FROM activation_sessions;
SELECT * FROM micro_acts;
```

## Phase 2: Event Collection Setup (Week 1-2)

### Step 2.1: Configure Supabase Realtime

1. Enable Realtime for the `analytics_events` table:
   - Go to Supabase Dashboard → Database → Replication
   - Enable replication for `analytics_events` table

2. Test Realtime subscription:
   ```javascript
   import { createClient } from '@supabase/supabase-js'
   
   const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)
   
   const channel = supabase
     .channel('analytics-events')
     .on('postgres_changes', 
       { event: 'INSERT', schema: 'public', table: 'analytics_events' },
       (payload) => console.log('New event:', payload)
     )
     .subscribe()
   ```

### Step 2.2: Create Event Collection API

Create a Supabase Edge Function for event validation:

```bash
# Create edge function
supabase functions new track-event
```

Edit `supabase/functions/track-event/index.ts`:

```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

serve(async (req) => {
  try {
    const { event_name, event_category, properties, context } = await req.json()
    
    // Validation
    if (!event_name || !event_category) {
      return new Response(
        JSON.stringify({ error: 'Missing required fields' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      )
    }
    
    // Initialize Supabase client
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? ''
    )
    
    // Get user from JWT
    const authHeader = req.headers.get('Authorization')!
    const { data: { user }, error: authError } = await supabaseClient.auth.getUser(
      authHeader.replace('Bearer ', '')
    )
    
    if (authError || !user) {
      return new Response(
        JSON.stringify({ error: 'Unauthorized' }),
        { status: 401, headers: { 'Content-Type': 'application/json' } }
      )
    }
    
    // Insert event
    const { error: insertError } = await supabaseClient
      .from('analytics_events')
      .insert({
        user_id: user.id,
        event_name,
        event_category,
        event_properties: properties,
        device_type: context?.device_type,
        platform: context?.platform,
        app_version: context?.app_version
      })
    
    if (insertError) throw insertError
    
    return new Response(
      JSON.stringify({ success: true }),
      { headers: { 'Content-Type': 'application/json' } }
    )
  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    )
  }
})
```

Deploy the function:
```bash
supabase functions deploy track-event
```

### Step 2.3: Integrate Event Tracking in React Native

Create `analytics.ts` in your React Native app:

```typescript
import { supabase } from './supabase'

export const trackEvent = async (
  eventName: string,
  eventCategory: string,
  properties?: Record<string, any>
) => {
  try {
    const { data, error } = await supabase.functions.invoke('track-event', {
      body: {
        event_name: eventName,
        event_category: eventCategory,
        properties,
        context: {
          device_type: 'mobile',
          platform: Platform.OS,
          app_version: '1.0.0'
        }
      }
    })
    
    if (error) console.error('Event tracking error:', error)
  } catch (err) {
    console.error('Failed to track event:', err)
  }
}

// Usage examples:
export const trackActivationStarted = () => 
  trackEvent('activation_started', 'activation')

export const trackMicroActLogged = (category: string, impactScope: string) =>
  trackEvent('microact_created', 'micro_acts', { category, impact_scope: impactScope })

export const trackWaveJoined = (waveId: string) =>
  trackEvent('wave_joined', 'waves', { wave_id: waveId })
```

## Phase 3: Batch Jobs Setup (Week 2-3)

### Step 3.1: Create Daily Metrics Calculation Job

Create a Supabase Edge Function or cron job:

```sql
-- Create function to run daily metrics calculation
CREATE OR REPLACE FUNCTION calculate_daily_metrics()
RETURNS void AS $$
BEGIN
  -- Insert daily user metrics for yesterday
  INSERT INTO daily_user_metrics (
    user_id,
    metric_date,
    flourish_index,
    add_value_index,
    activation_completed,
    activation_streak,
    micro_acts_count,
    wave_participated
  )
  SELECT 
    u.id as user_id,
    (CURRENT_DATE - INTERVAL '1 day')::date as metric_date,
    calculate_flourish_index(u.id, (CURRENT_DATE - INTERVAL '1 day')::date) as flourish_index,
    calculate_add_value_index(u.id, (CURRENT_DATE - INTERVAL '1 day')::date) as add_value_index,
    EXISTS(SELECT 1 FROM activation_sessions WHERE user_id = u.id AND DATE(started_at) = (CURRENT_DATE - INTERVAL '1 day')::date AND is_completed = true) as activation_completed,
    COALESCE((SELECT current_streak FROM user_streaks WHERE user_id = u.id), 0) as activation_streak,
    (SELECT COUNT(*) FROM micro_acts WHERE user_id = u.id AND DATE(created_at) = (CURRENT_DATE - INTERVAL '1 day')::date) as micro_acts_count,
    EXISTS(SELECT 1 FROM wave_participation WHERE user_id = u.id AND DATE(joined_at) = (CURRENT_DATE - INTERVAL '1 day')::date) as wave_participated
  FROM users u
  WHERE u.is_active = true
  ON CONFLICT (user_id, metric_date) DO UPDATE
  SET 
    flourish_index = EXCLUDED.flourish_index,
    add_value_index = EXCLUDED.add_value_index;
  
  -- Calculate platform metrics
  INSERT INTO platform_metrics (
    metric_date,
    dau,
    new_users,
    activations_completed,
    micro_acts_total,
    avg_flourish_index,
    avg_add_value_index
  )
  SELECT 
    (CURRENT_DATE - INTERVAL '1 day')::date,
    COUNT(DISTINCT CASE WHEN last_activity_date = (CURRENT_DATE - INTERVAL '1 day')::date THEN id END),
    COUNT(CASE WHEN created_at::date = (CURRENT_DATE - INTERVAL '1 day')::date THEN 1 END),
    (SELECT COUNT(*) FROM activation_sessions WHERE DATE(started_at) = (CURRENT_DATE - INTERVAL '1 day')::date AND is_completed = true),
    (SELECT COUNT(*) FROM micro_acts WHERE DATE(created_at) = (CURRENT_DATE - INTERVAL '1 day')::date),
    (SELECT AVG(flourish_index) FROM daily_user_metrics WHERE metric_date = (CURRENT_DATE - INTERVAL '1 day')::date),
    (SELECT AVG(add_value_index) FROM daily_user_metrics WHERE metric_date = (CURRENT_DATE - INTERVAL '1 day')::date)
  FROM users
  ON CONFLICT (metric_date) DO UPDATE
  SET 
    dau = EXCLUDED.dau,
    new_users = EXCLUDED.new_users,
    activations_completed = EXCLUDED.activations_completed;
END;
$$ LANGUAGE plpgsql;
```

### Step 3.2: Schedule the Job

Using Supabase's `pg_cron` extension:

```sql
-- Enable pg_cron
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Schedule daily metrics job at 2 AM UTC
SELECT cron.schedule(
  'calculate-daily-metrics',
  '0 2 * * *',
  'SELECT calculate_daily_metrics();'
);

-- Verify scheduled jobs
SELECT * FROM cron.job;
```

Alternatively, use GitHub Actions or external cron service.

## Phase 4: Dashboard Development (Week 3-5)

### Step 4.1: Set Up Dashboard Project

```bash
# Create Next.js project
npx create-next-app@latest addvalue-dashboards
cd addvalue-dashboards

# Install dependencies
npm install @supabase/supabase-js recharts date-fns
npm install -D @types/node @types/react
```

### Step 4.2: Create API Routes

Create `pages/api/metrics/flourish-index.ts`:

```typescript
import { createClient } from '@supabase/supabase-js'
import type { NextApiRequest, NextApiResponse } from 'next'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
)

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  const { from, to } = req.query
  
  try {
    const { data, error } = await supabase
      .from('daily_user_metrics')
      .select('metric_date, flourish_index')
      .gte('metric_date', from)
      .lte('metric_date', to)
      .order('metric_date', { ascending: true })
    
    if (error) throw error
    
    // Calculate average
    const avgFlourishIndex = data.reduce((sum, d) => sum + (d.flourish_index || 0), 0) / data.length
    
    res.status(200).json({
      data,
      summary: {
        average: avgFlourishIndex.toFixed(2),
        count: data.length
      }
    })
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch data' })
  }
}
```

### Step 4.3: Create Dashboard Components

Create `components/FlourishIndexChart.tsx`:

```typescript
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts'
import { useEffect, useState } from 'react'

export default function FlourishIndexChart() {
  const [data, setData] = useState([])
  
  useEffect(() => {
    fetch('/api/metrics/flourish-index?from=2024-01-01&to=2024-01-31')
      .then(res => res.json())
      .then(result => setData(result.data))
  }, [])
  
  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <h2 className="text-2xl font-bold mb-4">Flourish Index Trend</h2>
      <LineChart width={800} height={400} data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="metric_date" />
        <YAxis domain={[0, 100]} />
        <Tooltip />
        <Legend />
        <Line 
          type="monotone" 
          dataKey="flourish_index" 
          stroke="#10b981" 
          strokeWidth={2}
        />
      </LineChart>
    </div>
  )
}
```

## Phase 5: Testing & Validation (Week 5-6)

### Step 5.1: Data Quality Tests

Create test script `scripts/test_data_quality.sql`:

```sql
-- Test 1: Check for missing data
SELECT 
  'Missing activation data' as test,
  COUNT(*) as failures
FROM users u
WHERE u.last_activity_date >= CURRENT_DATE - INTERVAL '7 days'
  AND NOT EXISTS (
    SELECT 1 FROM activation_sessions 
    WHERE user_id = u.id AND started_at >= CURRENT_DATE - INTERVAL '7 days'
  );

-- Test 2: Verify index calculations
SELECT 
  'Invalid Flourish Index' as test,
  COUNT(*) as failures
FROM daily_user_metrics
WHERE flourish_index < 0 OR flourish_index > 100;

-- Test 3: Check for duplicate events
SELECT 
  'Duplicate events' as test,
  COUNT(*) as failures
FROM (
  SELECT user_id, event_name, created_at, COUNT(*) as cnt
  FROM analytics_events
  GROUP BY user_id, event_name, created_at
  HAVING COUNT(*) > 1
) duplicates;
```

### Step 5.2: Performance Testing

```sql
-- Check query performance
EXPLAIN ANALYZE
SELECT 
  metric_date,
  AVG(flourish_index) as avg_flourish
FROM daily_user_metrics
WHERE metric_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY metric_date;

-- Ensure indexes are being used
-- Should show "Index Scan" not "Seq Scan"
```

### Step 5.3: Load Testing

Use a tool like `k6` to test API endpoints:

```javascript
import http from 'k6/http'
import { check } from 'k6'

export let options = {
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 0 },
  ],
}

export default function () {
  let res = http.get('https://your-app.com/api/metrics/flourish-index?from=2024-01-01&to=2024-01-31')
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 200ms': (r) => r.timings.duration < 200,
  })
}
```

## Monitoring & Maintenance

### Set Up Alerts

Create monitoring queries to run hourly:

```sql
-- Alert if no events in last hour
SELECT 
  CASE 
    WHEN COUNT(*) = 0 THEN 'ALERT: No events in last hour'
    ELSE 'OK'
  END as status
FROM analytics_events
WHERE created_at >= NOW() - INTERVAL '1 hour';

-- Alert if batch job failed
SELECT 
  CASE
    WHEN NOT EXISTS (
      SELECT 1 FROM daily_user_metrics 
      WHERE metric_date = CURRENT_DATE - INTERVAL '1 day'
    ) THEN 'ALERT: Daily metrics not calculated'
    ELSE 'OK'
  END as status;
```

### Create Admin Dashboard

Add a simple admin page to monitor system health:

```typescript
// pages/admin/health.tsx
export default function HealthDashboard() {
  return (
    <div>
      <h1>Analytics System Health</h1>
      <MetricCard title="Event Ingestion" value={eventRate} unit="events/min" />
      <MetricCard title="Pipeline Lag" value={lagTime} unit="seconds" />
      <MetricCard title="Error Rate" value={errorRate} unit="%" />
      <JobStatus jobs={batchJobs} />
    </div>
  )
}
```

## Rollout Checklist

- [ ] Database schema deployed and tested
- [ ] Row Level Security policies verified
- [ ] Event collection API deployed
- [ ] React Native tracking integrated
- [ ] Batch jobs scheduled and running
- [ ] Dashboards deployed and accessible
- [ ] Monitoring and alerts configured
- [ ] Documentation completed
- [ ] Team training conducted
- [ ] Privacy policies updated
- [ ] User consent flows implemented
- [ ] Load testing completed
- [ ] Security audit passed

## Troubleshooting

### Issue: Events not being captured
- Check API endpoint is accessible
- Verify user authentication token
- Check Supabase RLS policies
- Review Edge Function logs

### Issue: Batch jobs not running
- Verify pg_cron is enabled
- Check scheduled job list: `SELECT * FROM cron.job;`
- Review job run history: `SELECT * FROM cron.job_run_details;`
- Check database permissions

### Issue: Dashboard showing no data
- Verify API endpoints return data
- Check date range filters
- Ensure RLS policies allow access
- Review browser console for errors

## Next Steps After Implementation

1. Monitor system for first week closely
2. Gather feedback from Product and Community teams
3. Iterate on dashboard UX based on feedback
4. Implement additional metrics as needed
5. Set up automated reports
6. Plan for ML/AI features in future phases

## Support

For implementation support:
- Technical questions: engineering@valueadders.world
- Data questions: data@valueadders.world
- Issues: Create GitHub issue in repository
