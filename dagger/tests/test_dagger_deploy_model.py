import pytest
from models.orchestrate import Ansible, Helm, Kubectl, Secret, Terraform, Orchestrate
from pydantic import ValidationError

from .conftest import locate_dagger_deploy_yaml


def test_terraform_model(deploy_model):
    """Test the Terraform model within the Orchestrate class."""
    for _, modules in deploy_model.root.items():
        if modules.terraform:
            for terraform in modules.terraform:
                try:
                    Terraform(**terraform.dict())
                except ValidationError as e:
                    pytest.fail(f"Terraform model not fulfilled. {e.errors()}")


def test_secrets_model(deploy_model):
    """Test the Secret model within the Orchestrate class."""
    for _, modules in deploy_model.root.items():
        if modules.secrets:
            for secret in modules.secrets:
                try:
                    Secret(**secret.dict())
                except ValidationError as e:
                    pytest.fail(f"Secret model not fulfilled. {e.errors()}")


def test_ansible_model(deploy_model):
    """Test the Ansible model within the Orchestrate class."""
    for _, modules in deploy_model.root.items():
        if modules.ansible:
            for ansible in modules.ansible:
                try:
                    Ansible(**ansible.dict())
                except ValidationError as e:
                    pytest.fail(f"Ansible model not fulfilled. {e.errors()}")


def test_ansible_model_optional_vars_section(deploy_model):
    """Test the Ansible model without a vars section within the Orchestrate class."""
    for _, modules in deploy_model.root.items():
        if modules.ansible and len(modules.ansible) > 1:
            try:
                Ansible(**modules.ansible[1].dict())
            except ValidationError as e:
                pytest.fail(f"Ansible model not fulfilled. {e.errors()}")


def test_helm_model_git_and_set(deploy_model):
    """Test the Helm model within the Orchestrate class."""
    for _, modules in deploy_model.root.items():
        if modules.helm:
            for helm in modules.helm:
                try:
                    Helm(**helm.dict())
                except ValidationError as e:
                    pytest.fail(f"Helm model not fulfilled. {e.errors()}")


def test_helm_model_only_values(deploy_model):
    """Test the Helm model with only values within the Orchestrate class."""
    for _, modules in deploy_model.root.items():
        if modules.helm and len(modules.helm) > 1:
            try:
                Helm(**modules.helm[1].dict())
            except ValidationError as e:
                pytest.fail(f"Helm model not fulfilled. {e.errors()}")


def test_kubectl_model(deploy_model):
    """Test the Kubectl model within the Orchestrate class."""
    for _, modules in deploy_model.root.items():
        if modules.kubectl:
            for kubectl in modules.kubectl:
                try:
                    Kubectl(**kubectl.dict())
                except ValidationError as e:
                    pytest.fail(f"Kubectl model not fulfilled. {e.errors()}")


def test_deploy_play_name_model(deploy_model):
    """Test the deploy_play_name model within the Orchestrate class."""
    for _, modules in deploy_model.root.items():
        try:
            Orchestrate(root={_: modules})
        except ValidationError as e:
            pytest.fail(f"deploy_play_name model not fulfilled. {e.errors()}")


def test_locate_dagger_deploy_yaml_test_file():
    """Test we are able to find a file."""
    file = locate_dagger_deploy_yaml()
    assert file.exists()
