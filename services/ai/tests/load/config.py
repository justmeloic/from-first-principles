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

"""
Load testing configuration for different scenarios.

This module defines common load testing scenarios that can be referenced
by the load_test.sh script or used directly with Locust.
"""

# Scenario configurations
SCENARIOS = {
    'smoke': {
        'users': 5,
        'spawn_rate': 1,
        'run_time': '30s',
        'description': 'Quick smoke test to verify setup',
    },
    'load': {
        'users': 50,
        'spawn_rate': 5,
        'run_time': '5m',
        'description': 'Standard load test',
    },
    'stress': {
        'users': 200,
        'spawn_rate': 20,
        'run_time': '10m',
        'description': 'Stress test to find breaking points',
    },
    'soak': {
        'users': 30,
        'spawn_rate': 2,
        'run_time': '30m',
        'description': 'Extended test to find memory leaks',
    },
}
