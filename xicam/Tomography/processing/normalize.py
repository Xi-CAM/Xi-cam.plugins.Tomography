#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xicam.plugins import ProcessingPlugin, Input, InOut
import tomopy
import numpy as np
import numpy


class set_numexpr_threads(object):

    def __init__(self, nthreads):
        #cpu_count = mp.cpu_count()
        #if nthreads is None or nthreads > cpu_count:
        #    self.n = cpu_count
        #else:
        #    self.n = nthreadsz
        pass

    def __enter__(self):
        #self.oldn = ne.set_num_threads(self.n)
        pass
    def __exit__(self, exc_type, exc_value, traceback):
        #ne.set_num_threads(self.oldn)
        pass

class Normalize(ProcessingPlugin):
    """
    Normalize raw 3D projection data with flats and darks
    """

    tomo = InOut(description="3D tomographic data", type=np.ndarray)
    flats = Input(description="3D flat field data", type=np.ndarray)
    darks = Input(description="3D dark field data", type=np.ndarray)
    
    def evaluate(self):

        import tomopy.util.mproc
        tomopy.util.mproc.set_numexpr_threads = set_numexpr_threads

        self.tomo.value = tomopy.normalize(
            self.tomo.value,
            self.flats.value,
            self.darks.value)

    @staticmethod
    def normalize(arr, flat, dark):
        denom = flat - dark
        out = arr - dark
        out = out / denom

        return out
