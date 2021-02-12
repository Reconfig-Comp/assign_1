"""
Utility module providing the directed graph data structure and corresponding functions to build and modify a graph.
"""

class DirectedGraph:
    """
    A class to describe a directed graph and allied functionalities

    Attributes
    ----------
    dGrph : dictionary
        Dictionary storing the graph

    Methods
    -------
        * addEdge(edge)
        * addVertex(vrtx)
        * listVertices()
        * listEdges()
    """

    def __init__(self, dGrph=None):
        """
        Constructor

        Parameters
        ----------
        dGrph : dictionary
            Use an existing dictionary as graph. Default: None.
            Creates a new dictionary in case no parameter is given.
        """
        if dGrph is None:
            dGrph = {}
        self.dGrph = dGrph    

    def addEdge(self, edge):
        """
        Adds an directed edge between two vertices (1st element -> 2nd element).
        If the edge is already present, just the vertices are updated. 
        If the edge is not present, then new vertix is added.

        Parameters
        ----------
        edge : set
            Set of vertices between which the edge should be formed. Size 2.
        """
        edge = set(edge)
        (vrtx1, vrtx2) = tuple(edge)
        if vrtx1 in self.dGrph:
            self.dGrph[vrtx1].append(vrtx2)
        else:
            self.dGrph[vrtx1] = [vrtx2]

    def addVertex(self, vrtx):
        """
        Adds an empty vertex to the graph with no edges connected.

        Parameters
        ----------
        vrtx : str
            Name of the vertex to be added
        """
        if vrtx not in self.dGrph:
            self.dGrph[vrtx] = []

    def listVertices(self):
        """
        Get the list of vertices in the graph.

        Returns
        -------
        List of dictionary keys representing vertices
        """
        return list(self.dGrph.keys())

    def listEdges(self):
        """
        Get the list of edges present in the graph.

        Returns
        -------
        List of size 2 sets representing an edge from first element
        to second element in the set.
        """
        edgename = []
        for vrtx in self.dGrph:
            for nxtvrtx in self.dGrph[vrtx]:
                if {nxtvrtx, vrtx} not in edgename:
                    edgename.append({vrtx, nxtvrtx})
        return edgename

# for unit testing this module
if __name__ == '__main__':
    # Create the dictionary with graph elements
    g = DirectedGraph()
    g.addEdge({'a','e'})
    g.addEdge({'d','e'})
    print("List of edges")
    print(g.listEdges())
    print("List of vertices")
    print(g.listVertices())