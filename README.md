# Insider One QA Assessment

General notes:
- .env was pushed for demo purposes
- sync and async api tests are made just for demo as well

---

## Running Tests via Docker (recommended)

Docker bundles Python, Chrome, ChromeDriver, and Allure — no local installations needed.

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Compose v2)

### 1. Build the image (one-time)

```bash
docker compose build
```

### 2. Run each test category

> Reports are written to `reports/` and screenshots to `screenshots/` on your host machine.

**UI tests** — headless Chrome inside the container:

```bash
docker compose run --rm ui
```

**API tests — synchronous:**

```bash
docker compose run --rm api-sync
```

**API tests — asynchronous:**

```bash
docker compose run --rm api-async
```

**Load tests** — headless Locust, 1 user, 30 s run:

```bash
docker compose run --rm load
```

**Load tests — web UI mode** (live dashboard at `http://localhost:8089`):

```bash
docker compose run --rm --service-ports load \
  locust -f tests/load/locustfile.py --host=https://www.n11.com
```

Then open `http://localhost:8089`, configure users/spawn-rate, and click **Start**.

### Reports

After any pytest run, open the self-contained HTML report:

```
reports/allure-report/index.html
```

No server required — open directly in a browser.

---

## Running Tests Locally (without Docker)

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Allure CLI (one-time)

Allure CLI is a separate Java-based tool required to generate the HTML report.

**Option A — Scoop (recommended on Windows):**
```bash
# Install Scoop if you don't have it
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression

# Install Allure
scoop install allure
```

**Option B — Manual:**
1. Install [Java 8+](https://www.java.com/en/download/) if not already installed
2. Download the latest Allure zip from [github.com/allure-framework/allure2/releases](https://github.com/allure-framework/allure2/releases)
3. Extract it and add the `bin/` folder to your system `PATH`

**Verify installation:**
```bash
allure --version
```

---

### UI Tests (Chrome)

```bash
.\run_ui_tests.bat
```

Or run directly from the CLI with browser selection:

**Chrome:**

```bash
pytest tests/ui/ --browser=chrome --alluredir=reports/allure-results
allure generate reports/allure-results --single-file -o reports/allure-report --clean
```

**Firefox:**

```bash
pytest tests/ui/ --browser=firefox --alluredir=reports/allure-results
allure generate reports/allure-results --single-file -o reports/allure-report --clean
```

### API Tests (sync)

```bash
.\run_api_tests.bat
```

Or run directly from the CLI:

```bash
pytest tests/api/test_pet_crud.py tests/api/test_pet_negative.py --alluredir=reports/allure-results
allure generate reports/allure-results --single-file -o reports/allure-report --clean
```

### API Tests (async)

```bash
.\run_api_tests_async.bat
```

Or run directly from the CLI:

```bash
pytest tests/api/test_pet_crud_async.py tests/api/test_pet_negative_async.py --alluredir=reports/allure-results
allure generate reports/allure-results --single-file -o reports/allure-report --clean
```

### All Tests

```bash
.\run_all_tests.bat
```

---

## What the scripts do

Each `.bat` file runs two commands sequentially — allure always runs after pytest, even when tests fail, so the report is always generated:

```
pytest <suite> --alluredir=reports/allure-results
allure generate reports/allure-results --single-file -o reports/allure-report --clean
```

---

## Load Tests (local, run separately — no pytest)

### Headless mode (terminal output, auto-stops after 30s)

```bash
locust -f tests/load/locustfile.py --host=https://www.n11.com --users 1 --spawn-rate 1 --run-time 30s --headless
```

### Web UI mode (live dashboard at http://localhost:8089)

```bash
locust -f tests/load/locustfile.py --host=https://www.n11.com
```

Then open `http://localhost:8089` in your browser, set users/spawn-rate, and click **Start**. Stop manually when done.
