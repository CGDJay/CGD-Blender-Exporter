import bpy
import bmesh
import subprocess
import time
import os
import datetime


pref = bpy.context.preferences.addons[__package__].preferences

#### Functions

def CreateFolderStructure(SourceDir, AssetName):

    # create folder structure
    fbxdir = os.path.join(SourceDir, AssetName+'//')
    DCCdir = os.path.join(SourceDir, AssetName+'//DCC//')
    Texdir = os.path.join(SourceDir, AssetName+'//Textures//')

    mode = 0o666

    if os.path.exists(fbxdir) == False:
        os.mkdir(fbxdir, mode)
    if os.path.exists(DCCdir) == False:
        os.mkdir(DCCdir, mode)
    if os.path.exists(Texdir) == False:
        os.mkdir(Texdir, mode)

    return (DCCdir, fbxdir, Texdir)

def RenameSuffixNumber(objList,newSuffix,fn):
    
    # deprecate due to changes made on the match & rename operator may still need 
    valuelist = ('.001', '.002', '.003', '.004', '.005', '.006', '.007', '.008', '.009', '.010',
                    '.011', '.012', '.013', '.014', '.015', '.016', '.017', '.018', '.019', '.020',)
    for obj in objList:
        if obj.name.endswith(valuelist):
            obj.name = obj.name[:-4] + newSuffix
        else:
            obj.name += newSuffix
    return (fn)

def CheckNameASCII(obj):
    Name = obj.name
    _IsASCII = Name.isascii()

    #print ("Does Object Follow ASCII:"+str(_IsASCII))

    return (not _IsASCII)

def CheckNgon(obj):
    if obj.type != "MESH":
        return()
    _HasNgon = False
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)

    for f in bm.faces:
        verts = f.verts
        vlist = []

        for v in verts:
            # print(v)
            vlist.append(v)

            if len(vlist) > 4:
                #print ("Has Ngon")
                _HasNgon = True

    return (_HasNgon)

def CheckCollision(obj):
    _HasCollision = False

    tags = ["UBX_", "UCX_", "USP_"]

    chilsNames = []
    chilsNames.append(obj.name)
    for i in obj.children_recursive:
        chilsNames.append(i.name)

    Name = obj.name

    obNames = []
    for ob in bpy.data.objects:
        obNames.append(ob.name)

    for i in obNames:
        if i in chilsNames:
            obNames.remove(i)

    for i in obNames:
        if i in ob.name:
            if ob.name[0:4] in tags:
                #print ("HasCollision")
                _HasCollision = True

    return (_HasCollision)

def CheckMaterial(obj):
    if obj.type != "MESH":
        return()
    _HasMaterial = True

    if len(obj.data.materials) == 0:
        # print("NoMaterial")
        _HasMaterial = False

    return (_HasMaterial)

def CheckManifold(obj):
    if obj.type != "MESH":
        return()
    
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)

    is_manifold = True

    for edge in bm.edges:
        if len(edge.link_faces) != 2:
            is_manifold = False
            break

    if is_manifold:
        for vert in bm.verts:
            if len(set([len(e.link_faces) for e in vert.link_edges])) != 1:
                is_manifold = False
                break

    return (is_manifold)

def CheckSmallFaces(obj):
    pref = bpy.context.preferences.addons[__package__].preferences
    if obj.type != "MESH":
        return()

    _HasSmallFaces = False
    scale = (obj.scale)
    scale = sum(scale)
    scale = (scale) / 3
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)

    for f in bm.faces:
        area = f.calc_area() * scale
        #print (area)
        if area < (pref.float_faceAreaLimit/10000):
            #print("mesh Contains Small Faces")
            _HasSmallFaces = True
            break
        else:
            pass
    return (_HasSmallFaces)

def ValidationMessage(self, obj, _IsManifold, _HasMaterial, _HasCollision, _HasNgon, _IsASCII, _HasSmallFaces):
    pref = bpy.context.preferences.addons[__package__].preferences
    _ObjectName = obj.name+"---------------------------------"

    Warning = False

    message = ""
    message = message+_ObjectName+"\n"

    _IsManifoldMessage = "is manifold = "+str(_IsManifold)

    _HasMaterialMessage = "Has Material = "+str(_HasMaterial)

    _HasCollisionMessage = "Has Collision = "+str(_HasCollision)

    _HasNgonMessage = "contains Ngons = "+str(_HasNgon)

    _HasSmallFacesMessage = "contains Small Faces = "+str(_HasSmallFaces)

    _IsASCIIMessage = "Object Name contains invalid characters = " + \
        str(_IsASCII)

    if pref.bool_Enable_CheckManifold == True:
        if _IsManifold == False:
            message = message+_IsManifoldMessage+"\n"
            Warning = True

    if pref.bool_Enable_CheckMaterial == True:
        if _HasMaterial == False:
            message = message+_HasMaterialMessage+"\n"
            Warning = True

    if pref.bool_Enable_CheckCollision == True:
        if _HasCollision == False:
            Warning = True
            message = message+_HasCollisionMessage+"\n"

    if pref.bool_Enable_CheckName == True:
        if _IsASCII == True:
            Warning = True
            message = message+_IsASCIIMessage+"\n"

    if pref.bool_Enable_CheckNGon == True:
        if _HasNgon == True:
            Warning = True
            message = message+_HasNgonMessage+"\n"

    if pref.bool_Enable_CheckFaceSize == True:
        if _HasSmallFaces == True:
            Warning = True
            message = message+_HasSmallFacesMessage+"\n"

    if Warning == True:
        # print("Warning")
        message = ('Warning!!!========================='+"\n"+message)

    return (message)

def ParentRecursive(Obj):
    if Obj.parent:
        return [Obj.parent] + ParentRecursive(Obj.parent)
    else:
        return [Obj]

def process_exists(process_name):
    progs = str(subprocess.check_output('tasklist'))

    #print (progs)
    
    if process_name in progs:
        print('Connected')
        time.sleep(15)
        return True
    else:
        print('retry')
        time.sleep(2)
        return False

def get_time(self):
    now = datetime.datetime.now()

    current_time = now.strftime("%H:%M")

    return str("Current Time: "+current_time)

def ObjNameWithoutNum():
    DisplayName=''
    valuelist = ('.001', '.002', '.003', '.004', '.005', '.006', '.007', '.008', '.009', '.010',
                '.011', '.012', '.013', '.014', '.015', '.016', '.017', '.018', '.019', '.020',)

    obj=ParentRecursive(bpy.context.view_layer.objects.active)[-1]

    if obj.name.endswith(valuelist):
        DisplayName = obj.name[:-4]
    else:
        DisplayName=obj.name
    return (DisplayName)