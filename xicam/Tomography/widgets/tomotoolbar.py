from qtpy.QtWidgets import *
from qtpy.QtGui import *
from qtpy.QtCore import *

from xicam.gui.static import path


class TomoToolbar(QToolBar):
    sigFullReconstruction = Signal()
    sigSliceReconstruction = Signal()
    sigMultiSliceReconstruction = Signal()
    sig3DPreviewReconstruction = Signal()

    def __init__(self, parent=None):
        super(TomoToolbar, self).__init__(parent)

        self.addAction(QIcon(path('icons/run.png')), 'Full Reconstruction', self.sigFullReconstruction.emit)
        self.addAction(QIcon(path('icons/slice.png')), 'Slice Reconstruction', self.sigSliceReconstruction.emit)
        self.addAction(QIcon(path('icons/multislice.png')), 'Multi-Slice Reconstruction',
                       self.sigMultiSliceReconstruction.emit)
        self.addAction(QIcon(path('icons/3dpreview.png')), '3D Preview Reconstruction',
                       self.sig3DPreviewReconstruction.emit)
