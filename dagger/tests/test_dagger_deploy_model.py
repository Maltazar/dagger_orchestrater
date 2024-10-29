import os
import sys
import pytest
from models.deploy import Ansible, Helm, Kubectl, Secret, Terraform, DeployModel
from pydantic import ValidationError

from .conftest import locate_dagger_deploy_yaml


def test_terraform_model(deploy_model):
    """Test the DeployModel class."""
    for root_key in deploy_model.root.keys():
        terraform = deploy_model.root[root_key].get("terraform")
        if terraform:
            try:
                Terraform(**terraform[0])
            except ValidationError as e:
                pytest.fail(f"Terraform model not fulfilled. {e.errors()}")


def test_secrets_model(deploy_model):
    """Tests the secrets pydantic model"""
    for root_key in deploy_model.root.keys():
        secrets = deploy_model.root[root_key].get("secrets")
        if secrets:
            try:
                Secret(**secrets[0])
            except ValidationError as e:
                pytest.fail(f"Secret model not fulfilled. {e.errors()}")


def test_ansible_model(deploy_model):
    """Tests the ansible pydantic model"""
    for root_key in deploy_model.root.keys():
        ansible = deploy_model.root[root_key].get("ansible")
        if ansible:
            try:
                Ansible(**ansible[0])
            except ValidationError as e:
                pytest.fail(f"Ansible model not fulfilled. {e.errors()}")


def test_ansible_model_optional_vars_section(deploy_model):
    """Tests the ansible model without a vars section"""
    for root_key in deploy_model.root.keys():
        ansible = deploy_model.root[root_key].get("ansible")
        if ansible and len(ansible) > 1:
            try:
                Ansible(**ansible[1])
            except ValidationError as e:
                pytest.fail(f"Ansible model not fulfilled. {e.errors()}")


def test_helm_model_git_and_set(deploy_model):
    """Test the helm model"""
    for root_key in deploy_model.root.keys():
        helm = deploy_model.root[root_key].get("helm")
        if helm:
            try:
                Helm(**helm[0])
            except ValidationError as e:
                pytest.fail(f"Helm model not fulfilled. {e.errors()}")


def test_helm_model_only_values(deploy_model):
    """Test the helm model"""
    for root_key in deploy_model.root.keys():
        helm = deploy_model.root[root_key].get("helm")
        if helm and len(helm) > 1:
            try:
                Helm(**helm[1])
            except ValidationError as e:
                pytest.fail(f"Helm model not fulfilled. {e.errors()}")


def test_kubectl_model(deploy_model):
    """Tests the kubectl model"""
    for root_key in deploy_model.root.keys():
        kubectl = deploy_model.root[root_key].get("kubectl")
        if kubectl:
            try:
                Kubectl(**kubectl[0])
            except ValidationError as e:
                pytest.fail(f"Kubectl model not fulfilled. {e.errors()}")


def test_deploy_play_name_model(deploy_model):
    """Tests the deploy_play_name model"""
    for root_key in deploy_model.root.keys():
        deploy_play_name = deploy_model.root[root_key]
        try:
            DeployModel(root={root_key: deploy_play_name})
        except ValidationError as e:
            pytest.fail(f"deploy_play_name model not fulfilled. {e.errors()}")


def test_locate_dagger_deploy_yaml_test_file():
    """Test we are able to find a file"""
    file = locate_dagger_deploy_yaml()
    assert file.exists()
