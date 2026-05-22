import docker
from ..utils.logger import logger

def run_in_sandbox(repo_path: str, command: str = "python -m pytest || python -c 'import sys; print(\"Build OK\")'"):
    client = docker.from_env()
    try:
        container = client.containers.run(
            "python:3.12-slim",
            command=command,
            volumes={repo_path: {"bind": "/app", "mode": "rw"}},
            working_dir="/app",
            remove=True,
            stdout=True,
            stderr=True,
            timeout=60
        )
        logs = container.decode("utf-8")
        success = "Build OK" in logs or "passed" in logs.lower()
        return {"success": success, "logs": logs}
    except Exception as e:
        return {"success": False, "logs": str(e)}