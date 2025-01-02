import dagger

from src.handlers.extension import ExtensionHandler

class TerraformExtension(ExtensionHandler):
    async def setup_container(self) -> dagger.Container:
        """Setup Terraform container"""
        return (
            await self.client.container()
            .from_("hashicorp/terraform:latest")
            .with_workdir("/workspace")
            .with_mounted_directory("/workspace", self.client.host().directory("."))
        )

    async def validate(self) -> bool:
        """Validate Terraform configuration"""
        if not self.container:
            return False
            
        result = await self.container.with_exec(["terraform", "init"]).with_exec(["terraform", "validate"]).exit_code()
        return result == 0

    async def execute(self) -> bool:
        """Execute Terraform deployment"""
        if not self.container:
            return False
            
        # Apply Terraform configuration
        result = await (
            self.container
            .with_exec(["terraform", "init"])
            .with_exec(["terraform", "apply", "-auto-approve"])
            .exit_code()
        )
        return result == 0 