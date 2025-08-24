import bpy
from bpy.types import AddonPreferences
from bl_ui.utils import PresetPanel
from bpy.types import Panel, Menu, PropertyGroup, Operator,UIList
from bl_operators.presets import AddPresetBase
from .utils import ObjNameWithoutNum
from bpy.props import StringProperty, IntProperty, CollectionProperty
# preset menu
class Export_MT_presets(Menu):
    bl_label = "Export Presets"
    preset_subdir = "export_Prop"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset

class Export_PT_presets(PresetPanel, Panel):
    bl_label = 'Export Presets'
    preset_subdir = 'export_prop_save'
    preset_operator = 'script.execute_preset'
    preset_add_operator = 'gamedev_export.preset_add'

class Export_OT_add_preset(AddPresetBase, Operator):
    bl_idname = "gamedev_export.preset_add"
    bl_label = "Add a new preset"
    preset_menu = "Export_MT_presets"

    # Variable used for all preset values
    preset_defines = ["Export_Prop = bpy.context.scene.export_Prop","operatorparam_list = bpy.context.scene.operatorparam_list",]

    # Properties to store in the preset
    preset_values = [
        "Export_Prop.ForwardAxis",
        "Export_Prop.UpwardAxis",
        "Export_Prop.CustomProps",
        "Export_Prop.Modifiers",
        "Export_Prop.SourceDir",
        "Export_Prop.RunOperators",
        "operatorparam_list"

    ]

    # Where to store the preset
    preset_subdir = "export_prop_save"

def updateCategory(self, context):
    GameDev_CustomExportPanel.bl_category = bpy.context.preferences.addons[
        __package__].preferences.String_Catergory

    try:
        bpy.utils.unregister_class(GameDev_CustomExportPanel)

    except:
        pass

    bpy.utils.register_class(GameDev_CustomExportPanel)


class GameDev_CustomExportPanel(Panel):
    bl_label = "GameDev Export"
    bl_idname = "gamedev_export.panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Export'
    #bl_options = {'DEFAULT_CLOSED'}
    bl_context = "objectmode"


    def draw(self, context):
        pref = bpy.context.preferences.addons[__package__].preferences
        scene = context.scene
        Prop = scene.export_Prop
        layout = self.layout
        

        obj=context.object

        if pref.bool_Enable_MiscOperators==True:
            box=layout.box()
            col=box.column()

            row = col.row(align = True)
            row.alignment = 'CENTER'
            row.label(text=Prop.CurrentTime,icon='TIME')

            row = col.row(align = True)
            row.alignment = 'CENTER'
            row.label(text='Take a break every hour!',icon='FUND')

            row = col.row(align = True)
            row.scale_y = 1.5
            row.operator("web.playlist", icon="SOUND",
                        text="Music playlist") 
            
            row = col.row(align = True)
            row.scale_y = 1.5
            row.operator("view3d.scalemesh", icon="USER",
                        text="Scale Ref")     
        
        box=layout.box()
        col=box.column()
        
        header, panel = box.panel("_PT_Save_Files", default_closed=False)
        header.label(text="Save Files")
        if panel:
            box = panel.box()
            col=box.column()

            row = col.row(align = True)
            row.alignment = 'CENTER'
            row.label(text='Save Blend File')

            row = col.row(align = True)
            row.prop(Prop, "SourceDir")

            row = col.row(align = True)
            row.prop(Prop, "FileName")

            row = col.row(align = True)
            row.scale_y = 1.5
            row.operator("view3d.folder_struct",
                            icon="NEWFOLDER", text="folder structure save")
            row.operator("view3d.open_directory",
                            icon="FILE_FOLDER", text="Open Directory")    

            row = col.row(align = True)
            row.scale_y = 1.5 
            row.operator("view3d.open_reference",
                            icon="FILE_FOLDER", text="Open/Save Reference")     
                
            unit = scene.unit_settings
            row = col.row(align = True)
            row.alignment = 'CENTER'
            row.prop(unit, "system")
            
            row = col.row(align = True)
            row.alignment = 'CENTER'
            row.prop(unit, "length_unit")
        
        box=layout.box()
        col=box.column()
        header, panel = col.panel("_PT_Modify_Object", default_closed=True)
        header.label(text="Modify Object")
        if panel:
            box = panel.box()
            col=box.column()
            row = col.row(align = True)
            
            row.alignment = 'CENTER'
            row.label(text='Object Modifiers')       
            

            row = col.row(align = True)
            row.scale_y = 1.5
            
            ColLable=''
            obj = []
            obj = bpy.context.selected_objects

            ColLable = 'Selected Objects: '+str(len(obj))
            row.label(text= (ColLable) )


            #Re add this code when ready to add now rename method
            # if Prop.HPCollection or Prop.LPCollection == None:
            #    ColLable= 'please select HP and LP collection'
            
            # if Prop.HPCollection and Prop.LPCollection != None:
            #   

            #     for i in Prop.LPCollection.all_objects: 
            #         obj.append(i) 
            #     for i in Prop.HPCollection.all_objects: 
            #         obj.append(i) 

            #     if len(obj)%2==0:
            #         ColLable = 'Selected Objects:'+str(len(obj))
            #     else:
            #         ColLable = 'Selected Objects: '+str(len(obj)) +('    Please select a even amount')
            


            # row = col.row(align = True)
            # row.prop(Prop, "HPCollection")
            # row.prop(Prop, "LPCollection")

            row = col.row(align = True)
            row.scale_y = 1.5
            row.operator("view3d.old_rename_children", icon="SORTALPHA",
                        text="Match & Rename")

            row = col.row(align = True)
            row.scale_y = 1.5
            row.prop(Prop, "Modifierlist")
    
            row = col.row(align = True)

            row.operator("view3d.remove_modifier_type", icon="REMOVE",
                        text="remove modifier type")
            
            row.operator("view3d.apply_modifier_type", icon="CHECKMARK",
                    text="Apply modifier type")       

            row = col.row(align = True)
                    
            row.operator("view3d.make_single_user", icon="USER",
                    text="Make single User")   
        
        box=layout.box()
        col=box.column()
        header, panel = col.panel("_PT_HighPoly_LowPoly", default_closed=True)
        header.label(text="High Poly, Low Poly")
        if panel:
            box = panel.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Low Poly And HighPoly Export')
            
            col=box.column()
            row = col.row(align = True)
            row.alignment = 'CENTER'
            row.label(text='Object name : '+(ObjNameWithoutNum()))
            
            col=box.column()

            row = col.row(align = True) 
            row.prop(Prop,"TextureRes")
            row.prop(Prop, "bool_Enable_BakeOnExport")
            


            row = col.row(align = True)
            row.scale_y = 1.5
            lpExport=row.operator("view3d.custom_export", icon="MESH_CIRCLE",
                        text="Export LowPoly")
            lpExport.LP = True
            lpExport.HP = False

            row.scale_y = 1.5
            hpExport=row.operator("view3d.custom_export", icon="MESH_UVSPHERE",
                        text="Export HighPoly")
            hpExport.LP = False
            hpExport.HP = True

            row = col.row(align = True)
            row.operator("view3d.open_painter_file",
                        icon="IMAGE", text="Open Painter File")   
        
        box=layout.box()
        col=box.column()
        header, panel = col.panel("_PT_Standard_Export", default_closed=True)
        header.label(text="Standard Export")
        
        if panel:
            box = panel.box()

            row = box.row()
            
            row.alignment = 'CENTER'
            row.label(text='Final Export')

            row = box.row()
            row.prop(Prop, "ForwardAxis")
            row.prop(Prop, "UpwardAxis")

            row = box.row()
            row.prop(Prop, "CustomProps")
            row.prop(Prop, "Modifiers")

            row = box.row()
            row.scale_y = 1
            row.operator("view3d.validatemesh",
                        icon="CHECKBOX_HLT", text="Validate Asset")
            
            row = box.row()
            row.scale_y = 1.5
            exportOperator=row.operator("view3d.custom_export", icon="EXPORT", text="Export")
            exportOperator.LP=False
            exportOperator.HP=False

            # row = box.row()
            # row.scale_y = 1
            # box.template_collection_exporters()


            # row.operator("view3d.custom_export_experimental",
            #             icon="CHECKBOX_HLT", text="Export Experimental")


        
        box=layout.box()
        col=box.column()
        header, panel = col.panel("_PT_Advance", default_closed=True)
        header.label(text="Advance")
        if panel:
            box = panel.box()
            row = box.row()
            row.prop(Prop,"RunOperators")
            
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text="Export Operator List")

            row = box.row()
            row.template_list("MY_UI_OperatorParamList", "The_List", scene,
                            "operatorparam_list", scene, "operatorparam_list_index")

            row = box.row()
            row.operator('operatorparam_list.new_item', text='NEW')
            row.operator('operatorparam_list.delete_item', text='REMOVE')

            if scene.operatorparam_list_index >= 0 and scene.operatorparam_list:
                item = scene.operatorparam_list[scene.operatorparam_list_index]
                
                row = box.row()
                row.prop(item, "name")

            row = box.row()
            row.operator('operatorparam_list.run', text= 'Run')
        
        col=box.column()

class OperatorListItem(PropertyGroup):
    """Group of properties representing an item in the list."""


    def get_prop_items(self, context, edit_text):
        #print(edit_text)
        searchlist=[]

        for a in dir(bpy.ops):
            for i in dir(getattr(bpy.ops, a)):
                i="bpy.ops."+str(a)+"."+str(i)+"()"
                searchlist.append(i)
        return (searchlist)

    name: StringProperty(
           name="bl_id",
           description="A name for this item",
           default="Insert Operator ID",
           maxlen=2000,
           search=get_prop_items
           , search_options={'SUGGESTION'})
    
class MY_UI_OperatorParamList(UIList):
    """Demo UIList."""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

        # We could write some code to decide which icon to use here...
        custom_icon = 'OBJECT_DATAMODE'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon = custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon = custom_icon)

class OperatorParamList_OT_NewItem(Operator):
    """Add a new item to the list."""

    bl_idname = "operatorparam_list.new_item"
    bl_label = "Add a new item"

    def execute(self, context):
        context.scene.operatorparam_list.add()
   
        return{'FINISHED'}

class OperatorParamList_OT_DeleteItem(Operator):
    """Delete the selected item from the list."""

    bl_idname = "operatorparam_list.delete_item"
    bl_label = "Deletes an item"

    @classmethod
    def poll(cls, context):
        return context.scene.operatorparam_list

    def execute(self, context):
        operatorparam_list = context.scene.operatorparam_list
        index = context.scene.operatorparam_list_index

        operatorparam_list.remove(index)
        context.scene.operatorparam_list_index = min(max(0, index - 1), len(operatorparam_list) - 1)

        return{'FINISHED'}

class OperatorParamList_OT_Run(Operator):
    """Add a new item to the list."""

    bl_idname = "operatorparam_list.run"
    bl_label = "run operators in param list"

    def execute(self, context):
        for i in context.scene.operatorparam_list:
            try:
                exec(i.name)
            except:
                print('"' +i.name +'" '+ "Failed To Excecute, please check the ID name is correct")
                
   
        return{'FINISHED'}



classes = (
    GameDev_CustomExportPanel,
    Export_OT_add_preset,
    Export_PT_presets,
    Export_MT_presets,
    OperatorListItem,
    OperatorParamList_OT_NewItem,
    OperatorParamList_OT_DeleteItem,
    MY_UI_OperatorParamList,
    OperatorParamList_OT_Run
)

def register():
    GameDev_CustomExportPanel.bl_category = bpy.context.preferences.addons[
        __package__].preferences.String_Catergory

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.operatorparam_list = CollectionProperty(type = OperatorListItem)
    bpy.types.Scene.operatorparam_list_index = IntProperty(name = "Index for textureparam_list",
                                                default = 0)    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.operatorparam_list
    del bpy.types.Scene.operatorparam_list_index    