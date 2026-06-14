import threading


def go():
    threading.Thread(target=lambda: None, daemon=True).start()
