# Key Metrics for AddValue App

## Overview
This document defines the key metrics for the AddValue App to track user engagement, value creation, and community health. All metrics align with the Living Constitution and the principle that technology must serve humanity.

## User Activation Metrics

### 1. Activation Day Completion Rate
- **Definition**: Percentage of users who complete the full Activation Day flow (18 affirmations, 8 rounds)
- **Formula**: (Users completing all 8 rounds / Total users starting Activation Day) × 100
- **Target**: 80% completion rate
- **Collection**: Track start and completion timestamps in `activation_sessions` table

### 2. Daily Active Users (DAU)
- **Definition**: Number of unique users engaging with the app each day
- **Formula**: COUNT(DISTINCT user_id) WHERE last_activity_date = CURRENT_DATE
- **Collection**: Update `users.last_activity_date` on any user action

### 3. Weekly Active Users (WAU)
- **Definition**: Number of unique users engaging with the app in the past 7 days
- **Formula**: COUNT(DISTINCT user_id) WHERE last_activity_date >= CURRENT_DATE - INTERVAL '7 days'
- **Target**: 1000 WAU by end of Q1
- **Collection**: Track via `users.last_activity_date`

### 4. Monthly Active Users (MAU)
- **Definition**: Number of unique users engaging with the app in the past 30 days
- **Formula**: COUNT(DISTINCT user_id) WHERE last_activity_date >= CURRENT_DATE - INTERVAL '30 days'
- **Collection**: Track via `users.last_activity_date`

## Micro-Act Metrics

### 5. Daily Micro-Acts Count
- **Definition**: Total number of micro-acts logged per day
- **Formula**: COUNT(*) FROM micro_acts WHERE created_at::date = CURRENT_DATE
- **Collection**: Count entries in `micro_acts` table

### 6. Micro-Acts Per User (Average)
- **Definition**: Average number of micro-acts logged per active user
- **Formula**: Total micro-acts / DAU
- **Target**: 3-5 micro-acts per active user per day
- **Collection**: Aggregate from `micro_acts` table

### 7. Micro-Act Category Distribution
- **Definition**: Breakdown of micro-acts by category (compassion, creativity, service, etc.)
- **Collection**: GROUP BY category in `micro_acts` table

## Mood & Well-being Metrics

### 8. Mood Shift Index
- **Definition**: Average change in user mood from start to end of Activation Day
- **Formula**: AVG(end_mood_score - start_mood_score)
- **Scale**: -10 to +10 (where positive indicates improvement)
- **Target**: Average positive shift of +3 or higher
- **Collection**: Store in `activation_sessions` table

### 9. Flourish Index
- **Definition**: Composite score measuring user well-being across multiple dimensions
- **Components**:
  - Mood improvement (40% weight)
  - Micro-acts frequency (30% weight)
  - Community engagement (20% weight)
  - Activation Day consistency (10% weight)
- **Scale**: 0-100
- **Formula**: (mood_score × 0.4) + (microact_score × 0.3) + (community_score × 0.2) + (consistency_score × 0.1)
- **Collection**: Calculated daily from multiple tables

### 10. Add-Value Index
- **Definition**: Measure of the value a user adds to others and the community
- **Components**:
  - Micro-acts benefiting others (50% weight)
  - Community interactions (30% weight)
  - Wave participation (20% weight)
- **Scale**: 0-100
- **Collection**: Calculated from `micro_acts`, `community_interactions`, and `wave_participation` tables

## Community Engagement Metrics

### 11. Weekly Wave Participation Rate
- **Definition**: Percentage of active users participating in Weekly Waves
- **Formula**: (Users in Weekly Wave / WAU) × 100
- **Target**: 60% participation rate
- **Collection**: Track in `wave_participation` table

### 12. Wave Attendance
- **Definition**: Number of users attending each Weekly Wave event
- **Collection**: COUNT participants in `wave_participation` WHERE wave_id = X

### 13. Community Feed Engagement
- **Definition**: Average interactions (likes, comments, shares) per community post
- **Formula**: (Total interactions / Total posts)
- **Collection**: Track in `community_interactions` table

### 14. Captain Activation Rate
- **Definition**: Percentage of citizens who become Captains
- **Formula**: (COUNT users WHERE role = 'captain' / COUNT users) × 100
- **Target**: 5% of users become Captains
- **Collection**: Track in `users.role` field

## Retention Metrics

### 15. 7-Day Retention Rate
- **Definition**: Percentage of new users who return within 7 days
- **Formula**: (Users active on day 7 / Users who signed up 7 days ago) × 100
- **Target**: 40% retention
- **Collection**: Calculate from `users.created_at` and `users.last_activity_date`

### 16. 30-Day Retention Rate
- **Definition**: Percentage of new users who return within 30 days
- **Formula**: (Users active on day 30 / Users who signed up 30 days ago) × 100
- **Target**: 25% retention
- **Collection**: Calculate from `users.created_at` and `users.last_activity_date`

### 17. Activation Day Streak
- **Definition**: Consecutive days a user completes Activation Day
- **Collection**: Track in `user_streaks` table
- **Target**: Average streak of 7+ days

## Technical Metrics

### 18. Data Collection Success Rate
- **Definition**: Percentage of events successfully captured
- **Formula**: (Successful events / Total events attempted) × 100
- **Target**: 99.5% success rate
- **Collection**: Monitor via event logging and error tracking

### 19. Dashboard Load Time
- **Definition**: Average time for dashboards to load and display data
- **Target**: < 2 seconds for 95th percentile
- **Collection**: Track via performance monitoring

### 20. API Response Time
- **Definition**: Average response time for analytics API endpoints
- **Target**: < 200ms for 95th percentile
- **Collection**: Track via API monitoring

## Privacy & Data Sovereignty

All metrics collection adheres to:
- AES-256 encryption for data at rest
- Anonymization of personal data in aggregated reports
- User consent for data collection
- Compliance with data sovereignty requirements
- Alignment with Living Constitution principles

## Reporting Cadence

- **Real-time**: DAU, micro-acts count
- **Daily**: All user engagement metrics, Flourish Index, Add-Value Index
- **Weekly**: Retention rates, Wave participation, trend analysis
- **Monthly**: Growth metrics, cohort analysis, strategic insights
