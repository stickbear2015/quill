import threading


def go():
    threading.Thread(  # GATE-40-OK: legacy short-lived worker
        target=lambda: None, daemon=True
    ).start()
