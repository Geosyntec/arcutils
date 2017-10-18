import sys
import os
from pkg_resources import resource_filename

import pytest

from unittest import mock

try:
    import arcpy
    _NO_ARCPY = False
except ImportError:
    _NO_ARCPY = True
    arcpy = mock.MagicMock()

from arcutils import mapping


rasterpath = resource_filename("arcutils.tests.data.mapping.load_data", 'test_dem.tif')
vectorpath = resource_filename("arcutils.tests.data.mapping.load_data", 'test_wetlands.shp')


@pytest.mark.skipif(_NO_ARCPY, reason='No arcpy')
@pytest.mark.parametrize(('filename', 'filetype', 'objtype', 'greedy'), [
    (rasterpath, 'JUNK', None, False),
    ('junk.shp', 'grid', None, False),
    (12345, 'grid', None, False),
    (vectorpath, 'grid', None, False),
    (vectorpath, 'raster', None, False),
    (vectorpath, 'layer', arcpy.mapping.Layer, False),
    (vectorpath, 'shape', arcpy.mapping.Layer, False),
    (rasterpath, 'raster', arcpy.Raster, False),
    (rasterpath, 'gRId', arcpy.Raster, False),
    (rasterpath, 'layer', arcpy.mapping.Layer, False),
    (rasterpath, 'layer', arcpy.Raster, True),
])
def test_load_data(filename, filetype, objtype, greedy):
    if objtype is None:
        with pytest.raises(ValueError):
            mapping.load_data(filename, filetype)
    else:
        data = mapping.load_data(filename, filetype, greedyRasters=greedy)
        assert isinstance(data, objtype)


@pytest.mark.skipif(_NO_ARCPY, reason='No arcpy')
class Test_EasyMapDoc(object):
    def setup(self):
        self.mxd = resource_filename("propagator.testing.EasyMapDoc", "test.mxd")
        self.ezmd = mapping.EasyMapDoc(self.mxd)

        self.knownlayer_names = ['ZOI', 'wetlands', 'ZOI_first_few', 'wetlands_first_few']
        self.knowndataframe_names = ['Main', 'Subset']
        self.add_layer_path = resource_filename("propagator.testing.EasyMapDoc", "ZOI.shp")

    def test_layers(self):
        assert hasattr(self.ezmd, 'layers')
        layers_names = [layer.name for layer in self.ezmd.layers]
        assert layers_names == self.knownlayer_names

    def test_dataframes(self):
        assert hasattr(self.ezmd, 'dataframes')
        df_names = [df.name for df in self.ezmd.dataframes]
        assert df_names == self.knowndataframe_names

    def test_findLayerByName(self):
        name = 'ZOI_first_few'
        lyr = self.ezmd.findLayerByName(name)
        assert isinstance(lyr, arcpy.mapping.Layer)
        assert lyr.name == name

    def test_add_layer_with_path(self):
        assert len(self.ezmd.layers) == 4
        self.ezmd.add_layer(self.add_layer_path)
        assert len(self.ezmd.layers) == 5

    def test_add_layer_with_layer_and_other_options(self):
        layer = arcpy.mapping.Layer(self.add_layer_path)
        assert len(self.ezmd.layers) == 4
        self.ezmd.add_layer(layer, position='bottom', df=self.ezmd.dataframes[1])
        assert len(self.ezmd.layers) == 5

    def test_bad_layer(self):
        with pytest.raises(ValueError):
            self.ezmd.add_layer(123456)

    def test_bad_position(self):
        with pytest.raises(ValueError):
            self.ezmd.add_layer(self.add_layer_path, position='junk')
