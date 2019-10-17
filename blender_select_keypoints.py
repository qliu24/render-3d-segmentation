import os
import bpy
import sys
import numpy as np
import pickle

'''
RENDER_MODEL_VIEWS.py
brief:
    render projections of a 3D model from viewpoints specified by an input parameter file
usage:
    blender blank.blend --background --python blender_select_keypoints.py -- <shape_obj_anchor_dir> <output_dir>

inputs:
       <shape_obj_anchor_dir>: dir of the 3D shape model keypoint .off files
       <output_dir>: output folder path for keypoint 3d locations

author: Qing Liu
'''

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# bpy.ops.wm.addon_install(filepath='/mnt/1TB_SSD/qing/blender-off-addon/import_off.py')
bpy.ops.wm.addon_enable(module='import_off')

# Input parameters
anchor_dir = sys.argv[-2]
output_dir = sys.argv[-1]
if not os.path.exists(output_dir):
    os.mkdir(output_dir)
    

keypoint_list = ['left_back_light','left_back_trunk','left_back_wheel',
                 'left_front_light','left_front_wheel',
                 'left_window_center','left_window_up',
                 'lower_left_rearwindow','lower_left_windshield',
                 'lower_right_rearwindow','lower_right_windshield',
                 'right_back_light','right_back_trunk','right_back_wheel',
                 'right_front_light','right_front_wheel', 
                 'right_window_center','right_window_up', 
                 'upper_left_rearwindow','upper_left_windshield',
                 'upper_right_rearwindow','upper_right_windshield']

for mi in range(1,11):
    mi_keypoints = []
    for kk in keypoint_list:
        vert_ls = []
        keypoint_name = '{:02d}_{}'.format(mi, kk)
        mkfile = os.path.join(anchor_dir, 'car', keypoint_name+'.off')
        
        # de-select all objects
        for obj_name in list(bpy.data.objects.keys()):
            bpy.data.objects[obj_name].select = False
            
        if os.path.exists(mkfile):
            bpy.ops.import_mesh.off(filepath=mkfile)
            bpy.data.objects[keypoint_name].select = True
            for vv in bpy.context.active_object.data.vertices:
                vert_ls.append(list(vv.co))
                
        mi_keypoints.append(vert_ls)
        
    save_file = os.path.join(output_dir, '{:02d}_anchor_xyz.pickle'.format(mi))
    print('saving achor points to: ' + save_file)
    with open(save_file, 'wb') as fh:
        pickle.dump(mi_keypoints, fh)