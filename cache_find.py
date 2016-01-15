# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CacheFind
                                 A QGIS plugin
 take coordinates from cache page and display as marker
                              -------------------
        begin                : 2016-01-11
        git sha              : $Format:%H$
        copyright            : (C) 2016 by rfile
        email                : lbase@finormile.com
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
from PyQt4.QtGui import QColor
from qgis.core import *
from qgis.gui import *
from qgis.utils import iface
import re
import clipboard
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from cache_find_dialog import CacheFindDialog
import os.path


class CacheFind:
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
                'CacheFind_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = CacheFindDialog()

        # Declare instance attributes
        
        self.actions = []
        self.menu = self.tr(u'&Showcache')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'cachefind')
        self.toolbar.setObjectName(u'CacheFind')

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
        return QCoreApplication.translate('CacheFind', message)

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

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/CacheFind/icon2.png'
        self.add_action(
                icon_path,
                text=self.tr(u'CacheFind'),
                callback=self.run,
                parent=self.iface.mainWindow())
        self.dlg.convertedTxt.setText("x y coordinates ")
        crdsfrompb = clipboard.paste()
        self.dlg.coordsTxt.setText(crdsfrompb)
        self.dlg.cnvrtBtn.clicked.connect(self.chgcoords)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                    self.tr(u'&Showcache'),
                    action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        # if result == 1:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
        inline = self.dlg.coordsTxt
        inline.clear()
        crdspb = clipboard.paste()
        self.dlg.coordsTxt.setText(crdspb)

    def chgcoords(self):
        # coords should look like this:
        # N25° 36.875 W080° 19.366
        coords = self.dlg.coordsTxt.text()
        if re.match('^N[0-9]{1,2}\xb0\s[0-9]{1,2}\.[0-9]{1,3}\sW[0-9]{1,3}\xb0\s[0-9]{1,2}\.[0-9]{1,3}', coords):
            lat = coords[1:3]
            fmin = coords[5:11]
            lon = coords[14:16]
            smin = coords[18:24]
            latdeg = int(lat)
            londeg = int(lon)
            latmin = float(fmin)
            lonmin = float(smin)
            declat = latdeg + (latmin / 60)
            declon = londeg + (lonmin / 60)
        # coords may look like this:
        # N 27° 53.553 W 082° 31.913
        elif re.match('^N\s[0-9]{1,2}\xb0\s[0-9]{1,2}\.[0-9]{1,3}\sW\s[0-9]{1,3}\xb0\s[0-9]{1,2}\.[0-9]{1,3}', coords):
            lat = coords[2:4]
            fmin = coords[6:12]
            lon = coords[16:18]
            smin = coords[20:26]
            latdeg = int(lat)
            londeg = int(lon)
            latmin = float(fmin)
            lonmin = float(smin)
            declat = latdeg + (latmin / 60)
            declon = londeg + (lonmin / 60)
        else:
            self.dlg.convertedTxt.setText("string does not match pattern we were expecting")
            return;

        dec_coords = str((declon * -1)) + "," + str(declat)
        self.dlg.convertedTxt.setText(dec_coords)
        mypoint = QgsPoint((declon * -1), declat)

        # canvas = QgsMapCanvas()
        canvas = self.iface.mapCanvas()
        m = QgsVertexMarker(canvas)
        m.setCenter(mypoint)
        m.setColor(QColor(255, 0, 0))
        m.setIconSize(5)
        m.setIconType(QgsVertexMarker.ICON_BOX) # or ICON_CROSS, ICON_X
        m.setPenWidth(3)
        m.show()
        iface.actionPanToSelected()
        self.iface.actionPan()
        # TODO: clear the text box after this is run maybe put the text in a label first
    # stolen from quickdraw by rfile
    def zoomToItems(self):
        def getBBOX(item):
            if isinstance(item, QgsVertexMarker):
                return QgsRectangle(item.point, item.point)
            return item.asGeometry().boundingBox()
        
        if not self.drawStack:
            return
    
        canvas = self.iface.mapCanvas()
        extent = getBBOX(self.drawStack[0])
        for item in self.drawStack[1:]:
            bbox = getBBOX(item)
            extent.combineExtentWith(bbox)
    
        if extent:
            canvas.setExtent(extent)
            canvas.updateFullExtent()
    # stolen from quickdraw by rfile
