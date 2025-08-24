import bpy
from bpy.types import AddonPreferences
from bpy.props import (
    StringProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    EnumProperty,
    PointerProperty,
)

from .Panel import updateCategory


class Panel_Preferences(AddonPreferences):
    bl_idname = __package__
    # properties menu
    bool_Enable_MiscOperators: BoolProperty(
    name="Enable misc operators", default=True)

    bool_Enable_CustomExport: BoolProperty(
        name="Enable custom export panel", default=True)

    bool_Enable_CheckManifold: BoolProperty(
        name="Validate non- manifold", default=True)

    bool_Enable_CheckMaterial: BoolProperty(
        name="Validate matrial", default=True)

    bool_Enable_CheckNGon: BoolProperty(
        name="Validate Ngons", default=True)

    bool_Enable_CheckCollision: BoolProperty(
        name="Validate Collision", default=True)

    bool_Enable_CheckName: BoolProperty(
        name="Validate name", default=True)

    bool_Enable_CheckFaceSize: BoolProperty(
        name="Validate micro faces", default=True)

    float_faceAreaLimit: FloatProperty(
        name="micro face size <", unit='AREA', default=0.005)

    String_Catergory: StringProperty(
        name="String_Catergory", default='GameDev', update=updateCategory)

    Painter_Dir: StringProperty(name="Substance Painter Exe Directory", subtype='FILE_PATH',
        default='D:\SteamLibrary\steamapps\common\Substance 3D Painter 2023\Adobe Substance 3D Painter.exe')
    
    Template_Dir: StringProperty(name="Substance Painter Project Template", subtype='FILE_PATH',
        default='D:/Desktop/SubstancePainterLibrary/templates/UE5.spt')

    Enum_PrefixSuffix: EnumProperty(name="prefix/suffix file name", description='Export Front axis',
        items={
            ('Prefix', 'Prefix', 'Prefix'),
            ('Suffix', 'Suffix', 'Suffix'),
            ('None', 'None', 'None'),
        }, default='Prefix')

    PlaylistLink: StringProperty(
        name="Play list Link", default='https://www.youtube.com/watch?v=wKRL7vkWMoc&t=658s')
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.scale_y = 2
        box.scale_x = 2
        box.label(text="Properties:", icon="TOOL_SETTINGS")
        
        box.prop(self, "bool_Enable_CustomExport")
        box.prop(self, "String_Catergory")
        box.prop(self, "bool_Enable_MiscOperators")

        box = layout.box()
        box.label(text="Validate :", icon="DOT")
        col =box.column(align = True)

        row= col.row(align = True)
        row.prop(self, "bool_Enable_CheckManifold")
        row.prop(self, "bool_Enable_CheckMaterial")
        row.prop(self, "bool_Enable_CheckName")

        row= col.row(align = True)
        row.prop(self, "bool_Enable_CheckNGon")
        row.prop(self, "bool_Enable_CheckCollision")
        row.prop(self, "bool_Enable_CheckFaceSize")
        
        row= col.row(align = True)
        row.prop(self, "float_faceAreaLimit")

        box = layout.box()
        box.label(text="Export Settings :", icon="DOT")

        col=box.column(align = True)
    
        row=col.row(align = True)
        row.prop(self, "Enum_PrefixSuffix")

        row=col.row(align = True)
        row.prop(self, "Painter_Dir")
        row.prop(self, "Template_Dir")

        box = layout.box()
        box.label(text="Misc settings", icon="DOT")
        col=box.column(align = True)
        row=col.row(align = True)
        row.prop(self, "PlaylistLink")

classes = (
    Panel_Preferences,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
