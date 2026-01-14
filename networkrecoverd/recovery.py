import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def run_dummy_recovery():
    script_path = (
        Path(__file__).resolve().parent.parent / "recovery-scripts" / "dummy.sh"
    )

    logger.info("Starting recovery script: %s", script_path)

    try:
        result = subprocess.run(
            [str(script_path)], capture_output=True, text=True, check=False
        )

        if result.returncode == 0:
            logger.info("Recovery script completed successfuly")
        else:
            logger.warning("Recovery script failed (exit code %s)", result.returncode)
            logger.warning("stdout: %", result.stdout.strip())
            logger.warning("stderr: %", result.stderr.strip())

    except Exception:
        logger.exception("Unexpected error while running recovery script: %s")
