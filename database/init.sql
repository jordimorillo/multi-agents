-- Multi-Agent System Database Schema
-- PostgreSQL 15+

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tasks table - Main tasks created by orchestrator
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    priority INTEGER DEFAULT 5,
    project_path TEXT,
    
    -- Linear integration
    linear_issue_id VARCHAR(100),
    linear_issue_url TEXT,
    linear_team_id VARCHAR(100),
    
    -- GitHub integration
    github_repo VARCHAR(200),
    github_branch VARCHAR(200),
    github_pr_url TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    failed_at TIMESTAMP,
    
    -- Task breakdown
    total_subtasks INTEGER DEFAULT 0,
    completed_subtasks INTEGER DEFAULT 0,
    
    -- Metrics
    estimated_duration_minutes INTEGER,
    actual_duration_minutes INTEGER,
    llm_cost_usd DECIMAL(10, 4) DEFAULT 0.0,
    
    CONSTRAINT valid_status CHECK (status IN (
        'pending', 'analyzing', 'in_progress', 'completed', 'failed', 'cancelled'
    ))
);

-- Subtasks table - Individual agent tasks
CREATE TABLE subtasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    agent_id VARCHAR(100) NOT NULL,
    
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    
    -- Linear integration
    linear_issue_id VARCHAR(100),
    linear_issue_url TEXT,
    
    -- GitHub integration
    github_branch VARCHAR(200),
    github_pr_url TEXT,
    github_commits TEXT[], -- Array of commit SHAs
    
    -- Dependencies
    depends_on UUID[], -- Array of subtask IDs
    blocks UUID[], -- Array of subtask IDs this blocks
    
    -- Execution details
    assigned_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    failed_at TIMESTAMP,
    
    -- Result
    result_summary TEXT,
    files_changed TEXT[], -- Array of file paths
    
    -- Metrics
    llm_tokens_used INTEGER DEFAULT 0,
    llm_cost_usd DECIMAL(10, 4) DEFAULT 0.0,
    execution_time_seconds INTEGER,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_status CHECK (status IN (
        'pending', 'waiting_dependency', 'assigned', 'in_progress', 
        'completed', 'failed', 'cancelled'
    ))
);

-- Agents table - Agent status and metadata
CREATE TABLE agents (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    role VARCHAR(200) NOT NULL,
    specialization TEXT NOT NULL,
    
    status VARCHAR(50) NOT NULL DEFAULT 'idle',
    current_task_id UUID REFERENCES subtasks(id),
    
    -- Stats
    total_tasks_completed INTEGER DEFAULT 0,
    total_tasks_failed INTEGER DEFAULT 0,
    total_execution_time_seconds BIGINT DEFAULT 0,
    total_llm_cost_usd DECIMAL(10, 4) DEFAULT 0.0,
    average_task_duration_minutes DECIMAL(10, 2) DEFAULT 0.0,
    success_rate DECIMAL(5, 2) DEFAULT 100.0,
    
    -- Health
    last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_error TEXT,
    last_error_at TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_status CHECK (status IN (
        'idle', 'working', 'error', 'offline'
    ))
);

-- Agent logs table - Detailed execution logs
CREATE TABLE agent_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(100) NOT NULL REFERENCES agents(id),
    subtask_id UUID REFERENCES subtasks(id),
    
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    details JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_level CHECK (level IN (
        'debug', 'info', 'warning', 'error', 'critical'
    ))
);

-- System events table - Event sourcing
CREATE TABLE system_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(100) NOT NULL,
    
    task_id UUID REFERENCES tasks(id),
    subtask_id UUID REFERENCES subtasks(id),
    agent_id VARCHAR(100) REFERENCES agents(id),
    
    payload JSONB NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- RAG updates table - Track RAG knowledge evolution
CREATE TABLE rag_updates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(100) REFERENCES agents(id),
    
    update_type VARCHAR(50) NOT NULL,
    pattern_id VARCHAR(100),
    pattern_data JSONB NOT NULL,
    
    confidence DECIMAL(5, 4),
    source_task_id UUID REFERENCES tasks(id),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_update_type CHECK (update_type IN (
        'pattern_added', 'pattern_updated', 'pattern_removed',
        'anti_pattern_added', 'collaboration_pattern'
    ))
);

-- Indexes for performance
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
CREATE INDEX idx_tasks_linear_issue ON tasks(linear_issue_id);

CREATE INDEX idx_subtasks_task_id ON subtasks(task_id);
CREATE INDEX idx_subtasks_agent_id ON subtasks(agent_id);
CREATE INDEX idx_subtasks_status ON subtasks(status);
CREATE INDEX idx_subtasks_depends_on ON subtasks USING GIN(depends_on);

CREATE INDEX idx_agents_status ON agents(status);
CREATE INDEX idx_agents_last_heartbeat ON agents(last_heartbeat);

CREATE INDEX idx_agent_logs_agent_id ON agent_logs(agent_id);
CREATE INDEX idx_agent_logs_subtask_id ON agent_logs(subtask_id);
CREATE INDEX idx_agent_logs_created_at ON agent_logs(created_at DESC);
CREATE INDEX idx_agent_logs_level ON agent_logs(level);

CREATE INDEX idx_system_events_task_id ON system_events(task_id);
CREATE INDEX idx_system_events_agent_id ON system_events(agent_id);
CREATE INDEX idx_system_events_event_type ON system_events(event_type);
CREATE INDEX idx_system_events_created_at ON system_events(created_at DESC);

CREATE INDEX idx_rag_updates_agent_id ON rag_updates(agent_id);
CREATE INDEX idx_rag_updates_pattern_id ON rag_updates(pattern_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers
CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subtasks_updated_at BEFORE UPDATE ON subtasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Seed initial agents
INSERT INTO agents (id, name, role, specialization) VALUES
('agent-01-fullstack-architect', 'Marcus Chen', 'Full-Stack Architect & Coordinator', 'System architecture, technical coordination, project orchestration'),
('agent-02-frontend-specialist', 'Elena Rodriguez', 'Frontend Specialist', 'Frontend frameworks, user interfaces, performance optimization'),
('agent-03-backend-specialist', 'David Kumar', 'Backend Specialist', 'Backend development, API design, data architecture'),
('agent-04-devops-specialist', 'Sarah Johnson', 'DevOps & Infrastructure Specialist', 'CI/CD, container orchestration, cloud infrastructure'),
('agent-05-security-specialist', 'Alex Thompson', 'Security Specialist', 'Security audits, compliance, vulnerability assessment'),
('agent-06-performance-specialist', 'Maria Garcia', 'Performance Specialist', 'Performance optimization, scalability, Core Web Vitals'),
('agent-07-qa-specialist', 'James Wilson', 'QA & Testing Specialist', 'Testing strategies, quality assurance, accessibility'),
('agent-08-seo-specialist', 'Sophie Martin', 'SEO Specialist', 'SEO optimization, content strategy, technical SEO'),
('agent-09-ux-specialist', 'Rachel Kim', 'UX Specialist', 'User experience design, interface design, usability'),
('agent-10-data-specialist', 'Michael Brown', 'Data Specialist', 'Data architecture, analytics, business intelligence'),
('agent-11-ai-specialist', 'Nina Patel', 'AI Specialist', 'AI/ML integration, intelligent automation, model optimization'),
('agent-12-observer-optimizer', 'System Observer', 'Observer & Optimizer', 'System analysis, continuous improvement, RAG management')
ON CONFLICT (id) DO NOTHING;

-- Create views for common queries
CREATE VIEW v_task_overview AS
SELECT 
    t.id,
    t.title,
    t.status,
    t.priority,
    t.total_subtasks,
    t.completed_subtasks,
    ROUND((t.completed_subtasks::DECIMAL / NULLIF(t.total_subtasks, 0)) * 100, 2) as progress_percent,
    t.linear_issue_url,
    t.github_pr_url,
    t.created_at,
    t.completed_at,
    EXTRACT(EPOCH FROM (COALESCE(t.completed_at, CURRENT_TIMESTAMP) - t.created_at))/60 as duration_minutes
FROM tasks t;

CREATE VIEW v_agent_performance AS
SELECT 
    a.id,
    a.name,
    a.status,
    a.total_tasks_completed,
    a.total_tasks_failed,
    a.success_rate,
    a.average_task_duration_minutes,
    a.total_llm_cost_usd,
    a.last_heartbeat,
    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - a.last_heartbeat)) as seconds_since_heartbeat
FROM agents a;

-- Grant permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO multiagent;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO multiagent;
