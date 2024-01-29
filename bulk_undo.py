import bpy


from bpy.types import (
    IntProperty,
    Operator,
    
)

class MTools_OT_BulkUndo(Operator):
    """Execute a predefined number of undo steps"""
    bl_label = "Undo"
    bl_idname = "mops.bulk_undo"

    undo_steps: IntProperty(name="Number of undo steps")

    def draw(self, context):
        row = self.layout
        row.prop(self, "undo_steps", text="?")

    def execute(self, context):
        u = self.undo_steps
        self.report(
            {'INFO'}, 'Undo steps: %u' %
            (u)
        )
        for i in range(u):
            bpy.ops.ed.undo()

        return {'FINISHED'}


class MTools_OT_BulkRedo(Operator):
    """Execute a predefined number of redo steps"""
    bl_label = "Redo"
    bl_idname = "mops.bulk_redo"

    redo_steps: IntProperty(name="Number of redo steps")

    def draw(self, context):  
        row = self.layout
        row.prop(self, "redo_steps", text="?")

    def execute(self, context):
        u = self.redo_steps
        self.report(
            {'INFO'}, 'Redo steps: %u' %
            (u)
        )
        for i in range(u):
            bpy.ops.ed.redo()

        return {'FINISHED'}
    

classes = (
    MTools_OT_BulkUndo,
    MTools_OT_BulkRedo,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    


def unregister():


    for cls in classes:
        bpy.utils.unregister_class(cls)