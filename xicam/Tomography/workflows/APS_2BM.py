from xicam.core.execution.workflow import Workflow
from xicam.core.execution.daskexecutor import DaskExecutor
# from xicam.plugins.Workflow import Workflow, DaskWorkflow
from xicam.Tomography.processing.read_APS2BM import read_APS2BM
from xicam.Tomography.processing.normalize import Normalize
from xicam.Tomography.processing.remove_outlier import RemoveOutlier
from xicam.Tomography.processing.array_max import ArrayMax
from xicam.Tomography.processing.minus_log import MinusLog
from xicam.Tomography.processing.retrieve_phase import RetrievePhase
from xicam.Tomography.processing.remove_stripe_fw import RemoveStripeFw
from xicam.Tomography.processing.pad import Pad
from xicam.Tomography.processing.angles import Angles
from xicam.Tomography.processing.recon import Recon
from xicam.Tomography.processing.crop import Crop
from xicam.Tomography.processing.array_divide import ArrayDivide
from xicam.Tomography.processing.circ_mask import CircMask
from xicam.Tomography.processing.write_tiff_stack import WriteTiffStack
import tomopy
import numpy as np


class TomoWorkflow(Workflow):
    def __init__(self):
        super(TomoWorkflow, self).__init__('APS-2BM')
        read = read_APS2BM()
        read.sinoindex.value = 1050
        read.chunksize.value = 5


        norm = Normalize()
        # read.tomo.connect(norm.tomo)
        # read.flats.connect(norm.flats)
        # read.dark.connect(norm.darks)

        outliers = RemoveOutlier()
        # norm.normalized.connect(outliers.arr)
        outliers.dif.value = 500
        outliers.size.value = 5

        # maximum = ArrayMax()
        # outliers.corrected.connect(maximum.arr)
        # maximum.floor.value = 1e-16

        # neglog = MinusLog()
        # maximum.out.connect(neglog.arr)

        # phase = RetrievePhase()
        # maximum.out.connect(phase.arr)
        # phase.pixel_size.value=6.5e-5
        # phase.dist.value=3
        # phase.energy.value=27

        stripe = RemoveStripeFw()
        stripe.level.value = 8
        stripe.wname.value = 'db5'
        stripe.sigma.value = 4
        stripe.pad.value = True

        padding = Pad()
        padding.axis.value = 2
        padding.npad.value = 448
        padding.mode.value = 'edge'

        # angles = Angles()
        # angles.nang.value=0
        # angles.ang1.value=90
        # angles.ang2.value=180


        gridrec = Recon()
        ## padding.padded.connect(gridrec.tomo)
        #read.angles.connect(gridrec.angles)
        gridrec.filter_name.value = 'butterworth'
        gridrec.algorithm.value = 'gridrec'
        gridrec.center.value = np.array([1295 + 448])  # 1295
        gridrec.filter_par.value = np.array([0.2, 2])
        # gridrec.sinogram_order.value = True

        crop = Crop()
        crop.p11.value = 448
        crop.p22.value = 448
        crop.p12.value = 448
        crop.p21.value = 448
        crop.axis.value = 0

        divide = ArrayDivide()

        circularmask = CircMask()
        circularmask.val.value = 0
        circularmask.axis.value = 0
        circularmask.ratio.value = 1

        #circularmask.recon.visualize = True

        writetiff = WriteTiffStack()

        print("------------------------------------------")
        print("------------------------------------------")
        print("------------------------------------------")
        print("------------------------------------------")

        # create connections
        g1 = Workflow()

        g1.add(norm, "norm")
        g1.add(stripe)
        g1.add(padding)
        g1.add(gridrec, "gridrec")
        g1.add(crop)
        g1.add(circularmask)
        g1.autoConnectAll()

        #self.connect(g1, norm)
        #self.connect(g1, stripe)
        #print("XYZ", g1.convertGraph(), g1.findEndTasks())

        self.add(read)
        self.add(g1)

        #print(g1.gridrec)
        #read.angles.connect(g1.gridrec.angles)

        self.connect(read, g1.norm)
        self.connect(read.angles, g1.gridrec.angles)

        self.stream(read, g1)



        print("------------------------------------------")
        print("------------------------------------------")
        print("------------------------------------------")
        print("------------------------------------------")





