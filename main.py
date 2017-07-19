#-------------------------------------------------------------------------------
# Name:        main.py
# Purpose:     Resilience and Energy Orchestration Processing
#
# Author:      Holly Tina Ferguson hfergus2@nd.edu
#
# Created:     06/05/2017
# Copyright:   (c) Holly Tina Ferguson 2015
# License:     The University of Notre Dame
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

    # Take USGS data sets (3 curves) for a location and get back
    basedir = "C:\\Users\\holly\\Desktop\\USGS\\nshmp-haz-master\\curves_east_donotmodify"
    models = ["PGA","SA0P2","SA1P0"] #different types of hazard models used

    #read all files
    cityhazardfunctions = ReadHazardData(models,basedir) # nested dict. {city: {model: (X,Y) }}
    #print(json.dumps(cityhazardfunctions,indent=4)) #print to debug if something goes horrendously wrong

    # usgsdata = [[20, 18, 16, 14, 12, 10, 8, 6, 4, 2],[20, 19, 18, 15, 12, 11, 9, 6, 5, 2, 1]] #fakedata
    # querypoint = 10

    curv = Curves()

    city_splines = curv.querycurves(cityhazardfunctions,savefigs=True)

    print(city_splines["Chicago IL"]["PGA"]([0.42]))

    # Construct Semantic Graph..........................................................................................
    # Currently using locally stored files, will need to add this API automation from my scrips from Drive
    # Note, in script, will need to reset the location of the stored file to be findable by this next lines
    #inputfileIFCXML = Call API script using IronPython
    inputfileIFCXML = 'C:/Users/hfergus2/Desktop/Orchestration/TempXMLs/RC_FRAME.ifcxml'
    outputpath='output.csv'
    material_flag = 0
    level_flag = 0
    structure_flag = 0
    puncture_flag = 0
    test_query_sequence_flag = 0

    print "Constructing Graph"
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

    mylist_of_parameters = [str(inputfileIFCXML) + " " + str(outputpath) + " " + str(material_flag) + " " + str(level_flag) + " " + str(structure_flag) + " " + str(puncture_flag) + " " + str(test_query_sequence_flag)]
    subprocess.call(["python", "C:/Users/hfergus2/Desktop/GeoLinked/GeoLmain.py", str(inputfileIFCXML), str(outputpath), str(material_flag), str(level_flag), str(structure_flag), str(puncture_flag), str(test_query_sequence_flag) ])
    #subprocess.call(["python", "C:/Users/hfergus2/Desktop/GeoLinked/GeoLmain.py", "--args", str(inputfileIFCXML), str(outputpath), str(material_flag), str(level_flag), str(structure_flag), str(puncture_flag), str(test_query_sequence_flag) ])
    #USO_new = USOmain(inputfileIFCXML, outputpath, material_flag, level_flag, structure_flag, puncture_flag, test_query_sequence_flag)
    print "Storing Graph"
    #store it somewhere

    # Call Green Scale..................................................................................................
    GreenScale_InitialRun = 0
    # Currently using locally stored files, will need to add this API automation from my scrips from Drive
    # Note, in script, will need to reset the location of the stored file to be findable by this next lines
    #inputfileGBXML = Call API script using IronPython
    inputfileGBXML = 'C:/Users/hfergus2/Desktop/Orchestration/TempXMLs/RC_FRAME_2016.xml'
    #Call GS Code (will run Thermal and EE), will want to store results plus return a dictinoary of EE values



    # Query for pre-analysis Matlab Module

    # RSA parsing

    # Something about Damage Module

    # Loss Module



    print "Main Finished"

if __name__ == "__main__":
    #logging.basicConfig()
    main(sys.argv[1:])
    #main(inputfile, outputfile)




