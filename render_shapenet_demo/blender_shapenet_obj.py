#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
blender_hand_anno_parts.py
brief:
    render projections of a 3D model and its hand annotated parts from viewpoints specified by an input parameter file
usage:
	blender blank.blend --background --python blender_hand_anno_parts.py -- <img_savedir> <model_id> <model_dir> <par_file>

inputs:
       <img_savedir>: path to save images
       <model_id>: shapenet model id
       <model_dir>: path to shapenet model files
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
img_savedir = sys.argv[-4]
model_id = sys.argv[-3]
model_dir = sys.argv[-2]
par_file = sys.argv[-1]

if not os.path.exists(img_savedir):
    os.mkdir(img_savedir)
    
view_params = [[float(x) for x in line.strip().split(' ')] for line in open(par_file).readlines()]

bpy.context.scene.render.alpha_mode = 'TRANSPARENT'
bpy.data.scenes['Scene'].render.resolution_percentage = 100
camObj = bpy.data.objects['Camera']

# import the object
shape_file = os.path.join(model_dir, model_id, 'models', 'model_normalized.obj')
if not os.path.exists(shape_file):
    shape_file = os.path.join(model_dir, model_id, 'model.obj')
    
bpy.ops.import_scene.obj(filepath=shape_file,use_split_groups=False,use_split_objects=False)
if 'model_normalized.obj' in shape_file:
    obj_car = bpy.data.objects["model_normalized"]
else:
    obj_car = bpy.data.objects["model"]

for param in view_params:
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
    # bpy.context.space_data.context = 'WORLD'
    # opt.setup_lighting(use_sun_light=1, use_additional_light=False, loc=(cx, cy, cz-0.2))
    loc1 = (cx*10, cy*10, (cz-0.05)*10)
    xydis = np.sqrt(loc1[0]**2+loc1[1]**2)
    loc2 = (xydis*np.sign(loc1[0]), 0, loc1[2])
    loc3 = (0, xydis*np.sign(loc1[1]), loc1[2])
    
    opt.use_sun_light(energy=1, loc=loc1)
#     opt.use_point_light(energy=0.5, loc=[loc2,loc3])

    # ** multiply tilt by -1 to match pascal3d annotations **
    theta_deg = (-1*theta_deg)%360
    
    
    # render image of the whole object
    syn_image_file = '%s_a%03d_e%03d_t%03d_d%03d.png' % (model_id, round(azimuth_deg), round(elevation_deg), round(theta_deg), round(rho*100))
    bpy.data.scenes['Scene'].render.filepath = os.path.join(img_savedir, syn_image_file)
    bpy.ops.render.render( write_still=True )
    
    
    

