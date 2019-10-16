mode = bpy.context.active_object.mode
bpy.ops.object.mode_set(mode='OBJECT')
electedVerts=[v for v in bpy.context.active_object.data.vertices if v.select]
for v in selectedVerts:
    print(v.co)
    
bpy.ops.object.mode_set(mode=mode)