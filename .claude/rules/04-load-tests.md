# Load Test Rules

## Framework
- Locust is the load testing framework. Tests are in tests/load/locustfile.py.
- Load tests are NOT run via pytest. They use the locust CLI or web UI.
- The locustfile.py defines HttpUser subclasses with @task-decorated methods.

## Test Design
- Simulate realistic user journeys: homepage -> search -> browse results.
- Use catch_response=True on all self.client calls for controlled reporting.
- Set browser-like User-Agent headers to reduce bot detection blocking.
- Use between(1, 3) wait_time to simulate realistic user pacing.
- Name requests descriptively using the name= parameter.

## Running
- Default: 1 user, 1 spawn-rate (per assessment requirements).
- Headless mode: --headless --run-time 30s
- Web UI mode: omit --headless, access http://localhost:8089
