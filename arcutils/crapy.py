"""
Wrappers around crappy arcpy APIs: crapy
"""

from contextlib import contextmanager
from functools import wraps

import numpy


def check_arcpy(func):  # pragma: no cover
    """ Decorator that checks for and imports arcpy if its available
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            global arcpy
            import arcpy
            return func(*args, **kwargs)
        except ImportError:
            raise RuntimeError('`arcpy` is not available on this system')

    return wrapper


@check_arcpy
def update_status():  # pragma: no cover
    """ Decorator to allow a function to take a additional keyword
    arguments related to printing status messages to stdin or as arcpy
    messages.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        msg = kwargs.pop("msg", None)
        verbose = kwargs.pop("verbose", False)
        asMessage = kwargs.pop("asMessage", False)
        addTab = kwargs.pop("addTab", False)

        if verbose:
            if addTab:
                msg = '\t' + msg
            if asMessage:
                arcpy.AddMessage(msg)
            else:
                print(msg)

        return func(*args, **kwargs)
    return wrapper


@contextmanager
@check_arcpy
def Extension(name):
    """ Context manager to facilitate the use of ArcGIS extensions

    Inside the context manager, the extension will be checked out. Once
    the interpreter leaves the code block by any means (e.g., successful
    execution, raised exception) the extension will be checked back in.

    Examples
    --------
    >>> import arcutils, arcpy
    >>> with arcutils.mapping.Extension("spatial"):
    ...     arcpy.sa.Hillshade("C:/data/dem.tif")

    """

    if arcpy.CheckExtension(name) == u"Available":
        status = arcpy.CheckOutExtension(name)
        yield status
    else:
        raise RuntimeError("%s license isn't available" % name)

    arcpy.CheckInExtension(name)


@contextmanager
@check_arcpy
def OverwriteState(state):
    """ Context manager to temporarily set the ``overwriteOutput``
    environment variable.

    Inside the context manager, the ``arcpy.env.overwriteOutput`` will
    be set to the given value. Once the interpreter leaves the code
    block by any means (e.g., successful execution, raised exception),
    ``arcpy.env.overwriteOutput`` will reset to its original value.

    Parameters
    ----------
    path : str
        Path to the directory that will be set as the current workspace.

    Examples
    --------
    >>> import arcutils
    >>> with arcutils.mapping.OverwriteState(False):
    ...     # some operation that should fail if output already exists

    """

    orig_state = arcpy.env.overwriteOutput
    arcpy.env.overwriteOutput = bool(state)
    yield state
    arcpy.env.overwriteOutput = orig_state


@contextmanager
@check_arcpy
def WorkSpace(path):
    """ Context manager to temporarily set the ``workspace``
    environment variable.

    Inside the context manager, the `arcpy.env.workspace`_ will
    be set to the given value. Once the interpreter leaves the code
    block by any means (e.g., successful execution, raised exception),
    `arcpy.env.workspace`_ will reset to its original value.

    .. _arcpy.env.workspace: http://goo.gl/0NpeFN

    Parameters
    ----------
    path : str
        Path to the directory that will be set as the current workspace.

    Examples
    --------
    >>> import arcutils.mapping.OverwriteState(False):
    ...     # some operation that should fail if output already exists

    """

    orig_workspace = arcpy.env.workspace
    arcpy.env.workspace = path
    yield path
    arcpy.env.workspace = orig_workspace


@check_arcpy
class RasterTemplate(object):
    """ Georeferencing template for Rasters.

    This mimics the attributes of the ``arcpy.Raster`` class enough
    that it can be used as a template to georeference numpy arrays
    when converting to rasters.

    Parameters
    ----------
    cellsize : int or float
        The width of the raster's cells.
    xmin, ymin : float
        The x- and y-coordinates of the raster's lower left (south west)
        corner.

    Attributes
    ----------
    cellsize : int or float
        The width of the raster's cells.
    extent : Extent
        Yet another mock-ish class that ``x`` and ``y`` are stored in
        ``extent.lowerLeft`` as an ``arcpy.Point``.

    See also
    --------
    arcpy.Extent

    """

    def __init__(self, cellsize, xmin, ymin):
        self.meanCellWidth = cellsize
        self.meanCellHeight = cellsize
        self.extent = arcpy.Extent(xmin, ymin, numpy.nan, numpy.nan)

    @classmethod
    def from_arcpy_raster(cls, arcpy_raster):
        """ Alternative constructor to generate a RasterTemplate from
        an actual raster.

        Parameters
        ----------
        raster : arcpy.Raster
            The raster whose georeferencing attributes need to be
            replicated.

        Returns
        -------
        template : RasterTemplate

        """
        template = cls(
            arcpy_raster.meanCellHeight,
            arcpy_raster.extent.lowerLeft.X,
            arcpy_raster.extent.lowerLeft.Y,
        )
        return template


@check_arcpy
def get_field_names(layerpath):
    """
    Gets the names of fields/columns in a feature class or table.
    Relies on `arcpy.ListFields`_.

    .. _arcpy.ListFields: http://goo.gl/Siq5y7

    Parameters
    ----------
    layerpath : str, arcpy.Layer, or arcpy.table
        The thing that has fields.

    Returns
    -------
    fieldnames : list of str

    """

    return [f.name for f in arcpy.ListFields(layerpath)]
