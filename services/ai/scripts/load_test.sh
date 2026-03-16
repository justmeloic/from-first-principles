#!/bin/bash
# Copyright 2025 Loïc Muhirwa
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Load testing script for AI Service API
# Usage: ./scripts/load_test.sh [scenario]
# Scenarios: smoke, load, stress, soak, web

set -e

SCENARIO=${1:-smoke}
HOST=${HOST:-http://localhost:8081}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AI_DIR="$(dirname "$SCRIPT_DIR")"
REPORTS_DIR="$AI_DIR/tests/load/reports"

# Ensure reports directory exists
mkdir -p "$REPORTS_DIR"

echo "🚀 Running load test scenario: $SCENARIO"
echo "📍 Target host: $HOST"

case $SCENARIO in
  smoke)
    echo "Running smoke test (5 users, 30s)..."
    locust -f "$AI_DIR/tests/load/locustfile.py" \
      --host="$HOST" \
      --headless \
      -u 5 \
      -r 1 \
      -t 30s \
      --html="$REPORTS_DIR/smoke_report.html"
    ;;

  load)
    echo "Running load test (50 users, 5m)..."
    locust -f "$AI_DIR/tests/load/locustfile.py" \
      --host="$HOST" \
      --headless \
      -u 50 \
      -r 5 \
      -t 5m \
      --html="$REPORTS_DIR/load_report.html"
    ;;

  stress)
    echo "Running stress test (200 users, 10m)..."
    locust -f "$AI_DIR/tests/load/locustfile.py" \
      --host="$HOST" \
      --headless \
      -u 200 \
      -r 20 \
      -t 10m \
      --html="$REPORTS_DIR/stress_report.html"
    ;;

  soak)
    echo "Running soak test (30 users, 30m)..."
    locust -f "$AI_DIR/tests/load/locustfile.py" \
      --host="$HOST" \
      --headless \
      -u 30 \
      -r 2 \
      -t 30m \
      --html="$REPORTS_DIR/soak_report.html"
    ;;

  web)
    echo "Starting Locust web UI at http://localhost:8089"
    locust -f "$AI_DIR/tests/load/locustfile.py" --host="$HOST"
    ;;

  *)
    echo "Unknown scenario: $SCENARIO"
    echo ""
    echo "Available scenarios:"
    echo "  smoke   - Quick smoke test (5 users, 30s)"
    echo "  load    - Standard load test (50 users, 5m)"
    echo "  stress  - Stress test to find breaking points (200 users, 10m)"
    echo "  soak    - Extended test for memory leaks (30 users, 30m)"
    echo "  web     - Start Locust web UI"
    echo ""
    echo "Usage: ./scripts/load_test.sh [scenario]"
    echo "       HOST=http://your-host:8081 ./scripts/load_test.sh load"
    exit 1
    ;;
esac

echo "✅ Load test complete!"
