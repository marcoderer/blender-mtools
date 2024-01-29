# frequently used imports in blender modules, delete what you don't use
import bpy
import os
from pathlib import Path

from bpy.types import (
    IntProperty,
    FloatProperty,
    EnumProperty,
    StringProperty,
    Operator,
    
)

class ADDON_OT_SomeOperation(Operator):
    """Description goes here"""
    bl_idname = "addon.some_operation"
    bl_label = "Some Operation"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls,context):
        # Check things first, like:
        return context.mode == 'OBJECT' and context.selected_objects

    def draw(self, context):
        # If the operator has its own layout
        self.layout.label(text="Hello")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        # do something interesting

        return {'FINISHED'}
    

classes = (
    ADDON_OT_SomeOperation,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    


def unregister():


    for cls in classes:
        bpy.utils.unregister_class(cls)