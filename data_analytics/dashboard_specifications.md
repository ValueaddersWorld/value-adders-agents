# Dashboard Specifications for AddValue App

## Overview
This document specifies the initial dashboards for monitoring user engagement, well-being, and community health in the AddValue App. All dashboards are designed to provide actionable insights while respecting user privacy and data sovereignty.

## Dashboard 1: Flourish Index Dashboard

### Purpose
Monitor user well-being and the effectiveness of Activation Day in improving mood and overall flourishing.

### Target Audience
- Product team
- Strategy team
- Community managers
- Leadership

### Key Visualizations

#### 1.1 Flourish Index Trend (Line Chart)
- **Metric**: Average Flourish Index over time
- **Time Range**: Last 30 days, last 90 days, or custom range
- **Granularity**: Daily
- **Y-Axis**: Flourish Index (0-100)
- **X-Axis**: Date
- **Features**:
  - Trend line showing direction
  - Moving average (7-day)
  - Target line at 70 (healthy threshold)
- **Data Source**: `daily_user_metrics.flourish_index`
- **Query**: 
  ```sql
  SELECT 
    metric_date,
    AVG(flourish_index) as avg_flourish_index,
    COUNT(DISTINCT user_id) as users_measured
  FROM daily_user_metrics
  WHERE metric_date >= CURRENT_DATE - INTERVAL '30 days'
  GROUP BY metric_date
  ORDER BY metric_date;
  ```

#### 1.2 Flourish Index Distribution (Histogram)
- **Metric**: Distribution of user Flourish Index scores
- **Bins**: 0-20, 21-40, 41-60, 61-80, 81-100
- **Show**: Number and percentage of users in each range
- **Color Coding**: Red (0-40), Yellow (41-60), Green (61-100)
- **Data Source**: `daily_user_metrics` (most recent date)

#### 1.3 Mood Shift Analysis (Bar Chart)
- **Metric**: Average mood shift from Activation Day
- **Breakdown**: By hour of day, day of week
- **Y-Axis**: Mood shift (-10 to +10)
- **Features**:
  - Highlight hours with best mood improvement
  - Show completion rates alongside
- **Data Source**: `activation_sessions`
- **Query**:
  ```sql
  SELECT 
    EXTRACT(HOUR FROM started_at) as hour_of_day,
    AVG(mood_shift) as avg_mood_shift,
    COUNT(*) FILTER (WHERE is_completed = true) as completions
  FROM activation_sessions
  WHERE started_at >= CURRENT_DATE - INTERVAL '30 days'
  GROUP BY EXTRACT(HOUR FROM started_at)
  ORDER BY hour_of_day;
  ```

#### 1.4 Activation Day Completion Funnel
- **Metric**: User progression through Activation Day
- **Stages**:
  1. Started session (100%)
  2. Completed 4 rounds (% of started)
  3. Completed 8 rounds (% of started)
  4. Logged end mood (% of completed)
- **Visualization**: Funnel chart
- **Data Source**: `activation_sessions`

#### 1.5 Streak Performance (Heatmap)
- **Metric**: User activation streaks
- **Display**: Calendar heatmap for individual users or aggregate
- **Color Intensity**: Based on number of users active each day
- **Features**:
  - Show current average streak
  - Show longest streak achieved
- **Data Source**: `user_streaks`, `activation_sessions`

### KPIs (Top of Dashboard)
- **Average Flourish Index**: Current 7-day average
- **Mood Improvement Rate**: % of sessions with positive mood shift
- **Daily Activation Rate**: % of active users completing Activation Day
- **Average Streak Length**: Mean current streak across all users

### Filters
- Date range selector
- User cohort (new users, returning users, captains)
- Activation Day time (morning, afternoon, evening)

### Refresh Rate
- Real-time updates every 5 minutes during peak hours
- Hourly updates during off-peak

---

## Dashboard 2: Add-Value Index Dashboard

### Purpose
Track the value users are adding to others and the community through micro-acts, interactions, and participation.

### Target Audience
- Community managers
- Product team
- Leadership
- Marketing team

### Key Visualizations

#### 2.1 Add-Value Index Trend (Area Chart)
- **Metric**: Average Add-Value Index over time
- **Time Range**: Last 30 days with comparison to previous period
- **Stacking**: Breakdown by component (micro-acts 50%, community 30%, waves 20%)
- **Y-Axis**: Add-Value Index (0-100)
- **X-Axis**: Date
- **Features**:
  - Show component contributions
  - Highlight top value-adding days
- **Data Source**: `daily_user_metrics.add_value_index`

#### 2.2 Micro-Acts Impact Analysis (Stacked Bar Chart)
- **Metric**: Micro-acts by impact scope
- **Categories**: Self, One Person, Group, Community, World
- **Y-Axis**: Number of micro-acts
- **X-Axis**: Date or category
- **Show**: Distribution and trends over time
- **Data Source**: `micro_acts.impact_scope`
- **Query**:
  ```sql
  SELECT 
    impact_scope,
    COUNT(*) as count,
    AVG(value_added_score) as avg_value
  FROM micro_acts
  WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
  GROUP BY impact_scope
  ORDER BY count DESC;
  ```

#### 2.3 Micro-Act Categories (Pie Chart)
- **Metric**: Distribution of micro-acts by category
- **Categories**: Compassion, Creativity, Service, Gratitude, Learning, Connection, Sustainability, Wellness, Other
- **Show**: Count and percentage for each category
- **Interactive**: Click to drill down into specific category trends
- **Data Source**: `micro_acts.category`

#### 2.4 Top Value Adders (Leaderboard Table)
- **Metric**: Users with highest Add-Value Index
- **Columns**:
  - Rank
  - Username (anonymized if needed)
  - Add-Value Index
  - Micro-acts count
  - Community interactions
  - Wave participation
- **Limit**: Top 50 users
- **Time Range**: Last 7 days or 30 days
- **Privacy**: Option to anonymize usernames
- **Data Source**: `daily_user_metrics`

#### 2.5 Community Engagement Metrics (Multi-Metric Card)
- **Metrics**:
  - Posts created today/this week
  - Average interactions per post
  - Community feed engagement rate
  - Micro-acts shared to feed (%)
- **Visualization**: Metric cards with trend indicators
- **Data Source**: `community_posts`, `community_interactions`

#### 2.6 Value Creation Timeline (Timeline Chart)
- **Metric**: Significant value-adding events
- **Display**: Chronological timeline of high-impact micro-acts and community moments
- **Filters**: By impact scope, category, value score
- **Features**: Click to see details of each micro-act
- **Data Source**: `micro_acts` WHERE `value_added_score >= 8`

### KPIs (Top of Dashboard)
- **Average Add-Value Index**: Current 7-day average
- **Daily Micro-Acts**: Total micro-acts logged today
- **Community Engagement**: Interactions per active user
- **High-Impact Acts**: Micro-acts with scope >= "group" today

### Filters
- Date range selector
- User role (citizen, captain)
- Impact scope
- Category
- Visibility (shared to feed vs. private)

### Refresh Rate
- Real-time updates every 2 minutes for micro-acts count
- Every 10 minutes for calculated indices

---

## Dashboard 3: Wave Participation Dashboard

### Purpose
Monitor Weekly Wave participation, engagement, and impact on community connection.

### Target Audience
- Community managers
- Wave hosts/captains
- Leadership

### Key Visualizations

#### 3.1 Wave Attendance Trend (Line Chart)
- **Metric**: Number of participants per Wave
- **Time Range**: Last 12 weeks
- **Y-Axis**: Participant count
- **X-Axis**: Week/Date
- **Features**:
  - Show capacity utilization if max_participants is set
  - Trend line
  - Average attendance line
- **Data Source**: `wave_participation`, `wave_events`
- **Query**:
  ```sql
  SELECT 
    w.scheduled_at::date as wave_date,
    w.title,
    COUNT(p.id) as participant_count,
    w.max_participants,
    ROUND(100.0 * COUNT(p.id) / NULLIF(w.max_participants, 0), 1) as capacity_pct
  FROM wave_events w
  LEFT JOIN wave_participation p ON w.id = p.wave_id
  WHERE w.status = 'completed'
    AND w.scheduled_at >= CURRENT_DATE - INTERVAL '12 weeks'
  GROUP BY w.id, w.scheduled_at, w.title, w.max_participants
  ORDER BY w.scheduled_at;
  ```

#### 3.2 Energy Boost Analysis (Box Plot)
- **Metric**: Energy level change (before vs. after Wave)
- **Display**: Distribution of energy boost per Wave
- **Y-Axis**: Energy level change (-10 to +10)
- **X-Axis**: Wave date
- **Show**: Median, quartiles, outliers
- **Data Source**: `wave_participation.energy_level_after - energy_level_before`

#### 3.3 Participation Quality Metrics (Gauge Charts)
- **Metrics**:
  - Discussion Participation Rate (% of attendees participating in discussion)
  - Micro-Act Sharing Rate (% of attendees sharing micro-acts)
  - Average Session Rating (1-5 stars)
  - Average Duration (minutes)
- **Visualization**: Multiple gauge charts
- **Data Source**: `wave_participation`

#### 3.4 Wave Participation Rate (Stacked Area Chart)
- **Metric**: Participation rate over time
- **Calculation**: (Wave participants / WAU) × 100
- **Breakdown**: First-time participants vs. returning
- **Y-Axis**: Percentage
- **X-Axis**: Week
- **Target Line**: 60% participation rate
- **Data Source**: `wave_participation`, `weekly_active_users` view

#### 3.5 Host Performance (Table)
- **Metric**: Performance metrics by Wave host
- **Columns**:
  - Host name
  - Waves hosted
  - Avg. attendance
  - Avg. rating
  - Avg. energy boost
  - Participation rate
- **Sorting**: By any column
- **Data Source**: `wave_events`, `wave_participation`
- **Query**:
  ```sql
  SELECT 
    u.username as host_name,
    COUNT(DISTINCT w.id) as waves_hosted,
    AVG(p.participant_count) as avg_attendance,
    AVG(p.avg_rating) as avg_rating,
    AVG(p.avg_energy_boost) as avg_energy_boost
  FROM users u
  JOIN wave_events w ON u.id = w.host_id
  JOIN (
    SELECT 
      wave_id,
      COUNT(*) as participant_count,
      AVG(rating) as avg_rating,
      AVG(energy_level_after - energy_level_before) as avg_energy_boost
    FROM wave_participation
    GROUP BY wave_id
  ) p ON w.id = p.wave_id
  WHERE w.status = 'completed'
  GROUP BY u.id, u.username
  ORDER BY waves_hosted DESC;
  ```

#### 3.6 Upcoming Waves Calendar
- **Display**: Calendar view of scheduled Waves
- **Show**: Date, time, host, registered participants
- **Features**: 
  - Click to see Wave details
  - Registration count vs. capacity
  - Host information
- **Data Source**: `wave_events` WHERE status = 'scheduled'

### KPIs (Top of Dashboard)
- **This Week's Participation**: Number and % of WAU
- **Average Wave Rating**: Current month average
- **Energy Boost**: Average energy level increase
- **Retention Rate**: % of participants attending multiple Waves

### Filters
- Date range selector
- Host selector
- Wave type/theme (if applicable)
- Participant type (first-time vs. returning)

### Refresh Rate
- Real-time during live Waves
- Every 30 minutes for scheduled/completed Waves

---

## Dashboard 4: User Growth & Retention Dashboard

### Purpose
Track user acquisition, activation, retention, and churn patterns.

### Target Audience
- Product team
- Strategy team
- Marketing team
- Leadership

### Key Visualizations

#### 4.1 User Growth (Line Chart)
- **Metrics**:
  - Total users (cumulative)
  - New users (daily/weekly)
  - Active users (DAU, WAU, MAU)
- **Time Range**: Last 90 days
- **Multiple Lines**: Show all metrics on same chart
- **Data Source**: `users`, `daily_active_users`, `weekly_active_users`, `monthly_active_users` views

#### 4.2 Retention Cohorts (Cohort Table)
- **Display**: Cohort retention analysis
- **Rows**: User cohorts by signup week
- **Columns**: Week 0, Week 1, Week 2, ..., Week 12
- **Values**: Retention percentage
- **Color Coding**: Heat map coloring
- **Data Source**: `users.created_at`, `users.last_activity_date`
- **Query**:
  ```sql
  WITH cohorts AS (
    SELECT 
      DATE_TRUNC('week', created_at) as cohort_week,
      user_id,
      created_at
    FROM users
    WHERE created_at >= CURRENT_DATE - INTERVAL '12 weeks'
  )
  SELECT 
    c.cohort_week,
    COUNT(DISTINCT c.user_id) as cohort_size,
    COUNT(DISTINCT CASE WHEN u.last_activity_date >= c.created_at + INTERVAL '7 days' THEN c.user_id END) as week_1_retained,
    -- ... continue for other weeks
  FROM cohorts c
  JOIN users u ON c.user_id = u.id
  GROUP BY c.cohort_week
  ORDER BY c.cohort_week DESC;
  ```

#### 4.3 Activation Funnel (Funnel Chart)
- **Stages**:
  1. Signed up
  2. Completed profile
  3. Completed first Activation Day
  4. Logged first micro-act
  5. Joined first Wave
  6. Became active (3+ sessions)
- **Show**: Conversion rate at each stage
- **Data Source**: Multiple tables

#### 4.4 User Engagement Segments (Pie Chart)
- **Segments**:
  - Power Users (daily activation + 5+ micro-acts/week)
  - Active Users (weekly activation + 2+ micro-acts/week)
  - Casual Users (monthly activation)
  - At-Risk Users (no activity in 14 days)
  - Churned (no activity in 30 days)
- **Show**: Count and percentage for each segment
- **Data Source**: Calculated from multiple metrics

#### 4.5 Feature Adoption (Stacked Bar Chart)
- **Features**:
  - Activation Day
  - Micro-act logging
  - Wave participation
  - Community feed
  - Profile completion
- **Metrics**: % of users who have used each feature
- **Breakdown**: By user cohort or time period
- **Data Source**: Multiple tables

### KPIs (Top of Dashboard)
- **DAU/WAU/MAU**: Current values with % change
- **7-Day Retention**: Current cohort retention rate
- **30-Day Retention**: Current cohort retention rate
- **New Users Today**: Count with trend

### Filters
- Date range
- User cohort
- Acquisition source (if tracked)

---

## Dashboard 5: Executive Summary Dashboard

### Purpose
High-level overview for leadership and strategic decision-making.

### Target Audience
- CEO
- Leadership team
- Board members
- Strategic partners

### Key Visualizations

#### 5.1 North Star Metrics (Metric Cards)
- **Primary Metrics**:
  - Weekly Active Users (WAU)
  - Average Flourish Index
  - Average Add-Value Index
  - Wave Participation Rate
- **Show**: Current value, % change vs. last period, trend indicator
- **Color Coding**: Green (positive), Yellow (neutral), Red (negative)

#### 5.2 Strategic Goals Progress (Progress Bars)
- **Goals**:
  - Reach 1000 WAU (with progress %)
  - Achieve 70+ avg Flourish Index
  - Maintain 60%+ Wave participation
  - 40%+ 7-day retention rate
- **Visualization**: Progress bars with current vs. target
- **Timeline**: Show projected completion date

#### 5.3 Platform Health Score (Gauge)
- **Composite Score**: Weighted combination of:
  - User growth (25%)
  - Engagement (25%)
  - Well-being impact (25%)
  - Community health (25%)
- **Scale**: 0-100
- **Color Zones**: 
  - Red (0-50): Critical
  - Yellow (51-75): Warning
  - Green (76-100): Healthy

#### 5.4 Key Trends (Small Multiples)
- **Charts**: Mini trend charts for:
  - DAU/WAU/MAU trends
  - Activation completion rate
  - Micro-acts per user
  - Wave attendance
  - Retention rates
- **Time Range**: Last 30 days
- **Format**: Sparklines or small line charts

#### 5.5 Impact Highlights (Text Summary)
- **Auto-generated Summary**: Key insights and wins
  - "Mood improvement up 15% this week"
  - "Wave participation reached all-time high"
  - "1000 WAU milestone achieved"
  - "5 users achieved 30-day activation streak"
- **Data Source**: Automated analysis of metrics

### Refresh Rate
- Daily updates (morning refresh)
- On-demand refresh available

---

## Technical Implementation Notes

### Technology Stack
- **Visualization Library**: Recharts, D3.js, or Plotly
- **Dashboard Framework**: React + Next.js or similar
- **Data Source**: Supabase PostgreSQL with real-time subscriptions
- **Caching**: Redis for frequently accessed metrics
- **API**: REST or GraphQL for data fetching

### Performance Optimization
- Pre-calculate complex metrics in `daily_user_metrics` and `platform_metrics` tables
- Use materialized views for heavy queries
- Implement query result caching
- Lazy load dashboard components
- Use pagination for large data sets

### Real-Time Updates
- Use Supabase real-time subscriptions for live metrics
- WebSocket connections for Wave participation during live events
- Polling fallback for browsers without WebSocket support

### Access Control
- Role-based dashboard access (admin, community_manager, viewer)
- Row-level security enforced at database level
- Audit logging for dashboard access

### Data Privacy
- Anonymize user identifiers in aggregated views
- Option to toggle between anonymized and identified data (for authorized users)
- No PII displayed in shared/exported dashboards
- Encryption for data in transit (HTTPS/TLS)

### Export & Reporting
- Export capabilities: CSV, PDF, PNG
- Scheduled reports via email
- API access for programmatic data retrieval
- Customizable report templates

## Next Steps
1. Create wireframes/mockups for each dashboard
2. Develop dashboard components incrementally
3. Set up data pipeline for metric calculations
4. Implement caching strategy
5. Create user documentation
6. Conduct user testing with Product and Community teams
7. Iterate based on feedback
