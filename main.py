#-------------------------------------------------------------------------------
# Name:        main.py
# Purpose:     Resilience and Energy Orchestration Processing
#
# Author:      Holly Tina Ferguson hfergus2@nd.edu
#
# Created:     06/05/2017
# Copyright:   (c) Holly Tina Ferguson 2015
# License:     The University of Notre Dame

# Line 66-71 Below have the directions for asking for an x value along the splines we are able to generate from USGS
# import pymatlab   # This is the library for interfacing with matlab, you will need to install this through the interpreter page
# pymatlab documentation: https://pypi.python.org/pypi/pymatlab
#-------------------------------------------------------------------------------

# #!/usr/bin/python
import sys, os, getopt
import json
import subprocess
import importlib
from os import path
import pandas as pd
#sys.path.append(path.abspath('../GeoLinked'))
#from GeoLinked.Geo_Link import Geo_Link
#x = Geo_Link()
from curves import Curves
import rdflib
from rdflib import Graph
from rdflib import URIRef, BNode, Literal
from rdflib.namespace import RDF
from rdflib import Namespace
import pymatlab   # This is the library for interfacing with matlab, you will need to install this through the interpreter page
from pymatlab.matlab import MatlabSession
from Q_Semantic_Graph import GraphData


def ReadHazardData(model_names,base_directory):
    """
    modelnames: MUST be same as subdirectory names, or else all hell breaks loose
    base_directory: curves folders generated using the hazard model from USGS
    """
    hazard_data = {} # {city_name: model:[(X1, Y1), ...] }
    for _model in model_names:
        print(_model)
        f = os.path.join(base_directory ,_model,"total.csv")
        df = pd.read_csv(f,header=None) #read in the total.csv file as a dataframe in pandas
        df.drop(df.columns[[1,2]],inplace=True,axis=1) #drop the lat and long
        city_names = df.iloc[:,0].values.tolist()[1:] # all values after the first row are city names
        X = df.iloc[0,1:].values.tolist() #all x values
        for i,c in enumerate(city_names):
            Y = df.iloc[(i+1),1:]
            if c in hazard_data:
                hazard_data[c][_model] = zip(X,Y) #ignore the type assertion for now
            else:
                hazard_data[c] = {_model:zip(X,Y)}
    return hazard_data

def main(argv, other_stuff=0):

    print "Orchestration Main Started"

    # Take USGS data sets (3 curves) for a location and get back........................................................
    basedir = "C:\\Users\\holly\\Desktop\\USGS\\nshmp-haz-master\\curves_east_donotmodify"
    models = ["PGA","SA0P2","SA1P0"] #different types of hazard models used
    #read all files
    cityhazardfunctions = ReadHazardData(models,basedir) # nested dict. {city: {model: (X,Y) }}
    #print(json.dumps(cityhazardfunctions,indent=4)) #print to debug if something goes horrendously wrong
    curv = Curves()
    city_splines = curv.querycurves(cityhazardfunctions,savefigs=True)
    # To get the y values for a given list of x's, set these values
    # So, you will set the location from the curve sets we have already generated
    # (for locaiotns we have either see the folders ehre or see the USGS files and sitesE.geojson and sitesW.geojson)
    # The models we have access to set (so the middle term here) without further editing the USGS tool are on line 51 above
    demo_x = [0.42] #[0.1, 0.2, 0.3, 0.4, 0.5] # So this would be some set of x values you want the cooresponding y values for
    print(city_splines["Chicago IL"]["PGA"](demo_x))


    # Construct Semantic Graph..........................................................................................
    # Currently using locally stored files, will need to add this API automation from my scrips from Drive
    # Note, in script, will need to reset the location of the stored file to be findable by these next lines
    #inputfileIFCXML = Call API script using IronPython
    inputfileIFCXML = 'C:/Users/hfergus2/Desktop/Orchestration/TempXMLs/RC_FRAME.ifcxml'
    outputpath='output.csv'
    material_flag = 0
    level_flag = 0
    structure_flag = 0
    puncture_flag = 0
    test_query_sequence_flag = 0
    SemanticGraph_InitialRun = 0
    # Currently using locally stored files, will need to add this API automation from my scrips from Drive
    #geo_link = Geo_Link()
    #geo_link.inputfile = os.path.abspath(inputfileIFCXML)
    #geo_link.material_flag = material_flag
    #geo_link.level_flag = level_flag
    #geo_link.structure_flag = structure_flag
    #geo_link.puncture_flag = puncture_flag
    #geo_link.test_query_sequence_flag = test_query_sequence_flag
    #geo_link.run()
    # Alternatively, a method like this may work, but will need some tweeking as this is done seperately at this point
    mylist_of_parameters = [str(inputfileIFCXML) + " " + str(outputpath) + " " + str(material_flag) + " " + str(level_flag) + " " + str(structure_flag) + " " + str(puncture_flag) + " " + str(test_query_sequence_flag)]
    subprocess.call(["python", "C:/Users/hfergus2/Desktop/GeoLinked/GeoLmain.py", str(inputfileIFCXML), str(outputpath), str(material_flag), str(level_flag), str(structure_flag), str(puncture_flag), str(test_query_sequence_flag) ])
    #subprocess.call(["python", "C:/Users/hfergus2/Desktop/GeoLinked/GeoLmain.py", "--args", str(inputfileIFCXML), str(outputpath), str(material_flag), str(level_flag), str(structure_flag), str(puncture_flag), str(test_query_sequence_flag) ])
    #USO_new = USOmain(inputfileIFCXML, outputpath, material_flag, level_flag, structure_flag, puncture_flag, test_query_sequence_flag)
    print "Storing Graph"
    #store it somewhere...currently we are saving it and accessing it from here: "C:/Users/holly/Desktop/GeoLinked/FinalGraph/MyGraph.ttl"


    # Query Semantic Graph..............................................................................
    # Now we want to get data from my graph
    # NOTE: more queries will probably have to be written.
    # If you go to this path where the graph serialization was stored, currenlty left in the single room model at the time of this code
    # Then you can see the triples that were able to be pulled out of the GeoLinked project:
    #           "C:/Users/holly/Desktop/GeoLinked/FinalGraph/MyGraph.ttl"
    # If you run other models, they will replace this file above, but if you need multiple runnin,
    # then a versioning system will have to added to the processing, probably back in the GeoLinked Project or running GeoLinked from here
    # For now, this is the process of pulling levels and spaces from the models with SPARQL queries:
    outputfile = 'C:/Users/holly/Desktop/GeoLinked/FinalGraph/MyGraph.ttl'  # From the top folder and in FinalGraph
    SGA_Based_Graph = Graph()
    SGA_Based_Graph = SGA_Based_Graph.parse(outputfile, format="turtle")
    #SGA_Based_Graph.serialize(destination=outputfile, format='turtle')
    graph_data = GraphData()
    # I have added a few examples of how you might colelct a certain type of data from the graph
    # You will need to add more queries that retrieve and format the information as you see fit per the project needs

    # If uncommented, will print all data in graph so you can learn the structure and what you can and cannot ask it for
    print "Running All Data Example Query"
    graph_data.get_all_data(SGA_Based_Graph)

    # If uncommented, will return levels in the building and their heights as a dict: [spaceBoundary: (list of data)]
    print "Running Levels Example Query"
    levels = graph_data.get_levels(SGA_Based_Graph)  # Just copying MyGraph.ttl from other project for now
    for i in levels:
        print i, len(levels[i]), levels[i]

    # If uncommented, will return spaces in their respective building if multi-building: [space_collection: (list of spaces)]
    print "Running Spaces Example Query"
    spaces1 = graph_data.get_spaces(SGA_Based_Graph)  # Just copying MyGraph.ttl from other project for now
    for i in spaces1:
        print i, len(spaces1[i]), spaces1[i]

    # Call Green Scale..................................................................................................
    # Running the GS Tool (it has been updated to 2016 Revit) will need ot be added as this project progresses
    GreenScale_InitialRun = 0 # Change flag once first run is complete
    # Currently using locally stored files, will need to add this API automation from my scrips from Drive
    # Note, in script, will need to reset the location of the stored file to be findable by this next lines
    #inputfileGBXML = Call API script using IronPython
    inputfileGBXML = 'C:/Users/hfergus2/Desktop/Orchestration/TempXMLs/RC_FRAME_2016.xml'
    #Call GS Code (will run Thermal and EE), will want to store results plus return a dictinoary of EE values


    # Query for pre-analysis Matlab Module..............................................................................
    # Call Matlab Modules as needed, example call works like this using the import pymatlab library:
    # Example is form http://compgroups.net/comp.lang.python/calling-a-matlab-gui-from-python-using-pymat/1687289
    #mlabsession = MatlabSession()
    #mlabsession.run('cd ~/path_to_project')
    #mlabsession.run('addpath(genpath(pwd))')
    #mlabsession.run('run path-to-.m-script')

    print "Main Finished"

if __name__ == "__main__":
    #logging.basicConfig()
    main(sys.argv[1:])
    #main(inputfile, outputfile)




