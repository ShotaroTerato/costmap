# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CostMap
                                 A QGIS plugin
 create costmap
                              -------------------
        begin                : 2017-05-30
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Shotaro.T
        email                : syoutarou41211@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import processing
import glob, qgis
import yaml
from qgis.analysis import QgsRasterCalculatorEntry, QgsRasterCalculator
from osgeo import gdal
from osgeo.gdalnumeric import *
from osgeo.gdalconst import *
import struct
from numpy import *
import numpy as np
from qgis.core import *
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from cost_map_dialog import CostMapDialog
import os.path
import os


class CostMap:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'CostMap_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&cost map')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'CostMap')
        self.toolbar.setObjectName(u'CostMap')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('CostMap', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = CostMapDialog()
        self.dlg.button_box.accepted.connect(self.set_text)

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action
    
    def set_text(self):
        #current_dir = os.getcwd()
        #f = open(current_dir + "/.qgis2/python/plugins/CostMap/robot_params.yaml", "r+")
        #data = yaml.load(f)
        #self.dlg.textEdit.setText(str(data))
        #self.dlg.textEdit.setText(str(self.iface.mapCanvas().layerCount()))
        pass

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/CostMap/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'costmap'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&cost map'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    calc_results = []
    def run(self):
        global calc_results
        global size_x
        global size_y
        global size_z
        global max_speed
        global min_speed
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            current_dir = os.getcwd()
            f = open(current_dir + "/.qgis2/python/plugins/CostMap/robot_params.yaml", "r+")
            data = yaml.load(f)
            size_x = data['robot_size']['x']
            size_y = data['robot_size']['y']
            size_z = data['robot_size']['z']
            max_speed = data['max_speed']
            min_speed = data['min_speed']
            attributes = data['attributes']
            for i in attributes.keys():
                attribute_name = i
                threshold = attributes[attribute_name]['threshold']
                speed = attributes[attribute_name]['speed']
                self.calc(attribute_name, threshold, speed)
            
            output = self.calc_results[0]
            for rst in range(len(self.calc_results)-1):
                output = self.merge_layer(output, self.calc_results[rst+1])
    
    def calc(self, attribute_name, threshold, speed):
        layer = QgsMapLayerRegistry.instance().mapLayersByName(attribute_name)
        if len(layer) != 0:
            path = "/home/tera/maps/"
            
            gdal_layer = gdal.Open(layer[0].source())
            maparray = np.array(gdal_layer.GetRasterBand(1).ReadAsArray())
            maplist = maparray.tolist()
            for i in range(maparray.shape[0]):
                for j in range(maparray.shape[1]):
                    if maplist[i][j] > threshold:
                        maplist[i][j] = max_speed - speed
                    else:
                        maplist[i][j] = max_speed - max_speed
            maparray2 = np.array(maplist)
            dst_filename = path + layer[0].name() + '_cost.tif'
            x_pixels = maparray.shape[0]
            y_pixels = maparray.shape[1]
            driver = gdal.GetDriverByName('GTiff')
            outlayer = driver.Create(
               dst_filename,
               y_pixels,
               x_pixels,
               1,
               gdal.GDT_Float32, )
            outlayer.GetRasterBand(1).WriteArray(maparray2)
            outlayer.SetGeoTransform(gdal_layer.GetGeoTransform())
            outlayer.SetProjection(gdal_layer.GetProjection())
            outlayer.FlushCache()
            self.calc_results.append(dst_filename)
        else:
            pass
    
    def merge_layer(self, result1, result2):
        map1 = QgsRasterLayer(result1, QFileInfo(result1).baseName())
        entries = []
        ras1 = QgsRasterCalculatorEntry()
        ras1.ref = 'result1@1'
        ras1.raster = map1
        ras1.bandNumber = 1
        entries.append(ras1)
        
        map2 = QgsRasterLayer(result2, QFileInfo(result2).baseName())
        ras2 = QgsRasterCalculatorEntry()
        ras2.ref = 'result2@1'
        ras2.raster = map2
        ras2.bandNumber = 1
        entries.append(ras2)
        
        sum_culc = QgsRasterCalculator('(("result1@1">"result2@1")*"result1@1")+(("result2@1">"result1@1")*"result2@1")', '/home/tera/maps/cost_map.tif', 'GTiff', map1.extent(), map1.width(), map1.height(), entries)
        sum_culc.processCalculation()
        out = QgsRasterLayer("/home/tera/maps/cost_map.tif", "cost_map.tif")
        return out
