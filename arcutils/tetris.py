import arcpy


def tetris_plot(srclayer, boxsize, srcfields, datafields, locfield='loc',
                resfield='result', intervalfield='interval',
                dstlayer=None):

    # Create an insert cursor
    cursor_columns = ('SHAPE@', locfield, resfield, intervalfield)
    with arcpy.da.InsertCursor(dstlayer, cursor_columns) as cursor:

        #loop through the Tetris segments
        for row in arcpy.da.SearchCursor(srclayer, srcfields):

            startX = row[1] - (boxsize * 0.5)
            startY = row[2] - (boxsize * 0.5)

            #for every box in tetris:
            for i, field in enumate(datafields):

                nextbox_X = startX
                nextbox_Y = startY - (boxsize)
                string_args = {
                    'field': field,
                    'i': i,
                    'nextbox_X': nextbox_X,
                    'nextbox_Y': nextbox_Y,
                }

                #build the geometry of Tetris
                # point 1
                points = [
                    arcpy.Point(startX, startY),
                    arcpy.Point(startX+boxsize, startY),
                    arcpy.Point(startX+boxsize, startY-boxsize)
                    arcpy.Point(startX,startY-boxsize)
                ]

                poinnt_array = arcpy.Array(points)
                geom = arcpy.Polygon(poinnt_array)

                 #actually create the feature + attribute data
                cursor.insertRow((geom, row[0], row[i+3], field))

                #features.append(pol)
                #increment Tetris Depth
                startX = nextbox_X
                startY = nextbox_Y
