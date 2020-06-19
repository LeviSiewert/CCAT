import bpy
import os
import sys
from pathlib import Path
from bpy.props import BoolProperty, PointerProperty, \
	StringProperty, EnumProperty
import os
import subprocess
import json
import ensurepip
import datetime
import shutil

#ensurepip.bootstrap()
pybin = bpy.app.binary_path_python
subprocess.check_call([pybin, '-m', 'pip', 'install', 'openpyxl'])

import openpyxl

bl_info = {
	"name": "CCAL",
	"author": "Your Name Here",
	"version": (1, 0),
	"blender": (2, 80, 0),
	"location": "View3D > Add > Mesh > New Object",
	"description": "Adds a new Mesh Object",
	"warning": "",
	"doc_url": "",
	"category": "Add Mesh"}
#fun/op that copies and phastes latf excel + json to folder path if 


class MyEnumItems(bpy.types.PropertyGroup):
	@classmethod
	def register(cls):
		bpy.types.Scene.my_enum_items = bpy.props.PointerProperty(type=MyEnumItems)

	@classmethod
	def unregister(cls):
		del bpy.types.Scene.my_enum_items

	sofenum : bpy.props.EnumProperty(
		name="S.O.F.",
		description="sofenum",
		items = (("def",",",""),("wip","W.I.P.","Work In Progress"),("blockout","Blockout","ye its a blockout"),("polish","Polishing","Polishing BB"),("prog","Progressive","PRogressivly working on and updateing model")),)
	teamenum : bpy.props.EnumProperty(
		name="Team",
		description = "teamenum",
		items = (("def",".",""),("mod","Modeling","Modeling Team"),("rig","Rigging","Rigging Team"),("tex","Texturing","Texturing Team"),("anim","Animation","Animation Team"), ("li","Lighting","Lighting Team")))
	atypeenum : bpy.props.EnumProperty(
		name="File Type/layer",
		description = "File Type/layer",
		items = (("def",".",""),("asset","Asset",""),("Env","Enviroment",""),("anim","Animation File",""),("lig","Lighting",""),("subenv","Sub Envirment","")))
	la_ex: StringProperty(
		name = "Local asset tracking file",
		default = "",
		description = "Place the prop overview excel file Here",
		subtype = "FILE_PATH")

class OT_copylatf(bpy.types.Operator):
	bl_label = "Create New LATF file"
	bl_idname= "ccal.copylatf"
	
	def execute(self, context):
		#pref = bpy.context.preferences.addons[__name__].preferences
		#print(pref.ao_ex)
		copyflnamelist = ["latf.xlsx","latfjson.txt"]
		for i in copyflnamelist:
			filepath = (bpy.utils.user_resource('SCRIPTS', "addons") + "\\"+__name__+ "\\"+"bin"+"\\"+i)
			filedest = os.path.dirname(bpy.context.blend_data.filepath)
			print ("ccal: copying", i ,"from bin to file location")
			shutil.copy2(filepath,filedest)
		return {'FINISHED'}

class OT_TestOP(bpy.types.Operator):
	bl_label = "test operation"
	bl_idname= "ccal.testop"
	
	def execute(self, context):
		#pref = bpy.context.preferences.addons[__name__].preferences
		#print(pref.ao_ex)
		return {'FINISHED'}

def msgbox(message="", title="Message Box", icon= 'INFO'):
	def draw(self, context):
		self.layout.label(text=message)
	bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

def cellinfo (col, min, max, sheet):
	#returns a library of the ranges defined w/  the values as keys in lowercase
	cell_dic = {}
	rangevalues = []
	
	for i in range(min,max):
		rangevalues.append(col + str(i))
	print (rangevalues[-1])
	for b in rangevalues:
		print 
		if sheet[b].value == None:
			continue
		cell_dic.update({sheet[b].value.lower():b})

	return cell_dic    

class OT_write(bpy.types.Operator):
	bl_idname = "ccal.write"
	bl_label = "get variables from name"

	#call this to assign variables to the scene 

	def execute(self, context):
		basefilename = bpy.path.basename(bpy.context.blend_data.filepath)
		filename = basefilename.split("_")
		filedir = os.path.dirname(bpy.context.blend_data.filepath)
		pref = context.preferences.addons[__name__].preferences
		latfexcelloc = bpy.context.scene.my_enum_items.la_ex
		latfexceldir = os.path.dirname(bpy.path.abspath(latfexcelloc))


		if filename[0].isdigit() == False:
			if filename[0].lower() =="r":
				filetype = "run"
				#file is running, cancel writing of script
				#return "cancelwrite"
			elif  filename[0].lower() == "asset":
				#file is of the finished asset type, team is later overwritten/created by the dropdown menu
				#needs work
				filetype = "fin" if bpy.context.scene.my_enum_items.teamenum == 'def' else bpy.context.scene.my_enum_items.teamenum
				vteam = "tex"
				vatype = filename[0].lower()
				vtype = filename[1].lower()
				vclass = filename[2].lower()
				vvnum = filename[-1].replace('.blend', '')
				print (vatype, vtype, vclass, vvnum)
			else:
				#file is not running or finished asset, continue writing process.
				#replace with assignments to scene variables.
				filetype = "asset" 
				vteam = filename[0].lower() if bpy.context.scene.my_enum_items.teamenum == 'def' else bpy.context.scene.my_enum_items.teamenum
				vatype = filename[1].lower()
				vtype = filename[2].lower()
				vclass = filename[3].lower()
				vid = filename[4].lower()
				vvnum = filename[5].replace('.blend', '')
				print (vteam, vatype, vtype, vclass, vvnum)
			print (filetype)
			#write to latf
			#need to make this filedir a user assignable variable, and if no file exists dont write
			print(bpy.path.abspath(latfexceldir + "\\latfjson.txt"))
			with open(bpy.path.abspath(latfexceldir + "\\latfjson.txt")) as json_file:
				latfjson = json.load(json_file)
			latfexcel = openpyxl.load_workbook(bpy.path.abspath(latfexcelloc))
			latfsheet = latfexcel.active
			latfsheet.insert_rows(8)
			latfsheet[latfjson["dat"]] = datetime.datetime.now()
			latfsheet[latfjson["fname"]] =  bpy.path.basename(bpy.context.blend_data.filepath)
			latfsheet[latfjson["artist"]] = pref.artistname
			latfsheet[latfjson["sof"]] = bpy.context.scene.my_enum_items.sofenum
			latfsheet[latfjson["team"]] = vteam
			latfsheet[latfjson["vnum"]] = vvnum 
			latfsheet[latfjson["sof"+vteam]] = bpy.context.scene.my_enum_items.sofenum

			latfexcel.save(bpy.path.abspath(latfexcelloc))
			latfexcel.close()
			#/write to latf

			#search and write to files.
			aofplist = [pref.ao_ex, pref.car_ex, pref.char_ex, pref.prop_ex]

			for i in aofplist:

				if os.path.isdir(i):
					msgbox("Error: preferences points to directory not excel file", "CCAL Plugin", 'ERROR')
					print("Error: preferences points to directory not excel file")
					continue

				if i.lower().endswith(".xlsx") == False:
					msgbox("Error: preferences points to" + bpy.path.basename(i) + "which is not a excel file", "CCAL Plugin", 'ERROR')
					print ("Error: preferences points to" + bpy.path.basename(i) + "which is not a excel file")
					continue
				#bug here. runs all code even after continue is suppost to jump to next itteration
				print (i)

				aoexcel = openpyxl.load_workbook(i)
				aosheet = aoexcel.active
				print (bpy.path.basename(i))
				
				jsonname = (bpy.path.abspath(i)).replace(bpy.path.basename(i),'') + (bpy.path.basename(i)).split(".")[0] + "json.txt"
				print (jsonname) 

				with open(jsonname) as json_file:
					aojson = json.load(json_file)


				col = (str(aojson["id"]))[0]
				
				celldic = cellinfo(col,int((str(aojson["id"]))[1:]), 150, aosheet)

				if vid in celldic:
					row = (str(celldic[vid]))[1:] #results in row from id found in dictionary
					aosheet[(str(aojson["sof"+vteam]))[0] + row] = bpy.context.scene.my_enum_items.sofenum
					#current problem: dic only returns asset, doesnt support ma asset, later func needed (if statment checking m asset and replacing variables?)

					aoexcel.save(bpy.path.abspath(i))
					aoexcel.close()
					print("ccal: printed to", aofplist , "at row", row)
					break
				else:
					print ("ccal: Did not find cell in", i)
					
		else:
			print("ccal: scene file, not yet supported")
			#this file is a scene file, run checks for scene files

		return{'FINISHED'}


class CCAT_PT_PrimPanel(bpy.types.Panel):
	bl_label = "Crown Creations"
	bl_idname = "CCAT_PT_PrimPanel"
	bl_space_type = "VIEW_3D"   
	bl_region_type = "UI"
	bl_category = "simple panel"
	bl_context = "objectmode"
	
	
	def draw(self, context):
		layout = self.layout
		#layout.prop(context.scene.my_enum_items, "atypeenum")
		layout.prop(context.scene.my_enum_items, "teamenum")
		layout.prop(context.scene.my_enum_items, "sofenum")
		layout.prop(context.scene.my_enum_items, "la_ex", text="local Asset excel")
		if bpy.context.scene.my_enum_items.la_ex == '':
			layout.operator("ccal.copylatf")


class CCAL_PT_PrefPanel(bpy.types.AddonPreferences):
	bl_idname = __name__
	ao_ex: StringProperty(
		name = "Asset overview Excel File",
		default = os.path.splitdrive(__file__)[0],
		description = "Place the Asset overview excel file Here",
		subtype = "FILE_PATH")

	car_ex: StringProperty(
		name = "Car overview Excel File",
		default = os.path.splitdrive(__file__)[0],
		description = "Place the Car overview excel file Here",
		subtype = "FILE_PATH")
	
	char_ex: StringProperty(
		name = "Character overview Excel File",
		default = os.path.splitdrive(__file__)[0],
		description = "Place the Character overview excel file Here",
		subtype = "FILE_PATH")

	prop_ex: StringProperty(
		name = "prop overview Excel File",
		default = os.path.splitdrive(__file__)[0],
		description = "Place the prop overview excel file Here",
		subtype = "FILE_PATH")

	artistname: StringProperty(
		name = "Artist Name:",
		default = '',
		description = "What is your name good traveler?")

	def draw(self, context):
		layout = self.layout
		col = layout.column()
		col.prop(self, "ao_ex", text="Asset Overview Excel File")
		col.prop(self, "car_ex", text="Car Overview Excel File")
		col.prop(self, "char_ex", text="Character Overview Excel File")
		col.prop(self, "prop_ex", text="Prop Overview Excel File")
		col.prop(self, "artistname", text="Artist Name")

def register():
	bpy.utils.register_class(MyEnumItems)
	bpy.utils.register_class(OT_copylatf)
	bpy.utils.register_class(CCAT_PT_PrimPanel)
	bpy.utils.register_class(CCAL_PT_PrefPanel)
	bpy.utils.register_class(OT_write)
	bpy.utils.register_class(OT_TestOP)


def unregister():
	bpy.utils.unregister_class(MyEnumItems)
	bpy.utils.unregister_class(CCAT_PT_PrimPanel)
	bpy.utils.unregister_class(CCAL_PT_PrefPanel)
	bpy.utils.unregister_class(OT_TestOP)
	bpy.utils.unregister_class(OT_write)
	bpy.utils.unregister_class(OT_copylatf)

if __name__ == "__main__":
	register()
	