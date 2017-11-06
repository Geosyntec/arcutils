import os
from pkg_resources import resource_filename

try:
    import arcpy
except ImportError:
    arcpy = None

import pytest

from arcutils import crapy


@pytest.mark.skipif(arcpy is None, reason='No arcpy')
class Test_Extension(object):
    def setup(self):
        self.known_available = 'spatial'
        self.known_unavailable = 'tracking'

    @pytest.mark.skipif(True, reason="Test status: WIP")
    def test_unlicensed_extension(self):
        with pytest.raises(RuntimeError):
            with crapy.Extension(self.known_unavailable):
                raise

    def test_licensed_extension(self):
        assert arcpy.CheckExtension(self.known_available) == u'Available'
        with crapy.Extension(self.known_available) as ext:
            assert ext == 'CheckedOut'

        assert arcpy.CheckExtension(self.known_available) == u'Available'

    def teardown(self):
        arcpy.CheckInExtension(self.known_available)


@pytest.mark.skipif(arcpy is None, reason='No arcpy')
class Test_OverwriteState(object):
    def test_true_true(self):
        arcpy.env.overwriteOutput = True

        assert arcpy.env.overwriteOutput
        with crapy.OverwriteState(True):
            assert arcpy.env.overwriteOutput

        assert arcpy.env.overwriteOutput

    def test_false_false(self):
        arcpy.env.overwriteOutput = False

        assert not arcpy.env.overwriteOutput
        with crapy.OverwriteState(False):
            assert not arcpy.env.overwriteOutput

        assert not arcpy.env.overwriteOutput

    def test_true_false(self):
        arcpy.env.overwriteOutput = True

        assert arcpy.env.overwriteOutput
        with crapy.OverwriteState(False):
            assert not arcpy.env.overwriteOutput

        assert arcpy.env.overwriteOutput

    def test_false_true(self):
        arcpy.env.overwriteOutput = False

        assert not arcpy.env.overwriteOutput
        with crapy.OverwriteState(True):
            assert arcpy.env.overwriteOutput

        assert not arcpy.env.overwriteOutput


@pytest.mark.skipif(arcpy is None, reason='No arcpy')
class Test_WorkSpace(object):
    def setup(self):
        self.baseline = os.getcwd()
        self.new_ws = u'C:/Users'

        arcpy.env.workspace = self.baseline

    def test_workspace(self):
        assert arcpy.env.workspace == self.baseline
        with crapy.WorkSpace(self.new_ws):
            assert arcpy.env.workspace == self.new_ws

        assert arcpy.env.workspace == self.baseline


@pytest.mark.skipif(arcpy is None, reason='No arcpy')
def test_RasterTemplate():
    size, x, y = 8, 1, 2
    template = crapy.RasterTemplate(size, x, y)
    assert template.meanCellWidth == size
    assert template.meanCellHeight == size
    assert template.extent.lowerLeft.X == x
    assert template.extent.lowerLeft.Y == y


@pytest.mark.skipif(arcpy is None, reason='No arcpy')
def test_get_field_names():
    expected = [u'FID', u'Shape', u'Station', u'Latitude', u'Longitude']
    layer = resource_filename('arcutils.tests._data.crapy.get_field_names', 'input.shp')
    result = crapy.get_field_names(layer)
    assert result == expected
