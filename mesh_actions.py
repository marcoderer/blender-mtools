import bpy
from bpy.types import (
    BoolProperty,
    EnumProperty,
    Operator,
)


class MTools_OT_SeparateSelectObject(Operator):
    """Separate object by selection and set it as active object."""
    bl_label = "Separate & Make Active"
    bl_idname = "mops.separate_select_object"
    bl_options = {"REGISTER", "UNDO"}

    # An enum with available separate methods
    separate_method: EnumProperty(
        items={
            ('SELECTED', 'Selected', "Selected mesh"),
            ('MATERIAL', 'Material', "Based on material"),
            ('LOOSE', 'Loose', "Based on loose part")
        },
        name="Separate Method",
        description="Choose a method to separate mesh",
        default='SELECTED'
    )
    set_mode_to_object: BoolProperty(
        name="Object Mode",
        description=(
            "With this option toggled on, the context will be"
            "set to object mode after the separate execution."
        ),
        default=False
    )
    make_new_obj_active: BoolProperty(
        name="Make active",
        description=(
            "With this option you can choose to set"
            "the newly created object as active object"
            "(in case of multiple objects the first created "
            "will be set active)"
        ),
        default=False
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        mesh = obj.data
        return obj is not None and obj.type in 'MESH' \
            and any(v.select for v in mesh.vertices)

    # ? Add functionality to work with curve separation?
    def execute(self, context):
        start_sel = context.selected_objects
        obj = context.active_object
        mesh = obj.data
        mesh.separate(type=self.separate_method)
        end_sel = context.selected_objects
        new_objs = [o for o in end_sel if o not in start_sel]
        if self.make_new_obj_active and new_objs:
            obj.editmode_toggle()
            obj = new_objs[0]
            context.view_layer.objects.active = obj
            if not self.set_mode_to_object:
                obj.editmode_toggle()
        # Deselect all other objects but the new created object
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)

        self.report(
            {'INFO'},
            f"Separate {self.separate_method[2]}."
        )

        return {'FINISHED'}


classes = (
    MTools_OT_SeparateSelectObject,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)
