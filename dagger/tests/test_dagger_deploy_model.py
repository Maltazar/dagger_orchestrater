"""Tests for the dagger_deploy_model module."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import pytest
from models.deploy import Ansible, Helm, Kubectl, Secret, Terraform, DeployModel
from pydantic import ValidationError

from .conftest import locate_dagger_deploy_yaml


def test_terraform_model(deploy_model):
    """Test the DeployModel class."""

    # Assuming the first key is dynamic, we can access it like this:
    terraform = deploy_model.root.get("deploy_play_name").get("terraform")
    try:
        Terraform(**terraform[0])
    except ValidationError as e:
        pytest.fail(f"Terraform model not fulfilled. {e.errors()}")


def test_secrets_model(deploy_model):
    """Tests the secrets pydantic model"""
    secrets = deploy_model.root.get("deploy_play_name").get("secrets")

    try:
        Secret(**secrets[0])
    except ValidationError as e:
        pytest.fail(f"Secret model not fulfilled. {e.errors()}")


def test_ansible_model(deploy_model):
    """Tests the ansible pydantic model"""
    ansible = deploy_model.root.get("deploy_play_name").get("ansible")

    try:
        Ansible(**ansible[0])
    except ValidationError as e:
        pytest.fail(f"Ansible model not fulfilled. {e.errors()}")


def test_ansible_model_optional_vars_section(deploy_model):
    """Tests the ansible model without a vars section"""
    ansible = deploy_model.root.get("deploy_play_name").get("ansible")

    try:
        Ansible(**ansible[1])
    except ValidationError as e:
        pytest.fail(f"Ansible model not fulfilled. {e.errors()}")


def test_helm_model_git_and_set(deploy_model):
    """Test the helm model"""
    helm = deploy_model.root.get("deploy_play_name").get("helm")

    try:
        Helm(**helm[0])
    except ValidationError as e:
        pytest.fail(f"Helm model not fulfilled. {e.errors()}")


def test_helm_model_only_values(deploy_model):
    """Test the helm model"""
    helm = deploy_model.root.get("deploy_play_name").get("helm")

    try:
        Helm(**helm[1])
    except ValidationError as e:
        pytest.fail(f"Helm model not fulfilled. {e.errors()}")


def test_kubectl_model(deploy_model):
    """Tests the kubectl model"""
    kubectl = deploy_model.root.get("deploy_play_name").get("kubectl")

    try:
        Kubectl(**kubectl[0])
    except ValidationError as e:
        pytest.fail(f"Kubectl model not fulfilled. {e.errors()}")


def test_deploy_play_name_model(deploy_model):
    """Tests the deploy_play_name model"""
    deploy_play_name = deploy_model.root.get("deploy_play_name")
    try:
        DeployModel(**deploy_play_name)
    except ValidationError as e:
        pytest.fail(f"deploy_play_name model not fulfilled. {e.errors()}")


def test_locate_dagger_deploy_yaml_test_file():
    """Test we are able to find a file"""
    file = locate_dagger_deploy_yaml()
    assert file.exists()
