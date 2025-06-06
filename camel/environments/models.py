# ========= Copyright 2023-2024 @ CAMEL-AI.org. All Rights Reserved. =========
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ========= Copyright 2023-2024 @ CAMEL-AI.org. All Rights Reserved. =========

from datetime import datetime, timezone
from typing import Any, Dict, Optional, Protocol, Tuple

from pydantic import BaseModel, Field


class Action(BaseModel):
    r"""Represents an action taken in an environment.

    This class defines the input context, the LLM-generated output, and
    metadata required for verification and tracking within an RL
    framework.

    Attributes:
        llm_response (str): The response generated by the LLM.
        metadata (Dict[str, Any]): Additional metadata such as model
            parameters, prompt details, or response confidence scores.
        timestamp (datetime): The timestamp when the action was
            generated (UTC).
    """

    index: int = Field(default=0, description="...")

    llm_response: str = Field(description="Generated response from the LLM")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the generation",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the response was generated (UTC)",
    )


class Observation(BaseModel):
    r"""Environment observation.

    Attributes:
        question: The question posed to the LLM.
        context: Additional context for the question.
        metadata: Optional metadata about the observation.
    """

    question: str = Field(..., description="The question posed to the LLM")
    context: Dict[str, Any] = Field(
        default_factory=dict, description="Additional context for the question"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional metadata about the observation"
    )


class StepResult(BaseModel):
    r"""Result of an environment step.

    Attributes:
        observation: The next observation.
        reward: Dictionary of reward scores for different aspects.
        done: Whether the episode is complete.
        info: Additional information about the step.
    """

    observation: Observation = Field(..., description="The next observation")
    reward: float = Field(..., description="Total reward of the action")
    rewards_dict: Dict[str, float] = Field(
        default_factory=dict,
        description="Dictionary of reward scores for different aspects",
    )
    done: bool = Field(..., description="Whether the episode is complete")
    info: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional information about the step",
    )

    def as_tuple(
        self,
    ) -> Tuple[Observation, float, bool, Dict[str, Any]]:
        r"""Returns all fields of the model as a tuple, in declaration order"""
        self.info["rewards_dict"] = self.rewards_dict
        return (self.observation, self.reward, self.done, self.info)


class Environment(Protocol):
    async def reset(self) -> Observation:
        r"""Reset the environment to an initial state.

        Returns:
            Initial observation for the episode
        """
        ...

    async def step(self, action: Action) -> StepResult:
        r"""Take a step in the environment.

        Args:
            action: Action containing everything that is needed
            to progress in the environment

        Returns:
            StepResult containing next observation, reward, done flag, and info
        """
        ...

    async def close(self) -> None:
        r"""Perform a full cleanup of all environment resources."""
        ...
