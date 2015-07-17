import os
import unittest
from __main__ import vtk, qt, ctk, slicer

from GuideletLib import *
import logging
import time

#
# ProstateTrusNav ###
#

class ProstateTrusNav(GuideletLoadable):
  """Uses GuideletLoadable class, available at:
  """

  def __init__(self, parent):
    GuideletLoadable.__init__(self, parent)
    #pydevd.settrace()
    self.parent.title = "ProstateTrusNavigation"
    self.parent.categories = ["IGT"]
    self.parent.dependencies = []
    self.parent.contributors = [""]
    self.parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    """
    self.parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# ProstateTrusNavWidget
#

class ProstateTrusNavWidget(GuideletWidget):
  """Uses GuideletWidget base class, available at:
  """

  def __init__(self, parent = None):
    GuideletWidget.__init__(self, parent)
    # do specific init here

  def setup(self):
    GuideletWidget.setup(self)
    # do specific setup here

  def addLauncherWidgets(self):
    GuideletWidget.addLauncherWidgets(self)
    # add launcher widget here

  def collectParameterList(self):
    parameterlist = GuideletWidget.collectParameterList(self)
    # collect parameters here
    return parameterlist

  def createGuideletInstance(self, parameterList = None):
    return ProstateTrusNavGuidelet(None, self.guideletLogic,  parameterList)

  def createGuideletLogic(self):
    return ProstateTrusNavLogic()

#
# ProstateTrusNavLogic ###
#

class ProstateTrusNavLogic(GuideletLogic):
  """Uses GuideletLogic base class, available at:
  """ 

  def __init__(self, parent = None):
    GuideletLogic.__init__(self, parent)

  def createParameterNode(self):
    node = GuideletLogic.createParameterNode(self)
    parameterList = {'RecordingFilenamePrefix': "ProstateTrusNavRecording-",
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
	
#	
#	ProstateTrusNavTest ###
#

class ProstateTrusNavTest(GuideletTest):
  """This is the test case for your scripted module.
  """
  
  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    GuideletTest.runTest(self)
    #self.test_ProstateTrusNav1() #add applet specific tests here

class ProstateTrusNavGuidelet(Guidelet):

  def __init__(self, parent, logic, parameterList=None, widgetClass=None):
    Guidelet.__init__(self, parent, logic, parameterList, widgetClass)
    logging.debug('ProstateTrusNavGuidelet.__init__')

    moduleDirectoryPath = slicer.modules.prostatetrusnav.path.replace('ProstateTrusNav.py', '')

    # Set up main frame.

    self.sliceletDockWidget.setObjectName('ProstateTrusNavPanel')
    self.sliceletDockWidget.setWindowTitle('ProstateTrusNav')
    
    self.mainWindow.setWindowTitle('ProstateTrusNavigation')
    self.mainWindow.windowIcon = qt.QIcon(moduleDirectoryPath + '/Resources/Icons/ProstateTrusNav.png')

    self.addConnectorObservers()
    
    # Setting up callback functions for widgets.
    self.setupConnections()
    
    # Set needle and cautery transforms and models
    self.setupScene()

    # Setting button open on startup.
    self.ultrasoundCollapsibleButton.setProperty('collapsed', False)

    self.showFullScreen()

  def createFeaturePanels(self):
    featurePanelList = Guidelet.createFeaturePanels(self)

    return featurePanelList

  def __del__(self):
    self.cleanup()

  # Clean up when slicelet is closed
  def cleanup(self):
    Guidelet.cleanup(self)
    logging.debug('cleanup')
    
  #   button.setStyleSheet(style)
    
  def setupConnections(self):#find common connections, add specials in overridden method
    logging.debug('ProstateTrusNav.setupConnections()')
    Guidelet.setupConnections(self)
    
  def setupScene(self): #applet specific
    logging.debug('setupScene')
    Guidelet.setupScene(self)

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

  def disconnect(self):
    logging.debug('ProstateTrusNav.disconnect()')
    Guidelet.disconnect(self)