from arcutils.crapy import check_arcpy
try:
    import arcpy
except ImportError:
    arcpy = None


@check_arcpy
def load_data(datapath, datatype, greedyRasters=True, **verbosity):
    """ Loads vector and raster data from filepaths.

    Parameters
    ----------
    datapath : str, arcpy.Raster, or arcpy.mapping.Layer
        The (filepath to the) data you want to load.
    datatype : str
        The type of data you are trying to load. Must be either
        "shape" (for polygons) or "raster" (for rasters).
    greedyRasters : bool (default = True)
        Currently, arcpy lets you load raster data as a "Raster" or as a
        "Layer". When ``greedyRasters`` is True, rasters loaded as type
        "Layer" will be forced to type "Raster".

    Returns
    -------
    data : `arcpy.Raster`_ or `arcpy.mapping.Layer`_
        The data loaded as an arcpy object.

    .. _arcpy.Raster: http://goo.gl/AQgFXW
    .. _arcpy.mapping.Layer: http://goo.gl/KfrGNa

    """

    dtype_lookup = {
        'raster': arcpy.Raster,
        'grid': arcpy.Raster,
        'shape': arcpy.mapping.Layer,
        'layer': arcpy.mapping.Layer,
    }

    try:
        objtype = dtype_lookup[datatype.lower()]
    except KeyError:
        msg = "Datatype {} not supported. Must be raster or layer".format(datatype)
        raise ValueError(msg)

    # if the input is already a Raster or Layer, just return it
    if isinstance(datapath, objtype):
        data = datapath
    # otherwise, load it as the datatype
    else:
        try:
            data = objtype(datapath)
        except:
            raise ValueError("could not load {} as a {}".format(datapath, objtype))

    if greedyRasters and isinstance(data, arcpy.mapping.Layer) and data.isRasterLayer:
        data = arcpy.Raster(datapath)

    return data


@check_arcpy
class EasyMapDoc(object):
    """ The object-oriented map class Esri should have made.

    Create this the same you would make any other
    `arcpy.mapping.MapDocument`_. But now, you can directly list and
    add layers and dataframes. See the two examples below.

    Has ``layers`` and ``dataframes`` attributes that return all of the
    `arcpy.mapping.Layer`_ and `arcpy.mapping.DataFrame`_ objects in the
    map, respectively.

    .. _arcpy.mapping.MapDocument: http://goo.gl/rf4GBH
    .. _arcpy.mapping.DataFrame: http://goo.gl/ctJu3B
    .. _arcpy.mapping.Layer: http://goo.gl/KfrGNa

    Attributes
    ----------
    mapdoc : arcpy.mapping.MapDocument
        The underlying arcpy MapDocument that serves as the basis for
        this class.

    Examples
    --------
    >>> # Adding a layer with the Esri version:
    >>> import arcpy
    >>> md = arcpy.mapping.MapDocument('CURRENT')
    >>> df = arcpy.mapping.ListDataFrames(md)
    >>> arcpy.mapping.AddLayer(df, myLayer, 'TOP')

    >>> # And now with an ``EasyMapDoc``:
    >>> import gisutils
    >>> ezmd = gisutils.mapping.EasyMapDoc('CURRENT')
    >>> ezmd.add_layer(myLayer)

    """

    def __init__(self, *args, **kwargs):
        try:
            self.mapdoc = arcpy.mapping.MapDocument(*args, **kwargs)
        except RuntimeError:
            self.mapdoc = None

    @property
    def layers(self):
        """
        All of the layers in the map.
        """
        return arcpy.mapping.ListLayers(self.mapdoc)

    @property
    def dataframes(self):
        """
        All of the dataframes in the map.
        """
        return arcpy.mapping.ListDataFrames(self.mapdoc)

    def findLayerByName(self, name):
        """ Finds a `layer`_ in the map by searching for an exact match
        of its name.

        .. _layer: http://goo.gl/KfrGNa

        Parameters
        ----------
        name : str
            The name of the layer you want to find.

        Returns
        -------
        lyr : arcpy.mapping.Layer
            The map layer or None if no match is found.

        .. warning:: Group Layers are not returned.

        Examples
        --------
        >>> import gisutils
        >>> ezmd = gisutils.mapping.EasyMapDoc('CURRENT')
        >>> wetlands = ezmd.findLayerByName("wetlands")
        >>> if wetlands is not None:
        ...     # do something with `wetlands`

        """

        for lyr in self.layers:
            if not lyr.isGroupLayer and lyr.name == name:
                return lyr

    def add_layer(self, layer, df=None, position='top'):
        """ Simply adds a `layer`_ to a map.

        .. _layer: http://goo.gl/KfrGNa

        Parameters
        ----------
        layer : str or arcpy.mapping.Layer
            The dataset to be added to the map.
        df : arcpy.mapping.DataFrame, optional
            The specific dataframe to which the layer will be added. If
            not provided, the data will be added to the first dataframe
            in the map.
        position : str, optional ('TOP')
            The positional within `df` where the data will be added.
            Valid options are: 'auto_arrange', 'bottom', and 'top'.

        Returns
        -------
        layer : arcpy.mapping.Layer
            The successfully added layer.

        Examples
        --------
        >>> import gisutils
        >>> ezmd = gisutils.mapping.EasyMapDoc('CURRENT')
        >>> watersheds = gisutils.load_data("C:/gis/hydro.gdb/watersheds")
        >>> ezmd.add_layer(watersheds)

        """

        # if no dataframe is provided, select the first
        if df is None:
            df = self.dataframes[0]

        # check that the position is valid
        valid_positions = ['auto_arrange', 'bottom', 'top']
        if position.lower() not in valid_positions:
            raise ValueError('Position: %s is not in %s' % (position.lower, valid_positions))

        # layer can be a path to a file. if so, convert to a Layer object
        layer = load_data(layer, 'layer')

        # add the layer to the map
        arcpy.mapping.AddLayer(df, layer, position.upper())

        # return the layer
        return layer
