"""Assign a measured site material. Usage: blender file.blend --python tools/toggle_mars_layer.py -- color|elevation|slope"""
import sys

import bpy

SITE = "NASA_HiRISE_DTM_Jezero_FieldSite_4m"
LAYERS = {
    "color": "Mars_NASA_HiRISE_Viking_Color",
    "elevation": "Mars_Layer_Elevation_Measured",
    "slope": "Mars_Layer_Slope_Measured",
}


def main() -> None:
    choice = "color"
    if "--" in sys.argv:
        choice = sys.argv[sys.argv.index("--") + 1]
    material_name = LAYERS[choice]
    material = bpy.data.materials[material_name]
    mesh = bpy.data.objects[SITE].data
    if not mesh.materials:
        mesh.materials.append(material)
    else:
        mesh.materials[0] = material
    bpy.context.scene["active_mars_layer"] = choice
    print("ACTIVE_LAYER", choice, material_name)


if __name__ == "__main__":
    main()
