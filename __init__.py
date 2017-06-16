# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CostMap
                                 A QGIS plugin
 create costmap
                             -------------------
        begin                : 2017-05-30
        copyright            : (C) 2017 by Shotaro.T
        email                : syoutarou41211@gmail.com
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
    """Load CostMap class from file CostMap.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .cost_map import CostMap
    return CostMap(iface)
