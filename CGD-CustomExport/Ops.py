import bpy
import subprocess
import os
from mathutils import Vector
import webbrowser 
import pathlib
from bpy.props import (PointerProperty, EnumProperty,
StringProperty, FloatVectorProperty, BoolProperty)

from bpy.types import PropertyGroup, Operator


from .utils import (
CreateFolderStructure, CheckCollision,
CheckManifold,CheckMaterial,CheckNameASCII,CheckNgon,
CheckSmallFaces,ValidationMessage,process_exists,ParentRecursive, get_time, RenameSuffixNumber)
from . import lib_remote

pref = bpy.context.preferences.addons[__package__].preferences

def Addprop(self, context):
    obj=context.object
    obj["Export Ready"] = True

class GameDev_Export_Prop(PropertyGroup):

    ExportReady: BoolProperty(name='Export Ready', default=False ,update = Addprop)

    moditem = [
        (item.identifier, item.name, item.description, item.icon, item.value)
        for item in bpy.types.Modifier.bl_rna.properties['type'].enum_items
    ]

    Modifierlist: EnumProperty(
        items=moditem,
        name="Modifier",
        default='BEVEL',
    )

    SourceDir: StringProperty(name="SourceDir", subtype='DIR_PATH', maxlen=0)
    TransformOld: FloatVectorProperty(name="TransformOld", default=(0, 0, 0))

    ForwardAxis: EnumProperty(name="ForwardAxis", description='Export Front axis',
                              items={
                                  ('X', 'X', 'X Forward',1),
                                  ('Y', 'Y', 'Y Forward',2),
                                  ('Z', 'Z', 'Z Forward',3),
                              }, default='Y')
    UpwardAxis: EnumProperty(name="UpAxis", description='Export Front axis',
                             items={
                                 ('X', 'X', 'X Upward',1),
                                 ('Y', 'Y', 'Y Upward',2),
                                 ('Z', 'Z', 'Z Upward',3),
                             }, default='Z')
    TextureRes: EnumProperty(name="Texture Resolution", description='Texture Resolution in painter',
                             items={
                                 ('512', '512', '512x512',1),
                                 ('1024', '1024', '1024x1024',2),
                                 ('2048', '2048', '2048x2048',3),
                                 ('4096', '4096', '4096x4096',4),
                             }, default='1024')
    
    CustomProps: BoolProperty(name='UseCustomProps', default=False)
    Modifiers: BoolProperty(name='UseModifiers', default=True)
    FileName: StringProperty(name='FileName', default='')

    CurrentTime: StringProperty(name='CurrentTime',get=get_time,)

    bool_Enable_BakeOnExport: BoolProperty(
        name="Bake On Export", default=True)
    
    RunOperators: BoolProperty(name='Run Export Operators', default=False)
    
    LPCollection: PointerProperty(
        type=bpy.types.Collection,
        name="LP",
        description="Collection for LP Rename"
    )


    HPCollection: PointerProperty(
        type=bpy.types.Collection,
        name="HP",
        description="Collection for HP Rename"
    )   

class GameDev_FolderStruct (Operator):
    bl_idname = "view3d.folder_struct"
    bl_label = "Create Folder Structure"
    bl_description="Save Asset source folder structure"

    @classmethod
    def poll(cls, context):
        scene = context.scene
        Export_Prop = scene.export_Prop

        if Export_Prop.SourceDir== '' or Export_Prop.FileName=='':
            return (False)
        else:
            return (True)
        
    def execute(self, context):
        scene = context.scene
        Export_Prop = scene.export_Prop

        dir = CreateFolderStructure(
            Export_Prop.SourceDir, Export_Prop.FileName)
        bpy.ops.wm.save_as_mainfile(
            filepath=dir[0]+Export_Prop.FileName+'.blend',compress=True)
        return {'FINISHED'}

class OpenDirectory(Operator):
    bl_idname = "view3d.open_directory"
    bl_label = "Open Directory"
    bl_description="Open Asset source folder"

    @classmethod
    def poll(cls, context):
        scene = context.scene
        Export_Prop = scene.export_Prop
        if Export_Prop.SourceDir== '' or Export_Prop.FileName=='':
            return (False)
        else:
            path = Export_Prop.SourceDir + Export_Prop.FileName
            return (os.path.exists(path))

    def execute(self, context):
        scene = context.scene
        Export_Prop = scene.export_Prop

        path = Export_Prop.SourceDir + Export_Prop.FileName
        path = os.path.realpath(path)
        os.startfile(path)
        return {'FINISHED'}

class OpenReference(Operator):
    bl_idname = "view3d.open_reference"
    bl_label = "Open Directory"
    bl_description="Open Asset source folder"

    @classmethod
    def poll(cls, context):
        scene = context.scene
        Export_Prop = scene.export_Prop
        if Export_Prop.SourceDir== '' or Export_Prop.FileName=='':
            return (False)
        else:
            path = Export_Prop.SourceDir + Export_Prop.FileName
            return (os.path.exists(path))

    def execute(self, context):
        scene = context.scene
        Export_Prop = scene.export_Prop

        path = Export_Prop.SourceDir + Export_Prop.FileName +'\\DCC\\'+Export_Prop.FileName+ '.pur'
        if os.path.exists(path):
            path = os.path.realpath(path)
            os.startfile(path)
        else:
            open(Export_Prop.SourceDir + Export_Prop.FileName +'\\DCC\\'+Export_Prop.FileName+ '.pur', "x")
            os.startfile(path)
        return {'FINISHED'}

class OldRenameChildren(Operator):
    bl_idname = "view3d.old_rename_children"
    bl_label = "Old Rename children"
    bl_description="match meshes by position and rename (requires a even amount of selected objects)"

    @classmethod
    def poll(cls, context):
        if len(bpy.context.selected_objects)==0:
            return (False)
        if len(bpy.context.selected_objects)%2==0:
            return (True)
        else:
            return (False)

    def execute(self, context):

        def get_BoundBoxC(object):
            centre = sum((Vector(b) for b in object.bound_box), Vector())
            centre /= 8
            return [object.matrix_world @ Vector(v) for v in object.bound_box]

        def get_BoundBoxA(object):
            area = object.dimensions.x*object.dimensions.y*object.dimensions.z
            return (area)

        obj = bpy.context.selected_objects
        BB = []

        for o in obj:

            BBI = (get_BoundBoxC(o), get_BoundBoxA(o), o.name)
            BB.append(BBI)

        BB = sorted(BB, key=lambda i: i[0])
        print(BB)

        names = [i[2] for i in BB]

        for i, o in enumerate(range(1, len(names), 2)):
            pair = (names[o], names[o-1])
            #print (pair)
            bpy.context.scene.objects[pair[0]].name = "Object_{:03d}".format(i)
            bpy.context.scene.objects[pair[1]].name = "Object_{:03d}".format(i)

        return {'FINISHED'}

class RenameChildren(Operator):
    bl_idname = "view3d.rename_children"
    bl_label = "Rename children"
    bl_description="match meshes by position and rename (requires a even amount of selected objects)"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        Export_Prop = scene.export_Prop
        if Export_Prop.HPCollection and Export_Prop.LPCollection != None:
            if len(bpy.context.selected_objects)%2==0:
                return (True)
        else:
            return (False)

    def execute(self, context):
        scene = context.scene
        Export_Prop = scene.export_Prop
        def get_BoundBoxC(object):
            centre = sum((Vector(b) for b in object.bound_box), Vector())
            centre /= 8
            return [object.matrix_world @ Vector(v) for v in object.bound_box]

        def get_BoundBoxA(object):
            area = object.dimensions.x*object.dimensions.y*object.dimensions.z
            return (area)

        obj = []

        obj= bpy.context.selected_objects
        for i in Export_Prop.LPCollection.all_objects[0:]: 
            obj.append(i) 
        for i in Export_Prop.HPCollection.all_objects[0:]: 
            obj.append(i) 
        
        BB = []

        for o in obj:

            BBI = (get_BoundBoxC(o), get_BoundBoxA(o), o.name)
            BB.append(BBI)

        BB = sorted(BB, key=lambda i: i[0])
        print(BB)

        names = [i[2] for i in BB]

        for i, o in enumerate(range(1, len(names), 2)):
            pair = (names[o], names[o-1])

            bpy.context.scene.objects[pair[0]].name = "Object_{:03d}".format(i)
            bpy.context.scene.objects[pair[1]].name = "Object_{:03d}".format(i)

        for obj in Export_Prop.LPCollection.all_objects: 
            if '.' in obj.name :
                obj.name=obj.name.split('.',1)[0] + '_low'
            else:
                obj.name=obj.name + '_low'
        for obj in Export_Prop.HPCollection.all_objects: 
            if '.' in obj.name :
                obj.name=obj.name.split('.',1)[0] + '_high'
            else:
                obj.name=obj.name + '_high' 

        print(Export_Prop.LPCollection.name)
        return {'FINISHED'}


class MakeSingleUser(Operator):
    bl_idname = "view3d.make_single_user"
    bl_label = "Make Single User"
    bl_description="Make selected single user object data"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if len(bpy.context.selected_objects)>0:
            return (True)
        else:
            return (False)
    def execute(self, context):

        bpy.ops.object.make_single_user(
            object=True, obdata=True, material=False, animation=False, obdata_animation=False)

        return {'FINISHED'}

class RemoveModifierType(Operator):
    bl_idname = "view3d.remove_modifier_type"
    bl_label = "Remove Modifier Type"
    bl_description="Remove modifier from selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if len(bpy.context.selected_objects)>0:
            return (True)
        else:
            return (False)
    def execute(self, context):
        scene = context.scene
        Export_Prop = scene.export_Prop

        for o in bpy.context.selected_objects:
            for m in o.modifiers:
                if (m.type == Export_Prop.Modifierlist):
                    o.modifiers.remove(m)

        return {'FINISHED'}
    
class ApplyModifierType(Operator):
    bl_idname = "view3d.apply_modifier_type"
    bl_label = "Apply Modifier Type"
    bl_description="Apply modifier to selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if len(bpy.context.selected_objects)>0:
            return (True)
        else:
            return (False)
        
    def execute(self, context):
        scene = context.scene
        Export_Prop = scene.export_Prop

        #print (Export_Prop.Modifierlist)

        for obj in bpy.context.selected_objects:
            bpy.context.view_layer.objects.active = obj
            for modifier in obj.modifiers:
                if modifier.type == Export_Prop.Modifierlist:
                    bpy.ops.object.modifier_apply(
                        modifier=modifier.name
                    )

        return {'FINISHED'}

class OpenPainterFile(Operator):
    bl_idname = "view3d.open_painter_file"
    bl_label = "Open painter File"
    bl_description="Open excisting painter file for selected Asset (based of object name and save value settings)"

    @classmethod
    def poll(cls, context):
        scene = context.scene
        Export_Prop = scene.export_Prop

        valuelist = ('.001', '.002', '.003', '.004', '.005', '.006', '.007', '.008', '.009', '.010',
                     '.011', '.012', '.013', '.014', '.015', '.016', '.017', '.018', '.019', '.020',)

        parentobj = ParentRecursive(bpy.context.view_layer.objects.active)[-1]
        SppName = parentobj.name
        if parentobj.name.endswith(valuelist):
            SppName = parentobj.name[:-4]

        path = Export_Prop.SourceDir+'/' + Export_Prop.FileName+'//DCC//'+SppName+'.spp'

        return (os.path.exists(path))

    def execute(self, context):
        scene = context.scene
        Export_Prop = scene.export_Prop
        
        valuelist = ('.001', '.002', '.003', '.004', '.005', '.006', '.007', '.008', '.009', '.010',
                     '.011', '.012', '.013', '.014', '.015', '.016', '.017', '.018', '.019', '.020',)


        parentobj = ParentRecursive(bpy.context.view_layer.objects.active)[-1]
        SppName = parentobj.name
        if parentobj.name.endswith(valuelist):
            SppName = parentobj.name[:-4]
        else:
            pass

        path = Export_Prop.SourceDir+'/' + Export_Prop.FileName+'//DCC//'+SppName+'.spp'

        path = os.path.realpath(path)
        os.startfile(path)

        return {'FINISHED'}

class ValidateAsset(Operator):
    bl_idname = "view3d.validatemesh"
    bl_label = "Validate Asset"
    bl_description="Validate Asset for required check"

    def execute(self, context):
        # create and clear log
        bpy.ops.screen.info_log_show()
        bpy.ops.info.select_all()
        bpy.ops.info.report_delete()

        if bpy.context.view_layer.objects.active.parent != None:
            parent = bpy.context.view_layer.objects.active.parent
            bpy.context.view_layer.objects.active.select_set(False)
            bpy.context.view_layer.objects.active = parent
            parent.select_set(True)

        objs = []
        objs.append(bpy.context.view_layer.objects.active)

        for obj in bpy.context.selected_objects:
            for chil in obj.children_recursive:
                objs.append(chil)

        if bpy.context.view_layer.objects.active.parent != None:
            _HasCollision = CheckCollision(
                bpy.context.view_layer.objects.active.parent)

        else:
            _HasCollision = CheckCollision(
                bpy.context.view_layer.objects.active)

        for obj in objs:
            _IsManifold = CheckManifold(obj)
            _HasMaterial = CheckMaterial(obj)
            _HasNgon = CheckNgon(obj)
            _IsASCII = CheckNameASCII(obj)
            _HasSmallFaces = CheckSmallFaces(obj)
            _HasCollision = CheckCollision(obj)
            #print(_HasCollision)
            message = ValidationMessage(
                self, obj, _IsManifold, _HasMaterial, _HasCollision, _HasNgon, _IsASCII, _HasSmallFaces)
            self.report({'INFO'}, message)

        return {'FINISHED'}


class GameDev_Export (Operator):
    bl_idname = "view3d.custom_export"
    bl_label = "Export"
    bl_description = "Export selected mesh heirachy (parent and children)"
    bl_options = {'REGISTER', 'UNDO'}

    LP: BoolProperty(name='LowPoly', default=False)
    HP: BoolProperty(name='HighPoly', default=False)

    @classmethod
    def poll(cls, context):
        scene = context.scene
        Export_Prop = scene.export_Prop
        if Export_Prop.SourceDir== '' or Export_Prop.FileName=='':
            return (False)
        else:
            if len(bpy.context.selected_objects)>0:

                path = Export_Prop.SourceDir + Export_Prop.FileName
                return (os.path.exists(path))

    def execute(self, context):
        pref = bpy.context.preferences.addons[__package__].preferences
        scene = context.scene
        Export_Prop = scene.export_Prop

        # select parented object
        parentobj = ParentRecursive(bpy.context.view_layer.objects.active)[-1]

        # select all objects attached to parent
        objname = parentobj.name
        baseobj = []
        baseobj.append(parentobj)
        ModObj=[]

        # Gets alist of all objects in the heirachy
        for obj in bpy.data.objects[objname].children_recursive:
            bpy.data.objects[obj.name].select_set(True)
            baseobj.append(obj)
            bpy.context.view_layer.objects.active=obj
        
        for o in baseobj:
            mods = o.modifiers
            for mod in mods:
                if hasattr(mod,'object'):
                    if mod.object not in baseobj:
                        ModObj.append(mod.object)

        if self.LP == self.HP :
            baseobj=[item for item in baseobj if item not in ModObj]
            OriginalLocation = parentobj.matrix_world.to_translation()
            parentobj.location=parentobj.location - OriginalLocation

            for o in ModObj:
                o.location = o.location - OriginalLocation

        # create folder structure
        fbxdir = os.path.join(Export_Prop.SourceDir,
                              Export_Prop.FileName+'\\')

        if self.LP or self.HP == True:
            fbxdir = os.path.join(Export_Prop.SourceDir,
                                  Export_Prop.FileName+'\\DCC\\')
            
        
        # Create file path and name
        global fn
        fn=''
        mode = 0o666
        if os.path.exists(fbxdir) == False:
            os.mkdir(fbxdir, mode)
        
        if pref.Enum_PrefixSuffix == 'Prefix':
            fn = os.path.join(fbxdir, 'SM_'+parentobj.name)
        
        if pref.Enum_PrefixSuffix == 'Suffix':
            fn = os.path.join(fbxdir, parentobj.name+'_SM')
        
        if pref.Enum_PrefixSuffix == 'None':
            fn = os.path.join(fbxdir, parentobj.name)


        if self.HP == True:
            RenameSuffixNumber(baseobj,"_high",fn)
            fn=fn = os.path.join(fbxdir, parentobj.name)

        if self.LP == True:
            RenameSuffixNumber(baseobj,"_low",fn)
            fn=fn = os.path.join(fbxdir, parentobj.name)
            
        print(parentobj.name)
        print(fn)
        

        # set substance painter directory based off asset name 

        global SppDir
        SppDir = Export_Prop.SourceDir+'/' + Export_Prop.FileName + \
            '//DCC//'+parentobj.name[:-4]+'.spp'

        SppDir=SppDir.replace ("\\","/")

        #Set all objects as selected for the exporter
        for obj in baseobj :
            obj.select_set(True)
        
        bpy.ops.export_scene.fbx(
            filepath=fn + ".fbx", check_existing=True,
            filter_glob='*.fbx', use_selection=True,
            apply_unit_scale=True, use_mesh_modifiers=Export_Prop.Modifiers,
            use_mesh_modifiers_render=True, mesh_smooth_type='EDGE',
            use_subsurf=False, use_mesh_edges=False,
            use_tspace=True, use_triangles=True,
            use_custom_props=Export_Prop.CustomProps,
            add_leaf_bones=False, bake_anim=True,
            embed_textures=False, batch_mode='OFF',
            use_batch_own_dir=False, use_metadata=False,
            axis_forward=Export_Prop.ForwardAxis, axis_up=Export_Prop.UpwardAxis,
            apply_scale_options='FBX_SCALE_NONE')

        #Reset Object location
        if self.LP == self.HP :
            parentobj.location=OriginalLocation
            for o in ModObj:
                o.location= o.location + OriginalLocation


        if self.HP == True:
            for obj in baseobj :
                obj.name=obj.name.rsplit('_',1)[0]

        if self.LP == True:
            for obj in baseobj :
                obj.name=obj.name.rsplit('_',1)[0]


        global TextPath
        TextPath= '"'+Export_Prop.SourceDir + Export_Prop.FileName+'\Textures\"'
        fn=fn.replace ("\\","/")

        # I using low poly export will remote execute painter python commands to bake and set the texture resolution
        if self.LP == True:
            if os.path.exists(SppDir):
                try:
                    os.rename(SppDir, SppDir)
                    cmd_str = '"'+pref.Painter_Dir+'" --enable-remote-scripting --disable-version-checking'+' --mesh "'+fn + \
                        '.fbx" --export-path '+TextPath+' "'+SppDir+'"'
                    #print(cmd_str)
                    subprocess.Popen(cmd_str, shell=True)
                    bpy.ops.wm.painter_check()

                except OSError as e:
                    print("File is open, updating mesh")
                    Remote = lib_remote.RemotePainter()
                    Remote.checkConnection()
                    s='''
import substance_painter.project
import substance_painter.logging

substance_painter.logging.log(substance_painter.logging.INFO,"Python","Updating mesh")

mesh_reloading_settings = substance_painter.project.MeshReloadingSettings(import_cameras=True,preserve_strokes=True)

substance_painter.logging.log(substance_painter.logging.INFO,"Python",substance_painter.project.last_imported_mesh_path())

substance_painter.project.reload_mesh(substance_painter.project.last_imported_mesh_path())
'''
                    lines = s.split('\n')
                    for line in lines:
                        print (line)
                        Remote.execScript(line , "python")
            else:
                cmd_str = '"'+pref.Painter_Dir+'" --enable-remote-scripting --disable-version-checking'
                subprocess.Popen(cmd_str, shell=True)
                bpy.ops.wm.painter_check()

        #reset operator variables
        self.LP = False
        self.HP = False
        return {'FINISHED'}

# This modal operator is used to execute the substance painter python cmds

class ModalTimerOperator(Operator):

    """Operator which runs itself from a timer"""
    bl_idname = "wm.painter_check"
    bl_label = "Modal painter Check"

    _timer = None

    p: bpy.props.BoolProperty(name='Open', default=False)

    def modal(self, context, event):
        scene = context.scene
        Prop = scene.export_Prop
        pref = bpy.context.preferences.addons[__package__].preferences
        
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            self.p = process_exists('Adobe Substance 3D Painte')
            #print(self.p)

        if self.p == True:

            Remote = lib_remote.RemotePainter()
            tmplpath=pref.Template_Dir
            Remote.checkConnection()

            s= '''
import substance_painter.logging
import substance_painter.ui
import substance_painter.project
import substance_painter.textureset
import substance_painter.baking
from substance_painter.baking import BakingParameters
import substance_painter.export
import time 
settings=substance_painter.project.Settings(export_path='''+TextPath+''')
substance_painter.project.create(mesh_file_path="''' +fn+'''.fbx" '''+''', template_file_path="'''+tmplpath+'''", settings=settings)

active_stack = substance_painter.textureset.get_active_stack()

baking_params = BakingParameters.from_texture_set(active_stack.material())
texture_set = baking_params.texture_set()
common_params = baking_params.common()
ao_params = baking_params.baker(MeshMapUsage.AO)

BakingParameters.set({ common_params['HipolySuffix'] : ('_high') ,common_params['LowpolySuffix'] : ('_low') ,common_params['HipolyMesh'] : ("file:///'''+fn[:-3]+'''high.fbx")})
substance_painter.project.save_as("'''+SppDir+'''")

new_resolution = substance_painter.textureset.Resolution('''+Prop.TextureRes+''','''+Prop.TextureRes+''')

if active_stack.material().get_resolution() !=substance_painter.textureset.Resolution('''+Prop.TextureRes+''','''+Prop.TextureRes+''') : active_stack.material().set_resolution(new_resolution)


'''


            b='''
substance_painter.baking.bake_selected_textures_async()
#substance_painter.ui.switch_to_mode(substance_painter.ui.UIMode(1))

'''
            if Prop.bool_Enable_BakeOnExport==True:
                s+=b
            


            lines = s.split('\n')
            for line in lines:
                print (line)
                Remote.execScript(line , "python")
            


            return {'FINISHED'}
        else:
            return {'PASS_THROUGH'}

    def execute(self, context):
        
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

class OpenMusicPlaylist(Operator):
    """Operator which runs itself from a timer"""
    bl_idname = "web.playlist"
    bl_label = "Open Music Playlist"
    @classmethod
    def poll(cls, context):
        pref = bpy.context.preferences.addons[__package__].preferences
        if pref.PlaylistLink=="":
            return(False)
        else:
            return(True)
  
    def execute(self, context):
        pref = bpy.context.preferences.addons[__package__].preferences
        url = pref.PlaylistLink

        webbrowser.open_new_tab(url)
        return {'FINISHED'}

class ImportScaleMesh(Operator):
    """import a Scale refence mesh"""
    bl_idname = "view3d.scalemesh"
    bl_label = "import a Scale refence"
    def execute(self, context):
        file_path = __file__
        file_path=file_path.replace ("Ops.py","ScaleMesh.blend")
        print (file_path)
        src_path= file_path 
        with bpy.data.libraries.load(src_path) as (data_from, data_to):
            data_to.objects = data_from.objects
        for obj in data_to.objects:
            bpy.context.scene.collection.objects.link(obj)
        return {'FINISHED'}
      
classes = (
    GameDev_Export_Prop,
    GameDev_Export,
    GameDev_FolderStruct,
    ValidateAsset,
    RenameChildren,
    RemoveModifierType,
    ApplyModifierType,
    OpenDirectory,
    OpenPainterFile,
    MakeSingleUser,
    ModalTimerOperator,
    OpenMusicPlaylist,
    ImportScaleMesh, 
    OldRenameChildren,
    OpenReference,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.export_Prop = PointerProperty(
        type=GameDev_Export_Prop)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.export_Prop
