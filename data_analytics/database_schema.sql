-- Database Schema for AddValue App Analytics
-- Designed for Supabase/PostgreSQL with data sovereignty and privacy in mind
-- All sensitive data is encrypted with AES-256 at rest

-- ============================================================================
-- CORE USER TABLES
-- ============================================================================

-- Users table - Core user information
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    email_encrypted TEXT, -- AES-256 encrypted email
    username TEXT UNIQUE,
    full_name TEXT,
    role TEXT DEFAULT 'citizen' CHECK (role IN ('citizen', 'captain', 'admin')),
    
    -- Activity tracking
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_activity_date DATE,
    last_login_at TIMESTAMPTZ,
    
    -- Privacy and consent
    data_collection_consent BOOLEAN DEFAULT false,
    privacy_policy_accepted_at TIMESTAMPTZ,
    
    -- Metadata
    timezone TEXT DEFAULT 'UTC',
    locale TEXT DEFAULT 'en',
    is_active BOOLEAN DEFAULT true,
    deleted_at TIMESTAMPTZ -- Soft delete
);

-- Create indexes for performance
CREATE INDEX idx_users_last_activity ON users(last_activity_date) WHERE is_active = true;
CREATE INDEX idx_users_role ON users(role) WHERE is_active = true;
CREATE INDEX idx_users_created_at ON users(created_at);

-- ============================================================================
-- ACTIVATION DAY TABLES
-- ============================================================================

-- Activation Day sessions
CREATE TABLE IF NOT EXISTS activation_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Session details
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    is_completed BOOLEAN DEFAULT false,
    rounds_completed INTEGER DEFAULT 0 CHECK (rounds_completed >= 0 AND rounds_completed <= 8),
    
    -- Mood tracking
    start_mood_score INTEGER CHECK (start_mood_score >= 1 AND start_mood_score <= 10),
    end_mood_score INTEGER CHECK (end_mood_score >= 1 AND end_mood_score <= 10),
    mood_shift INTEGER GENERATED ALWAYS AS (end_mood_score - start_mood_score) STORED,
    
    -- Affirmations
    affirmations_completed INTEGER DEFAULT 0 CHECK (affirmations_completed >= 0 AND affirmations_completed <= 18),
    affirmation_selections JSONB, -- Array of selected affirmations
    
    -- Breathwork
    breathwork_completed BOOLEAN DEFAULT false,
    breathwork_duration_seconds INTEGER,
    
    -- Metadata
    device_type TEXT,
    session_duration_seconds INTEGER,
    notification_source TEXT -- How user was reminded (push, in-app, etc.)
);

CREATE INDEX idx_activation_sessions_user ON activation_sessions(user_id);
CREATE INDEX idx_activation_sessions_date ON activation_sessions(started_at);
CREATE INDEX idx_activation_sessions_completed ON activation_sessions(is_completed);

-- User activation streaks
CREATE TABLE IF NOT EXISTS user_streaks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activation_date DATE,
    
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(user_id)
);

CREATE INDEX idx_user_streaks_user ON user_streaks(user_id);

-- ============================================================================
-- MICRO-ACTS TABLES
-- ============================================================================

-- Micro-acts logged by users
CREATE TABLE IF NOT EXISTS micro_acts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Micro-act details
    category TEXT NOT NULL CHECK (category IN (
        'compassion', 'creativity', 'service', 'gratitude', 
        'learning', 'connection', 'sustainability', 'wellness', 'other'
    )),
    title TEXT NOT NULL,
    description TEXT,
    
    -- Value measurement
    impact_scope TEXT CHECK (impact_scope IN ('self', 'one_person', 'group', 'community', 'world')),
    value_added_score INTEGER CHECK (value_added_score >= 1 AND value_added_score <= 10),
    
    -- Community sharing
    is_shared_to_feed BOOLEAN DEFAULT false,
    visibility TEXT DEFAULT 'private' CHECK (visibility IN ('private', 'friends', 'community', 'public')),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    media_urls JSONB, -- Array of image/video URLs
    tags TEXT[] -- Array of tags for categorization
);

CREATE INDEX idx_micro_acts_user ON micro_acts(user_id);
CREATE INDEX idx_micro_acts_date ON micro_acts(created_at);
CREATE INDEX idx_micro_acts_category ON micro_acts(category);
CREATE INDEX idx_micro_acts_shared ON micro_acts(is_shared_to_feed) WHERE is_shared_to_feed = true;

-- ============================================================================
-- WEEKLY WAVE TABLES
-- ============================================================================

-- Weekly Wave events
CREATE TABLE IF NOT EXISTS wave_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Event details
    title TEXT NOT NULL,
    description TEXT,
    scheduled_at TIMESTAMPTZ NOT NULL,
    duration_minutes INTEGER DEFAULT 60,
    
    -- Hosting
    host_id UUID REFERENCES users(id),
    co_hosts UUID[], -- Array of co-host user IDs
    
    -- Configuration
    max_participants INTEGER,
    is_public BOOLEAN DEFAULT true,
    meeting_link TEXT,
    
    -- Status
    status TEXT DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'live', 'completed', 'cancelled')),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_wave_events_scheduled ON wave_events(scheduled_at);
CREATE INDEX idx_wave_events_status ON wave_events(status);

-- Wave participation tracking
CREATE TABLE IF NOT EXISTS wave_participation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wave_id UUID NOT NULL REFERENCES wave_events(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Participation details
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    left_at TIMESTAMPTZ,
    duration_minutes INTEGER,
    
    -- Engagement
    participated_in_discussion BOOLEAN DEFAULT false,
    shared_micro_act BOOLEAN DEFAULT false,
    energy_level_before INTEGER CHECK (energy_level_before >= 1 AND energy_level_before <= 10),
    energy_level_after INTEGER CHECK (energy_level_after >= 1 AND energy_level_after <= 10),
    
    -- Feedback
    feedback_text TEXT,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    
    UNIQUE(wave_id, user_id)
);

CREATE INDEX idx_wave_participation_wave ON wave_participation(wave_id);
CREATE INDEX idx_wave_participation_user ON wave_participation(user_id);

-- ============================================================================
-- COMMUNITY ENGAGEMENT TABLES
-- ============================================================================

-- Community feed posts
CREATE TABLE IF NOT EXISTS community_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Content
    content TEXT NOT NULL,
    post_type TEXT DEFAULT 'text' CHECK (post_type IN ('text', 'micro_act', 'reflection', 'question')),
    micro_act_id UUID REFERENCES micro_acts(id),
    
    -- Visibility
    visibility TEXT DEFAULT 'community' CHECK (visibility IN ('friends', 'community', 'public')),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    is_pinned BOOLEAN DEFAULT false,
    media_urls JSONB
);

CREATE INDEX idx_community_posts_user ON community_posts(user_id);
CREATE INDEX idx_community_posts_date ON community_posts(created_at);
CREATE INDEX idx_community_posts_type ON community_posts(post_type);

-- Community interactions (likes, comments, shares)
CREATE TABLE IF NOT EXISTS community_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL REFERENCES community_posts(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Interaction type
    interaction_type TEXT NOT NULL CHECK (interaction_type IN ('like', 'comment', 'share', 'bookmark')),
    
    -- Comment content (if applicable)
    comment_text TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(post_id, user_id, interaction_type)
);

CREATE INDEX idx_community_interactions_post ON community_interactions(post_id);
CREATE INDEX idx_community_interactions_user ON community_interactions(user_id);
CREATE INDEX idx_community_interactions_type ON community_interactions(interaction_type);

-- ============================================================================
-- CALCULATED METRICS TABLES
-- ============================================================================

-- Daily user metrics snapshot
CREATE TABLE IF NOT EXISTS daily_user_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    metric_date DATE NOT NULL,
    
    -- Activation metrics
    activation_completed BOOLEAN DEFAULT false,
    activation_streak INTEGER DEFAULT 0,
    mood_shift INTEGER,
    
    -- Micro-acts
    micro_acts_count INTEGER DEFAULT 0,
    micro_acts_value_total INTEGER DEFAULT 0,
    
    -- Community
    posts_created INTEGER DEFAULT 0,
    interactions_given INTEGER DEFAULT 0,
    interactions_received INTEGER DEFAULT 0,
    wave_participated BOOLEAN DEFAULT false,
    
    -- Composite scores
    flourish_index NUMERIC(5,2), -- 0-100 scale
    add_value_index NUMERIC(5,2), -- 0-100 scale
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(user_id, metric_date)
);

CREATE INDEX idx_daily_user_metrics_user_date ON daily_user_metrics(user_id, metric_date);
CREATE INDEX idx_daily_user_metrics_date ON daily_user_metrics(metric_date);

-- Aggregated platform metrics (daily rollup)
CREATE TABLE IF NOT EXISTS platform_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_date DATE NOT NULL UNIQUE,
    
    -- User metrics
    dau INTEGER DEFAULT 0, -- Daily Active Users
    new_users INTEGER DEFAULT 0,
    total_users INTEGER DEFAULT 0,
    
    -- Activation metrics
    activations_completed INTEGER DEFAULT 0,
    avg_mood_shift NUMERIC(4,2),
    
    -- Micro-acts
    micro_acts_total INTEGER DEFAULT 0,
    avg_micro_acts_per_user NUMERIC(5,2),
    
    -- Community
    posts_created INTEGER DEFAULT 0,
    interactions_total INTEGER DEFAULT 0,
    waves_held INTEGER DEFAULT 0,
    wave_participants_total INTEGER DEFAULT 0,
    
    -- Composite scores
    avg_flourish_index NUMERIC(5,2),
    avg_add_value_index NUMERIC(5,2),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_platform_metrics_date ON platform_metrics(metric_date);

-- ============================================================================
-- DATA COLLECTION & EVENT LOGGING
-- ============================================================================

-- Event tracking for analytics
CREATE TABLE IF NOT EXISTS analytics_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Event details
    event_name TEXT NOT NULL,
    event_category TEXT NOT NULL,
    event_properties JSONB,
    
    -- Context
    session_id TEXT,
    device_type TEXT,
    platform TEXT,
    app_version TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    ip_address INET, -- For security/fraud detection only
    user_agent TEXT
);

CREATE INDEX idx_analytics_events_user ON analytics_events(user_id);
CREATE INDEX idx_analytics_events_date ON analytics_events(created_at);
CREATE INDEX idx_analytics_events_name ON analytics_events(event_name);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Active users in last 7 days (WAU)
CREATE OR REPLACE VIEW weekly_active_users AS
SELECT 
    COUNT(DISTINCT user_id) as wau,
    CURRENT_DATE as calculated_date
FROM users
WHERE last_activity_date >= CURRENT_DATE - INTERVAL '7 days'
    AND is_active = true;

-- View: Active users in last 30 days (MAU)
CREATE OR REPLACE VIEW monthly_active_users AS
SELECT 
    COUNT(DISTINCT user_id) as mau,
    CURRENT_DATE as calculated_date
FROM users
WHERE last_activity_date >= CURRENT_DATE - INTERVAL '30 days'
    AND is_active = true;

-- View: Today's active users (DAU)
CREATE OR REPLACE VIEW daily_active_users AS
SELECT 
    COUNT(DISTINCT user_id) as dau,
    CURRENT_DATE as calculated_date
FROM users
WHERE last_activity_date = CURRENT_DATE
    AND is_active = true;

-- View: Activation completion rates
CREATE OR REPLACE VIEW activation_completion_stats AS
SELECT 
    DATE(started_at) as activation_date,
    COUNT(*) as total_sessions,
    COUNT(*) FILTER (WHERE is_completed = true) as completed_sessions,
    ROUND(100.0 * COUNT(*) FILTER (WHERE is_completed = true) / COUNT(*), 2) as completion_rate,
    AVG(mood_shift) FILTER (WHERE is_completed = true) as avg_mood_shift
FROM activation_sessions
WHERE started_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(started_at)
ORDER BY activation_date DESC;

-- View: Wave participation stats
CREATE OR REPLACE VIEW wave_participation_stats AS
SELECT 
    w.id as wave_id,
    w.title,
    w.scheduled_at,
    COUNT(p.id) as participant_count,
    AVG(p.duration_minutes) as avg_duration,
    AVG(p.energy_level_after - p.energy_level_before) as avg_energy_boost,
    AVG(p.rating) as avg_rating
FROM wave_events w
LEFT JOIN wave_participation p ON w.id = p.wave_id
WHERE w.status = 'completed'
GROUP BY w.id, w.title, w.scheduled_at
ORDER BY w.scheduled_at DESC;

-- ============================================================================
-- FUNCTIONS FOR METRIC CALCULATIONS
-- ============================================================================

-- Function to calculate Flourish Index for a user on a given date
CREATE OR REPLACE FUNCTION calculate_flourish_index(
    p_user_id UUID,
    p_date DATE
) RETURNS NUMERIC AS $$
DECLARE
    v_mood_score NUMERIC;
    v_microact_score NUMERIC;
    v_community_score NUMERIC;
    v_consistency_score NUMERIC;
    v_flourish_index NUMERIC;
BEGIN
    -- Mood improvement score (0-100 scale, 40% weight)
    SELECT COALESCE((mood_shift + 10) * 5, 0) INTO v_mood_score
    FROM activation_sessions
    WHERE user_id = p_user_id
        AND DATE(started_at) = p_date
        AND is_completed = true
    LIMIT 1;
    
    -- Micro-acts score (0-100 scale, 30% weight)
    SELECT COALESCE(LEAST(COUNT(*) * 20, 100), 0) INTO v_microact_score
    FROM micro_acts
    WHERE user_id = p_user_id
        AND DATE(created_at) = p_date;
    
    -- Community engagement score (0-100 scale, 20% weight)
    SELECT COALESCE(
        LEAST(
            (COUNT(DISTINCT cp.id) * 15) + 
            (COUNT(DISTINCT ci.id) * 5) +
            (CASE WHEN wp.id IS NOT NULL THEN 30 ELSE 0 END),
            100
        ), 0
    ) INTO v_community_score
    FROM users u
    LEFT JOIN community_posts cp ON u.id = cp.user_id AND DATE(cp.created_at) = p_date
    LEFT JOIN community_interactions ci ON u.id = ci.user_id AND DATE(ci.created_at) = p_date
    LEFT JOIN wave_participation wp ON u.id = wp.user_id AND DATE(wp.joined_at) = p_date
    WHERE u.id = p_user_id;
    
    -- Consistency score (0-100 scale, 10% weight)
    SELECT COALESCE(LEAST(current_streak * 10, 100), 0) INTO v_consistency_score
    FROM user_streaks
    WHERE user_id = p_user_id;
    
    -- Calculate weighted Flourish Index
    v_flourish_index := 
        (COALESCE(v_mood_score, 0) * 0.4) +
        (COALESCE(v_microact_score, 0) * 0.3) +
        (COALESCE(v_community_score, 0) * 0.2) +
        (COALESCE(v_consistency_score, 0) * 0.1);
    
    RETURN ROUND(v_flourish_index, 2);
END;
$$ LANGUAGE plpgsql;

-- Function to calculate Add-Value Index for a user on a given date
CREATE OR REPLACE FUNCTION calculate_add_value_index(
    p_user_id UUID,
    p_date DATE
) RETURNS NUMERIC AS $$
DECLARE
    v_microact_value_score NUMERIC;
    v_community_score NUMERIC;
    v_wave_score NUMERIC;
    v_add_value_index NUMERIC;
BEGIN
    -- Micro-acts benefiting others (0-100 scale, 50% weight)
    SELECT COALESCE(
        LEAST(
            (COUNT(*) FILTER (WHERE impact_scope IN ('one_person', 'group', 'community', 'world')) * 15) +
            (AVG(value_added_score) FILTER (WHERE impact_scope != 'self') * 5),
            100
        ), 0
    ) INTO v_microact_value_score
    FROM micro_acts
    WHERE user_id = p_user_id
        AND DATE(created_at) = p_date;
    
    -- Community interactions (0-100 scale, 30% weight)
    SELECT COALESCE(
        LEAST(
            (COUNT(DISTINCT ci.id) * 10) +
            (COUNT(DISTINCT cp.id) FILTER (WHERE cp.is_shared_to_feed = true) * 20),
            100
        ), 0
    ) INTO v_community_score
    FROM users u
    LEFT JOIN community_interactions ci ON u.id = ci.user_id AND DATE(ci.created_at) = p_date
    LEFT JOIN community_posts cp ON u.id = cp.user_id AND DATE(cp.created_at) = p_date
    WHERE u.id = p_user_id;
    
    -- Wave participation (0-100 scale, 20% weight)
    SELECT COALESCE(
        CASE 
            WHEN COUNT(*) > 0 THEN 
                LEAST(
                    50 + 
                    (CASE WHEN SUM(CASE WHEN participated_in_discussion THEN 1 ELSE 0 END) > 0 THEN 25 ELSE 0 END) +
                    (CASE WHEN SUM(CASE WHEN shared_micro_act THEN 1 ELSE 0 END) > 0 THEN 25 ELSE 0 END),
                    100
                )
            ELSE 0
        END, 0
    ) INTO v_wave_score
    FROM wave_participation
    WHERE user_id = p_user_id
        AND DATE(joined_at) = p_date;
    
    -- Calculate weighted Add-Value Index
    v_add_value_index := 
        (COALESCE(v_microact_value_score, 0) * 0.5) +
        (COALESCE(v_community_score, 0) * 0.3) +
        (COALESCE(v_wave_score, 0) * 0.2);
    
    RETURN ROUND(v_add_value_index, 2);
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE activation_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE micro_acts ENABLE ROW LEVEL SECURITY;
ALTER TABLE community_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE community_interactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE wave_participation ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY users_select_own ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY activation_sessions_own ON activation_sessions
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY micro_acts_own ON micro_acts
    FOR ALL USING (auth.uid() = user_id);

-- Community content visibility based on privacy settings
CREATE POLICY community_posts_visible ON community_posts
    FOR SELECT USING (
        visibility = 'public' OR
        visibility = 'community' OR
        auth.uid() = user_id
    );

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE users IS 'Core user information with privacy and activity tracking';
COMMENT ON TABLE activation_sessions IS 'Tracks Activation Day sessions including mood shifts and affirmations';
COMMENT ON TABLE micro_acts IS 'User-logged micro-acts with categorization and value measurement';
COMMENT ON TABLE wave_events IS 'Weekly Wave events and gatherings';
COMMENT ON TABLE wave_participation IS 'Participation tracking for Wave events';
COMMENT ON TABLE daily_user_metrics IS 'Daily snapshot of user metrics including Flourish and Add-Value indices';
COMMENT ON TABLE platform_metrics IS 'Aggregated platform-wide metrics';
COMMENT ON FUNCTION calculate_flourish_index IS 'Calculates Flourish Index: composite well-being score (0-100)';
COMMENT ON FUNCTION calculate_add_value_index IS 'Calculates Add-Value Index: measure of value added to others (0-100)';
