#!/bin/bash
# Initialize Redis Streams and Consumer Groups for Multi-Agent System

set -e

echo "🚀 Initializing Redis Streams for Multi-Agent System..."

# Wait for Redis to be ready
until redis-cli ping > /dev/null 2>&1; do
  echo "⏳ Waiting for Redis to be ready..."
  sleep 1
done

echo "✅ Redis is ready!"

# Create streams and consumer groups for each agent
AGENTS=(
  "agent-01-fullstack-architect"
  "agent-02-frontend-specialist"
  "agent-03-backend-specialist"
  "agent-04-devops-specialist"
  "agent-05-security-specialist"
  "agent-06-performance-specialist"
  "agent-07-qa-specialist"
  "agent-08-seo-specialist"
  "agent-09-ux-specialist"
  "agent-10-data-specialist"
  "agent-11-ai-specialist"
  "agent-12-observer-optimizer"
)

for agent in "${AGENTS[@]}"; do
  STREAM_NAME="tasks:${agent}"
  GROUP_NAME="${agent}-workers"
  
  echo "📋 Creating stream: ${STREAM_NAME}"
  
  # Create stream with initial dummy message (will be removed)
  redis-cli XADD "${STREAM_NAME}" "*" init "true" > /dev/null
  
  # Create consumer group
  echo "👥 Creating consumer group: ${GROUP_NAME}"
  redis-cli XGROUP CREATE "${STREAM_NAME}" "${GROUP_NAME}" 0 MKSTREAM > /dev/null 2>&1 || echo "   Group already exists"
  
  # Remove dummy message
  redis-cli XTRIM "${STREAM_NAME}" MAXLEN 0 > /dev/null
done

# Create pub/sub channels
echo "📢 Setting up pub/sub channels..."
CHANNELS=(
  "events:task-created"
  "events:task-completed"
  "events:task-failed"
  "events:agent-coordination"
  "events:system-alerts"
)

for channel in "${CHANNELS[@]}"; do
  echo "   - ${channel}"
done

# Create system state keys
echo "🔧 Initializing system state..."
redis-cli HSET "system:agents" "initialized" "true" > /dev/null
redis-cli HSET "system:metrics" "tasks_total" 0 > /dev/null
redis-cli HSET "system:metrics" "tasks_completed" 0 > /dev/null
redis-cli HSET "system:metrics" "tasks_failed" 0 > /dev/null

echo ""
echo "✅ Redis initialization completed!"
echo ""
echo "📊 Summary:"
echo "   - Streams created: ${#AGENTS[@]}"
echo "   - Consumer groups: ${#AGENTS[@]}"
echo "   - Pub/sub channels: ${#CHANNELS[@]}"
echo ""
echo "🎯 System is ready to receive tasks!"
