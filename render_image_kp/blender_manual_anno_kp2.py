#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
blender_hand_anno_parts.py
brief:
    render projections of a 3D model and its hand annotated parts from viewpoints specified by an input parameter file
usage:
	blender blank.blend --background --python blender_hand_anno_parts.py -- <img_savedir> <anno_savedir> <model_id> <model_dir> <anno_dir> <par_file>

inputs:
       <img_savedir>: path to save images
       <anno_savedir>: path to save the depth maps
       <model_id>: shapenet model id
       <model_dir>: path to shapenet model files
       <anno_dir>: path to hand annotated part .obj files
       <par_file>: txt file - each line is '<azimith angle> <elevation angle> <in-plane rotation angle> <distance>'
author: Qing Liu
'''

import os
import bpy
import sys
import math
import random
import numpy as np
import glob
import pickle
import render_opt as opt
import mathutils


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# Input parameters
surface = sys.argv[-7] # plain, white/black/red/green/blue, random_pic
color_dic={'white':(1,1,1),'black':(0,0,0),'red':(1,0,0),'green':(0,1,0),'blue':(0,0,1)}
material_dic={'6710c87e34056a29aa69dfdc5532bb13':'material_2',
              '42af1d5d3b2524003e241901f2025878':'material_1',
              '4ef6af15bcc78650bedced414fad522f':'material_3',
              '473dd606c5ef340638805e546aa28d99':'material_3_16',
              'd4251f9cf7f1e0a7cac1226cb3e860ca':'material_1',
              'bad0a52f07afc2319ed410a010efa019':'material_25,material_48,material_47'
             }
img_savedir = sys.argv[-6]
anno_savedir = sys.argv[-5]
model_id = sys.argv[-4]
model_dir = sys.argv[-3]
anno_dir = sys.argv[-2]
par_file = sys.argv[-1]

if not os.path.exists(img_savedir):
    os.mkdir(img_savedir)
    
if not os.path.exists(anno_savedir):
    os.mkdir(anno_savedir)

view_params = [[float(x) for x in line.strip().split(' ')] for line in open(par_file).readlines()]

bpy.context.scene.render.alpha_mode = 'TRANSPARENT'
bpy.data.scenes['Scene'].render.resolution_percentage = 100
camObj = bpy.data.objects['Camera']

# obj_plane = bpy.data.objects["Plane"]
# obj_cylinder = bpy.data.objects["Cylinder"]

# import the object
shape_file = os.path.join(model_dir, model_id, 'models', 'model_normalized.obj')
bpy.ops.import_scene.obj(filepath=shape_file,use_split_groups=False,use_split_objects=False)
obj_car = bpy.data.objects["model_normalized"]

# read random surface image list
texture_imgs = glob.glob('/mnt/4TB_b/qing/dataset/COCO/train2017/*.jpg')
if surface=='random_pic':
    obj_car.active_material_index = 0
    for i in range(len(obj_car.material_slots)):
        bpy.ops.object.material_slot_remove({'object': obj_car})

    # fix the uv of the object
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects.active=obj_car
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.sphere_project()
    bpy.ops.object.mode_set(mode='OBJECT')
    
elif surface in color_dic.keys():
    print('Make surface {}.'.format(surface))
    if model_id in material_dic.keys():
        mtl_name=material_dic[model_id]
        if ',' in mtl_name:
            for mm in mtl_name.split(','):
                mtl = bpy.data.materials[mm]
                mtl.diffuse_color=color_dic[surface]
        else:
            mtl = bpy.data.materials[mtl_name]
            mtl.diffuse_color=color_dic[surface]
    else:
        print('Unknown model id for material list. Keep surface plain.')
else:
    pass
    


# read the keypoint coords
# kp_file = os.path.join(anno_dir, 'annotations', '{}.txt'.format(model_id))
# kp_list = [[float(x) for x in line.replace(',','').strip().split(' ')[-3:]] for line in open(kp_file).readlines()]

for param in view_params:
    if surface=='random_pic':
        opt.add_image_to_obj(obj_plane, np.random.choice(texture_imgs))
        opt.add_image_to_obj(obj_cylinder, np.random.choice(texture_imgs))
        opt.add_image_to_obj(obj_car, np.random.choice(texture_imgs))
    elif surface=='random_color':
        opt.add_image_to_obj(obj_plane, np.random.choice(texture_imgs))
        opt.add_image_to_obj(obj_cylinder, np.random.choice(texture_imgs))
        
        if model_id in material_dic.keys():
            mtl_name=material_dic[model_id]
            r_color=np.random.random(size=(3,))
            if ',' in mtl_name:
                for mm in mtl_name.split(','):
                    mtl = bpy.data.materials[mm]
                    mtl.diffuse_color=r_color
            else:
                mtl = bpy.data.materials[mtl_name]
                mtl.diffuse_color=r_color
        else:
            print('Unknown model id for material list. Keep surface plain.')
    
    azimuth_deg = param[0]
    elevation_deg = param[1]
    theta_deg = param[2]
    rho = param[3]

    cx, cy, cz = opt.obj_centened_camera_pos(rho, azimuth_deg, elevation_deg)
    q1 = opt.camPosToQuaternion(cx, cy, cz)
    q2 = opt.camRotQuaternion(cx, cy, cz, theta_deg)
    q = opt.quaternionProduct(q2, q1)
    camObj.location[0] = cx
    camObj.location[1] = cy 
    camObj.location[2] = cz
    camObj.rotation_mode = 'QUATERNION'
    camObj.rotation_quaternion[0] = q[0]
    camObj.rotation_quaternion[1] = q[1]
    camObj.rotation_quaternion[2] = q[2]
    camObj.rotation_quaternion[3] = q[3]

    # clear default lights
    bpy.ops.object.select_by_type(type='LAMP')
    bpy.ops.object.delete(use_global=False)

    # set environment lighting
    #bpy.context.space_data.context = 'WORLD'
    # opt.setup_lighting(use_sun_light=1, use_additional_light=False, loc=(cx, cy, cz-0.2))
    loc1 = (cx*10, cy*10, (cz-0.05)*10)
    xydis = np.sqrt(loc1[0]**2+loc1[1]**2)
    loc2 = (xydis*np.sign(loc1[0]), 0, loc1[2])
    loc3 = (0, xydis*np.sign(loc1[1]), loc1[2])
    
    opt.use_sun_light(energy=1, loc=loc1)
    opt.use_point_light(energy=0.8, loc=[loc2,loc3])

    # ** multiply tilt by -1 to match pascal3d annotations **
    theta_deg = (-1*theta_deg)%360
    
    
    # render image of the whole object
    syn_image_file = '%s_a%03d_e%03d_t%03d_d%03d.png' % (model_id, round(azimuth_deg), round(elevation_deg), round(theta_deg), round(rho*100))
    bpy.data.scenes['Scene'].render.filepath = os.path.join(img_savedir, syn_image_file)
    bpy.ops.render.render( write_still=True )
    
    # render keypoint locations
#     loc_keypoints = []
#     for vv in kp_list:
#         vv_g = [vv[0],-vv[2],vv[1]]
#         px, py, pz = opt.project_by_object_utils(camObj, mathutils.Vector(vv_g))
#         loc_keypoints.append([px, py, pz])
        
#     syn_anno_file = syn_image_file.replace('.png','.pkl')
#     with open(os.path.join(anno_savedir, syn_anno_file), 'wb') as fh:
#         pickle.dump(loc_keypoints, fh)
    
    
    
