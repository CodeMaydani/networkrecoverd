import argparse
import logging
import os
import time
from typing import TypedDict

from dotenv import load_dotenv

from networkrecoverd.connectivity import has_internet
from networkrecoverd.notifications import ask_user
from networkrecoverd.recovery import run_dummy_recovery

# CHECK_INTERVAL = 10  # seconds
# for testing
CHECK_INTERVAL = 1  # seconds
FAILURE_THRESHOLD = 3  # debounce count

logger = logging.getLogger(__name__)


class MonitorState(TypedDict):
    failure_count: int
    prompt_shown: bool


def run_monitoring_cycle(state: MonitorState, host: str, port: int, timeout: float):
    is_online: bool = has_internet(host, port, timeout)

    if is_online:
        if state["failure_count"] > 0 or state["prompt_shown"]:
            logger.info("Internet recovered; resetting state")
        state["failure_count"] = 0
        state["prompt_shown"] = False
        return state

    # Internet is down
    state["failure_count"] += 1
    logger.info("Internet down (failure %d)", state["failure_count"])

    if state["failure_count"] >= FAILURE_THRESHOLD and not state["prompt_shown"]:
        logger.info("Failure treshold reached (%d). Prompting user.", FAILURE_THRESHOLD)

        if ask_user():
            logger.info("User chose to run recovery.")
            run_dummy_recovery()
            state["failure_count"] = 0
            state["prompt_shown"] = True
        else:
            logger.info("User declined recovery.")
            state["prompt_shown"] = True

    return state


def setup_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single connectivity check and exit (useful for debugging).",
    )

    return parser


def main():
    parser = setup_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
    )

    load_dotenv()

    host = os.getenv("NETWORKRECOVERD_HOST", "8.8.8.8")
    port = int(os.getenv("NETWORKRECOVERD_PORT", 53))
    timeout = float(os.getenv("NETWORKRECOVERD_TIMEOUT", 3))

    logger.info("networkrecoverd starting (once=%s)", args.once)

    # Initial deamon state
    state: MonitorState = {
        "failure_count": 0,
        "prompt_shown": False,
    }

    if args.once:
        run_monitoring_cycle(state.copy(), host, port, timeout)
        return

    try:
        while True:
            state = run_monitoring_cycle(state.copy(), host, port, timeout)
            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        logger.info("Interrupted by user. exiting.")


if __name__ == "__main__":
    main()
