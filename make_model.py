# frequently used imports in blender modules, delete what you don't use
import bpy
import os
from pathlib import Path
from mathutils import Vector

from bpy.types import (
    BoolProperty,
    EnumProperty,
    StringProperty,
    Operator,
)

from . import ui
from . import utils

empty_locs = [
    ('AVG', 'Average', 'Roughly the center of your model'),
    ('AVGFLOOR', 'Average Floor', 'On the floor right under your model'),
    ('WORLDORIGIN', 'World Origin', 'The place where it all began')
]

class MTools_OT_MakeAsset(Operator):
    bl_label = "Make asset"
    bl_idname = "mops.make_asset"

    catalog: StringProperty(
        name="Collection name",
        default="Models",
    )
    render_preview: BoolProperty(
        name="Render preview",
        default=False,
        description="Rendering a preview"
    )
    save_ext: BoolProperty(
        name="Save external",
        default=False,
        description="Save the asset to an external .blend library"
    )
    ext_path: StringProperty(
        name="Collection name",
        default="Choose a .blend library",
        subtype='DIR_PATH'
    )

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and context.selected_objects

    def invoke(self, context, event):
        return super().invoke(context, event)

    def execute(self, context):

        return {'FINISHED'}


class MTools_OT_UnpackAsset(Operator):
    bl_label = "Unpack Asset"
    bl_idname = "mops.unpack_asset"

    @classmethod
    def poll(cls, context):
        active = context.active_object
        return active and active.type == 'EMPTY' and active.instance_collection and active.instance_type == 'COLLECTION'

    def invoke(self, context, event):
        self.keep_empty = event.alt
        return self.execute(context)

    def execute(self, context):
        active = context.active_object

        instances = {active} | {
            obj for obj in context.selected_objects if obj.type == 'EMPTY' and obj.instance_collection}

        if any((i.instance_collection.library for i in instances)):
            bpy.ops.object.make_local(type='ALL')

            for instance in instances:
                instance.select_set(True)

        for instance in instances:
            collection = instance.instance_collection

            root_children = self.assemble_instance_collection(
                context, instance, collection)

            for child in root_children:
                utils.parent(child, instance)

                instance.select_set(True)
                context.view_layer.objects.active = instance

        bpy.ops.outliner.orphans_purge(
            do_local_ids=True,
            do_linked_ids=True,
            do_recursive=True)

        return {'FINISHED'}


class MTools_OT_MakeModel(Operator):
    bl_label = "Create assembly model"
    bl_idname = "mops.make_model"

    mod_name: StringProperty(
        name="Model name",
        default="My model"
    )
    empty_loc: EnumProperty(
        name="Controller Location",
        items=empty_locs,
        description="Location of the empty controller",
        default='AVGFLOOR'
    )
    # empty_style: EnumProperty(
    #     name="Controller Location",
    #     items=empty_ops,
    #     description="Controller style",
    #     default='AX'
    # )
    col_name: StringProperty(
        name="Collection name",
        default="Models"
    )

    is_asset: BoolProperty(
        name="Mark as asset",
        default=False
    )
    new_col: BoolProperty(
        name="New collection",
        default=False
    )
    # has_empty: BoolProperty(
    #     name = "Empty as handle already present",
    #     default = False
    # )
    catalog: StringProperty(
        name="Catalog name",
        default="Models",
    )
    render_preview: BoolProperty(
        name="Render preview",
        default=False,
        description="Rendering a preview"
    )
    save_ext: BoolProperty(
        name="Save external",
        default=False,
        description="Save the asset to an external .blend library"
    )
    ext_path: StringProperty(
        name="Collection name",
        default="Choose a .blend library",
        subtype='DIR_PATH'
    )
    # mod_size: FloatVectorProperty(
    #     name="Size of complete model",
    #     default=False
    # )

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and context.selected_objects

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        uiprops = scn.ui_props
        col = layout.column()
        col.prop(self, 'mod_name', text="What is your model's name?")
        col.separator()
        row = col.column_flow(colums=2)
        row.label(text="Choose a collection:")
        # Experimental treenode list
        row = layout.row()
        row.template_list(
            "MTools_PG_TreeItem_UL_basic",
            "",
            scn,
            "myListTree",
            scn,
            "myListTree_index",
            sort_lock=True
        )

        grid = layout.grid_flow(columns=2)

        # grid.operator("mops.debug", text="Reset").action = "reset3"
        # grid.operator("mops.debug", text="Clear").action = "clear"
        # grid.operator("mops.debug", text="Print").action = "print"

        # row.prop(context.scene, "col_select", text="")
        col.separator()

        # col.label(text="We will add an empty to act as controller. Choose a style:")
        # row = col.row(align=True)
        # row.prop(self, 'empty_ops', expand=True)
        col.label(text="Where would you like to position the controller?")
        row = col.row(align=True)
        row.prop(self, 'empty_loc', expand=True)
        col.separator()
        col.prop(self, "is_asset", text="Pack model and assign as asset")
        if self.is_asset:
            box = col.box()
            box.prop(
                uiprops,
                "show_asset_panel",
                text="Asset details",
                icon='TRIA_DOWN' if uiprops.show_bulk_undo else 'TRIA_RIGHT',
                emboss=False)
            if uiprops.show_asset_panel:
                # self.draw_asset_panel(context, box)
                ui.draw_make_asset_panel(context, box)

    def invoke(self, context, event):
        utils.update_asset_catalogs(self, context)
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        name = self.mod_name.strip()
        coll = self.col_name()
        empty_loc = self.empty_loc()
        ass = self.is_asset()
        ass_cat = self.catalog()
        ass_pre = self.render_preview()
        ass_save = self.save_ext()
        ass_save_path = self.ext_path()
        vl = context.view_layer
        # mod_size = self.mod_size()
        cat = self.catalog()

        if name:
            #### First we assemble the model ###
            # Get all the objects we have to include
            sel_objs, controller = \
                self.get_objects_to_assemble(self, context)
            # If nothing is selected, terminate
            if len(sel_objs) == 0:
                utils.popup_message(
                    message="No objects were selected.\nOperation cancelled.",
                    title="Operation cancelled")
                self.report(
                    {'INFO'},
                    "Cancelled operation. No objects were selected")
                return {'CANCELLED'}
            # Check if there is a parent empty controller, if not: create one
            if not controller:
                controller = bpy.data.objects.new(
                    name=self.mod_name, object_data=None)
                controller.empty_display_type = 'CUBE'
                controller.empty_display_size = 0.5
                context.scene.objects.link(controller)
                controller.show_axis = True
                controller.show_name = True
                controller.show_in_front
                # ... and set als parent to the other objects
                for o in sel_objs:
                    o.parent = controller
                    o.transform_apply(
                        location=False, rotation=True, scale=True)
            # Put all objects in chosen collection
            for o in sel_objs:
                context.collection[coll].link(o)
            # Make asset
            if self.is_asset:
                asset = self.create_asset(context, name, sel_objs, coll, cat)
            # Render preview thumbnail of the asseet
            thumbpath = os.path.join(utils.get_path(), 'resources', 'thumb.png')
            self.render_viewport(context, thumbpath)
            thumb = bpy.data.images.load(filepath=thumbpath)
            asset.preview_ensure()
            asset.preview.image_size = thumb.size
            # CodeManX is a legend
            asset.preview.image_pixels_float[:] = thumb.pixels

            bpy.data.images.remove(thumb)
            bpy.data.images.remove(bpy.data.images['Render Result'])
            os.unlink(thumbpath)
            return {'FINISHED'}

        else:
            utils.popup_message(
                "You'll have to provide a name for the model",
                title="Missing: asset name")

            return {'CANCELLED'}
    ## TODO: onderstaande functies uit operator halen indien nuttig
    def draw_asset_panel(self, context, layout):
        split = layout.split(factor=0.1)
        col = split.column()
        col = split.column()
        col.prop(
            context.window_manager,
            'mtools_catalogs',
            text='Choose Catalog'
        )
        col.prop(self, "render_preview", text="Render a preview")
        col.separator
        col.prop(self, "save_ext", text="Save to external .blend library")
        if self.save_ext:
            col.prop(self, "ext_path")

    def get_objects_to_assemble(self, context):
        '''Function to gather all assembly parts, non selected objects included'''
        sel = context.selected_objects
        objects = set()

        for obj in sel:
            objects.add(obj)
            # Also add non-selected parent objects
            if obj.parent and obj.parent not in sel:
                objects.add(obj.parent)
                if obj.parent.type == 'EMPTY':
                    # Identify parented empty as controller
                    controller = obj
            # Check if objects have booleans and include
            booleans = [mod for mod in obj.modifiers if mod.type == 'BOOLEAN']

            for mod in booleans:
                if mod.object and mod.object not in sel:
                    objects.add(mod.object)

            mirrors = [mod for mod in obj.modifiers if mod.type == 'MIRROR']
            # Same for mirror modifiers
            for mod in mirrors:
                if mod.mirror_object and mod.mirror_object not in sel:
                    objects.add(mod.mirror_object)
        # And also add non selected child objects of included parent
        for obj in context.visible_objects:
            if obj not in objects and obj.parent and obj.parent in objects:
                objects.add(obj)

        return objects, controller

    def create_asset(self, context, name, objects, collection, catalog):

        # Make a new collection within the collection where the model
        #  resides, to make an instance of.
        asscoll = bpy.data.collections.new(name)
        collection.children.link(asscoll)
        # Copy the model to the new collection,
        for o in objects:
            copy = o.copy()
            asscoll.link(copy)
        # Make an instance and add the copied model
        instance = bpy.data.objects.new(name, object_data=None)
        instance.instance_collection = asscoll
        instance.instance_type = 'COLLECTION'
        asscoll.objects.link(instance)
        # Mark the instance as asset
        instance.asset_mark()
        # If given, assign the asset to a catalog
        if catalog != 'NONE':
            instance.asset_data.catalog_id = self.catalogs[catalog]['uuid']

        collection.children.unlink(asscoll)

        return instance

    def render_viewport(self, context, filepath):

        resolution = (
            context.scene.render.resolution_x,
            context.scene.render.resolution_y)
        file_format = context.scene.render.image_settings.file_format
        lens = context.space_data.lens
        show_overlays = context.space_data.overlay.show_overlays

        context.scene.render.resolution_x = 128
        context.scene.render.resolution_y = 128
        context.scene.render.image_settings.file_format = 'JPEG'

        context.space_data.lens = self.thumbnail_lens

        if show_overlays:
            context.space_data.overlay.show_overlays = False

        bpy.ops.render.opengl()

        thumb = bpy.data.images.get('Render Result')

        if thumb:
            thumb.save_render(filepath=filepath)

        context.scene.render.resolution_x = resolution[0]
        context.scene.render.resolution_y = resolution[1]
        context.space_data.lens = lens

        context.scene.render.image_settings.file_format = file_format

        if show_overlays and self.toggle_overlays:
            context.space_data.overlay.show_overlays = True

    def get_empty_location(self, context, objects):

        rootobjs = [obj for obj in objects if not obj.type == 'EMPTY']

        if self.empty_loc in ['AVG', 'AVGFLOOR']:
            loc = utils.average_locations(
                [obj.matrix_world.decompose()[0] for obj in rootobjs])

            if self.empty_loc == 'AVGFLOOR':
                loc[2] = 0

        else:
            loc = Vector((0, 0, 0))

        return loc    

classes = (
    MTools_OT_MakeAsset,
    MTools_OT_UnpackAsset,
    MTools_OT_MakeModel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    


def unregister():


    for cls in classes:
        bpy.utils.unregister_class(cls)