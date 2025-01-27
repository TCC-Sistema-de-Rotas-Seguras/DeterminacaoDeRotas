import networkx as nx
import osmnx as ox

# download/model a street network for some city then visualize it
# get a fully bidirection network (as a MultiDiGraph)
# ox.settings.bidirectional_network_types += "drive"
# G = ox.graph.graph_from_place("São Bernardo do Campo, São Paulo, BRAZIL", network_type="drive")

# fig, ax = ox.plot.plot_graph(G)

# or get network by address, coordinates, bounding box, or any custom polygon
# ...useful when OSM just doesn't already have a polygon for the place you want
Fei_Location = (-23.72403491298448, -46.579397903870166)
one_mile = 1609  # meters
ox.settings.bidirectional_network_types += "drive"
fig, ax = ox.plot.plot_graph(G, node_size=0)
G = ox.graph.graph_from_point(Fei_Location, dist=one_mile, network_type="drive")
fig, ax = ox.plot.plot_graph(G, node_size=0)