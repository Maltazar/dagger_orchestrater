"""Tests for the dagger_deploy_model module."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import pytest
from models.deploy import Ansible, Helm, K3s, Kubectl, Secret, Terraform
from pydantic import ValidationError

from .conftest import locate_dagger_deploy_yaml


def test_terraform_model(deploy_model):
    """Test the DeployModel class."""

    terraform = deploy_model.get("k3s").get("terraform")
    try:
        Terraform(**terraform[0])
    except ValidationError as e:
        pytest.fail(f"Terraform model not fullfilled. {e.errors()}")


def test_secrets_model(deploy_model):
    """Tests the secrets pydantic model"""
    secrets = deploy_model.get("k3s").get("secrets")

    try:
        Secret(**secrets[0])
    except ValidationError as e:
        pytest.fail(f"Secret model not fullfilled. {e.errors()}")


def test_k3s_ansible_model(deploy_model):
    """Tests the ansible pydantic model"""
    ansible = deploy_model.get("k3s").get("ansible")

    try:
        Ansible(**ansible[0])
    except ValidationError as e:
        pytest.fail(f"Ansible model not fullfilled. {e.errors()}")


def test_ansible_model_optional_vars_section(deploy_model):
    """Tests the ansible model without a vars section"""
    ansible = deploy_model.get("k3s").get("ansible")

    try:
        Ansible(**ansible[1])
    except ValidationError as e:
        pytest.fail(f"Ansible model not fullfilled. {e.errors()}")


def test_helm_model(deploy_model):
    """Test the helm model"""
    helm = deploy_model.get("k3s").get("helm")

    try:
        Helm(**helm[0])
    except ValidationError as e:
        pytest.fail(f"Helm model not fullfilled. {e.errors()}")


def test_kubectl_model(deploy_model):
    """Tests the kubectl model"""
    kubectl = deploy_model.get("k3s").get("kubectl")

    try:
        Kubectl(**kubectl[0])
    except ValidationError as e:
        pytest.fail(f"Kubectl model not fullfilled. {e.errors()}")


def test_k3s_model(deploy_model):
    """Tests the k3s model"""
    k3s = deploy_model.get("k3s")
    try:
        K3s(**k3s)
    except ValidationError as e:
        pytest.fail(f"K3s model not fullfilled. {e.errors()}")


def test_locate_dagger_deploy_yaml_test_file():
    """Test we are able to find a file"""
    file = locate_dagger_deploy_yaml()
    assert file.exists()
