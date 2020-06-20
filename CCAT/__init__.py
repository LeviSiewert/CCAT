# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
	"name":        "CCAT",
	"description": "Crow Creations Tracking addon",
	"author":      "Levi Siewert",
	"version":     (0, 4, 1),
	"blender":     (2, 80, 0),
	"location":    "View 3D > Tool Shelf > CCAT",
	"warning":     "",  # used for warning icon and text in addons panel
	"wiki_url":    "https://github.com/LeviSiewert/CCAT",
	"tracker_url": "https://github.com/LeviSiewert/CCAT/issues",
	"category":    "System"
	}


import bpy
import os
import sys
from pathlib import Path
from bpy.props import BoolProperty, PointerProperty, \
	StringProperty, EnumProperty
from bpy.app.handlers import persistent 
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

# updater ops import, all setup in this file
from . import addon_updater_ops


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
class OBJECT_PT_DemoUpdaterPanel(bpy.types.Panel):
	"""Panel to demo popup notice and ignoring functionality"""
	bl_label = "Updater Demo Panel"
	bl_idname = "OBJECT_PT_hello"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS' if bpy.app.version < (2, 80) else 'UI'
	bl_context = "objectmode"
	bl_category = "Tools"

	def draw(self, context):
		layout = self.layout

		# Call to check for update in background
		# note: built-in checks ensure it runs at most once
		# and will run in the background thread, not blocking
		# or hanging blender
		# Internally also checks to see if auto-check enabled
		# and if the time interval has passed
		addon_updater_ops.check_for_update_background()


		layout.label(text="Demo Updater Addon")
		layout.label(text="")

		col = layout.column()
		col.scale_y = 0.7
		col.label(text="If an update is ready,")
		col.label(text="popup triggered by opening")
		col.label(text="this panel, plus a box ui")

		# could also use your own custom drawing
		# based on shared variables
		if addon_updater_ops.updater.update_ready == True:
			layout.label(text="Custom update message", icon="INFO")
		layout.label(text="")

		# call built-in function with draw code/checks
		addon_updater_ops.update_notice_box_ui(self, context)

class OT_copylatf(bpy.types.Operator):
	bl_label = "Create New LATF file"
	bl_idname= "ccat.copylatf"
	
	def execute(self, context):
		#pref = bpy.context.preferences.addons[__name__].preferences
		#print(pref.ao_ex)
		copyflnamelist = ["latf.xlsx","latfjson.txt"]
		for i in copyflnamelist:
			filepath = (bpy.utils.user_resource('SCRIPTS', "addons") + "\\"+__name__+ "\\"+"bin"+"\\"+i)
			filedest = os.path.dirname(bpy.context.blend_data.filepath)
			print ("ccat: copying", i ,"from bin to file location")
			shutil.copy2(filepath,filedest)
		return {'FINISHED'}

class OT_TestOP(bpy.types.Operator):
	bl_label = "test operation"
	bl_idname= "ccat.testop"
	
	def execute(self, context):
		#pref = bpy.context.preferences.addons[__name__].preferences
		print("yeha, test class has been called")
		
		#return {'FINISHED'}


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
	bl_idname = "ccat.write"
	bl_label = "get variables from name"

	#call this to assign variables to the scene 
	def execute(self, context):
		#writeexcel(self, context)
		basefilename = bpy.path.basename(bpy.context.blend_data.filepath)
		filename = basefilename.split("_")
		filedir = os.path.dirname(bpy.context.blend_data.filepath)
		pref = context.preferences.addons[__name__].preferences



		if filename[0].isdigit() == False: #checks if file is scene or asset, missing ma support
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
			
			latfexcelloc = bpy.context.scene.my_enum_items.la_ex
			latfexceldir = os.path.dirname(bpy.path.abspath(latfexcelloc))

			
			#write to latf
			if not bpy.context.scene.my_enum_items.la_ex == '':
			#print(bpy.path.abspath(latfexceldir + "\\latfjson.txt"))
				with open(bpy.path.abspath(latfexceldir + "\\latfjson.txt")) as json_file:
					latfjson = json.load(json_file)
				latfexcel = openpyxl.load_workbook(bpy.path.abspath(latfexcelloc))
				latfsheet = latfexcel.active

				varnestedlist = [
				["dat" , datetime.datetime.now()],
				["fname" ,  bpy.path.basename(bpy.context.blend_data.filepath)],
				["artist" , pref.artistname],
				["sof" , bpy.context.scene.my_enum_items.sofenum],
				["team" , vteam],
				["vnum" , vvnum ],
				["sof"+vteam , bpy.context.scene.my_enum_items.sofenum]]

				for i in varnestedlist:
					i.append(latfsheet[latfjson[i[0]]].value == i[1])

				if not all([varnestedlist[1][2], varnestedlist[3][2], varnestedlist[4][2]]):
					latfsheet.insert_rows(8)
					for i in varnestedlist:
						latfsheet[latfjson[i[0]]] = i [1]
						
				else:
					print("CCAT: Not sufficient change to warrent latf log")

				latfexcel.save(bpy.path.abspath(latfexcelloc))
				
				latfexcel.close()
				
			else:
				msgbox("Error: no latf excel found, please assign","CCAT PLugin",'ERROR')
			#/write to latf


			#search and write to files.
			aofplist = [pref.ao_ex, pref.car_ex, pref.char_ex, pref.prop_ex]

			for i in aofplist:

				if os.path.isdir(i):
					msgbox("Error: preferences points to directory not excel file", "CCAT Plugin", 'ERROR')
					print("Error: preferences points to directory not excel file")
					continue

				if i.lower().endswith(".xlsx") == False:
					msgbox("Error: preferences points to" + bpy.path.basename(i) + "which is not a excel file", "CCAT Plugin", 'ERROR')
					print ("Error: preferences points to" + bpy.path.basename(i) + "which is not a excel file")
					continue
				#bug here. runs all code even after continue is suppost to jump to next itteration 
					#bug not currently observed?
				print (i)

				aoexcel = openpyxl.load_workbook(i)
				aosheet = aoexcel.active
				print (bpy.path.basename(i))
				
				jsonname = (bpy.path.abspath(i)).replace(bpy.path.basename(i),'') + (bpy.path.basename(i)).split(".")[0] + "json.txt"
				print (jsonname) 

				with open(jsonname) as json_file:
					aojson = json.load(json_file)


				col = (str(aojson["id"]))[0]
				
				celldic = cellinfo(col,int((str(aojson["id"]))[1:]), 300, aosheet)
					#required: dynamic upper limit based on break of 3-5 empty cells

				if vid in celldic:
					row = (str(celldic[vid]))[1:] #results in row from id found in dictionary
					aosheet[(str(aojson["sof"+vteam]))[0] + row] = bpy.context.scene.my_enum_items.sofenum
					#current problem: dic only returns asset, doesnt support ma asset, later func needed (if statment checking m asset and replacing variables?)
					aoexcel.save(bpy.path.abspath(i))
					aoexcel.close()
					print("ccal: printed to", aofplist , "at row", row)
					break
				else:
					print ("ccat: Did not find cell in", i)
					aoexcel.close()
					
		else:
			print("ccat: scene file, not yet supported")
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
		layout.prop(context.scene.my_enum_items, "teamenum")
		layout.prop(context.scene.my_enum_items, "sofenum")
		layout.prop(context.scene.my_enum_items, "la_ex", text="local Asset excel")
		if bpy.context.scene.my_enum_items.la_ex == '':
			layout.operator("ccat.copylatf")




@addon_updater_ops.make_annotations
class CCAT_PT_PrefPanel(bpy.types.AddonPreferences):
	"""Demo bare-bones preferences"""
	bl_idname = __package__

	# addon updater preferences

	auto_check_update = bpy.props.BoolProperty(
		name="Auto-check for Update",
		description="If enabled, auto-check for updates using an interval",
		default=False,
		)
	updater_intrval_months = bpy.props.IntProperty(
		name='Months',
		description="Number of months between checking for updates",
		default=0,
		min=0
		)
	updater_intrval_days = bpy.props.IntProperty(
		name='Days',
		description="Number of days between checking for updates",
		default=7,
		min=0,
		max=31
		)
	updater_intrval_hours = bpy.props.IntProperty(
		name='Hours',
		description="Number of hours between checking for updates",
		default=0,
		min=0,
		max=23
		)
	updater_intrval_minutes = bpy.props.IntProperty(
		name='Minutes',
		description="Number of minutes between checking for updates",
		default=0,
		min=0,
		max=59
		)
	
	#my preferences
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

		# works best if a column, or even just self.layout
		mainrow = layout.row()
		col = mainrow.column()
		col.prop(self, "ao_ex", text="Asset Overview Excel File")
		col.prop(self, "car_ex", text="Car Overview Excel File")
		col.prop(self, "char_ex", text="Character Overview Excel File")
		col.prop(self, "prop_ex", text="Prop Overview Excel File")
		col.prop(self, "artistname", text="Artist Name")
		# updater draw function
		# could also pass in col as third arg
		addon_updater_ops.update_settings_ui(self, context)

		# Alternate draw function, which is more condensed and can be
		# placed within an existing draw function. Only contains:
		#   1) check for update/update now buttons
		#   2) toggle for auto-check (interval will be equal to what is set above)
		# addon_updater_ops.update_settings_ui_condensed(self, context, col)

		# Adding another column to help show the above condensed ui as one column
		# col = mainrow.column()
		# col.scale_y = 2
		# col.operator("wm.url_open","Open webpage ").url=addon_updater_ops.updater.website

@persistent
def writeonsave(self, context):
	return {bpy.ops.ccat.write()}
	#throwing '''TypeError: unhashable type: 'set'''' for some reason, but it works

classes = (
	#DemoPreferences,
	OBJECT_PT_DemoUpdaterPanel,
	MyEnumItems,
	OT_write,
	OT_copylatf,
	CCAT_PT_PrimPanel,
	CCAT_PT_PrefPanel,
	OT_TestOP

)




def register():

	bpy.app.handlers.save_post.append(writeonsave)
	# addon updater code and configurations
	# in case of broken version, try to register the updater first
	# so that users can revert back to a working version
	addon_updater_ops.register(bl_info)
	


	# register the example panel, to show updater buttons
	for cls in classes:
		addon_updater_ops.make_annotations(cls) # to avoid blender 2.8 warnings
		bpy.utils.register_class(cls)
	


def unregister():
	bpy.app.handlers.save_post.remove(writeonsave)
	# addon updater unregister
	addon_updater_ops.unregister()

	# register the example panel, to show updater buttons
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
