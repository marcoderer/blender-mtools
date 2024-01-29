import bpy
from bpy.types import  Panel


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


def draw_make_model_panel():
    pass


class MTOOLS_PT_MainPanel(Panel):
    bl_category = "MTools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"


class MTOOLS_PT_BulkUndo(MTOOLS_PT_MainPanel, Panel):
    bl_label = "Bulk Undo & Redo"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.label(icon='LOOP_BACK')
        undo_Tools = row.operator('mtools.bulk_undo', text='3')
        undo_Tools.undo_steps = 3

        undo_5 = row.operator('mtools.bulk_undo', text='5')
        undo_5.undo_steps = 5

        undo_10 = row.operator('mtools.bulk_undo', text='10')
        undo_10.undo_steps = 10

        undo_20 = row.operator('mtools.bulk_undo', text='20')
        undo_20.undo_steps = 20

        row = layout.row(align=True)
        row.label(icon='LOOP_FORWARDS')

        redo_Tools = row.operator('mtools.bulk_redo', text='3')
        redo_Tools.redo_steps = 3

        redo_5 = row.operator('mtools.bulk_redo', text='5')
        redo_5.redo_steps = 5

        redo_10 = row.operator('mtools.bulk_redo', text='10')
        redo_10.redo_steps = 10

        redo_20 = row.operator('mtools.bulk_redo', text='20')
        redo_20.redo_steps = 20

class MTOOLS_PT_MakeModel(MTOOLS_PT_MainPanel, Panel):
    bl_label = "Assembly Tools"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == "MESH" and obj.mode in {"OBJECT", "EDIT"}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
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

class MTOOLS_PT_MeshActions(MTOOLS_PT_MainPanel, Panel):
    bl_label = "Mesh Operations"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Separate & Select", icon="OUTLINER_DATA_MESH")
        row = layout.row(align=True)
        op = row.operator(
            "mops.separate_select_object",
            text="Selection",
            icon="ASSET_MANAGER",
            separate_method="SELECTED",
        )
        # op.separate_method= 'SELECTED'
        op = row.operator(
            "mops.separate_select_object",
            text="Loose",
            icon="ASSET_MANAGER",
            separate_method="LOOSE",
        )
        op = row.operator(
            "mops.separate_select_object",
            text="Material",
            icon="ASSET_MANAGER",
            separate_method="MATERIAL",
        )


class MTOOLS_PT_MeshGenerator(MTOOLS_PT_MainPanel, Panel):
    bl_label = "Mesh Generator"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column()
        col.label(text="Nothing here yet")


class MTOOLS_PT_SaveTool(MTOOLS_PT_MainPanel, Panel):
    bl_label = "Save tools"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column()
        col.label(text="Nothing here yet")


class MTOOLS_PT_ViewOps(MTOOLS_PT_MainPanel, Panel):
    bl_label = "View & Cam Ops"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Locking the camera to:")
        row = layout.row(align=True)
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

        row = layout.row()
        row.label(text="Viewpoint:")
        row = layout.row(align=True)
        row.operator("view3d.view_camera", text="Camera", icon='IMAGE_PLANE')
        row.operator("view3d.view_selected",
                     text="Selected", icon='STICKY_UVS_LOC')
        row.operator("view3d.view_all", text="All", icon='STICKY_UVS_DISABLE')

        row = layout.row(align=True)
        
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
        row = layout.row()
        row.prop(
            context.space_data.region_3d,
            'lock_rotation',
            text='Lock Rotation',
            toggle=True,
            icon='DECORATE_LOCKED')
        row = layout.row()
        row.label(text="Align camera to:")
        row = layout.row(align=True)
        row.operator("view3d.camera_to_view", text="View", icon='IMAGE_PLANE')
        row.operator("view3d.camera_to_view_selected",
                     text="Selected", icon='STICKY_UVS_LOC')
        row.operator("view3d.camera_to_view_all",
                     text="All", icon='STICKY_UVS_DISABLE')
        row = layout.row()
        row.label(text="Camera settings:")
        row = layout.row(align=True)
        row.label(text='Focal length', icon='RESTRICT_RENDER_OFF')
        row.prop(context.space_data, "lens", text="")

class MTOOLS_PT_DevTools(MTOOLS_PT_MainPanel, Panel):
    bl_label = "Dev Tools"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.operator("script.reload", text="Reload scripts")


classes = (
    MTOOLS_PT_MainPanel,
    MTOOLS_PT_BulkUndo,
    MTOOLS_PT_MakeModel,
    MTOOLS_PT_MeshActions,
    MTOOLS_PT_MeshGenerator,
    MTOOLS_PT_SaveTool,
    MTOOLS_PT_ViewOps,
    MTOOLS_PT_DevTools,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
