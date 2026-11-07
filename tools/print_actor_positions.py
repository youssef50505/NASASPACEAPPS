"""Print world positions needed to place routes on the existing site."""
import bpy

names = [
    "Joe_Astronaut", "Joe_JA", "ludovisions_FC1_rig", "MSL", "Wheels_objs",
    "MARS_NEW_Globe", "MARS_NEW_Globe_Camera", "MARS_NEW_Explore_Area_Pin",
    "Mars_Sun", "NASA_HiRISE_DTM_Jezero_FieldSite_4m",
]
for name in names:
    obj = bpy.data.objects.get(name)
    if obj is None:
        print("MISSING", name)
        continue
    loc = obj.matrix_world.translation
    print(f"{name} type={obj.type} loc=({loc.x:.3f},{loc.y:.3f},{loc.z:.3f}) dim={tuple(round(v, 2) for v in obj.dimensions)}")
print("FRAME_END", bpy.context.scene.frame_end)
records = bpy.context.scene.get("crew_grounding_records")
if records:
    print("GROUNDING", records[:1500])
