from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class AgentState:
    goal: str
    steps: List[str] = field(default_factory=list)
    current_step: int = 0
    observations: List[str] = field(default_factory=list)
    done: bool = False

    def next_step(self) -> Optional[str]:
        if self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            self.current_step += 1
            return step
        self.done = True
        return None