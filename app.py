import argparse
import logging
import sys
import database
import analytics

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s"
)

def run_pipeline(sample_data: dict, dt: float):
    try:
        logging.info("Initializing Database...")
        database.init_db()

        logging.info("Analyzing signal propagation...")
        report = analytics.analyze_signal_propagation(sample_data, dt)

        logging.info("Saving results to Database...")
        for eps, stats in report.items():
            database.save_result(eps, stats['peak'], stats['arrival'])
            logging.info(f"Saved: eps={eps} | peak={stats['peak']} | arrival={stats['arrival']}")

        logging.info("✅ Full Pipeline Executed Successfully: Simulation -> Analytics -> Database")

    except Exception as e:
        logging.error(f"❌ Pipeline failed: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Centralized Orchestrator for Simulation Pipeline")
    parser.add_argument("--dt", type=float, default=1.0e-11, help="Time step dt in seconds")
    args = parser.parse_args()

    # Dynamic/Configurable input data
    sample_data = {
        3.0: [0.1, 0.5, 0.2],
        5.0: [0.08, 0.4, 0.15]
    }

    run_pipeline(sample_data, args.dt)

if __name__ == "__main__":
    main()
