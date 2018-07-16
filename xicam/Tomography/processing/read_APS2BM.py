from xicam.plugins import ProcessingPlugin, Input, Output
import dxchange
import numpy as np
import copy

class read_APS2BM(ProcessingPlugin):
    """
    Remove high intensity bright spots from a N-dimensional array by chunking
    along the specified dimension, and performing (N-1)-dimensional median
    filtering along the other dimensions.
    """
    path = Input(description="Path to file", type=str)
    chunksize = Input(description="Number of sinograms to read simultaneously", type=int, default=1)
    sinoindex = Input(description="Index of (first) sinogram to read", type=int)

    tomo = Output(
        description=
        " Output array for result. If same as arr, process will be done in-place",
        type=np.ndarray)
    flats = Output(description="Array data for flat fields", type=np.ndarray)
    darks = Output(description="Array data for dark fields", type=np.ndarray)
    angles = Output(description="Tomogram angles", type=np.ndarray)

    def evaluate(self):
        self.tomo.value, self.flats.value, self.darks.value, self.angles.value = dxchange.read_aps_2bm(self.path.value,
                                                                                                       None,
                                                                                                       (
                                                                                                           self.sinoindex.value,
                                                                                                           int(
                                                                                                               self.sinoindex.value) + int(
                                                                                                               self.chunksize.value),
                                                                                                           1))

    def len(self):
        max_len = -1

        for input in self.inputs.items():
            try:
                if isinstance(input[1].value, list) or isinstance(input[1].value, tuple):
                    max_len = len(input[1].value)
            except:
                pass

        return max_len

    def emit(self):
        max_len = self.len()

        all_inputs = []
        for index in range(max_len):
            input_list = []

            for input in self.inputs.items():
                if isinstance(input[1].value, list) or isinstance(input[1].value, tuple):
                    try:
                        value = self.inputs[input[0]].value[index % len(input[1].value)]
                    except:
                        value = self.inputs[input[0]].value
                else:
                    value = self.inputs[input[0]].value

                input_list.append((input[0], value))
            all_inputs.append(input_list)

        for input_list in all_inputs:
            yield input_list

