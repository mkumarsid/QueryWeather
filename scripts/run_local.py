import os
import subprocess
import sys
import threading
from time import sleep

import uvicorn

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def run_uvicorn():
    # 🚫 Don't use reload=True inside a thread
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)


def run_streamlit():
    streamlit_script = os.path.join("app/web", "streamlit_dashboard.py")
    subprocess.run(
        [
            "streamlit",
            "run",
            streamlit_script,
            "--server.port",
            "8501",
            "--server.address",
            "127.0.0.1",
        ]
    )


if __name__ == "__main__":
    print("🚀 Launching FastAPI and Streamlit apps...")

    uvicorn_thread = threading.Thread(target=run_uvicorn, daemon=True)
    uvicorn_thread.start()

    sleep(1)
    run_streamlit()
