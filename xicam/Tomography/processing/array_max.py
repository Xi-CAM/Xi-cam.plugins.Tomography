#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, InOut
import numpy as np


class ArrayMax(ProcessingPlugin):
    """
    Maximum value of the tomoay
    """
    tomo = InOut(description="Input tomogram", type=np.ndarray)
    floor = Input(
        description="Floor value for comparison",
        type=float,
        default=0)

    def evaluate(self):
        self.tomo.value = np.maximum(self.tomo.value, self.floor.value)
