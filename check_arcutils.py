import sys
import matplotlib
matplotlib.use('agg')

import arcutils
status = arcutils.test(*sys.argv[1:])
sys.exit(status)
