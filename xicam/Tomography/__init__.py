import numpy as np
from functools import partial
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from xicam.core.data import NonDBHeader
from xicam.core import msg

from xicam.plugins import GUIPlugin, GUILayout

from xicam.gui.widgets.tabview import TabView
from xicam.gui.widgets.linearworkfloweditor import WorkflowEditor


class TomographyPlugin(GUIPlugin):
    name = 'Tomography'
    sigLog = Signal(int, str, str, np.ndarray)
    slice = 0
    multislice = 1
    preview3d = 2
    fullrecon = 3

    def __init__(self):
        from .widgets.RAWViewer import RAWViewer
        from .widgets.tomotoolbar import TomoToolbar
        from .widgets.sliceviewer import SliceViewer
        from .widgets.volumeviewer import VolumeViewer
        from .workflows.APS_2BM import Workflow
        self.workflow = Workflow()

        self.headermodel = QStandardItemModel()
        # self.alignmenttabview = TabView(self.headermodel)
        self.rawtabview = TabView(self.headermodel, widgetcls=RAWViewer, field='projection')
        self.recontabs = QTabWidget()

        self.workfloweditor = WorkflowEditor(self.workflow)
        self.workfloweditor.setHidden(True)

        self.tomotoolbar = TomoToolbar()
        self.tomotoolbar.sigSliceReconstruction.connect(self.sliceReconstruct)
        self.tomotoolbar.sigFullReconstruction.connect(self.fullReconstruction)

        self.stages = {
            'Alignment': GUILayout(QLabel('Alignment'), right=self.workfloweditor, top=self.tomotoolbar),
            'Preprocess': GUILayout(self.rawtabview, right=self.workfloweditor, top=self.tomotoolbar),
            'Reconstruct': GUILayout(self.recontabs, top=self.tomotoolbar, right=self.workfloweditor),
        }
        super(TomographyPlugin, self).__init__()

    def appendHeader(self, header: NonDBHeader, **kwargs):
        item = QStandardItem(header.startdoc.get('sample_name', '????'))
        item.header = header
        self.headermodel.appendRow(item)
        self.headermodel.dataChanged.emit(QModelIndex(), QModelIndex())

    def sliceReconstruct(self):
        currentitem = self.headermodel.item(self.rawtabview.currentIndex())
        if not currentitem: msg.showMessage('Error: You must open files before reconstructing.')
        try:
            msg.showBusy()
            msg.showMessage('Running slice reconstruction...', level=msg.INFO)
            path = self.headermodel.item(self.rawtabview.currentIndex()).header.startdoc['path']
            self.workflow.execute(None, path=path, threadkey='slicereconstruct',
                                  callback_slot=partial(self.showReconstruction, mode=self.slice),
                                  except_slot=self.exceptionCallback)
        except Exception as ex:
            msg.logError(ex)
            msg.showReady()
            msg.clearMessage()

    def fullReconstruction(self):
        from .widgets.volumeviewer import VolumeViewer
        volumeviewer = VolumeViewer()
        self.recontabs.addTab(volumeviewer, '????')

        currentitem = self.headermodel.item(self.rawtabview.currentIndex())
        if not currentitem: msg.showMessage('Error: You must open files before reconstructing.')
        try:
            msg.showBusy()
            msg.showMessage('Running slice reconstruction...', level=msg.INFO)
            currentheader = self.headermodel.item(self.rawtabview.currentIndex()).header
            readprocess = self.workflow.processes[0]  # hopefully! TODO: require a readprocess first
            readprocess.path.value = currentheader.startdoc['path']

            numofsinograms = currentheader.meta_array('primary').shape[1]

            self.workflow.execute_all(None, readprocess=range(0, int(numofsinograms), int(readprocess.chunksize.value)))

        except Exception as ex:
            msg.logError(ex)
            msg.showReady()
            msg.clearMessage()

    def exceptionCallback(self, ex):
        msg.notifyMessage("Reconstruction failed;\n see log for error")
        msg.showMessage("Reconstruction failed; see log for error")
        msg.logError(ex)
        msg.showReady()

    def showReconstruction(self, result, mode):
        print('result:', result)
        if mode == self.slice:
            from .widgets.sliceviewer import SliceViewer
            sliceviewer = SliceViewer()
            sliceviewer.setImage(list(result.values())[0].value.squeeze())
            self.recontabs.addTab(sliceviewer, '????')

        if mode == self.fullrecon:
            self.recontabs.widget(self.recontabs.count() - 1).appendData(list(result.values())[0].value[::4, ::4, ::4])
        msg.showReady()
