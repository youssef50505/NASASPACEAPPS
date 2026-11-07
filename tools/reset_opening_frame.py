"""Put the saved playhead back on the opening shot."""
import bpy

bpy.context.scene.frame_set(76)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_mainfile()
print("FRAME", bpy.context.scene.frame_current)
