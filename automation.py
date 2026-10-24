from datetime import datetime
import logging
import os
import schedule
import subprocess
import sys
import time

# Logging setup
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def job():
    logging.info(f"🕒 Automation Triggered at: {datetime.now()}")
    try:
        # Use current Python binary for environment safety
        result = subprocess.run(
            [sys.executable, "main.py"],
            check=True,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes timeout
        )
        logging.info("✅ Scheduled Simulation Pipeline completed successfully.")
        if result.stdout:
            logging.debug(f"Output: {result.stdout.strip()}")
    except subprocess.TimeoutExpired:
        logging.error("❌ Automation failed: Execution timed out after 300s.")
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Automation failed with return code {e.returncode}")
        if e.stderr:
            logging.error(f"Error Log: {e.stderr.strip()}")
    except Exception as e:
        logging.error(f"❌ Unexpected Error: {e}")


# Schedule job daily at midnight
schedule.every().day.at("00:00").do(job)

if __name__ == "__main__":
    logging.info("🤖 GPR Automation Service is running...")
    # Run once at startup for instant verification
    job()

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)  # Faster loop responsiveness
    except KeyboardInterrupt:
        logging.info("🛑 Automation Service stopped by user.")
