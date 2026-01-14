import socket


def has_internet(host: str = "8.8.8.8", port: int = 53, timeout: float = 3) -> bool:
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=timeout)
        return True
    except OSError:
        return False
