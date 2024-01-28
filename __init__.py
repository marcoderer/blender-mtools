import bpy
import os

from datetime import datetime, timedelta
from pathlib import Path

from mathutils import Vector
from bpy.props import (
    BoolProperty,
    PointerProperty,
    IntProperty,
    EnumProperty,
    StringProperty
)

from bpy.types import (
Panel,
Operator,
PropertyGroup,
UIList,
WindowManager,
)


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





# ------------------------------------------------------------
#    ENUMS
# ------------------------------------------------------------

empty_locs = [
    ('AVG', 'Average', 'Roughly the center of your model'),
    ('AVGFLOOR', 'Average Floor', 'On the floor right under your model'),
    ('WORLDORIGIN', 'World Origin', 'The place where it all began')
]

# ------------------------------------------------------------
#    USER LISTS
# ------------------------------------------------------------

class VIEW3D_UL_MyList(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'OUTLINER_COLLECTION'
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon=custom_icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon=custom_icon)

# ------------------------------------------------------------
#    HELPER FUNCTIONS
# ------------------------------------------------------------

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

def draw_make_asset_panel(self, context, layout):
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

# ------------------------------------------------------------
#    USER INTERFACE
# ------------------------------------------------------------

class MTools_PT_MainPanel(Panel):
    bl_idname = "MTools_PT_MTools"
    bl_label = "Marco's Toolbox"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MTools"
    

    @classmethod
    def poll(cls, context):
        return context.mode in {'EDIT_MESH', 'OBJECT'}

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        uiprops = scn.ui_props

        # box = layout.box()
        box = layout.box()
        box.prop(
            uiprops,
            "show_mesh_generator",
            text="Fancy Mesh Generator",
            icon='TRIA_DOWN' if uiprops.show_mesh_generator else 'TRIA_RIGHT',
            emboss=False)
        if uiprops.show_mesh_generator:
            self.draw_mesh_generator(context, box)

        box = layout.box()
        box.prop(
            uiprops,
            "show_bulk_undo",
            text="Bulk Undo & Redo",
            icon='TRIA_DOWN' if uiprops.show_bulk_undo else 'TRIA_RIGHT',
            emboss=False)
        if uiprops.show_bulk_undo:
            self.draw_bulk_undo(context, box)

        box = layout.box()
        box.prop(
            uiprops,
            "show_dev_tools",
            text="Dev Tools",
            icon='TRIA_DOWN' if uiprops.show_dev_tools else 'TRIA_RIGHT',
            emboss=False)
        if uiprops.show_dev_tools:
            self.draw_dev_tools(context, box)

        if context.mode == 'OBJECT':

            box = layout.box()
            box.prop(
                uiprops,
                "show_object_tools",
                text="Object Tools",
                icon='TRIA_DOWN' if uiprops.show_object_tools else 'TRIA_RIGHT',
                emboss=False)
            if uiprops.show_object_tools:
                self.draw_object_tools(uiprops, box)

            box = layout.box()
            box.prop(
                uiprops,
                "show_camera_shortcuts",
                text="Camera & Viewpoint Tools",
                icon='TRIA_DOWN' if uiprops.show_camera_shortcuts else 'TRIA_RIGHT',
                emboss=False)
            if uiprops.show_camera_shortcuts:
                self.draw_camera_shortcuts(context, box)

        elif context.mode == 'EDIT_MESH':

            box = layout.box()
            box.prop(
                uiprops,
                "show_edit_tools",
                text="Edit Tools",
                icon='TRIA_DOWN' if uiprops.show_edit_tools else 'TRIA_RIGHT',
                emboss=False)
            if uiprops.show_edit_tools:
                self.draw_edit_tools(context, box)

    def draw_mesh_generator(self, context, layout):
        col = layout.column()
        box = col.box()
        col = box.column(align=True)
        col.label(text="hier is nog wat werk te doen...")

    def draw_edit_tools(self, context, layout):
        col = layout.column()
        box = col.box()
        col = box.column(align=True)
        row = col.row()
        row.label(text="Separate & Select", icon='OUTLINER_DATA_MESH')
        row = col.row(align=True)
        op = row.operator("mops.separate_select_object",
                          text="Selection", icon='ASSET_MANAGER')
        op.separate_method = 'SELECTED'
        op = row.operator("mops.separate_select_object",
                          text="Loose", icon='ASSET_MANAGER')
        op.separate_method = 'LOOSE'
        op = row.operator("mops.separate_select_object",
                          text="Material", icon='ASSET_MANAGER')
        op.separate_method = 'MATERIAL'

    def draw_object_tools(self, context, layout):
        col = layout.column()
        box = col.box()
        col = box.column(align=True)
        col.operator("mops.make_model", text="Make a model",
                     icon='STICKY_UVS_LOC')
        col.separator
        box = col.box()
        box.label(text="Model options:")
        row = box.row(align=True)
        row.prop(context,
                 'placeholder',
                 text="Hide controller",
                 expand=True,
                 toggle=True
                 )
        row.prop(context,
                 'placeholder',
                 text="Position controller",
                 expand=True,
                 toggle=True
                 )
        row = box.row(align=True)
        row.prop(context,
                 'placeholder',
                 text="Select parts",
                 expand=True,
                 toggle=True
                 )
        row.prop(context,
                 'placeholder',
                 text="Autoselect",
                 expand=True,
                 toggle=True
                 )
        row = box.row(align=True)
        row.prop(context,
                 'placeholder',
                 text="Make duplicate",
                 expand=True,
                 toggle=True
                 )
        row.operator("mops.make_asset", text="Model > Asset")
        row.separator()
        row = box.row(align=True)
        row.prop(context,
                 'placeholder',
                 text="Add selected objects to model",
                 expand=True,
                 toggle=True
                 )
        row.prop(context,
                 'placeholder',
                 text="Remove selected objects from model",
                 expand=True,
                 toggle=True
                 )
        col.operator("mops.unpack_asset",
                     text="Asset > Model", icon='ASSET_MANAGER')

    def draw_camera_shortcuts(self, context, layout):
        col = layout.column()
        box = col.box()
        row = box.row()
        row.label(text="Locking the camera to:")
        row = box.row(align=True)
        row.prop(
            context.space_data,
            'lock_camera',
            text='View',
            toggle=True,
            icon='CON_CAMERASOLVER'
        )
        row.prop(
            context.space_data,
            'lock_cursor',
            text='3D cursor',
            toggle=True,
            icon='PIVOT_CURSOR'
        )

        row = box.row()
        row.label(text="Viewpoint:")
        row = box.row(align=True)
        row.operator("view3d.view_camera", text="Camera", icon='IMAGE_PLANE')
        row.operator("view3d.view_selected",
                     text="Selected", icon='STICKY_UVS_LOC')
        row.operator("view3d.view_all", text="All", icon='STICKY_UVS_DISABLE')

        row = box.row(align=True)
        # row.operator("mops.toggle_view_lock_active", text= "Lock on active")
        split = row.split(factor=0.9)

        row = split.row()
        subsplit = row.split(factor=0.4)
        col = subsplit.column()
        col.label(text="Lock view to:")
        col = subsplit.column()
        col.prop(
            context.space_data,
            'lock_object',
            text="",
            toggle=True,
            icon='MATCUBE'
        )
        col = split.column()
        col.operator("view3d.view_lock_clear",
                     text="", icon='DECORATE_UNLOCKED')
        row = box.row()
        row.prop(
            context.space_data.region_3d,
            'lock_rotation',
            text='Lock Rotation',
            toggle=True,
            icon='DECORATE_LOCKED')
        row = box.row()
        row.label(text="Align camera to:")
        row = box.row(align=True)
        row.operator("view3d.camera_to_view", text="View", icon='IMAGE_PLANE')
        row.operator("view3d.camera_to_view_selected",
                     text="Selected", icon='STICKY_UVS_LOC')
        row.operator("view3d.camera_to_view_all",
                     text="All", icon='STICKY_UVS_DISABLE')
        row = box.row()
        row.label(text="Camera settings:")
        row = box.row(align=True)
        row.label(text='Focal length', icon='RESTRICT_RENDER_OFF')
        row.prop(context.space_data, "lens", text="")

    def draw_bulk_undo(self, context, layout):
        # TODO: Undo history UIlist
        col = layout.column()
        box = col.box()
        row = box.row(align=True)
        row.label(icon='LOOP_BACK')
        undo_Tools = row.operator('mtools.bulk_undo', text='3')
        undo_Tools.undo_steps = 3

        undo_5 = row.operator('mtools.bulk_undo', text='5')
        undo_5.undo_steps = 5

        undo_10 = row.operator('mtools.bulk_undo', text='10')
        undo_10.undo_steps = 10

        undo_20 = row.operator('mtools.bulk_undo', text='20')
        undo_20.undo_steps = 20

        row = box.row(align=True)
        row.label(icon='LOOP_FORWARDS')

        redo_Tools = row.operator('mtools.bulk_redo', text='3')
        redo_Tools.redo_steps = 3

        redo_5 = row.operator('mtools.bulk_redo', text='5')
        redo_5.redo_steps = 5

        redo_10 = row.operator('mtools.bulk_redo', text='10')
        redo_10.redo_steps = 10

        redo_20 = row.operator('mtools.bulk_redo', text='20')
        redo_20.redo_steps = 20

    def draw_dev_tools(self, context, layout):
        col = layout.column()
        box = col.box()
        col = box.column()
        col.operator("script.reload", text="Reload scripts")


# ------------------------------------------------------------
#    OPERATORS
# ------------------------------------------------------------

class MTOOLS_OT_BackupTool(Operator):
    
    bl_idname = "mops.backup_tool"
    bl_label = "Backup blend files"
    
    keep: IntProperty(
        name="Number of backups",
        description= "The number of backupversions to keep of one file"
        )
    
    def execute(self,context):
        timestamp = datetime.now()
        srcdir = Path.cwd()
        dir_tmstamp = datetime.now.strftime("%Y%m%d%H%M%S")
        file_pattrns = "*.py"
        keep_last = 20
        
        py_list = list(srcdir.glob('**/*.py'))
        print(py_list)

        
        return {'FINISHED'}
    
    def remove_obsolete(self,context,dest_file_count):
        if self.keep > 20:
            pass
            
        

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

    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH"

    def execute(self, context):
        org_obj_list = {o.name for o in context.selected_objects}

        bpy.ops.mesh.separate(type=self.separate_method)
        bpy.ops.object.editmode_toggle()
        # Deselect all other objects but the new created object
        for obj in context.selected_objects:
            if obj and obj.name in org_obj_list:
                # Deselect everything selected before
                obj.select_set(False)
            else:
                # Set the new created object to active
                context.view_layer.objects.active = obj
                self.report({'INFO'}, f"Set active object to: {obj.name}")

        return {'FINISHED'}


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

    def draw(self, context):  # Draw options (typically displayed in the tool-bar)
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
                parent(child, instance)

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
                draw_make_asset_panel(context, box)

    def invoke(self, context, event):
        update_asset_catalogs(self, context)
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
                popup_message(
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
            thumbpath = os.path.join(get_path(), 'resources', 'thumb.png')
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
            popup_message(
                "You'll have to provide a name for the model",
                title="Missing: asset name")

            return {'CANCELLED'}

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
            loc = average_locations(
                [obj.matrix_world.decompose()[0] for obj in rootobjs])

            if self.empty_loc == 'AVGFLOOR':
                loc[2] = 0

        else:
            loc = Vector((0, 0, 0))

        return loc



# ------------------------------------------------------------
#    PROPERTIES
# ------------------------------------------------------------

class MTools_PG_UIProperties(PropertyGroup):
    '''Properties regarding the user interface'''
    show_edit_tools: BoolProperty(
        name="Show Edit Tools"
    )
    show_object_tools: BoolProperty(
        name="Show Object Tools"
    )
    show_camera_shortcuts: BoolProperty(
        name="Show Camera Shortcuts"
    )
    show_bulk_undo: BoolProperty(
        name="Show Bulk Undo"
    )
    show_dev_tools: BoolProperty(
        name="Show Dev Tools"
    )
    show_mesh_generator: BoolProperty(
        name="Show Mesh Generator"
    )
    placeholder: BoolProperty()
    show_asset_subpanel: BoolProperty(
        name="Show Asset subpanel"
    )

# ------------------------------------------------------------
#    REGISTER
# ------------------------------------------------------------

classes = (
    MTools_PT_MainPanel,
    MTools_PG_UIProperties,
    MTools_OT_UnpackAsset,
    MTools_OT_SeparateSelectObject,
    MTools_OT_BulkUndo,
    MTools_OT_BulkRedo,
    MTools_OT_MakeAsset,
    MTools_OT_MakeModel,
    VIEW3D_UL_MyList,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.ui_props = PointerProperty(
        type=MTools_PG_UIProperties,
        name="Addon Properties",
        description="Global properties that the addon uses"
    )


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == '__main__':
    register()
