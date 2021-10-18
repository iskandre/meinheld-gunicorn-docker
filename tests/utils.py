import json
import os
import sys
from typing import Any, Dict, List

from docker.client import DockerClient
from docker.errors import NotFound
from docker.models.containers import Container

CONTAINER_NAME = "meinheld-gunicorn-test"
IMAGE_NAME = os.getenv("IMAGE_NAME")
IMAGE_TAG = os.getenv("TAG_NAME")
if os.getenv("IS_SIMPLIFIED",0) == 1:
    IMAGE_TAG = IMAGE_TAG + '-simplified'
IMAGE_FULL_NAME = f"{IMAGE_NAME}:{IMAGE_TAG}"
# IMAGE_TAG = 'python3.7-alpine-latest-simplified'
# IMAGE_NAME = 'alexiskandre/meinheld-gunicorn'
# IMAGE_FULL_NAME = f"{IMAGE_NAME}:{IMAGE_TAG}"



def get_process_names(container: Container) -> List[str]:
    top = container.top()
    process_commands = [p[7] for p in top["Processes"]]
    gunicorn_processes = [p for p in process_commands if "gunicorn" in p]
    return gunicorn_processes


def get_gunicorn_conf_path(container: Container) -> str:
    gunicorn_processes = get_process_names(container)
    first_process = gunicorn_processes[0]
    first_part, partition, last_part = first_process.partition(" -c ")
    gunicorn_conf = last_part.strip().split()[0]
    return gunicorn_conf


def get_config(container: Container) -> Dict[str, Any]:
    gunicorn_conf = get_gunicorn_conf_path(container)
    result = container.exec_run(f"python {gunicorn_conf}")
    return json.loads(result.output.decode())


def remove_previous_container(client: DockerClient) -> None:
    try:
        previous = client.containers.get(CONTAINER_NAME)
        previous.stop()
        previous.remove()
    except NotFound:
        return None


def get_logs(container: Container) -> str:
    logs = container.logs()
    return logs.decode("utf-8")


def get_response_text1() -> str:
    python_version = os.getenv(
        "PYTHON_VERSION", "{}.{}".format(sys.version_info.major, sys.version_info.minor)
    )
    return f"Hello World from a default Python {python_version} app in a Docker container, with Meinheld and Gunicorn (default)"


def get_response_text2() -> str:
    python_version = os.getenv(
        "PYTHON_VERSION", "{}.{}".format(sys.version_info.major, sys.version_info.minor)
    )
    return f"Test app. From Meinheld with Gunicorn. Using Python {python_version}"


def generate_dockerfile_content(name: str) -> str:
    content = f"FROM {name}\n"
    content += "COPY ./app /app\n"
    return content
