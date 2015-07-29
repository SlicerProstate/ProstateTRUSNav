from __main__ import vtk, qt, ctk, slicer

from GuideletLoadable import *
import logging
import os
from subprocess import Popen

class ProstateTRUSNav(GuideletLoadable):
  """Uses GuideletLoadable class, available at:
  """

  def __init__(self, parent):
    GuideletLoadable.__init__(self, parent)
    #pydevd.settrace()
    self.parent.title = "ProstateTRUSNavigation"
    self.parent.categories = ["IGT"]
    self.parent.dependencies = []
    self.parent.contributors = ["Christian Herz, Andriy Fedorov"]
    self.parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    """
    self.parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.


class ProstateTRUSNavWidget(GuideletWidget):
  """Uses GuideletWidget base class, available at:
  """

  DEFAULT_PLUSSERVER_CHOOSER_TEXT = "Choose PlusServer.exe"
  DEFAULT_CONFIGURATION_CHOOSER_TEXT = "Select Configuration"

  def __init__(self, parent = None):
    GuideletWidget.__init__(self, parent)
    self.plusServerProcess = None
    self.configurationFile = self.getSetting('ConfigurationFile', self.DEFAULT_CONFIGURATION_CHOOSER_TEXT)
    self.serverExecutable = self.getSetting('PlusServer', self.DEFAULT_PLUSSERVER_CHOOSER_TEXT)

  def setup(self):

    plusServerCollapsibleButton = ctk.ctkCollapsibleButton()
    self.layout.addWidget(plusServerCollapsibleButton)
    self.configurationFileChooserButton = qt.QPushButton(self.configurationFile)
    self.configurationFileChooserButton.connect('clicked()', self.onConfigFileSelected)
    self.runPlusServerButton = qt.QPushButton("Run PlusServer")
    self.runPlusServerButton.setCheckable(True)
    self.runPlusServerButton.connect('clicked()', self.onRunPlusServerButtonClicked)

    self.serverFormLayout = qt.QFormLayout(plusServerCollapsibleButton)

    self.serverExecutableChooserButton = qt.QPushButton(self.serverExecutable)
    self.serverExecutableChooserButton.connect('clicked()', self.onServerExecutableSelected)

    hbox = qt.QHBoxLayout()
    hbox.addWidget(self.serverExecutableChooserButton)
    self.serverFormLayout.addRow(hbox)

    hbox = qt.QHBoxLayout()
    hbox.addWidget(self.configurationFileChooserButton)
    hbox.addWidget(self.runPlusServerButton)
    self.serverFormLayout.addRow(hbox)
    # add xml selector
    # add button for launching server
    GuideletWidget.setup(self)
    # do specific setup here
    self.launchGuideletButton.setEnabled(False)

    self.checkCommandAndArgument()

  def checkCommandAndArgument(self):
    if os.path.exists(self.serverExecutable) and os.path.exists(self.configurationFile):
      self.runPlusServerButton.setEnabled(True)
    else:
      self.runPlusServerButton.setEnabled(False)

  def getSetting(self, settingName, defaultValue=""):
    settings = qt.QSettings()
    value = settings.value(self.moduleName + '/' + settingName, defaultValue)
    return value if value is not None and value != "" else defaultValue

  def setSetting(self, settingName, value):
    settings = qt.QSettings()
    settings.setValue(self.moduleName + '/'+ settingName, value)

  def addLauncherWidgets(self):
    GuideletWidget.addLauncherWidgets(self)
    # add launcher widget here

  def onServerExecutableSelected(self):
    executable = qt.QFileDialog.getOpenFileName(self.parent, "PlusServer Executable",
                                                           self.serverExecutable, "*.exe")
    if executable != "" and executable.find("PlusServer.exe"):
      self.serverExecutable = executable
      self.serverExecutableChooserButton.setText(executable)
      self.setSetting("PlusServer", executable)
    self.checkCommandAndArgument()

  def onConfigFileSelected(self):
    self.configurationFile = qt.QFileDialog.getOpenFileName(self.parent, "Choose Configuration File",
                                                            self.configurationFile, "*.xml")
    if self.configurationFile != "":
      self.configurationFileChooserButton.setText(os.path.split(self.configurationFile)[1])
      self.setSetting("ConfigurationFile", self.configurationFile)
    self.checkCommandAndArgument()

  def onRunPlusServerButtonClicked(self):
    if self.runPlusServerButton.isChecked():
      command = [self.serverExecutable, "--config-file="+self.configurationFile]
      logging.info("Executing %s %s" % tuple(command))
      self.plusServerProcess = Popen([self.serverExecutable, "--config-file="+self.configurationFile])
      if self.plusServerProcess:
        self.runPlusServerButton.setText("Quit Plus Server")
        self.launchGuideletButton.setEnabled(True)
    else:
      if self.plusServerProcess:
        self.plusServerProcess.terminate()
        self.runPlusServerButton.setText("Run PlusServer")
        self.launchGuideletButton.setEnabled(False)

  def collectParameterList(self):
    parameterList = GuideletWidget.collectParameterList(self)
    if not parameterList:
      parameterList = dict()
    parameterList['OfflineVolumeToReconstruct'] = 0,
    return parameterList

  def createGuideletInstance(self, parameterList = None):
    return ProstateTRUSNavGuidelet(None, self.guideletLogic,  parameterList)

  def createGuideletLogic(self):
    return ProstateTRUSNavLogic()


class ProstateTRUSNavLogic(GuideletLogic):
  """Uses GuideletLogic base class, available at:
  """ 

  def __init__(self, parent = None):
    GuideletLogic.__init__(self, parent)

  def createParameterNode(self):
    node = GuideletLogic.createParameterNode(self)
    parameterList = {'RecordingFilenamePrefix': "ProstateTRUSNavRecording-",
                     'RecordingFilenameExtension': ".mhd",
                     'DefaultSavedScenesPath': os.path.dirname(slicer.modules.prostatetrusnav.path)+'/SavedScenes',
                     'PivotCalibrationErrorThresholdMm':  0.9,
                     'PivotCalibrationDurationSec': 5,
                     'EnableBreachWarningLight':'True',
                     'BreachWarningLightMarginSizeMm':2.0,
                     'TestMode':'False',
                     }

    for parameter in parameterList:
      if not node.GetParameter(parameter):
        node.SetParameter(parameter, str(parameterList[parameter]))

    return node
	

class ProstateTRUSNavTest(GuideletTest):
  """This is the test case for your scripted module.
  """
  
  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    GuideletTest.runTest(self)
    #self.test_ProstateTRUSNav1() #add applet specific tests here


class ProstateTRUSNavGuidelet(Guidelet):

  @staticmethod
  def showVolumeRendering(volumeNode):
    # Display reconstructed volume in Slicer 3D view
    if not volumeNode:
      return

    # Find existing VR display node
    volumeRenderingDisplayNode = None
    for displayNodeIndex in xrange(volumeNode.GetNumberOfDisplayNodes()):
      displayNode = volumeNode.GetNthDisplayNode(displayNodeIndex)
      if displayNode.IsA('vtkMRMLVolumeRenderingDisplayNode'):
        # Found existing VR display node
        volumeRenderingDisplayNode = displayNode
        break

    # Create new VR display node if not exist yet
    if not volumeRenderingDisplayNode:
      volRenderingLogic = slicer.modules.volumerendering.logic()
      volumeRenderingDisplayNode = volRenderingLogic.CreateVolumeRenderingDisplayNode()
      slicer.mrmlScene.AddNode(volumeRenderingDisplayNode)
      volumeRenderingDisplayNode.UnRegister(volRenderingLogic)
      volRenderingLogic.UpdateDisplayNodeFromVolumeNode(volumeRenderingDisplayNode,volumeNode)
      volumeNode.AddAndObserveDisplayNodeID(volumeRenderingDisplayNode.GetID())

    volumeRenderingDisplayNode.SetVisibility(True)
    volumeRenderingWidgetRep = slicer.modules.volumerendering.widgetRepresentation()
    volumeRenderingWidgetRep.setMRMLVolumeNode(volumeNode)

  def __init__(self, parent, logic, parameterList=None, widgetClass=None):
    Guidelet.__init__(self, parent, logic, parameterList, widgetClass)
    logging.debug('ProstateTRUSNavGuidelet.__init__')

    moduleDirectoryPath = slicer.modules.prostatetrusnav.path.replace('ProstateTRUSNav.py', '')

    # Set up main frame.

    self.sliceletDockWidget.setObjectName('ProstateTRUSNavPanel')
    self.sliceletDockWidget.setWindowTitle('ProstateTRUSNav')
    
    self.mainWindow.setWindowTitle('ProstateTRUSNavigation')
    self.mainWindow.windowIcon = qt.QIcon(moduleDirectoryPath + '/Resources/Icons/ProstateTRUSNav.png')

    # Set needle and cautery transforms and models
    self.setupScene()

    # Setting button open on startup.
    self.ultrasoundCollapsibleButton.setProperty('collapsed', False)

  def getUltrasoundClass(self):
    return ProstateTRUSNavUltrasound(self)

  def createFeaturePanels(self):
    featurePanelList = Guidelet.createFeaturePanels(self)
    return featurePanelList

  def __del__(self):
    self.cleanup()

  def cleanup(self):
    Guidelet.cleanup(self)
    logging.debug('cleanup')

  def setupConnections(self):#find common connections, add specials in overridden method
    logging.debug('ProstateTRUSNav.setupConnections()')
    Guidelet.setupConnections(self)

  def disconnect(self):
    logging.debug('ProstateTRUSNav.disconnect()')
    Guidelet.disconnect(self)

  def setupScene(self): #applet specific
    logging.debug('setupScene')

    logging.debug('Create transforms')

    # Build transform tree
    logging.debug('Set up transform tree')
    
    # Hide slice view annotations (patient name, scale, color bar, etc.) as they
    # decrease reslicing performance by 20%-100%
    logging.debug('Hide slice view annotations')
    import DataProbe
    dataProbeUtil=DataProbe.DataProbeLib.DataProbeUtil()
    dataProbeParameterNode=dataProbeUtil.getParameterNode()
    dataProbeParameterNode.SetParameter('showSliceViewAnnotations', '0')

    Guidelet.setupScene(self)

  def showDefaultView(self):
    self.onViewSelect(self.viewUltrasound3d)

  def onConnectorNodeConnected(self, caller, event, force=False):
    Guidelet.onConnectorNodeConnected(self, caller, event, force)
    # setting Red light icon

  def onConnectorNodeDisconnected(self, caller, event, force=False):
    Guidelet.onConnectorNodeDisconnected(self, caller, event, force)
    # set Green light icon

  def onGetVolumeReconstructorDeviceCommandResponseReceived(self, command, q):

    if command.GetStatus() != command.CommandSuccess:
      return

    volumeReconstructorDeviceIdsListString = command.GetResponseMessage()
    if volumeReconstructorDeviceIdsListString:
      volumeReconstructorDeviceIdsList = volumeReconstructorDeviceIdsListString.split(",")
    else:
      volumeReconstructorDeviceIdsList = []

    if len(volumeReconstructorDeviceIdsList) > 0:
      self.parameterNode.SetParameter("VolumeReconstructor", str(volumeReconstructorDeviceIdsList[0]))
    # self.ultrasound.volumeReconstructorIDSelector.clear()
    # self.ultrasound.volumeReconstructorIDSelector.addItems(volumeReconstructorDeviceIdsList)


class ProstateTRUSNavUltrasound(UltraSound):

  SCOUT_VOLUME_FILENAME = "ScoutScan.mha"
  RECORDING_FILENAME = "Recording.mha"
  SCOUT_RECORDING_FILENAME = "ScoutScanRecording.mha"
  LIVE_RECORDING_FILENAME = "LiveRecording.mha"
  SCOUT_VOLUME_NODE_NAME = "ScoutScan"
  OFFLINE_VOLUME_NODE_NAME = "RecVol_Reference"
  LIVE_VOLUME_NODE_NAME = "liveReconstruction"
  APPLY_HOLE_FILLING_FOR_SNAPSHOT = False
  SNAPSHOT_INTERVAL = 1
  OUTPUT_VOLUME_SPACING = 3
  LIVE_OUTPUT_VOLUME_SPACING = 1

  @property
  def roiNode(self):
    return self._roiNode

  @roiNode.setter
  def roiNode(self, node):
    self._roiNode=node
    if node is not None:
      self.startStopLiveReconstructionButton.setEnabled(True)
    else:
      self.startStopLiveReconstructionButton.setEnabled(False)


  def __init__(self, guideletParent):
    UltraSound.__init__(self, guideletParent)

    self.parameterNode = guideletParent.parameterNode
    self.parameterNodeObserver = None
    self.connectorNode = None
    self.connectorNodeObserverTagList = []
    self.connectorNodeConnected = False
    self._roiNode = None
    self.liveOutputSpacingValue = [1.0,1.0,1.0]
    self.outputOriginValue = None
    self.outputExtentValue = None
    self.defaultParameterNode = None

  def enable(self):
    pass

  def disable(self):
    pass

  def setupPanel(self, parentWidget):

    logging.debug('UltraSound.setupPanel')
    collapsibleButton = ctk.ctkCollapsibleButton()

    collapsibleButton.setProperty('collapsedHeight', 20)
    setButtonStyle(collapsibleButton, 2.0)
    collapsibleButton.text = "Ultrasound"
    parentWidget.addWidget(collapsibleButton)

    ultrasoundLayout = qt.QFormLayout(collapsibleButton)
    ultrasoundLayout.setContentsMargins(12,4,4,4)
    ultrasoundLayout.setSpacing(4)

    self.createOpenIGTLinkSelector()
    self.connectDisconnectButton = qt.QPushButton("Connect")
    self.connectDisconnectButton.setToolTip("If clicked, connection OpenIGTLink")

    hbox = qt.QHBoxLayout()
    hbox.addWidget(self.linkInputSelector)
    hbox.addWidget(self.connectDisconnectButton)
    ultrasoundLayout.addRow(hbox)

    self.setupIcons()

    self.captureIDSelector = qt.QComboBox()
    self.captureIDSelector.setToolTip("Pick capture device ID")
    self.captureIDSelector.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)

    self.volumeReconstructorIDSelector = qt.QComboBox()
    self.volumeReconstructorIDSelector.setToolTip( "Pick volume reconstructor device ID" )
    self.volumeReconstructorIDSelector.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)

    self.startStopRecordingButton = qt.QPushButton("  Start Recording")
    self.startStopRecordingButton.setCheckable(True)
    self.startStopRecordingButton.setIcon(self.recordIcon)
    self.startStopRecordingButton.setEnabled(False)
    self.startStopRecordingButton.setToolTip("If clicked, start recording")
    self.startStopRecordingButton.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)

    recordParametersControlsLayout = qt.QGridLayout()

    self.filenameLabel = self.createLabel("Filename:", visible=False)
    recordParametersControlsLayout.addWidget(self.filenameLabel, 1, 0)

     # Offline Reconstruction
    self.offlineReconstructButton = qt.QPushButton("  Offline Reconstruction")
    self.offlineReconstructButton.setCheckable(True)
    self.offlineReconstructButton.setIcon(self.recordIcon)
    self.offlineReconstructButton.setEnabled(False)
    self.offlineReconstructButton.setToolTip("If clicked, reconstruct recorded volume")
    self.offlineReconstructButton.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)

    offlineReconstructParametersLayout = qt.QGridLayout()

    self.outputVolumeDeviceLabel = self.createLabel("Output Volume Device:", visible=False)
    offlineReconstructParametersLayout.addWidget(self.outputVolumeDeviceLabel, 1, 0)

    self.offlineVolumeToReconstructLabel = self.createLabel("Volume to Reconstruct:", visible=False)
    offlineReconstructParametersLayout.addWidget(self.offlineVolumeToReconstructLabel, 2, 0)

    self.offlineVolumeToReconstructSelector = qt.QComboBox()
    self.offlineVolumeToReconstructSelector.setEditable(True)
    self.offlineVolumeToReconstructSelector.setToolTip( "Pick/set volume to reconstruct" )
    self.offlineVolumeToReconstructSelector.visible = False
    offlineReconstructParametersLayout.addWidget(self.offlineVolumeToReconstructSelector, 2, 1)

    hbox = qt.QHBoxLayout()
    hbox.addWidget(self.startStopRecordingButton)
    hbox.addWidget(self.offlineReconstructButton)
    ultrasoundLayout.addRow(hbox)

    # Scout scan (record and low resolution reconstruction) and live reconstruction
    # Scout scan part

    self.startStopScoutScanButton = qt.QPushButton("  Scout scan\n  Start recording")
    self.startStopScoutScanButton.setCheckable(True)
    self.startStopScoutScanButton.setIcon(self.recordIcon)
    self.startStopScoutScanButton.setToolTip("If clicked, start recording")
    self.startStopScoutScanButton.setEnabled(False)
    self.startStopScoutScanButton.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)

    self.scoutScanFilenameLabel = self.createLabel("Recording filename:", visible=False)
    self.scoutScanFilenameLabel.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Minimum)

    self.scoutFilenameCompletionBox = qt.QCheckBox()
    self.scoutFilenameCompletionBox.visible = False

    self.startStopLiveReconstructionButton = qt.QPushButton("  Start live reconstruction")
    self.startStopLiveReconstructionButton.setCheckable(True)
    self.startStopLiveReconstructionButton.setIcon(self.recordIcon)
    self.startStopLiveReconstructionButton.setToolTip("If clicked, start live reconstruction")
    self.startStopLiveReconstructionButton.setEnabled(False)
    self.startStopLiveReconstructionButton.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)

    self.displayRoiButton = qt.QToolButton()
    self.displayRoiButton.setCheckable(True)
    self.displayRoiButton.setIcon(self.visibleOffIcon)
    self.displayRoiButton.setToolTip("If clicked, display ROI")

    liveReconstructionAdvancedParametersLayout = qt.QGridLayout()

    self.liveOutputVolumeDeviceLabel = self.createLabel("Output volume device: ", visible=False)
    liveReconstructionAdvancedParametersLayout.addWidget(self.liveOutputVolumeDeviceLabel, 0, 0)

    self.liveVolumeToReconstructLabel = self.createLabel("Output filename:", visible=False)
    liveReconstructionAdvancedParametersLayout.addWidget(self.liveVolumeToReconstructLabel, 1, 0)

    self.liveVolumeToReconstructFilename = qt.QLineEdit()
    self.liveVolumeToReconstructFilename.setText("LiveReconstructedVolume.mha")
    self.liveVolumeToReconstructFilename.visible = False
    self.liveVolumeToReconstructFilename.setToolTip( "Volume for live reconstruction" )
    liveReconstructionAdvancedParametersLayout.addWidget(self.liveVolumeToReconstructFilename, 1, 1)

    self.liveFilenameCompletionLabel = self.createLabel("Add timestamp to filename:", visible=False)
    liveReconstructionAdvancedParametersLayout.addWidget(self.liveFilenameCompletionLabel, 2, 0)

    self.liveFilenameCompletionBox = qt.QCheckBox()
    self.liveFilenameCompletionBox.visible = False
    liveReconstructionAdvancedParametersLayout.addWidget(self.liveFilenameCompletionBox, 2, 1)

    liveReconstructionAdvancedParametersControlsLayout = qt.QGridLayout()

    self.outputExtentLiveReconstructionLabel = self.createLabel("Extent:", visible=False)
    liveReconstructionAdvancedParametersControlsLayout.addWidget(self.outputExtentLiveReconstructionLabel, 0, 0)

    hbox = qt.QHBoxLayout()
    hbox.addWidget(self.startStopScoutScanButton)
    hbox.addWidget(self.startStopLiveReconstructionButton)
    ultrasoundLayout.addRow(hbox)

    self.outputExtentROIBoxDirection1 = qt.QDoubleSpinBox()
    self.outputExtentROIBoxDirection1.setToolTip( "Display output extent (use ROI to modify it)" )
    self.outputExtentROIBoxDirection1.setReadOnly(True)
    self.outputExtentROIBoxDirection1.setRange(0,800)
    self.outputExtentROIBoxDirection1.visible = False
    liveReconstructionAdvancedParametersControlsLayout.addWidget(self.outputExtentROIBoxDirection1, 0, 1)

    self.outputExtentROIBoxDirection2 = qt.QDoubleSpinBox()
    self.outputExtentROIBoxDirection2.setToolTip( "Display output extent (use ROI to modify it)" )
    self.outputExtentROIBoxDirection2.setReadOnly(True)
    self.outputExtentROIBoxDirection2.setRange(0,800)
    self.outputExtentROIBoxDirection2.visible = False
    liveReconstructionAdvancedParametersControlsLayout.addWidget(self.outputExtentROIBoxDirection2, 0, 2)

    self.outputExtentROIBoxDirection3 = qt.QDoubleSpinBox()
    self.outputExtentROIBoxDirection3.setToolTip( "Display output extent (use ROI to modify it)" )
    self.outputExtentROIBoxDirection3.setReadOnly(True)
    self.outputExtentROIBoxDirection3.setRange(0,800)
    self.outputExtentROIBoxDirection3.visible = False
    liveReconstructionAdvancedParametersControlsLayout.addWidget(self.outputExtentROIBoxDirection3, 0, 3)

    self.snapshotTimer = qt.QTimer()
    self.snapshotTimer.setSingleShot(True)

    self.onConnectorNodeSelected()
    # self.createDefaultParameterSet()
    self.onParameterSetSelected()

    return collapsibleButton

  def createOpenIGTLinkSelector(self):
    self.linkInputSelector = slicer.qMRMLNodeComboBox()
    self.linkInputSelector.nodeTypes = ("vtkMRMLIGTLConnectorNode", "")
    self.linkInputSelector.selectNodeUponCreation = True
    self.linkInputSelector.addEnabled = False
    self.linkInputSelector.removeEnabled = True
    self.linkInputSelector.noneEnabled = False
    self.linkInputSelector.showHidden = False
    self.linkInputSelector.showChildNodeTypes = False
    self.linkInputSelector.setMRMLScene(slicer.mrmlScene)
    self.linkInputSelector.setToolTip("Select connector node")

  def setupScene(self):
    layoutManager = slicer.app.layoutManager()

    # live ultrasound
    liveUltrasoundNodeName = self.guideletParent.parameterNode.GetParameter('LiveUltrasoundNodeName')
    self.liveUltrasoundNode_Reference = slicer.util.getNode(liveUltrasoundNodeName)
    if not self.liveUltrasoundNode_Reference:
      imageSize=[800, 600, 1]
      imageSpacing=[0.2, 0.2, 0.2]
      # Create an empty image volume
      imageData=vtk.vtkImageData()
      imageData.SetDimensions(imageSize)
      imageData.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)
      thresholder=vtk.vtkImageThreshold()
      thresholder.SetInputData(imageData)
      thresholder.SetInValue(0)
      thresholder.SetOutValue(0)
      # Create volume node
      self.liveUltrasoundNode_Reference=slicer.vtkMRMLScalarVolumeNode()
      self.liveUltrasoundNode_Reference.SetName(liveUltrasoundNodeName)
      self.liveUltrasoundNode_Reference.SetSpacing(imageSpacing)
      self.liveUltrasoundNode_Reference.SetImageDataConnection(thresholder.GetOutputPort())
      # Add volume to scene
      slicer.mrmlScene.AddNode(self.liveUltrasoundNode_Reference)
      displayNode=slicer.vtkMRMLScalarVolumeDisplayNode()
      slicer.mrmlScene.AddNode(displayNode)
      colorNode = slicer.util.getNode('Grey')
      displayNode.SetAndObserveColorNodeID(colorNode.GetID())
      self.liveUltrasoundNode_Reference.SetAndObserveDisplayNodeID(displayNode.GetID())
      #self.liveUltrasoundNode_Reference.CreateDefaultStorageNode()

    # Show ultrasound in red view.
    redSlice = layoutManager.sliceWidget('Red')
    redSliceLogic = redSlice.sliceLogic()
    redSliceLogic.GetSliceCompositeNode().SetBackgroundVolumeID(self.liveUltrasoundNode_Reference.GetID())

    # Set up volume reslice driver.
    resliceLogic = slicer.modules.volumereslicedriver.logic()
    if resliceLogic:
      redNode = slicer.util.getNode('vtkMRMLSliceNodeRed')
      # Typically the image is zoomed in, therefore it is faster if the original resolution is used
      # on the 3D slice (and also we can show the full image and not the shape and size of the 2D view)
      redNode.SetSliceResolutionMode(slicer.vtkMRMLSliceNode.SliceResolutionMatchVolumes)
      resliceLogic.SetDriverForSlice(self.liveUltrasoundNode_Reference.GetID(), redNode)
      resliceLogic.SetModeForSlice(6, redNode) # Transverse mode, default for PLUS ultrasound.
    else:
      logging.warning('Logic not found for Volume Reslice Driver')

  def createCollapsibleButton(self, text, collapsed=False):
    collapsibleButton = ctk.ctkCollapsibleButton()
    collapsibleButton.text = text
    collapsibleButton.collapsed = collapsed
    return collapsibleButton

  def createLabel(self, text, visible=True):
    label = qt.QLabel()
    label.setText(text)
    label.visible = visible
    return label

  def setupConnections(self):
    self.linkInputSelector.connect("nodeActivated(vtkMRMLNode*)", self.onConnectorNodeSelected)
    self.startStopRecordingButton.connect('clicked(bool)', self.onStartStopRecordingButtonClicked)
    self.offlineReconstructButton.connect('clicked(bool)', self.onReconstVolume)
    self.startStopScoutScanButton.connect('clicked(bool)', self.onStartStopScoutScanButtonClicked)
    self.startStopLiveReconstructionButton.connect('clicked(bool)', self.onStartStopLiveReconstructionButtonClicked)
    self.displayRoiButton.connect('clicked(bool)', self.onDisplayRoiButtonClicked)
    self.linkInputSelector.connect('currentNodeIDChanged(QString)', self.updateParameterNodeFromGui)
    self.captureIDSelector.connect('currentIndexChanged(QString)', self.updateParameterNodeFromGui)
    self.volumeReconstructorIDSelector.connect('currentIndexChanged(QString)', self.updateParameterNodeFromGui)
    self.offlineVolumeToReconstructSelector.connect('currentIndexChanged(int)', self.updateParameterNodeFromGui)
    self.scoutFilenameCompletionBox.connect('clicked(bool)', self.updateParameterNodeFromGui)
    self.displayRoiButton.connect('clicked(bool)', self.updateParameterNodeFromGui)
    self.outputExtentROIBoxDirection1.connect('valueChanged(double)', self.updateParameterNodeFromGui)
    self.outputExtentROIBoxDirection2.connect('valueChanged(double)', self.updateParameterNodeFromGui)
    self.outputExtentROIBoxDirection3.connect('valueChanged(double)', self.updateParameterNodeFromGui)
    self.liveFilenameCompletionBox.connect('clicked(bool)', self.updateParameterNodeFromGui)
    self.snapshotTimer.timeout.connect(self.onRequestVolumeReconstructionSnapshot)
    self.connectDisconnectButton.connect('clicked(bool)', self.onConnectDisconnectButtonClicked)

  def disconnect(self):
    self.linkInputSelector.disconnect("nodeActivated(vtkMRMLNode*)", self.onConnectorNodeSelected)
    self.startStopRecordingButton.disconnect('clicked(bool)', self.onStartStopRecordingButtonClicked)
    self.offlineReconstructButton.disconnect('clicked(bool)', self.onReconstVolume)
    self.startStopScoutScanButton.disconnect('clicked(bool)', self.onStartStopScoutScanButtonClicked)
    self.startStopLiveReconstructionButton.disconnect('clicked(bool)', self.onStartStopLiveReconstructionButtonClicked)
    self.displayRoiButton.disconnect('clicked(bool)', self.onDisplayRoiButtonClicked)
    self.linkInputSelector.disconnect('currentNodeIDChanged(QString)', self.updateParameterNodeFromGui)
    self.captureIDSelector.disconnect('currentIndexChanged(QString)', self.updateParameterNodeFromGui)
    self.volumeReconstructorIDSelector.disconnect('currentIndexChanged(QString)', self.updateParameterNodeFromGui)
    self.offlineVolumeToReconstructSelector.disconnect('currentIndexChanged(int)', self.updateParameterNodeFromGui)
    self.scoutFilenameCompletionBox.disconnect('clicked(bool)', self.updateParameterNodeFromGui)
    self.displayRoiButton.disconnect('clicked(bool)', self.updateParameterNodeFromGui)
    self.outputExtentROIBoxDirection1.disconnect('valueChanged(double)', self.updateParameterNodeFromGui)
    self.outputExtentROIBoxDirection2.disconnect('valueChanged(double)', self.updateParameterNodeFromGui)
    self.outputExtentROIBoxDirection3.disconnect('valueChanged(double)', self.updateParameterNodeFromGui)
    self.liveFilenameCompletionBox.disconnect('clicked(bool)', self.updateParameterNodeFromGui)
    self.snapshotTimer.timeout.disconnect(self.onRequestVolumeReconstructionSnapshot)
    self.connectDisconnectButton.disconnect('clicked(bool)', self.onConnectDisconnectButtonClicked)

  def setupIcons(self):
    self.plusRemoteModuleDirectoryPath = slicer.modules.plusremote.path.replace("PlusRemote.py", "")
    self.recordIcon = qt.QIcon(self.plusRemoteModuleDirectoryPath + '/Resources/Icons/icon_Record.png')
    self.stopIcon = qt.QIcon(self.plusRemoteModuleDirectoryPath + '/Resources/Icons/icon_Stop.png')
    self.waitIcon = qt.QIcon(self.plusRemoteModuleDirectoryPath + '/Resources/Icons/icon_Wait.png')
    self.visibleOffIcon = qt.QIcon(":Icons\VisibleOff.png")
    self.visibleOnIcon = qt.QIcon(":Icons\VisibleOn.png")

  def onParameterSetSelected(self):
    if self.parameterNode and self.parameterNodeObserver:
      self.parameterNode.RemoveObserver(self.parameterNodeObserver)
      self.parameterNodeObserver = self.parameterNode.AddObserver('currentNodeChanged(vtkMRMLNode*)',
                                                                  self.updateGuiFromParameterNode)
    # Set up default values for new nodes
    if self.parameterNode:
      self.plusRemoteLogic.setDefaultParameters(self.parameterNode)
    self.updateGuiFromParameterNode()

  def updateGuiFromParameterNode(self):
    self.parameterValueList = {'RoiExtent1': self.outputExtentROIBoxDirection1,
                               'RoiExtent2': self.outputExtentROIBoxDirection2,
                               'RoiExtent3': self.outputExtentROIBoxDirection3}
    for parameter in self.parameterValueList:
      if self.parameterNode.GetParameter(parameter):
        #Block Signal to avoid call of updateParameterNodeFromGui when parameter is set programmatically - we only want to catch when user change values
        self.parameterValueList[parameter].blockSignals(True)
        self.parameterValueList[parameter].setValue(float(self.parameterNode.GetParameter(parameter)))
      self.parameterValueList[parameter].blockSignals(False)

    self.parameterCheckBoxList = {'RoiDisplay': self.displayRoiButton,
                                  'ScoutFilenameCompletion': self.scoutFilenameCompletionBox,
                                  'LiveFilenameCompletion': self.liveFilenameCompletionBox}
    for parameter in self.parameterCheckBoxList:
      if self.parameterNode.GetParameter(parameter):
        self.parameterCheckBoxList[parameter].blockSignals(True)
        if self.parameterNode.GetParameter(parameter) == "True":
          self.parameterCheckBoxList[parameter].setChecked(True)
        else:
          self.parameterCheckBoxList[parameter].setChecked(False)
      self.parameterCheckBoxList[parameter].blockSignals(False)
      self.onDisplayRoiButtonClicked()

    self.parameterVolumeList = {'OfflineVolumeToReconstruct': self.offlineVolumeToReconstructSelector}
    for parameter in self.parameterVolumeList:
      if self.parameterNode.GetParameter(parameter):
        self.parameterVolumeList[parameter].blockSignals(True)
        # self.parameterVolumeList[parameter].setCurrentIndex(int(self.parameterNode.GetParameter(parameter)))
      self.parameterVolumeList[parameter].blockSignals(False)

    self.parameterNodesList = {'OpenIGTLinkConnector': self.linkInputSelector}
    for parameter in self.parameterNodesList:
      if self.parameterNode.GetParameter(parameter):
        self.parameterNodesList[parameter].blockSignals(True)
        self.parameterNodesList[parameter].setCurrentNodeID(self.parameterNode.GetParameter(parameter))
      self.parameterNodesList[parameter].blockSignals(False)

    if self.parameterNode.GetParameter('CaptureID'):
      self.captureIDSelector.blockSignals(True)
      for i in range(0, self.captureIDSelector.count):
        if self.parameterNode.GetParameter('CaptureID') == self.captureIDSelector.itemText(i):
          self.captureIDSelector.setCurrentIndex(int(self.parameterNode.GetParameter('CaptureIdIndex')))
      self.captureIDSelector.blockSignals(False)

    if self.parameterNode.GetParameter('VolumeReconstructor'):
      self.volumeReconstructorIDSelector.blockSignals(True)
      for i in range(0, self.volumeReconstructorIDSelector.count):
        if self.parameterNode.GetParameter('VolumeReconstructor') == self.volumeReconstructorIDSelector.itemText(i):
          self.volumeReconstructorIDSelector.setCurrentIndex(int(self.parameterNode.GetParameter('VolumeReconstructorIndex')))
      self.volumeReconstructorIDSelector.blockSignals(False)

      self.roiNode = self.parameterNode.GetNthNodeReference('ROI', 0)

  def updateParameterNodeFromGui(self):
    #Update parameter node value to save when user change value in the interface
    if not self.parameterNode:
      return
    self.parametersList = {'OpenIGTLinkConnector': self.linkInputSelector.currentNodeID,
                           'CaptureID': self.captureIDSelector.currentText,
                           'CaptureIdIndex': self.captureIDSelector.currentIndex,
                           'VolumeReconstructor': self.volumeReconstructorIDSelector.currentText,
                           'VolumeReconstructorIndex': self.volumeReconstructorIDSelector.currentIndex,
                           'RoiDisplay': self.displayRoiButton.isChecked(),
                           'RoiExtent1': self.outputExtentROIBoxDirection1.value,
                           'RoiExtent2': self.outputExtentROIBoxDirection2.value,
                           'RoiExtent3': self.outputExtentROIBoxDirection3.value,
                           'OfflineVolumeToReconstruct': self.offlineVolumeToReconstructSelector.currentIndex,
                           'ScoutFilenameCompletion': self.scoutFilenameCompletionBox.isChecked(),
                           'LiveFilenameCompletion': self.liveFilenameCompletionBox.isChecked()}
    for parameter in self.parametersList:
      self.parameterNode.SetParameter(parameter, str(self.parametersList[parameter]))
    if self.roiNode:
      roiNodeID = self.roiNode.GetID()
      self.parameterNode.SetNthNodeReferenceID('ROI', 0, roiNodeID)

#
# Connector observation and actions
#
  def onConnectorNodeSelected(self):
    if self.connectorNode and self.connectorNodeObserverTagList:
      for tag in self.connectorNodeObserverTagList:
        self.connectorNode.RemoveObserver(tag)
      self.connectorNodeObserverTagList = []

    self.connectorNode = self.linkInputSelector.currentNode()

    if self.connectorNode:
      if self.connectorNode.GetState() == slicer.vtkMRMLIGTLConnectorNode.STATE_CONNECTED:
        self.onConnectorNodeConnected(None, None, True)
      else:
        self.onConnectorNodeDisconnected(None, None, True)

      # Add observers for connect/disconnect events
      events = [[slicer.vtkMRMLIGTLConnectorNode.ConnectedEvent, self.onConnectorNodeConnected],
                [slicer.vtkMRMLIGTLConnectorNode.DisconnectedEvent, self.onConnectorNodeDisconnected]]
      for tagEventHandler in events:
        connectorNodeObserverTag = self.connectorNode.AddObserver(tagEventHandler[0], tagEventHandler[1])
        self.connectorNodeObserverTagList.append(connectorNodeObserverTag)

  def onConnectorNodeConnected(self, caller, event, force=False):
    # Multiple notifications may be sent when connecting/disconnecting,
    # so we just if we know about the state change already
    if self.connectorNodeConnected and not force:
        return
    self.connectorNodeConnected = True
    self.captureIDSelector.setDisabled(False)
    self.volumeReconstructorIDSelector.setDisabled(False)
    self.plusRemoteLogic.getCaptureDeviceIds(self.linkInputSelector.currentNode().GetID(),
                                   self.onGetCaptureDeviceCommandResponseReceived)
    self.plusRemoteLogic.getVolumeReconstructorDeviceIds(self.linkInputSelector.currentNode().GetID(),
                                               self.onGetVolumeReconstructorDeviceCommandResponseReceived)
    self.connectDisconnectButton.setText("Disconnect")

  def onConnectorNodeDisconnected(self, caller, event, force=False):
    # Multiple notifications may be sent when connecting/disconnecting,
    # so we just if we know about the state change already
    if not self.connectorNodeConnected  and not force:
        return
    self.connectorNodeConnected = False
    self.startStopRecordingButton.setEnabled(False)
    self.startStopScoutScanButton.setEnabled(False)
    self.startStopLiveReconstructionButton.setEnabled(False)
    self.offlineReconstructButton.setEnabled(False)
    self.captureIDSelector.setDisabled(True)
    self.volumeReconstructorIDSelector.setDisabled(True)
    self.connectDisconnectButton.setText("Connect")

  def getLiveVolumeRecNode(self):
    liveVolumeRecNode = slicer.util.getNode(self.LIVE_VOLUME_NODE_NAME)
    return liveVolumeRecNode

  def getOfflineVolumeRecNode(self):
    offlineVolumeRecNode = slicer.util.getNode(self.OFFLINE_VOLUME_NODE_NAME)
    return offlineVolumeRecNode

  def getScoutVolumeNode(self):
    scoutScanVolumeNode = slicer.util.getNode(self.SCOUT_VOLUME_NODE_NAME)
    return scoutScanVolumeNode

#
# Functions called when commands/setting buttons are clicked
#
  # 1 - Commands buttons
  def onConnectDisconnectButtonClicked(self):
    if self.connectorNode.GetState() == slicer.vtkMRMLIGTLConnectorNode.STATE_CONNECTED:
      self.connectorNode.Stop()
    else:
      self.connectorNode.Start()

  def onStartStopRecordingButtonClicked(self):
    if self.startStopRecordingButton.isChecked():
      self.startStopRecordingButton.setText("  Stop Recording")
      self.startStopRecordingButton.setIcon(self.stopIcon)
      self.startStopRecordingButton.setToolTip( "If clicked, stop recording" )
      self.onStartRecording(self.generateRecordingOutputFilename())
    else:
      self.startStopRecordingButton.setText("  Start Recording")
      self.startStopRecordingButton.setIcon(self.recordIcon)
      self.startStopRecordingButton.setToolTip( "If clicked, start recording" )
      self.onStopRecording(self.onVolumeRecorded)

  def onStartStopScoutScanButtonClicked(self):
    if self.startStopScoutScanButton.isChecked():
      self.startStopScoutScanButton.setText("  Scout Scan\n  Stop Recording and Reconstruct Recorded Volume")
      self.startStopScoutScanButton.setIcon(self.stopIcon)
      self.startStopScoutScanButton.setToolTip( "If clicked, stop recording and reconstruct recorded volume" )
      self.onStartRecording(self.generateScoutRecordingOutputFilename())
    else:
      self.onStopRecording(self.onScoutVolumeRecorded)

  def onStartStopLiveReconstructionButtonClicked(self):
    if self.startStopLiveReconstructionButton.isChecked():
      if self.roiNode:
        self.updateVolumeExtentFromROI()
      self.startStopLiveReconstructionButton.setText("  Stop Live Reconstruction")
      self.startStopLiveReconstructionButton.setIcon(self.stopIcon)
      self.startStopLiveReconstructionButton.setToolTip( "If clicked, stop live reconstruction" )
      self.onStartRecording(self.getLiveRecordingOutputFilename())
      self.onStartReconstruction()
    else:
      self.startStopLiveReconstructionButton.setText("  Start Live Reconstruction")
      self.startStopLiveReconstructionButton.setIcon(self.recordIcon)
      self.startStopLiveReconstructionButton.setToolTip( "If clicked, start live reconstruction" )
      self.onStopRecording(self.printCommandResponse)
      self.onStopReconstruction()

  def onDisplayRoiButtonClicked(self):
    if self.displayRoiButton.isChecked():
      self.displayRoiButton.setIcon(self.visibleOnIcon)
      self.displayRoiButton.setToolTip("If clicked, hide ROI")
      if self.roiNode:
        self.roiNode.SetDisplayVisibility(1)
    else:
      self.displayRoiButton.setIcon(self.visibleOffIcon)
      self.displayRoiButton.setToolTip("If clicked, display ROI")
      if self.roiNode:
        self.roiNode.SetDisplayVisibility(0)

#
# Filenames completion
#
  def generateRecordingOutputFilename(self):
    return self.plusRemoteLogic.addTimestampToFilename(self.RECORDING_FILENAME)

  def generateScoutRecordingOutputFilename(self):
    return self.plusRemoteLogic.addTimestampToFilename(self.SCOUT_RECORDING_FILENAME)

  def getLiveRecordingOutputFilename(self):
    return self.plusRemoteLogic.addTimestampToFilename(self.LIVE_RECORDING_FILENAME)

  def getLiveReconstructionOutputFilename(self):
    return self.plusRemoteLogic.addTimestampToFilename(self.liveVolumeToReconstructFilename.text)

#
# Commands
#
  def onStartRecording(self, filename):
    self.plusRemoteLogic.startRecording(self.linkInputSelector.currentNode().GetID(), self.captureIDSelector.currentText,
                              filename, self.printCommandResponse)

  def onStopRecording(self, callback):
    self.plusRemoteLogic.stopRecording(self.linkInputSelector.currentNode().GetID(), self.captureIDSelector.currentText,
                             callback)

  def onStartReconstruction(self):
    if self.roiNode:
      self.updateVolumeExtentFromROI()
    self.plusRemoteLogic.startVolumeReconstuction(self.linkInputSelector.currentNode().GetID(),
                                         self.volumeReconstructorIDSelector.currentText,
                                         self.liveOutputSpacingValue, self.outputOriginValue,
                                         self.outputExtentValue, self.printCommandResponse,
                                         self.getLiveReconstructionOutputFilename(), self.LIVE_VOLUME_NODE_NAME)
    # Set up timer for requesting snapshot
    self.snapshotTimer.start(self.SNAPSHOT_INTERVAL*1000)

  def onStopReconstruction(self):
    self.snapshotTimer.stop()
    self.plusRemoteLogic.stopVolumeReconstruction(self.linkInputSelector.currentNode().GetID(),
                                        self.volumeReconstructorIDSelector.currentText, self.onVolumeLiveReconstructed,
                                        self.getLiveReconstructionOutputFilename(), self.LIVE_VOLUME_NODE_NAME)

  def onReconstVolume(self):
    self.offlineReconstructButton.setIcon(self.waitIcon)
    self.offlineReconstructButton.setText("  Offline Reconstruction in progress ...")
    self.offlineReconstructButton.setEnabled(False)
    outputSpacing = [self.OUTPUT_VOLUME_SPACING, self.OUTPUT_VOLUME_SPACING, self.OUTPUT_VOLUME_SPACING]
    self.plusRemoteLogic.reconstructRecorded(self.linkInputSelector.currentNode().GetID(), self.volumeReconstructorIDSelector.currentText,
                                   self.offlineVolumeToReconstructSelector.currentText, outputSpacing, self.onVolumeReconstructed,
                                   "RecVol_Reference.mha", self.OFFLINE_VOLUME_NODE_NAME)

  def onScoutScanReconstVolume(self):
    self.startStopScoutScanButton.setIcon(self.waitIcon)
    self.startStopScoutScanButton.setText("  Scout Scan\n  Reconstruction in progress ...")
    self.startStopScoutScanButton.setEnabled(False)
    outputSpacing = [self.OUTPUT_VOLUME_SPACING, self.OUTPUT_VOLUME_SPACING, self.OUTPUT_VOLUME_SPACING]
    self.plusRemoteLogic.reconstructRecorded(self.linkInputSelector.currentNode().GetID(), self.volumeReconstructorIDSelector.currentText,
                                             self.lastScoutRecordingOutputFilename, outputSpacing, self.onScoutVolumeReconstructed,
                                             self.SCOUT_VOLUME_FILENAME, self.SCOUT_VOLUME_NODE_NAME)

  def onRequestVolumeReconstructionSnapshot(self, stopFlag = ""):
    self.plusRemoteLogic.getVolumeReconstructionSnapshot(self.linkInputSelector.currentNode().GetID(),
                                                         self.volumeReconstructorIDSelector.currentText,
                                                         self.liveVolumeToReconstructFilename.text,
                                                         self.LIVE_VOLUME_NODE_NAME,
                                                         self.APPLY_HOLE_FILLING_FOR_SNAPSHOT, self.onSnapshotAcquired)

#
# Functions associated to commands
#
  def printCommandResponse(self, command, q):
    statusText = "Command {0} [{1}]: {2}\n".format(command.GetCommandName(), command.GetID(), command.StatusToString(command.GetStatus()))
    if command.GetResponseMessage():
      statusText = statusText + command.GetResponseMessage()
    elif command.GetResponseText():
      statusText = statusText + command.GetResponseText()
    print statusText

  def onGetCaptureDeviceCommandResponseReceived(self, command, q):
    self.printCommandResponse(command, q)
    if command.GetStatus() != command.CommandSuccess:
      return

    captureDeviceIdsListString = command.GetResponseMessage()
    if captureDeviceIdsListString:
      captureDevicesIdsList = captureDeviceIdsListString.split(",")
    else:
      captureDevicesIdsList = []

    for i in range(0,len(captureDevicesIdsList)):
      if self.captureIDSelector.findText(captureDevicesIdsList[i]) == -1:
        self.captureIDSelector.addItem(captureDevicesIdsList[i])

  def onGetVolumeReconstructorDeviceCommandResponseReceived(self, command, q):
    self.printCommandResponse(command, q)
    if command.GetStatus() != command.CommandSuccess:
      return

    volumeReconstructorDeviceIdsListString = command.GetResponseMessage()
    if volumeReconstructorDeviceIdsListString:
      volumeReconstructorDeviceIdsList = volumeReconstructorDeviceIdsListString.split(",")
    else:
      volumeReconstructorDeviceIdsList = []

    self.volumeReconstructorIDSelector.clear()
    self.volumeReconstructorIDSelector.addItems(volumeReconstructorDeviceIdsList)
    self.startStopRecordingButton.setEnabled(True)
    self.offlineReconstructButton.setEnabled(True)
    self.startStopScoutScanButton.setEnabled(True)
    if self.roiNode:
      self.startStopLiveReconstructionButton.setEnabled(True)

  def onVolumeRecorded(self, command, q):
    self.printCommandResponse(command, q)
    self.offlineReconstructButton.setEnabled(True)

    volumeToReconstructFileName = os.path.basename(command.GetResponseMessage())
    self.offlineVolumeToReconstructSelector.insertItem(0,volumeToReconstructFileName)
    self.offlineVolumeToReconstructSelector.setCurrentIndex(0)

  def onScoutVolumeRecorded(self, command, q):
    self.printCommandResponse(command,q)
    self.offlineReconstructButton.setEnabled(True)

    if command.GetStatus() == command.CommandExpired:
      print "Scout Volume Recording: Timeout while waiting for volume reconstruction result"
      return

    if command.GetStatus() == command.CommandSuccess:
      self.lastScoutRecordingOutputFilename = os.path.basename(command.GetResponseMessage())
      self.onScoutScanReconstVolume()

  def onVolumeReconstructed(self, command, q):
    self.printCommandResponse(command,q)

    self.offlineReconstructButton.setIcon(self.recordIcon)
    self.offlineReconstructButton.setText("Offline Reconstruction")
    self.offlineReconstructButton.setEnabled(True)
    self.offlineReconstructButton.setChecked(False)

    if command.GetStatus() == command.CommandExpired:
      # volume reconstruction command timed out
      print "Volume Reconstruction: Timeout while waiting for volume reconstruction result"
      return

    if command.GetStatus() != command.CommandSuccess:
      print "Volume Reconstruction: " + command.GetResponseMessage()
      return

    qt.QTimer.singleShot(100, self.onVolumeReconstructedFinalize)

  def onVolumeReconstructedFinalize(self):
    applicationLogic = slicer.app.applicationLogic()
    applicationLogic.FitSliceToAll()
    self.guideletParent.showVolumeRendering(self.getOfflineVolumeRecNode())

  def onScoutVolumeReconstructed(self, command, q):
    self.printCommandResponse(command,q)

    if command.GetStatus() == command.CommandExpired:
      print "Scout Volume Reconstruction: Timeout while waiting for scout volume reconstruction result"
      return

    self.startStopScoutScanButton.setIcon(self.recordIcon)
    self.startStopScoutScanButton.setText("  Scout Scan\n  Start Recording")
    self.startStopScoutScanButton.setEnabled(True)

    if command.GetStatus() != command.CommandSuccess:
      print "Scout Volume Reconstruction: " + command.GetResponseMessage()
      return

    scoutScanReconstructFileName = os.path.basename(command.GetResponseMessage())

    # Order of OpenIGTLink message receiving and processing is not guaranteed to be the same
    # therefore we wait a bit to make sure the image message is processed as well
    qt.QTimer.singleShot(100, self.onScoutVolumeReconstructedFinalize)

  def onScoutVolumeReconstructedFinalize(self):
    #Create and initialize ROI after scout scan because low resolution scout scan is used to set a smaller ROI for the live high resolution reconstruction
    self.onRoiInitialization()

    # if self.showScoutReconstructionResultOnCompletionCheckBox.isChecked():
    scoutScanVolumeNode = self.getScoutVolumeNode()

    scoutVolumeDisplay = scoutScanVolumeNode.GetDisplayNode()
    self.scoutWindow = scoutVolumeDisplay.GetWindow()
    self.scoutLevel = scoutVolumeDisplay.GetLevel()

    applicationLogic = slicer.app.applicationLogic()
    applicationLogic.FitSliceToAll()

    #3D view
    self.guideletParent.showVolumeRendering(scoutScanVolumeNode)

  def onSnapshotAcquired(self, command, q):
    self.printCommandResponse(command,q)

    if not self.startStopLiveReconstructionButton.isChecked():
      # live volume reconstruction is not active
      return

    # Order of OpenIGTLink message receiving and processing is not guaranteed to be the same
    # therefore we wait a bit to make sure the image message is processed as well
    qt.QTimer.singleShot(100, self.onSnapshotAcquiredFinalize)

  def onSnapshotAcquiredFinalize(self):
    self.guideletParent.showVolumeRendering(self.getLiveVolumeRecNode())
    self.snapshotTimer.start(self.SNAPSHOT_INTERVAL*1000)

  def onVolumeLiveReconstructed(self, command, q):
    self.printCommandResponse(command,q)

    if command.GetStatus() == command.CommandExpired:
      print "LIVE Volume Reconstruction: Failed to stop volume reconstruction"
      return

    if command.GetStatus() != command.CommandSuccess:
      print "LIVE Volume Reconstruction " + command.GetResponseMessage()
      return

    # Order of OpenIGTLink message receiving and processing is not guaranteed to be the same
    # therefore we wait a bit to make sure the image message is processed as well
    qt.QTimer.singleShot(100, self.onVolumeLiveReconstructedFinalize)

  def onVolumeLiveReconstructedFinalize(self):
    self.guideletParent.showVolumeRendering(self.getLiveVolumeRecNode())

#
# ROI initialization and update
#

  def onRoiInitialization(self):
    reconstructedNode = slicer.mrmlScene.GetNodesByName(self.SCOUT_VOLUME_NODE_NAME)
    reconstructedVolumeNode = slicer.vtkMRMLScalarVolumeNode.SafeDownCast(reconstructedNode.GetItemAsObject(0))

    roiCenterInit = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    roiRadiusInit = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    bounds = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    #ROI is initialized to fit scout scan reconstructed volume
    if reconstructedVolumeNode:
      reconstructedVolumeNode.GetRASBounds(bounds)
      for i in range(0,5,2):
        roiCenterInit[i] = (bounds[i+1] + bounds[i])/2
        roiRadiusInit[i] = (bounds[i+1] - bounds[i])/2
      if self.roiNode:
        self.roiNode.SetXYZ(roiCenterInit[0], roiCenterInit[2], roiCenterInit[4])
        self.roiNode.SetRadiusXYZ(roiRadiusInit[0], roiRadiusInit[2], roiRadiusInit[4])
      else:
        self.roiNode = slicer.vtkMRMLAnnotationROINode()
        self.roiNode.SetXYZ(roiCenterInit[0], roiCenterInit[2], roiCenterInit[4])
        self.roiNode.SetRadiusXYZ(roiRadiusInit[0], roiRadiusInit[2], roiRadiusInit[4])
        self.roiNode.Initialize(slicer.mrmlScene)
        self.roiNode.SetDisplayVisibility(0)
        self.roiNode.SetInteractiveMode(1)
    self.updateVolumeExtentFromROI()

  def updateVolumeExtentFromROI(self):
    #Update volume extent values each time user modifies the ROI, as we want volume to fit ROI for live reconstruction
    roiCenter = [0.0, 0.0, 0.0]
    roiRadius = [0.0, 0.0, 0.0]
    roiOrigin = [0.0, 0.0, 0.0]
    if self.roiNode:
      self.roiNode.GetXYZ(roiCenter)
      self.roiNode.GetRadiusXYZ(roiRadius)

    for i in range(0,len(roiCenter)):
        roiOrigin[i] = roiCenter[i] - roiRadius[i]
    self.outputOriginValue = roiOrigin
    #Radius in mm, extent in pixel
    self.outputExtentValue = [0, int((2*roiRadius[0])/self.LIVE_OUTPUT_VOLUME_SPACING), 0,
                              int((2*roiRadius[1])/self.LIVE_OUTPUT_VOLUME_SPACING), 0,
                              int((2*roiRadius[2])/self.LIVE_OUTPUT_VOLUME_SPACING)]
    self.liveOutputSpacingValue = [self.LIVE_OUTPUT_VOLUME_SPACING,
                                   self.LIVE_OUTPUT_VOLUME_SPACING,
                                   self.LIVE_OUTPUT_VOLUME_SPACING]

    self.outputExtentROIBoxDirection1.value = self.outputExtentValue[1]
    self.outputExtentROIBoxDirection2.value = self.outputExtentValue[3]
    self.outputExtentROIBoxDirection3.value = self.outputExtentValue[5]