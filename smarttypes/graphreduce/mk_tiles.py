

import mapnik
from mapnik import PostGIS

m = mapnik.Map(200,100)
m.background = mapnik.Color('#ffffff')
s = mapnik.Style()
r = mapnik.Rule()

point_symbolizer = mapnik.MarkersSymbolizer()
r.symbols.append(point_symbolizer)

s.rules.append(r)
m.append_style('My Style',s)
BUFFERED_TABLE = '(select * from twitter_reduction where id = 6) reduction' 
ds = PostGIS(host='localhost',user='timmyt',password='urllib2',dbname='smarttypes',table=BUFFERED_TABLE)
layer = mapnik.Layer('world')
layer.datasource = ds
layer.styles.append('My Style')
m.layers.append(layer)
m.zoom_all()
mapnik.render_to_file(m,'world.png', 'png')
print "rendered image to 'world.png'"

