import bpy
import os
from mathutils import Vector
from bpy.types import WindowManager

def get_catalogs(context, debug=False):

    asset_libraries = context.preferences.filepaths.asset_libraries
    all_catalogs = []

    for lib in asset_libraries:
        libname = lib.name
        libpath = lib.path

        cat_path = os.path.join(libpath, 'blender_assets.cats.txt')

        if os.path.exists(cat_path):
            if debug:
                print(libname, cat_path)

            with open(cat_path) as f:
                lines = f.readlines()

            for line in lines:
                if line != '\n' and not any([line.startswith(skip) for skip in [
                                            '#', 'VERSION']]) and len(line.split(':')) == 3:
                    all_catalogs.append(
                        line[:-1].split(':') + [libname, libpath])

    catalogs = {}

    for uuid, catalog, simple_name, libname, libpath in all_catalogs:
        if catalog not in catalogs:
            catalogs[catalog] = {'uuid': uuid,
                                 'simple_name': simple_name,
                                 'libname': libname,
                                 'libpath': libpath}

    if debug:
        print(catalogs)

    return catalogs

def parent(obj, parentobj):
    if obj.parent:
        unparent(obj)

    obj.parent = parentobj
    obj.matrix_parent_inverse = parentobj.matrix_world.inverted_safe()

def unparent(obj):
    if obj.parent:
        omx = obj.matrix_world.copy()
        obj.parent = None
        obj.matrix_world = omx

def get_path():
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

def get_name():
    return os.path.basename(get_path())

def get_prefs():
    return bpy.context.preferences.addons[get_name()].preferences

def popup_message(message, title="Info", icon="INFO"):
    def draw_message(self, context):
        if isinstance(message, list):
            for m in message:
                self.layout.label(text=m)
        else:
            self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw_message, title=title, icon=icon)

def average_locations(locationslist, size=3):
    avg = Vector.Fill(size)

    for n in locationslist:
        avg += n

    return avg / len(locationslist)

def update_asset_catalogs(self, context):
    self.catalogs = get_catalogs(context, debug=False)

    items = [('NONE', 'None', '')]

    for catalog in self.catalogs:
        items.append((catalog, catalog, ""))

    default = get_prefs().preferred_default_catalog if get_prefs(
    ).preferred_default_catalog in self.catalogs else 'NONE'
    WindowManager.mtools_catalogs = bpy.props.EnumProperty(
        name="Asset Categories", items=items, default=default)