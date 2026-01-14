import subprocess


def ask_user() -> bool:
    result = subprocess.run(
        [
            "zenity",
            "--question",
            "--title=Internet connection lost",
            "--text=Run recovery script?",
        ]
    )
    return result.returncode == 0
