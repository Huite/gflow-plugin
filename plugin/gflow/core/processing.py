"""
Utilities for processing input or output.

Currently wraps the QGIS functions for turning grids / meshes of head results
into line contours.
"""
from pathlib import Path
from typing import NamedTuple

import numpy as np
import processing
from PyQt5.QtCore import QVariant
from qgis.analysis import QgsMeshContours
from qgis.core import (
    QgsFeature,
    QgsField,
    QgsGeometry,
    QgsMeshDatasetIndex,
    QgsMeshLayer,
    QgsMeshRendererScalarSettings,
    QgsRasterLayer,
    QgsVectorLayer,
)
from gflow.core import geopackage


def raster_contours(
    gpkg_path: str,
    layer: QgsRasterLayer,
    name: str,
    start: float,
    stop: float,
    step: float,
) -> QgsVectorLayer:
    # Seemingly cannot use stop in any way, unless filtering them away.
    result = processing.run(
        "gdal:contour",
        {
            "INPUT": layer,
            "BAND": 1,
            "INTERVAL": step,
            "OFFSET": start,
            "FIELD_NAME": "head",
            "OUTPUT": "TEMPORARY_OUTPUT",
        },
    )

    path = result["OUTPUT"]
    vector_layer = QgsVectorLayer(path)

    result = processing.run(
        "qgis:extractbyexpression",
        {
            "INPUT": vector_layer,
            "EXPRESSION": f'"head" >= {start} AND "head" <= {stop}',
            "OUTPUT": "TEMPORARY_OUTPUT",
        },
    )
    # path = result["OUTPUT"]
    # vector_layer = QgsVectorLayer(result, name)

    newfile = not Path(gpkg_path).exists()
    written_layer = geopackage.write_layer(
        path=gpkg_path,
        layer=result["OUTPUT"],
        layername=name,
        newfile=newfile,
    )
    return written_layer


class SteadyContourData(NamedTuple):
    geometry: QgsGeometry
    head: float


def steady_contours(
    layer: QgsMeshLayer,
    index: int,
    name: str,
    start: float,
    stop: float,
    step: float,
) -> QgsVectorLayer:
    contourer = QgsMeshContours(layer)

    # Collect contours from mesh layer
    feature_data = []
    qgs_index = QgsMeshDatasetIndex(group=index, dataset=0)
    for value in np.arange(start, stop, step):
        geom = contourer.exportLines(
            qgs_index,
            value,
            QgsMeshRendererScalarSettings.NeighbourAverage,
        )
        if not geom.isNull():
            feature_data.append(SteadyContourData(geom, value))

    # Setup output layer
    contour_layer = QgsVectorLayer("Linestring", name, "memory")
    contour_layer.setCrs(layer.crs())
    provider = contour_layer.dataProvider()
    provider.addAttributes(
        [
            QgsField("head", QVariant.Double),
        ]
    )
    contour_layer.updateFields()

    # Add items to layer
    for item in feature_data:
        f = QgsFeature()
        f.setGeometry(item.geometry)
        # Make sure to convert to the appropriate Qt types
        # e.g. no numpy floats allowed
        f.setAttributes([round(float(item.head), 3)])
        provider.addFeature(f)
    contour_layer.updateExtents()

    return contour_layer


def mesh_contours(
    gpkg_path: str,
    layer: QgsMeshLayer,
    index: int,
    name: str,
    start: float,
    stop: float,
    step: float,
) -> QgsVectorLayer:
    vector_layer = steady_contours(layer, index, name, start, stop, step)

    newfile = not Path(gpkg_path).exists()
    written_layer = geopackage.write_layer(
        path=gpkg_path,
        layer=vector_layer,
        layername=name,
        newfile=newfile,
    )
    return written_layer