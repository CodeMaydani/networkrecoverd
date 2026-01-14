"""
Simulation script for networkrecoverd monitoring logic.

This script monkey-patches:
- has_internet
- ask_user
- run_dummy_recovery

to simulate various scenarios without real network, UI, or recovery scripts.
"""

from typing import Iterator

from networkrecoverd.daemon import MonitorState, run_monitoring_cycle

# --- scenario controls ------------------------------------------------------

# Simulated internet status over time
internet_sequence: Iterator[bool] = iter(
    [
        False,  # failure 1
        False,  # failure 2
        False,  # failure 3 -> should prompt
        False,  # still down, but no re-prompt
        True,  # recovered
        True,
    ]
)

# Simulated user responses (True = accept recovery, False = decline)
user_response_sequence: Iterator[bool] = iter(
    [
        True,  # user accepts recovery when prompted
    ]
)

# --- monkey patches ---------------------------------------------------------


def fake_has_internet(host: str, port: int, timeout: float) -> bool:
    try:
        return next(internet_sequence)
    except StopIteration:
        return True  # default to online


def fake_ask_user() -> bool:
    try:
        return next(user_response_sequence)
    except StopIteration:
        return False


def fake_run_dummy_recovery():
    print(">>> [SIMULATION] Recovery script executed")


# Patch imported symbols inside the daemon module
import networkrecoverd.daemon as daemon  # noqa: E402

daemon.has_internet = fake_has_internet  # ty:ignore[invalid-assignment]
daemon.ask_user = fake_ask_user  # ty:ignore[invalid-assignment]
daemon.run_dummy_recovery = fake_run_dummy_recovery  # ty:ignore[invalid-assignment]

# --- simulation -------------------------------------------------------------

state: MonitorState = {
    "failure_count": 0,
    "prompt_shown": False,
}

HOST = "8.8.8.8"
PORT = 53
TIMEOUT = 3

print("=== Starting monitoring simulation ===\n")

for i in range(1, 8):
    print(f"\n--- Cycle {i} ---")
    state = run_monitoring_cycle(state.copy(), HOST, PORT, TIMEOUT)
    print("State after cycle:", state)

print("\n=== Simulation complete ===")
