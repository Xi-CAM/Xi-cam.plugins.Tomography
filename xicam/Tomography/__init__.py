import numpy as np
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from xicam.core import msg
from xicam.core.data import load_header, NonDBHeader
from xicam.core.execution.workflow import Workflow

from xicam.plugins import GUIPlugin, GUILayout, manager as pluginmanager
from xicam.plugins.GUIPlugin import PanelState

from xicam.gui.widgets.tabview import TabView
from xicam.gui.widgets.linearworkfloweditor import WorkflowEditor


class TomographyPlugin(GUIPlugin):
    name = 'Tomography'
    sigLog = Signal(int, str, str, np.ndarray)

    def __init__(self):
        self.workflow = Workflow()

        self.headermodel = QStandardItemModel()
        self.alignmenttabview = TabView()
        self.alignmenttabview.setModel(self.headermodel)
        # self.alignmenttabview.setWidgetClass(AlignmentViewer)
        # self.toolbar = SAXSToolbar(self.tabview)

        self.stages = {
            'Alignment': GUILayout(self.alignmenttabview, left=WorkflowEditor(self.workflow),
                                   lefttop=PanelState.Disabled),
            'Preprocess': GUILayout(QLabel('Preprocess')),
            'Reconstruct': GUILayout(QLabel('Reconstruct'), ),
        }
        super(TomographyPlugin, self).__init__()

    def appendHeader(self, header: NonDBHeader, **kwargs):
        item = QStandardItem('???')
        item.header = header
        self.headermodel.appendRow(item)
        self.headermodel.dataChanged.emit(QModelIndex(), QModelIndex())
