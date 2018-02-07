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
    ang1 = Input(description='First proj. angle in deg', type=float)
    ang2 = Input(description='Last proj. angle in deg', type=int)
    angles = Output(description='Projection angles', type='np.ndarray')

    def evalulate(self):
        self.angles.value = tomopy.angles(self.nang.value, self.ang1.value,
                                          self.ang2.value)
