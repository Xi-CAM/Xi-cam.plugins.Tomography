#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, Output
import tomopy
import numpy as np


class Angles(ProcessingPlugin):
    """
    Return uniformly distributed projection angles in radian.
    """
    nang = Input(description='Number of projections', type=int)
    ang1 = Input(
        description='First proj. angle in deg', type=float, default=0.)
    ang2 = Input(description='Last proj. angle in deg', type=int, default=180.)
    angles = Output(description='Projection angles', type='np.ndarray')

    def evaluate(self):
        self.angles.value = tomopy.angles(
            self.nang.value, ang1=self.ang1.value, ang2=self.ang2.value)
