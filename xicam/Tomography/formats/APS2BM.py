from xicam.plugins.DataHandlerPlugin import DataHandlerPlugin, start_doc, descriptor_doc, event_doc, stop_doc, \
    embedded_local_event_doc

import os
import dxchange
import uuid
import re
import functools
from pathlib import Path
import h5py


class APS2BM(DataHandlerPlugin):
    """
    This plugin will only work for APS_2BM until a single entry point is made for DataExchange
    """
    name = 'APS2BM'

    descriptor_keys = []

    def __init__(self, path, *args, **kwargs):
        self.path = path
        super(APS2BM, self).__init__()

    def __call__(self, *args, **kwargs):
        if 'flat' in kwargs:
            return dxchange.read_aps_2bm(self.path, (0, 1, 1), **kwargs)[1]
        elif 'dark' in kwargs:
            return dxchange.read_aps_2bm(self.path, (0, 1, 1), **kwargs)[2]
        else:
            return dxchange.read_aps_2bm(self.path, *args, **kwargs)[0]

    @classmethod
    def getEventDocs(cls, path, descriptor_uid):
        for proj_index in range(cls.num_projections(path)):
            yield embedded_local_event_doc(descriptor_uid, 'projection', cls, (path,), {'proj': proj_index})

        for sino_index in range(cls.num_sinograms(path)):
            yield embedded_local_event_doc(descriptor_uid, 'sinogram', cls, (path,), {'sino': sino_index})

        for flat_index in range(cls.num_flats(path)):
            yield embedded_local_event_doc(descriptor_uid, 'flat', cls, (path,), {'flat': flat_index})

        for dark_index in range(cls.num_darks(path)):
            yield embedded_local_event_doc(descriptor_uid, 'dark', cls, (path,), {'dark': dark_index})

    @classmethod
    def num_projections(cls, path):
        with h5py.File(path, 'r') as h5:
            return h5['exchange']['data'].shape[0]

    @classmethod
    def num_sinograms(cls, path):
        with h5py.File(path, 'r') as h5:
            return h5['exchange']['data'].shape[1]

    @classmethod
    def num_flats(cls, path):
        with h5py.File(path, 'r') as h5:
            return h5['exchange']['data_white'].shape[0]

    @classmethod
    def num_darks(cls, path):
        with h5py.File(path, 'r') as h5:
            return h5['exchange']['data_dark'].shape[0]
