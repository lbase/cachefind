# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CacheFind
                                 A QGIS plugin
 take coordinates from cache page and display as marker
                             -------------------
        begin                : 2016-01-11
        copyright            : (C) 2016 by rfile
        email                : lbase@finormile.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load CacheFind class from file CacheFind.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .cache_find import CacheFind
    return CacheFind(iface)
