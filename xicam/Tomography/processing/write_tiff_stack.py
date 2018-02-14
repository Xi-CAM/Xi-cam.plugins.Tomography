#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input
import dxchange
import numpy as np


class WriteTiffStack(ProcessingPlugin):
    recon = Input(description="Data to be saved", type=np.ndarray)
    fname = Input(description="", type=str, default='/tmp/data.tiff')
    dtype = Input(description="Data-type", default=None)
    axis = Input(
        description="Axis along which stacking is done", type=int, default=0)
    start = Input(description="First index of the file", type=int, default=0)
    digit = Input(
        description="Number of digits in trailing index", type=int, default=5)
    overwrite = Input(description="True or false", type=bool, default=False)

    def evaluate(self):
        dxchange.write_tiff_stack(
            self.data.value,
            fname=self.fname.value,
            dtype=self.dtype.value,
            axis=self.axis.value,
            start=self.start.value,
            digit=self.digit.value,
            overwrite=self.overwrite.value)
