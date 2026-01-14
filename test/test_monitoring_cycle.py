from typing import Iterator

import networkrecoverd.daemon as daemon
from networkrecoverd.daemon import MonitorState, run_monitoring_cycle


def test_prompt_and_recovery_flow(monkeypatch):
    """
    Scenario:
    - Internet down 3 times → prompt
    - User accepts recovery
    - State resets correctly
    """

    # --- simulated sequences ----------------------------------------------

    internet_sequence: Iterator[bool] = iter(
        [
            False,  # failure 1
            False,  # failure 2
            False,  # failure 3 -> prompt
            True,  # recovered
        ]
    )

    user_response_sequence: Iterator[bool] = iter(
        [
            True,  # user accepts recovery
        ]
    )

    recovery_called = {"value": False}

    # --- fake implementations ---------------------------------------------

    def fake_has_internet(host: str, port: int, timeout: int) -> bool:
        try:
            return next(internet_sequence)
        except StopIteration:
            return True

    def fake_ask_user() -> bool:
        try:
            return next(user_response_sequence)
        except StopIteration:
            return False

    def fake_run_dummy_recovery():
        recovery_called["value"] = True

    # --- monkey-patch daemon dependencies ----------------------------------

    monkeypatch.setattr(daemon, "has_internet", fake_has_internet)
    monkeypatch.setattr(daemon, "ask_user", fake_ask_user)
    monkeypatch.setattr(daemon, "run_dummy_recovery", fake_run_dummy_recovery)

    # --- initial state ------------------------------------------------------

    state: MonitorState = {
        "failure_count": 0,
        "prompt_shown": False,
    }

    HOST = "8.8.8.8"
    PORT = 53
    TIMEOUT = 3

    # --- cycle 1 ------------------------------------------------------------

    state = run_monitoring_cycle(state.copy(), HOST, PORT, TIMEOUT)
    assert state["failure_count"] == 1
    assert state["prompt_shown"] is False

    # --- cycle 2 ------------------------------------------------------------

    state = run_monitoring_cycle(state.copy(), HOST, PORT, TIMEOUT)
    assert state["failure_count"] == 2
    assert state["prompt_shown"] is False

    # --- cycle 3 (prompt + recovery) ---------------------------------------

    state = run_monitoring_cycle(state.copy(), HOST, PORT, TIMEOUT)
    assert recovery_called["value"] is True
    assert state["failure_count"] == 0
    assert state["prompt_shown"] is True

    # --- cycle 4 (internet restored) ---------------------------------------

    state = run_monitoring_cycle(state.copy(), HOST, PORT, TIMEOUT)
    assert state["failure_count"] == 0
    assert state["prompt_shown"] is False
