#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
This is modified from 
RenderForCNN/render_pipeline/render_model_views.py by Weichao
vc-shapenet/blender_script.py by hao su, charles r. qi, yangyan li
to enable explictly control of lighting
'''

'''
RENDER_MODEL_VIEWS.py
brief:
    render projections of a 3D model from viewpoints specified by an input parameter file
usage:
	blender blank.blend --background --python render_model_views.py -- <shape_obj_filename> <shape_view_param_file> <syn_img_output_folder> <syn_anno_output_folder>

inputs:
       <shape_obj_filename>: .obj file of the 3D shape model
       <shape_view_params_file>: txt file - each line is '<azimith angle> <elevation angle> <in-plane rotation angle> <distance>'
       <syn_img_output_folder>: output folder path for rendered images of this model
       <syn_anno_output_folder>: output folder path for annotation of the rendered images

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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

import render_opt as opt

# Input parameters
shape_file = sys.argv[-4]
shape_view_params_file = sys.argv[-3]
syn_images_folder = sys.argv[-2]
syn_anno_folder = sys.argv[-1]
shape_file_name = shape_file.split('/')[-1].split('.')[0]
if not os.path.exists(syn_images_folder):
    os.mkdir(syn_images_folder)
    
if not os.path.exists(syn_anno_folder):
    os.mkdir(syn_anno_folder)

view_params = [[float(x) for x in line.strip().split(' ')] for line in open(shape_view_params_file).readlines()]

# import the object
if shape_file[-4:]=='.obj':
    bpy.ops.import_scene.obj(filepath=shape_file)
if shape_file[-4:]=='.off':
    # install the addon: https://github.com/alextsui05/blender-off-addon 
    # bpy.ops.wm.addon_install(filepath='/mnt/1TB_SSD/qing/blender-off-addon/import_off.py')
    bpy.ops.wm.addon_enable(module='import_off')
    bpy.ops.import_mesh.off(filepath=shape_file)
    
# fix the uv of the object
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.uv.sphere_project()
bpy.ops.object.mode_set(mode='OBJECT')

bpy.context.scene.render.alpha_mode = 'TRANSPARENT'
#bpy.context.scene.render.use_shadows = False
#bpy.context.scene.render.use_raytrace = False

bpy.data.objects['Lamp'].data.energy = 0

#m.subsurface_scattering.use = True

camObj = bpy.data.objects['Camera']


# remove default light
bpy.ops.object.select_all(action='TOGGLE')
if 'Lamp' in list(bpy.data.objects.keys()):
    bpy.data.objects['Lamp'].select = True
bpy.ops.object.delete()


# function for adding image texture to objects (including floor, background, etc)
texture_imgs = glob.glob('/mnt/4TB_b/qing/dataset/COCO/train2017/*.jpg')
def add_image_to_obj(obj, image_file_path):
    obj_name = obj.name
    img = bpy.data.images.load(image_file_path)
    tex = bpy.data.textures.new("tex_"+obj_name, 'IMAGE')
    tex.image=img

    mat = bpy.data.materials.new("mat_"+obj_name)
    tslot = mat.texture_slots.add()
    tslot.texture = tex
    
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
        
# get list of keypoints
anchor_dir = '/mnt/1TB_SSD/dataset/PASCAL3D+_release1.1/Anchor/'
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


keypoints = []
for kk in keypoint_list:
    vert_ls = []
    keypoint_name = '{}_{}'.format(shape_file_name, kk)
    mkfile = os.path.join(anchor_dir, 'car', keypoint_name+'.off')

    # de-select all objects
    for obj_name in list(bpy.data.objects.keys()):
        bpy.data.objects[obj_name].select = False

    if os.path.exists(mkfile):
        bpy.ops.import_mesh.off(filepath=mkfile)
        bpy.data.objects[keypoint_name].select = True
        for vv in bpy.context.active_object.data.vertices:
            flg = True
            for vv_curr in vert_ls:
                if vv.co.x == vv_curr.x and vv.co.y == vv_curr.y and vv.co.z == vv_curr.z:
                    flg=False
                    break
                    
            if flg:
                vert_ls.append(vv.co)

    keypoints.append(vert_ls)
    

# rendering different viewpoints
for param in view_params:
    obj_plane = bpy.data.objects["Plane"]
    add_image_to_obj(obj_plane, np.random.choice(texture_imgs))

    obj_cylinder = bpy.data.objects["Cylinder"]
    add_image_to_obj(obj_cylinder, np.random.choice(texture_imgs))
    
    obj_car = bpy.data.objects[shape_file_name]
    add_image_to_obj(obj_car, np.random.choice(texture_imgs))

    azimuth_deg = param[0]
    elevation_deg = param[1]
    theta_deg = param[2]
    rho = param[3]

    # clear default lights
    bpy.ops.object.select_by_type(type='LAMP')
    bpy.ops.object.delete(use_global=False)

    # set environment lighting
    #bpy.context.space_data.context = 'WORLD'
    opt.setup_lighting()

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
    # ** multiply tilt by -1 to match pascal3d annotations **
    theta_deg = (-1*theta_deg)%360
    syn_image_file = '%s_a%03d_e%03d_t%03d_d%03d.png' % (shape_file_name, round(azimuth_deg), round(elevation_deg), round(theta_deg), round(rho))
    bpy.data.scenes['Scene'].render.filepath = os.path.join(syn_images_folder, syn_image_file)
    bpy.ops.render.render( write_still=True )
    
    loc_keypoints = []
    for kk in keypoints:
        pos_kk = []
        for vv in kk:
            px, py, _ = opt.project_by_object_utils(camObj, vv)
            pos_kk.append([px, py])
            
        loc_keypoints.append(pos_kk)
        
    syn_anno_file = syn_image_file.replace('.png','.pkl')
    with open(os.path.join(syn_anno_folder, syn_anno_file), 'wb') as fh:
        pickle.dump(loc_keypoints, fh)
