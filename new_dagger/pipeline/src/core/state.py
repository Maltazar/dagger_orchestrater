from typing import Dict, Any
import logging
from ..models.state import ModuleState, ModuleStateInfo

logger = logging.getLogger(__name__)

class StateManager:
    """Manages module execution state and data sharing"""
    
    def __init__(self):
        self.states: Dict[str, ModuleStateInfo] = {}
        self.shared_data: Dict[str, Any] = {}
    
    def initialize_module(self, module_name: str) -> None:
        """Initialize a module's state"""
        self.states[module_name] = ModuleStateInfo(
            state=ModuleState.PENDING
        )
        logger.debug(f"Initialized module {module_name} in PENDING state")
    
    def set_module_state(self, 
                        module_name: str, 
                        state: ModuleState, 
                        data: Dict[str, Any] | None = None, 
                        error: str | None = None) -> None:
        """Update a module's state"""
        self.states[module_name] = ModuleStateInfo(
            state=state,
            data=data,
            error=error
        )
        logger.info(f"Module {module_name} state changed to {state}")
        
        if data:
            self.shared_data[module_name] = data
    
    def get_module_state(self, module_name: str) -> ModuleStateInfo:
        """Get current state of a module"""
        return self.states.get(module_name)
    
    def get_shared_data(self, module_name: str) -> Dict[str, Any] | None:
        """Get shared data from a module"""
        return self.shared_data.get(module_name) 