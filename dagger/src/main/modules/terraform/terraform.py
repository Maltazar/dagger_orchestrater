
from typing import List
from models import Terraform
import dagger
from dagger import dag, function, object_type
from helpers.helper import prepare_key_value_args 


@function
def terraform_plan(self, source: dagger.Directory, url: str, tf_vars: Terraform) -> dagger.Container:
    """Run Terraform plan using the provided directory and variables"""
    terraform_dir = self.clone_repository(url, "/git_dir")
    
    # Prepare the variables for the Terraform command
    var_args = prepare_key_value_args(tf_vars.vars)
    
    return (
        dag.container()
        .from_("hashicorp/terraform:light")
        .with_mounted_directory("/mnt", terraform_dir)
        .with_workdir("/mnt")
        .with_exec(["terraform", "init"])
        .with_exec(["terraform", "plan", "-out=tf.plan"] + var_args)
        .stdout()
    )

@function
def terraform_apply(self, source: dagger.Directory, url: str, tf_vars: Terraform) -> dagger.Container:
    """Run Terraform apply using the provided directory and variables"""
    terraform_dir = self.clone_repository(url, "/git_dir")
    
    # Prepare the variables for the Terraform command
    var_args = prepare_key_value_args(tf_vars.vars)
    
    return (
        dag.container()
        .from_("hashicorp/terraform:light")
        .with_mounted_directory("/mnt", terraform_dir)
        .with_workdir("/mnt")
        .with_exec(["terraform", "apply", "-auto-approve"] + var_args)
        .stdout()
    )