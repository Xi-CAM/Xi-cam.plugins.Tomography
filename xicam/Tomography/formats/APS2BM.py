from xicam.plugins.DataHandlerPlugin import DataHandlerPlugin, start_doc, descriptor_doc, event_doc, stop_doc, \
    embedded_local_event_doc

import os
import dxchange
import uuid
import re
import functools
from pathlib import Path
import h5py
import numpy as np

class APS2BM(DataHandlerPlugin):
    """
    This plugin will only work for APS_2BM until a single entry point is made for DataExchange
    """
    name = 'APS2BM'

    DEFAULT_EXTENTIONS = ['.hdf', '.h5']

    descriptor_keys = []

    def __call__(self, path, arr='data', slice=None, **kwargs):
        h5 = h5py.File(path, 'r')
        if arr == 'sino':
            return np.squeeze(h5['exchange']['data'][:][slice])
        else:
            return np.squeeze(h5['exchange'][arr][slice])
            # if 'flat' in kwargs:
            #     # return np.squeeze(dxchange.read_aps_2bm(path, (0, 1, 1), **kwargs)[1])
            # elif 'dark' in kwargs:
            #     return np.squeeze(dxchange.read_aps_2bm(path, (0, 1, 1), **kwargs)[2])
            # else:
            #     return np.squeeze(dxchange.read_aps_2bm(path, *args, **kwargs)[0])

    @classmethod
    def reduce_paths(cls, paths):
        return paths[0]

    @classmethod
    def getEventDocs(cls, path, descriptor_uid):
        for proj_index in range(cls.num_projections(path)):
            yield embedded_local_event_doc(descriptor_uid, 'projection', cls, (path, 'data', proj_index))

        for sino_index in range(cls.num_sinograms(path)):
            yield embedded_local_event_doc(descriptor_uid, 'sinogram', cls, (path, 'sino', sino_index))

        for flat_index in range(cls.num_flats(path)):
            yield embedded_local_event_doc(descriptor_uid, 'flat', cls, (path, 'data_white', flat_index))

        for dark_index in range(cls.num_darks(path)):
            yield embedded_local_event_doc(descriptor_uid, 'dark', cls, (path, 'data_dark', dark_index))

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

    @classmethod
    def getStartDoc(cls, path, start_uid):
        return start_doc(start_uid=start_uid, metadata={'path': path})

    @classmethod
    def getDescriptorDocs(cls, paths, start_uid, descriptor_uid):
        yield descriptor_doc(start_uid, descriptor_uid)

    @classmethod
    def title(cls, path):
        return Path(path).resolve().stem
