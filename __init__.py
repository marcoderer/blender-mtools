import bpy
import os

from . import bulk_undo
from . import make_model
from . import mesh_actions
from . import mesh_generator
from . import save_tool
from . import ui
from . import view_ops


bl_info = {
    "name": "MTOOLS",
    "description": "All sorts of goodies...",
    "author": "Marco Alibertis",
    "version": (0, 1),
    "blender": (3, 60, 0),
    "location": "3D View > UI > MTools Panel",
    "warning": "",
    "wiki_url": "",
    "category": "3D View"
}




def register():
    bulk_undo.register()
    make_model.register()
    mesh_actions.register()
    mesh_generator.register()
    save_tool.register()
    ui.register()
    view_ops.register()
    

def unregister():
    bulk_undo.unregister()
    make_model.unregister()
    mesh_actions.unregister()
    mesh_generator.unregister()
    save_tool.unregister()
    ui.unregister()
    view_ops.unregister()
    

if __name__ == '__main__':
    register()
