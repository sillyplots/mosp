### Supplementary Task: Headless Automation Environment Setup
*   **Framework:** Use Playwright (Python) for browser automation due to its lightweight footprint and native headless stability compared to Selenium.
*   **Dependencies:** Ensure the deployment script installs necessary Linux system dependencies for Chromium (`playwright install --with-deps`).
*   **Execution Profile:** Configure the browser context with standard desktop viewport dimensions, standard user-agent strings, and `headless=True`.
*   **Scheduling:** Package the execution script to run as a 1-minute interval cron job on a Linux VM, ensuring it logs performance and cleanly closes all browser processes on completion to avoid memory leaks.