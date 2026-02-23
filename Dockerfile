# ── Base image ────────────────────────────────────────────────────────────────
# Python 3.12 slim on Debian Bookworm — latest stable, minimal footprint
FROM python:3.12-slim-bookworm

# ── System dependencies ────────────────────────────────────────────────────────
# curl/unzip/gnupg: Chrome install prerequisites
# fonts-liberation/libnss3/etc.: Chrome runtime shared libraries
# default-jre-headless: Allure CLI (Java-based)
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        unzip \
        gnupg \
        ca-certificates \
        fonts-liberation \
        libasound2 \
        libatk-bridge2.0-0 \
        libatk1.0-0 \
        libc6 \
        libcairo2 \
        libcups2 \
        libdbus-1-3 \
        libexpat1 \
        libfontconfig1 \
        libgbm1 \
        libgcc1 \
        libglib2.0-0 \
        libgtk-3-0 \
        libnspr4 \
        libnss3 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libstdc++6 \
        libx11-6 \
        libx11-xcb1 \
        libxcb1 \
        libxcomposite1 \
        libxcursor1 \
        libxdamage1 \
        libxext6 \
        libxfixes3 \
        libxi6 \
        libxrandr2 \
        libxrender1 \
        libxss1 \
        libxtst6 \
        lsb-release \
        wget \
        xdg-utils \
        default-jre-headless \
    && rm -rf /var/lib/apt/lists/*

# ── Google Chrome (stable) ─────────────────────────────────────────────────────
RUN curl -fsSL https://dl.google.com/linux/linux_signing_key.pub \
        | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] \
        https://dl.google.com/linux/chrome/deb/ stable main" \
        > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# ── Allure CLI ─────────────────────────────────────────────────────────────────
ARG ALLURE_VERSION=2.32.0
RUN curl -fsSL \
        "https://github.com/allure-framework/allure2/releases/download/${ALLURE_VERSION}/allure-${ALLURE_VERSION}.tgz" \
        -o /tmp/allure.tgz \
    && tar -xzf /tmp/allure.tgz -C /opt \
    && ln -s "/opt/allure-${ALLURE_VERSION}/bin/allure" /usr/local/bin/allure \
    && rm /tmp/allure.tgz

# ── Python dependencies ────────────────────────────────────────────────────────
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download ChromeDriver via webdriver-manager so tests start faster
RUN python - <<'EOF'
from webdriver_manager.chrome import ChromeDriverManager
ChromeDriverManager().install()
EOF

# ── Copy project ───────────────────────────────────────────────────────────────
COPY . .

# Ensure output directories exist inside the image (volumes will overlay them)
RUN mkdir -p reports/allure-results reports/allure-report screenshots

# ── Default entrypoint ─────────────────────────────────────────────────────────
# Overridden per-service in docker-compose.yml
CMD ["pytest", "--help"]
