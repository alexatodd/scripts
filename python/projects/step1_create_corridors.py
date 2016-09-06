# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# prep_corridor_roads.py
# Created on: 2016-03-04 11:08:04.00000
#   (generated by ArcGIS/ModelBuilder)
# Usage: prep_corridor_roads <Workspace> 
# Description: 
# ---------------------------------------------------------------------------

# IMPORT ARCPY MODULE
import arcpy
from arcpy import env

# Input Parameters
scratch = arcpy.GetParameterAsText(0)
workspace =  arcpy.GetParameterAsText(1) #r"M:\plan\drc\projects\15090_High_Injury_Crash_Network\C_Data\Geodata\Crash_Analysis_2016_TEST.gdb" #
study_area = arcpy.GetParameterAsText(2) #
streets_lyr = arcpy.GetParameterAsText(3) #

arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True
# ****************************************************************************
# LOCAL VARIABLES:
# ****************************************************************************
# *street type codes*
# 1110 = FREEWAY
# 1200 = HIGHWAY
# 1300 = PRIMARY ARTERIAL
# 1400 = ARTERIAL
# 1450 = TERTIARY STREET - NEIGHBORHOOD COLLECTOR
# ***********************
# SOURCE DATA:
streets_lyr = r"K:\streets\streets.lyr"
study_area = r"K:\boundary\metropolitan_planning_area.lyr"
# Output
corridors = "corridors"
# Scratch output
streets_copy = scratch +"\\streets_copy"
Fwys_Dissolve = scratch +"\\street_type_fwys"
Streets_Dissolve = scratch +"\\street_type_nofwys"
street_types_merged = scratch +"\\street_types_merged"
xstreets = scratch +"\\xstreets"
corridors_long = scratch +"\\corridors_long"
corridors_split = scratch +"\\corridors_split"
corridors_mid = scratch +"\\corridors_mid"
# ***********************
# FIELDS
v = "VISIBLE"
h = "HIDDEN"
Ref_id = "UID"
parts = "parts"
buff_ID = "buff_ID"
dupFlag = "dupFlag"
street_types = []
fwy="fwy"
non_fwy="non_fwy"
streets_ID = "ORIG_FID"

field_dict = {
			fwy:{"fc":"metro_streets_Fwys","query":"\"TYPE\" = 1110 OR \"TYPE\" =1200","out_fc":Fwys_Dissolve,"layer":fwy+"_lyr"},
			non_fwy:{"fc":"metro_streets_noFwys","query":"(\"TYPE\" <> 1110 AND \"TYPE\" <> 1200) AND (\"STREETNAME\" is not null)","out_fc":Streets_Dissolve,"layer":non_fwy+"_lyr"},
			parts:{"type":"SHORT","query":"!Shape!.partCount"},
			"ORIG_FID":{"type":"LONG","query":"str(!OBJECTID!)"},
			buff_ID:{"type":"DOUBLE","query":"""float(str(!ORIG_FID!)+"."+str(!OBJECTID!))"""},
			dupFlag:{"type":"SHORT","query":0},
			Ref_id:{"stats":"Join_Count SUM; PREFIX FIRST; STREETNAME FIRST; severity_weight_auto SUM; severity_weight_ped SUM; severity_weight_bike SUM; Severity SUM","parts":"MULTI_PART","dissolve":"DISSOLVE_LINES"}}

# ****************************************************************************
# DEFINE FUNCTIONS
def communicateResults(message):
	arcpy.AddMessage(message)
	print (message)
def addLayerFields(fc, field_key=None):
	fc_lyr = fc+"_lyr"
	arcpy.MakeFeatureLayer_management(fc,fc_lyr)
	if field_key:
		for f in field_key:
			communicateResults("Adding and calculating field: "+str(f)+"...")
			arcpy.AddField_management(fc_lyr,f,field_dict[f]["type"])
			arcpy.CalculateField_management(fc_lyr,f,field_dict[f]["query"],"PYTHON_9.3","#")
	return fc_lyr
def saveInStudyArea(in_fc,select_type,select_fc,distance,out_fc,query=None):
	fc_lyr = in_fc+"_lyr"
	arcpy.MakeFeatureLayer_management(in_fc,fc_lyr,query)
	arcpy.MakeFeatureLayer_management(select_fc,select_fc+"_lyr")
	arcpy.SelectLayerByLocation_management(fc_lyr,select_type,select_fc+"_lyr", distance, "NEW_SELECTION")
	arcpy.CopyFeatures_management(fc_lyr,out_fc)
def streetPrep(street_type):
	arcpy.MakeFeatureLayer_management(streets_copy,field_dict[street_type]["fc"],field_dict[street_type]["query"], "", \
								"OBJECTID OBJECTID "+v+" NONE;\
								SHAPE SHAPE "+v+" NONE;\
								LOCALID LOCALID "+v+" NONE;\
								ZERO ZERO "+h+" NONE;\
								PREFIX PREFIX "+v+" NONE;\
								STREETNAME STREETNAME "+v+" NONE;\
								FTYPE FTYPE "+v+" NONE;\
								DIRECTION DIRECTION "+v+" NONE;\
								LEFTADD1 LEFTADD1 "+h+" NONE;\
								LEFTADD2 LEFTADD2 "+h+" NONE;\
								RGTADD1 RGTADD1 "+h+" NONE;\
								RGTADD2 RGTADD2 "+h+" NONE;\
								LEFTZIP LEFTZIP "+h+" NONE;\
								RIGHTZIP RIGHTZIP "+v+" NONE;\
								TYPE TYPE "+v+" NONE;\
								LCOUNTY LCOUNTY "+h+" NONE;\
								RCOUNTY RCOUNTY "+h+" NONE;\
								LCITY LCITY "+h+" NONE;\
								RCITY RCITY "+h+" NONE;\
								UP_DATE UP_DATE "+h+" NONE;\
								CR_DATE CR_DATE "+h+" NONE;\
								F_ZLEV F_ZLEV "+h+" NONE;\
								T_ZLEV T_ZLEV "+h+" NONE;\
								SHAPE_Length SHAPE_Length "+v+" NONE")
	communicateResults("Dissolving "+street_type+" street segments...")
	arcpy.Dissolve_management(field_dict[street_type]["fc"],field_dict[street_type]["out_fc"],"STREETNAME;DIRECTION","#","MULTI_PART","DISSOLVE_LINES")
	communicateResults("\tSuccessfully created: "+field_dict[street_type]["out_fc"])
	arcpy.MakeFeatureLayer_management(field_dict[street_type]["out_fc"],field_dict[street_type]["layer"],"#","#",
								"OBJECTID OBJECTID "+v+" NONE;\
								SHAPE SHAPE "+v+" NONE;\
								STREETNAME STREETNAME "+v+" NONE;\
								DIRECTION DIRECTION "+v+" NONE;\
								SHAPE_Length SHAPE_Length "+v+" NONE")
	street_types.append(field_dict[street_type]["layer"])
def CreateRefID(in_feature):
	communicateResults ("Creating reference ID...")
	communicateResults ("in_feature is:	" + in_feature)
	arcpy.AddXY_management(in_feature)
	arcpy.AddField_management(in_feature, Ref_id, "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
	arcpy.CalculateField_management(in_feature, Ref_id, "str(int(!POINT_X!))+\"-\"+str(int(!POINT_Y!))", "PYTHON", "")
	communicateResults ("Successfully added "+Ref_id + " to " + in_feature+".\n")

# ****************************************************************************
communicateResults("-----------------------------------------\nRunning Corridor Analysis...")
# # COPY RLIS STREETS DATA LAYER
arcpy.CopyFeatures_management(streets_lyr, streets_copy)
# # MAKE ROADS FEATURE LAYERS
streetPrep(fwy)
streetPrep(non_fwy)
communicateResults("Merging dissolved freeways and streets...\n")
arcpy.Merge_management(street_types, street_types_merged)
# # # ***********************************************************
# # # ***********************************************************
# # # Playing with cross-streets [work in progress]
# arcpy.FeatureToLine_management(street_types_merged,xstreets,"","ATTRIBUTES")
arcpy.MakeFeatureLayer_management(street_types_merged, "street_types_merged_lyr")
# # ***********************************************************
# # ***********************************************************
# NEW AS OF 16-05-26
# TO BREAK APART MULTIPART FEATURES THAT ARE MORE THAN A CERTAIN DISTANCE APART
sp1 = street_types_merged+"_sp1" # xstreets
sp1_buff = sp1+"_buff"
sp2 = sp1_buff+"_single"
list_fields = ["STREETNAME", "DIRECTION",buff_ID, dupFlag]

communicateResults("Starting analysis of multipart polylines...\n\tPrepping data...")
# arcpy.AddField_management(sp1,buff_ID, "DOUBLE")
# arcpy.CalculateField_management(sp1, buff_ID, 0)
# addLayerFields(sp1,[dupFlag])
sp1_lyr = sp1+"_lyr"
# # arcpy.MultipartToSinglepart_management("street_types_merged_lyr",sp1)
# arcpy.Buffer_analysis(sp1_lyr,sp1_buff, "75 Feet","FULL","ROUND","LIST",list_fields)
# # # ADD FIELD TO BUFFERS AND CALCULATE PARTS (CREATE LAYER)
# addLayerFields(sp1_buff,[parts])
sp1_buff_lyr = sp1_buff+"_lyr"

# arcpy.SelectLayerByAttribute_management(sp1_buff_lyr,"NEW_SELECTION",'"Parts" > 1')
# arcpy.MultipartToSinglepart_management(sp1_buff_lyr,sp2)

# addLayerFields(sp2,[buff_ID])
sp2_lyr = sp2+"_lyr"

arcpy.MultipartToSinglepart_management("street_types_merged_lyr",sp1)
arcpy.Buffer_analysis(sp1,sp1_buff,"75 Feet","FULL","ROUND","LIST",streets_ID)
# # ADD FIELD TO BUFFERS AND CALCULATE PARTS (CREATE LAYER)
addLayerFields(sp1_buff,[parts])
arcpy.SelectLayerByAttribute_management(sp1_buff+"_lyr","NEW_SELECTION",'"Parts" > 1')
arcpy.MultipartToSinglepart_management(sp1_buff+"_lyr",sp2)
addLayerFields(sp2,[buff_ID])
# # MAKE A LAYER OF THE SINGLE PART STREETS...
# # ...ADD A FIELD FOR THE CORRESPONDING BUFF_ID
# # ...AND ADD A FIELD TO FLAG DUPLICATE BUFFERS
addLayerFields(sp1,[buff_ID,dupFlag])
arcpy.CalculateField_management(sp1_lyr, buff_ID, 0)
# # MAKE A LAYER OF THE SINGLE PART STREETS...
# # ...ADD A FIELD FOR THE CORRESPONDING BUFF_ID
# # ...AND ADD A FIELD TO FLAG DUPLICATE BUFFERS
communicateResults("\tStarting search cursors...")
# # USE A SEARCH CURSOR TO SELECT EACH BUFFER (ONE BY ONE) AND THEN
# # USE THIS SELECTION TO SELECT STREET SEGMENTS THAT FALL WITHIN
tempT = 'tempfcTable'
arcpy.MakeTableView_management(sp2_lyr, tempT) #! changed from sp2 to sp2_lyr
values = [row[0] for row in arcpy.da.SearchCursor(tempT, buff_ID)]
uniqueValues = set(values)
buffs = str(len(uniqueValues))
communicateResults("\tTotal buffered polylines: "+buffs)
buffCount = 0
for aValue in uniqueValues:
	arcpy.SelectLayerByAttribute_management(sp2_lyr,"NEW_SELECTION", """\""""+buff_ID+"""\" = """+str(aValue)+"""\"""")
	arcpy.SelectLayerByLocation_management(sp1_lyr,"WITHIN_CLEMENTINI",sp2_lyr,"","NEW_SELECTION")
	arcpy.MakeFeatureLayer_management(sp1_lyr,sp1_lyr+"_temp")
	buffids = [row[0] for row in arcpy.da.SearchCursor(sp1_lyr+"_temp",buff_ID)]
	uniqueIds = set(buffids)
	for anId in uniqueIds:
		if not anId:
			buffCount += 1
			communicateResults(str(buffCount)+"/"+str(buffs)+"\tadding "+str(aValue)+" to "+str(buff_ID)+" of "+ str(sp1_lyr))
			arcpy.CalculateField_management(sp1_lyr+"_temp", buff_ID, aValue)
		else:
			communicateResults("\t\tDuplicate: "+str(anId))
			arcpy.CalculateField_management(sp1_lyr+"_temp",dupFlag,1)
communicateResults("\tCompleted search cursor. "+str(buffCount)+" unique buff_IDs.")
arcpy.SelectLayerByAttribute_management(sp1_lyr,"NEW_SELECTION","""\""""+buff_ID+"""\" = 0""")
arcpy.CalculateField_management(sp1_lyr,buff_ID,"OBJECTID") #! changed from ORIG_FID to OBJECTID
arcpy.SelectLayerByAttribute_management(sp1_lyr,"CLEAR_SELECTION")
arcpy.Dissolve_management(sp1_lyr,corridors_long,["STREETNAME","DIRECTION",buff_ID],"#","MULTI_PART","DISSOLVE_LINES")
communicateResults("Successfully created single parts from multipart lines with gaps.")
# # # **********************************************************
# # # **********************************************************
# # THIS IS NEW CONTENT AS OF 5-17-16
# # INCLUDED AS A WAY TO REDUCE ROAD SEG LENGTHS
# # TAKEN FROM M:\plan\drc\projects\15090_High_Injury_Crash_Network\G_Scripts_Tools\split_lines.py
corridors_long_lyr = corridors_long+"_lyr"

# arcpy.MakeFeatureLayer_management(corridors_long,corridors_long_lyr)
temp_gdb = r"M:\plan\drc\projects\15090_High_Injury_Crash_Network\C_Data\Geodata\temp.gdb"

temp_fc = temp_gdb+"\\temp_fc"
temp_points = temp_gdb+"\\temp_points"
in_fc = temp_fc
temp_fc_layer = corridors_long_lyr

max_len = 5280 * 3
test = True
splitCount = 0

arcpy.CopyFeatures_management(corridors_long,in_fc)
communicateResults("Splitting roads greater than " + str( max_len / 5280 ) + " miles...")
while test:
	splitCount += 1
	communicateResults("\tRound "+str(splitCount))
	arcpy.MakeFeatureLayer_management(in_fc, temp_fc_layer)
	# PROCESS: SELECT LAYER BY ATTRIBUTE
	arcpy.SelectLayerByAttribute_management(temp_fc_layer, "NEW_SELECTION", "\"Shape_Length\" > "+str(max_len)+"\"")
	# PROCESS: GET COUNT
	feature_count = int(arcpy.GetCount_management(temp_fc_layer).getOutput(0))
	if feature_count == 0: 
		test = False
		break
	else:
		communicateResults("\tSelected: "+str(feature_count))
		# Process: Feature Vertices To Points
		communicateResults("\tCreating midpoints...")
		temp_points = temp_points + str(splitCount)
		arcpy.FeatureVerticesToPoints_management(temp_fc_layer, temp_points, "MID")
		# Process: Split Line at Point
		communicateResults("\tSplitting lines...")
		temp_fc = temp_fc + str(splitCount)
		arcpy.SplitLineAtPoint_management(in_fc, temp_points, temp_fc, "6 Feet")
		in_fc = temp_fc
arcpy.CopyFeatures_management(in_fc, corridors_split)
communicateResults("Successfully split corridors.")
# # **********************************************************
# # **********************************************************
communicateResults("\nCopying corridors within the study area...")
saveInStudyArea(corridors_split,"HAVE_THEIR_CENTER_IN",study_area,"100 Feet",corridors,"""\"SHAPE_Length\" >2640""")
