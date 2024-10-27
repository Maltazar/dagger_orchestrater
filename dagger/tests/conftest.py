import pathlib

import pytest
import yaml


def locate_dagger_deploy_yaml() -> pathlib.Path:
    """Method to find the dagger deploy yaml file, as the working dir might ruin the location"""
    current_dir = pathlib.Path(__file__).resolve().parent.parent.parent
    dagger_deploy_file = pathlib.Path.joinpath(
        current_dir, "stage_files", "dagger_deploy.yaml"
    )
    return dagger_deploy_file


@pytest.fixture
def deploy_model():
    dagger_deploy_file = locate_dagger_deploy_yaml()

    with open(dagger_deploy_file, "r") as yaml_file:
        deploy_model = yaml.safe_load(yaml_file)
    yield deploy_model
