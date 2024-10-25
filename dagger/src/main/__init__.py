"""A generated module for DaggerOrchestrater functions

This module has been generated via dagger init and serves as a reference to
basic module structure as you get started with Dagger.

Two functions have been pre-created. You can modify, delete, or add to them,
as needed. They demonstrate usage of arguments and return types using simple
echo and grep commands. The functions can be called from the dagger CLI or
from one of the SDKs.

The first line in this comment block is a short description line and the
rest is a long description with more detail on the module's purpose or usage,
if appropriate. All modules should have a short description.
"""

# NOTE: it's recommended to move your code into other files in this package
# and keep __init__.py for imports only, according to Python's convention.
# The only requirement is that Dagger needs to be able to import a package
# called "main" (i.e., src/main/).
#
# For example, to import from src/main/main.py:
# >>> from .main import DaggerOrchestrater as DaggerOrchestrater

import dagger
from dagger import dag, function, object_type


@object_type
class DaggerOrchestrater:
    @function
    async def deploy(self, source: dagger.Directory) -> str:
        """Publish the application container after building and testing it on-the-fly"""
        terraform = await self.terraform(
            source, "https://github.com/simcax/terraform-proxmox-vm.git"
        )
        print(terraform)
        return print("ok")

    @function
    def terraform(self, source: dagger.Directory, url: str) -> dagger.Container:
        """Run Terraform commands using the provided directory"""
        terraform_dir = self.clone_repository(url, "/git_dir")
        return (
            dag.container()
            .from_("hashicorp/terraform:light")
            .with_mounted_directory("/mnt", terraform_dir)
            .with_workdir("/mnt")
            .with_exec(["terraform", "init"])
            .with_exec(["terraform", "plan", "-out=tf.plan"])
            .with_exec(["terraform", "apply", "-auto-approve"])
            .stdout()
        )

    def clone_repository(self, url: str, output_dir: str) -> dagger.Container:
        """Clone a repository from the provided URL"""
        return (
            dag.container()
            .from_("alpine/git:latest")
            .with_exec(["git", "clone", url, output_dir])
            .directory(output_dir)
        )

    @function
    def container_echo(self, string_arg: str) -> dagger.Container:
        """Returns a container that echoes whatever string argument is provided"""
        return dag.container().from_("alpine:latest").with_exec(["echo", string_arg])

    @function
    async def grep_dir(self, directory_arg: dagger.Directory, pattern: str) -> str:
        """Returns lines that match a pattern in the files of the provided Directory"""
        return await (
            dag.container()
            .from_("alpine:latest")
            .with_mounted_directory("/mnt", directory_arg)
            .with_workdir("/mnt")
            .with_exec(["grep", "-R", pattern, "."])
            .stdout()
        )
