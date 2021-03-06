#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates. All rights reserved.

import unittest

from ml.rl.net_builder import parametric_dqn
from ml.rl.net_builder.choosers import ParametricDQNNetBuilderChooser
from ml.rl.net_builder.parametric_dqn_net_builder import ParametricDQNNetBuilder
from ml.rl.parameters import NormalizationParameters
from ml.rl.preprocessing.identify_types import CONTINUOUS


try:
    from ml.rl.fb.prediction.fb_predictor_wrapper import (
        FbParametricDqnPredictorWrapper as ParametricDqnPredictorWrapper,
    )
except ImportError:
    from ml.rl.prediction.predictor_wrapper import (  # type: ignore
        ParametricDqnPredictorWrapper,
    )


class TestParametricDQNNetBuilder(unittest.TestCase):
    def _test_parametric_dqn_net_builder(
        self, chooser: ParametricDQNNetBuilderChooser
    ) -> None:
        builder = ParametricDQNNetBuilder.create_from_union(chooser)
        state_dim = 3
        state_norm_params = {
            i: NormalizationParameters(feature_type=CONTINUOUS, mean=0.0, stddev=1.0)
            for i in range(state_dim)
        }
        action_dim = 2
        action_norm_params = {
            i: NormalizationParameters(feature_type=CONTINUOUS, mean=0.0, stddev=1.0)
            for i in range(action_dim)
        }
        q_network = builder.build_q_network(state_norm_params, action_norm_params)
        x = q_network.input_prototype()
        y = q_network(x).q_value
        self.assertEqual(y.shape, (1, 1))
        serving_module = builder.build_serving_module(
            q_network, state_norm_params, action_norm_params
        )
        self.assertIsInstance(serving_module, ParametricDqnPredictorWrapper)

    def test_fully_connected(self):
        # Intentionally used this long path to make sure we included it in __init__.py
        chooser = ParametricDQNNetBuilderChooser(
            FullyConnected=parametric_dqn.fully_connected.FullyConnected.config_type()()
        )
        self._test_parametric_dqn_net_builder(chooser)
