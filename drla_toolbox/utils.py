from datetime import datetime

def current_time() -> str:
    return datetime.now().strftime("%H:%M:%S")
