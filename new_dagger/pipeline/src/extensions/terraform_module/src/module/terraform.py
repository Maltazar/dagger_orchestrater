from typing import Type
from pydantic import BaseModel
from pipeline.modules.base import BaseModule, ModuleResult
from ..config.model import TerraformConfig

class TerraformModule(BaseModule):
    """Terraform module implementation"""
    
    def get_config_model(self) -> Type[BaseModel]:
        return TerraformConfig
    
    async def validate(self, config: dict) -> bool:
        """Validate terraform configuration"""
        try:
            TerraformConfig.model_validate(config)
            return True
        except Exception:
            return False
    
    async def pre_execute(self, config: dict) -> ModuleResult:
        """Check terraform installation and dependencies"""
        try:
            # Add terraform installation check logic here
            return ModuleResult(
                success=True,
                message="Pre-execution checks passed"
            )
        except Exception as e:
            return ModuleResult(
                success=False,
                message="Pre-execution failed",
                error=str(e)
            )
    
    async def execute(self, config: dict) -> ModuleResult:
        """Execute terraform operations"""
        try:
            tf_config = TerraformConfig.model_validate(config)
            print(tf_config)
            # Add terraform execution logic here
            return ModuleResult(
                success=True,
                message="Terraform execution completed",
                data={"applied": True}
            )
        except Exception as e:
            return ModuleResult(
                success=False,
                message="Terraform execution failed",
                error=str(e)
            )
    
    async def post_execute(self, config: dict, result: ModuleResult) -> ModuleResult:
        """Cleanup and state management"""
        return result