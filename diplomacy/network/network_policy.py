# Copyright 2021 DeepMind Technologies Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Agent which steps using a network."""

from typing import Any, Sequence, Tuple
import numpy as np

from deepmind.diplomacy.environment import observation_utils as utils


class Policy:
  """Agent which delegates stepping and updating to a network."""

  def __init__(
      self,
      network_handler,
      num_players,
      temperature):

    self._network_handler = network_handler
    self._num_players = num_players
    self._obs_transform_state = None
    self._temperature = temperature
    self._str = f'OnPolicy(t={self._temperature})'

  def __str__(self):
    return self._str

  def reset(self):
    self._obs_transform_state = None
    self._network_handler.reset()

  def actions(
      self, slots_list: Sequence[int], observation: utils.Observation,
      legal_actions: Sequence[np.ndarray]
  ) -> Tuple[Sequence[Sequence[int]], Any]:
    """Produce a list of lists of actions.

    Args:
      slots_list: the slots this policy should produce actions for.
      observation: observations from the environment.
      legal_actions: the legal actions for every player in the game.

    Returns:
      - a len(slots_list) sequence of sequences of actions, each with the
        actions for the corresponding entry of slots_list.
      - Arbitrary step_outputs containing facts about the step
    """
    (transformed_obs,
     self._obs_transform_state) = self._network_handler.observation_transform(
         observation=observation,
         legal_actions=legal_actions,
         slots_list=slots_list,
         prev_state=self._obs_transform_state,
         temperature=self._temperature)

    (initial_outs, step_outs), final_actions = self._network_handler.inference(
        transformed_obs)

    return [final_actions[i] for i in slots_list], {
        'values': initial_outs['values'],
        'policy': step_outs['policy'],
        'actions': step_outs['actions']
    }
