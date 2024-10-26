import pytest
import yaml


@pytest.fixture
def deploy_model():
    with open("stage_files/dagger_deploy.yaml", "r") as yaml_file:
        deploy_model = yaml.safe_load(yaml_file)
    yield deploy_model
