import numpy as np
from functools import partial
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from xicam.core.data import load_header, NonDBHeader
from xicam.core.execution.workflow import Workflow
from xicam.core import msg

from xicam.plugins import GUIPlugin, GUILayout, manager as pluginmanager
from xicam.plugins.GUIPlugin import PanelState

from xicam.gui.threads import QThreadFuture
from xicam.gui.widgets.tabview import TabView
from xicam.gui.widgets.linearworkfloweditor import WorkflowEditor
from .widgets.RAWViewer import RAWViewer
from .widgets.tomotoolbar import TomoToolbar
from .widgets.sliceviewer import SliceViewer

from .workflows.APS_2BM import Workflow


class TomographyPlugin(GUIPlugin):
    name = 'Tomography'
    sigLog = Signal(int, str, str, np.ndarray)
    slice = 0
    multislice = 1
    preview3d = 2
    fullrecon = 3

    def __init__(self):
        self.workflow = Workflow()

        self.headermodel = QStandardItemModel()
        # self.alignmenttabview = TabView(self.headermodel)
        self.rawtabview = TabView(self.headermodel, widgetcls=RAWViewer, field='projection')
        self.recontabs = QTabWidget()

        self.workfloweditor = WorkflowEditor(self.workflow)
        self.workfloweditor.setHidden(True)

        self.tomotoolbar = TomoToolbar()
        self.tomotoolbar.sigSliceReconstruction.connect(self.sliceReconstruct)

        self.stages = {
            'Alignment': GUILayout(QLabel('Alignment'), right=self.workfloweditor, top=self.tomotoolbar),
            'Preprocess': GUILayout(self.rawtabview, right=self.workfloweditor, top=self.tomotoolbar),
            'Reconstruct': GUILayout(self.recontabs, top=self.tomotoolbar),
        }
        super(TomographyPlugin, self).__init__()

    def appendHeader(self, header: NonDBHeader, **kwargs):
        item = QStandardItem(header.startdoc.get('sample_name', '????'))
        item.header = header
        self.headermodel.appendRow(item)
        self.headermodel.dataChanged.emit(QModelIndex(), QModelIndex())

    def sliceReconstruct(self):
        msg.showBusy()
        msg.showMessage('Running slice reconstruction...', level=msg.INFO)
        self._reconthread = QThreadFuture(self.workflow.execute, (None,),
                                          callback_slot=partial(self.showReconstruction, mode=self.slice))
        self._reconthread.start()

    def showReconstruction(self, result, mode):
        if mode == self.slice:
            sliceviewer = SliceViewer()
            sliceviewer.setImage(list(result[0].values())[0].value)
            self.recontabs.addTab(sliceviewer, '????')
        msg.showReady()
