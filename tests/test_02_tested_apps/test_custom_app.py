import os
import time
from pathlib import Path
from typing import Dict

import docker
import pytest
import requests
from docker.models.containers import Container

from ..utils import (
    CONTAINER_NAME,
    IMAGE_FULL_NAME,
    IMAGE_NAME,
    IMAGE_TAG,
    generate_dockerfile_content,
    get_config,
    get_logs,
    get_response_text2,
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
    assert config_data["loglevel"] == "info"
    assert config_data["workers"] > 0
    assert config_data["bind"] == "0.0.0.0:8000"
    logs = get_logs(container)
    assert "Checking for script in /app/prestart.sh" in logs
    assert "Running script /app/prestart.sh" in logs
    assert "Running custom prestart.sh" in logs


@pytest.mark.parametrize(
    "environment",
    [
        {"MODULE_NAME": "custom_app.custom_main", "VARIABLE_NAME": "custom_var", "PORT":"8000"},
        {"APP_MODULE": "custom_app.custom_main:custom_var", "PORT":"8000"},
    ],
)
def test_custom_app(environment: Dict[str, str]) -> None:
    img_name = IMAGE_FULL_NAME
    image_test_name = 'test-build'
    dockerfile_content = generate_dockerfile_content(img_name)
    dockerfile = "Dockerfile"
    response_text = get_response_text2()
    sleep_time = int(os.getenv("SLEEP_TIME", 1))
    remove_previous_container(client)
    test_path = Path(__file__)
    path = test_path.parent / "custom_app"
    dockerfile_path = path / dockerfile
    dockerfile_path.write_text(dockerfile_content)
    client.images.build(path=str(path), dockerfile=dockerfile, tag=f'{image_test_name}:{IMAGE_TAG}')
    container = client.containers.run(
        f'{image_test_name}:{IMAGE_TAG}',
        name=CONTAINER_NAME,
        environment=environment,
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