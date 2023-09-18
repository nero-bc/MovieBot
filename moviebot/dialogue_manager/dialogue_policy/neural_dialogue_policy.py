"""Neural dialogue policy built on top of PyTorch."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, List

import torch
from sklearn.preprocessing import MultiLabelBinarizer

from moviebot.core.intents.agent_intents import AgentIntents
from moviebot.core.intents.user_intents import UserIntents
from moviebot.dialogue_manager.dialogue_state import DialogueState


class NeuralDialoguePolicy(torch.nn.Module):
    user_label_encoder = MultiLabelBinarizer().fit(
        [list(map(lambda x: x.value.label, UserIntents))]
    )
    agent_label_encoder = MultiLabelBinarizer().fit(
        [list(map(lambda x: x.value.label, AgentIntents))]
    )

    def __init__(
        self,
        input_size: int,
        hidden_size: int,
        output_size: int,
        possible_actions: List[Any],
    ) -> None:
        """Initializes the policy.

        Args:
            input_size: The size of the input vector.
            hidden_size: The size of the hidden layer.
            output_size: The size of the output vector.
            possible_actions: The list of possible actions.
        """
        super(NeuralDialoguePolicy, self).__init__()

        self.possible_actions = possible_actions

        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

    @abstractmethod
    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """Forward pass of the policy.

        Args:
            state: State or batch of states.

        Raises:
            NotImplementedError: If the method is not implemented in the
              subclass.
        Returns:
            Output of the policy.
        """
        raise NotImplementedError

    @abstractmethod
    def select_action(self, state: torch.Tensor) -> Any:
        """Selects an action based on the current state.

        Args:
            state: The current state.

        Raises:
            NotImplementedError: If the method is not implemented in the
              subclass.

        Returns:
            Selected action and optionally other information.
        """
        raise NotImplementedError

    @abstractmethod
    def save_policy(self, path: str) -> None:
        """Saves the policy.

        Args:
            path: Path to save the policy.

        Raises:
            NotImplementedError: If the method is not implemented in the
              subclass.
        """
        raise NotImplementedError

    @abstractmethod
    @classmethod
    def load_policy(cls, path: str) -> NeuralDialoguePolicy:
        """Loads the policy.

        Args:
            path: Path to load the policy from.

        Raises:
            NotImplementedError: If the method is not implemented in the
              subclass.

        Returns:
            The loaded policy.
        """
        raise NotImplementedError

    @classmethod
    def build_input_from_dialogue_state(
        cls, dialogue_state: DialogueState, **kwargs
    ) -> torch.Tensor:
        """Builds the input vector from the dialogue state.

        Args:
            dialogue_state: The dialogue state.

        Returns:
            The input vector.
        """
        dialogue_state_tensor = torch.tensor(
            [
                dialogue_state.is_beginning,
                dialogue_state.agent_req_filled,
                dialogue_state.agent_can_lookup,
                dialogue_state.agent_made_partial_offer,
                dialogue_state.agent_should_make_offer,
                dialogue_state.agent_made_offer,
                dialogue_state.agent_offer_no_results,
                dialogue_state.at_terminal_state,
            ],
            dtype=torch.float,
        )
        return dialogue_state_tensor

    @classmethod
    def build_input_from_dialogue_state_and_intents(
        cls,
        dialogue_state: DialogueState,
        user_intents: List[UserIntents],
        agent_intents: List[AgentIntents],
        **kwargs,
    ) -> torch.Tensor:
        """Builds the input vector from the dialogue state and previous intents.

        Args:
            dialogue_state: The dialogue state.
            user_intents: The user intents.
            agent_intents: The agent intents.

        Returns:
            The input vector.
        """
        dialogue_state_tensor = cls.build_input_from_dialogue_state(
            dialogue_state
        )

        if len(user_intents) == 0:
            user_intents_tensor = torch.zeros(
                len(cls.user_label_encoder.classes_), dtype=torch.float
            )
        else:
            user_intents_tensor = torch.tensor(
                cls.user_label_encoder.transform(
                    [list(map(lambda x: x.value.label, user_intents))]
                )[0],
                dtype=torch.float,
            )

        if len(agent_intents) == 0:
            agent_intents_tensor = torch.zeros(
                len(cls.agent_label_encoder.classes_), dtype=torch.float
            )
        else:
            agent_intents_tensor = torch.tensor(
                cls.agent_label_encoder.transform(
                    [list(map(lambda x: x.value.label, agent_intents))]
                )[0],
                dtype=torch.float,
            )

        return torch.cat(
            [dialogue_state_tensor, user_intents_tensor, agent_intents_tensor],
            dim=0,
        )

    @classmethod
    def build_input(
        cls, dialogue_state: DialogueState, **kwargs
    ) -> torch.Tensor:
        """Builds the input vector.

        Args:
            dialogue_state: The dialogue state.

        Returns:
            The input vector.
        """
        if kwargs.get("b_use_intents", False):
            return cls.build_input_from_dialogue_state_and_intents(
                dialogue_state, **kwargs
            )
        return cls.build_input_from_dialogue_state(dialogue_state)
