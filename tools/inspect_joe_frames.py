"""Find a frame where Joe is still beside the rover."""
import bpy
from mathutils import Vector

scene = bpy.context.scene
joe = bpy.data.objects["Joe_Astronaut"]
rover = bpy.data.objects["MSL"]
print("frame_start", scene.frame_start, "frame_end", scene.frame_end, "current", scene.frame_current)
for frame in range(scene.frame_start, scene.frame_end + 1, 20):
    scene.frame_set(frame)
    delta = joe.matrix_world.translation - rover.matrix_world.translation
    print(frame, [round(float(v), 1) for v in joe.matrix_world.translation], "from_rover", round(delta.length, 1))
