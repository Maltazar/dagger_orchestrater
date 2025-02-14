from typing import Dict, List, Set
import logging
from ..models.dependencies import ModuleDependencies

logger = logging.getLogger(__name__)

class DependencyManager:
    """Manages module dependencies and execution order"""
    
    def __init__(self):
        self.dependencies: Dict[str, ModuleDependencies] = {
            'secrets': ModuleDependencies(
                provides=['secrets']
            ),
            'terraform': ModuleDependencies(
                requires=['secrets'],
                provides=['infrastructure', 'terraform_state']
            ),
            'ansible': ModuleDependencies(
                requires=['secrets', 'terraform'],
                provides=['configured_nodes']
            ),
            'helm': ModuleDependencies(
                requires=['secrets', 'ansible'],
                provides=['helm_releases']
            ),
            'kubectl': ModuleDependencies(
                requires=['secrets', 'helm'],
                provides=['kubernetes_resources']
            )
        }
    
    def validate_dependencies(self, modules: List[str]) -> bool:
        """Validate that all module dependencies are satisfied"""
        try:
            for module in modules:
                if module not in self.dependencies:
                    raise ValueError(f"Unknown module: {module}")
                
                deps = self.dependencies[module]
                if deps.requires:
                    missing = [req for req in deps.requires 
                             if req not in modules]
                    if missing:
                        raise ValueError(
                            f"Module {module} requires {missing} but they are not configured"
                        )
            
            return True
            
        except Exception as e:
            logger.error(f"Dependency validation failed: {e}")
            return False
    
    def get_execution_order(self, modules: List[str]) -> List[str]:
        """Determine correct module execution order based on dependencies"""
        if not self.validate_dependencies(modules):
            raise ValueError("Cannot determine execution order: invalid dependencies")
        
        visited: Set[str] = set()
        ordered: List[str] = []
        
        def visit(module: str):
            """Depth-first traversal of module dependencies"""
            if module in visited:
                return
            
            visited.add(module)
            
            deps = self.dependencies[module]
            if deps.requires:
                for dep in deps.requires:
                    if dep in modules:
                        visit(dep)
            
            ordered.append(module)
        
        for module in modules:
            visit(module)
        
        return ordered
    
    def get_parallel_groups(self, modules: List[str]) -> List[Set[str]]:
        """Group modules that can be executed in parallel"""
        ordered = self.get_execution_order(modules)
        groups: List[Set[str]] = []
        current_group: Set[str] = set()
        
        for module in ordered:
            deps = self.dependencies[module]
            
            # Check if module can be added to current group
            if not deps.requires or all(
                req not in current_group for req in deps.requires
            ):
                current_group.add(module)
            else:
                if current_group:
                    groups.append(current_group)
                current_group = {module}
        
        if current_group:
            groups.append(current_group)
        
        return groups 