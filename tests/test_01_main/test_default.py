import os
import time

import docker
import requests
from docker.models.containers import Container

from ..utils import (
    CONTAINER_NAME,
    IMAGE_FULL_NAME,
    get_config,
    get_logs,
    get_response_text1,
    remove_previous_container,
)

client = docker.from_env()


def verify_container(container: Container, response_text: str) -> None:
    response = requests.get("http://127.0.0.1:8000")
    assert response.text == response_text
    config_data = get_config(container)
    assert config_data["workers_per_core"] == 1
    assert config_data["host"] == "0.0.0.0"
    assert config_data["port"] == "8000"
    assert config_data["loglevel"] == "warning"
    assert config_data["bind"] == "0.0.0.0:8000"
    logs = get_logs(container)
    assert "Checking for script in /app/prestart.sh" in logs
    assert "Running script /app/prestart.sh" in logs
    assert (
        "Running inside /app/prestart.sh, you could add migrations to this file" in logs
    )


def test_env_vars_1() -> None:
    img_name = IMAGE_FULL_NAME
    response_text = get_response_text1()
    sleep_time = int(os.getenv("SLEEP_TIME", 1))
    remove_previous_container(client)
    container = client.containers.run(
        img_name,
        name=CONTAINER_NAME,
        environment={"WORKERS_PER_CORE": 1, "PORT": "8000", "LOG_LEVEL": "warning"},
        ports={"8000": "8000"},
        detach=True,
    )
    time.sleep(sleep_time)
    verify_container(container, response_text)
    container.stop()
    # Test that everything works after restarting too
    container.start()
    time.sleep(sleep_time)
    verify_container(container, response_text)
    container.stop()
    container.remove()
