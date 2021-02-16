#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
blender_manual_anno_kp.py
brief:
    render projections of a 3D model and its manually annotated keypoints from viewpoints specified by an input parameter file
usage:
	blender blank.blend --background --python blender_manual_anno_kp.py -- <surface_color> <img_savedir> <anno_savedir> <model_id> <model_dir> <anno_dir> <par_file>

inputs:
       <surface_color>: one of ['random_color', 'random_pic', 'plain', 'white', 'black', 'red', 'green', 'blue']
       <img_savedir>: path to save images
       <anno_savedir>: path to save the keypoints
       <model_id>: shapenet model id
       <model_dir>: path to shapenet model files
       <anno_dir>: path to annotated keypoints .txt files
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
import mathutils
sys.path.insert(1,'../')
import render_opt as opt
import configparser
import argparse
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)    

def main(model_id, par_file, config_file):
    assert os.path.exists(config_file)
    cfg_parser = configparser.ConfigParser(allow_no_value=True)
    cfg_parser.read_file(open(config_file))
    
    model_dir = cfg_parser['Locations']['model_dir']
    anno_dir = cfg_parser['Locations']['anno_dir']
    img_savedir = os.path.join(cfg_parser['Locations']['img_savedir'], model_id)
    anno_savedir = os.path.join(cfg_parser['Locations']['anno_savedir'], model_id)
    texture_imgs = glob.glob(os.path.join(cfg_parser['Locations']['texture_img_dir'],'*.jpg'))
    surface = cfg_parser['Param']['surface']
    
    material_dic = cfg_parser['Material']
    color_dic = dict()
    for cc in cfg_parser['Color'].keys():
        color_dic[cc] = json.loads(cfg_parser['Color'][cc])
        
    kp_list = list(cfg_parser['Keypoints'])

    if not os.path.exists(img_savedir):
        os.makedirs(img_savedir)

    if not os.path.exists(anno_savedir):
        os.makedirs(anno_savedir)

    view_params = [[float(x) for x in line.strip().split(' ')] for line in open(par_file).readlines()]

    bpy.context.scene.render.alpha_mode = 'TRANSPARENT'
    bpy.data.scenes['Scene'].render.resolution_percentage = 100
    camObj = bpy.data.objects['Camera']

    obj_plane = bpy.data.objects["Plane"]
    obj_cylinder = bpy.data.objects["Cylinder"]

    # import the object
    shape_file = os.path.join(model_dir, model_id, 'models', 'model_normalized.obj')
    bpy.ops.import_scene.obj(filepath=shape_file,use_split_groups=False,use_split_objects=False)
    obj_car = bpy.data.objects["model_normalized"]

    mtl_ls = [] # surface material list
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
    elif surface == 'plain':
        pass
    else:
        if model_id in material_dic.keys():
            mtl_ls = material_dic[model_id].split(',')
        else:
            print('Unknown model id for material list. Keep surface plain.')
            
        if surface in color_dic.keys():
            print('Make surface {}.'.format(surface))
            for mm in mtl_ls:
                mtl = bpy.data.materials[mm]
                mtl.diffuse_color=color_dic[surface]
                

    # read the keypoint coords
    kp_file = os.path.join(anno_dir, '{}.txt'.format(model_id))
    kp_anno_dict = dict()
    with open(kp_file,'r') as fh:
        file_content = fh.readlines()
        
    for ll in file_content:
        assert len(ll.strip().split()) == 4, ll
        kp_name = ll.strip().split()[0]
        assert kp_name not in kp_anno_dict.keys()
        kp_xyz = [float(nn) for nn in ll.strip().split()[1:]]
        kp_anno_dict[kp_name] = kp_xyz
        

    for param in view_params:
        if surface=='random_pic':
            opt.add_image_to_obj(obj_plane, np.random.choice(texture_imgs))
            opt.add_image_to_obj(obj_cylinder, np.random.choice(texture_imgs))
            opt.add_image_to_obj(obj_car, np.random.choice(texture_imgs))
        elif surface=='random_color':
            opt.add_image_to_obj(obj_plane, np.random.choice(texture_imgs))
            opt.add_image_to_obj(obj_cylinder, np.random.choice(texture_imgs))
            
            for mm in mtl_ls:
                r_color=np.random.random(size=(3,))
                mtl = bpy.data.materials[mm]
                mtl.diffuse_color=r_color
        else:
            pass

        azimuth_deg = param[0]
        elevation_deg = param[1]
        theta_deg = param[2]
        rho = param[3]
        
        # aeroplane
        if elevation_deg<=-25 and rho>=3:
            rho -= 1
            
        cx, cy, cz = opt.obj_centened_camera_pos(rho, azimuth_deg, elevation_deg)
        if cz < -1:
            obj_plane.location = [0,0,-4]
        else:
            obj_plane.location = [0,0,-0.4]
        
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
        opt.setup_random_lighting((cx, cy, cz+0.2))

        # ** multiply tilt by -1 to match pascal3d annotations **
        theta_deg = (-1*theta_deg)%360

        # render depth map of the whole object
        syn_image_file = '%s_a%03d_e%03d_t%03d_d%03d.png' % (model_id, round(azimuth_deg), round(elevation_deg), round(theta_deg), round(rho*100))
        bpy.data.scenes['Scene'].render.filepath = os.path.join(img_savedir, syn_image_file)
        bpy.ops.render.render( write_still=True )

        loc_keypoints = dict()
        for kp_name in kp_list:
            if kp_name in kp_anno_dict:
                vv = kp_anno_dict[kp_name]
                vv_g = [vv[0],-vv[2],vv[1]]
                px, py, pz = opt.project_by_object_utils(camObj, mathutils.Vector(vv_g))
                loc_keypoints[kp_name] = [px, py, pz]

        syn_anno_file = syn_image_file.replace('.png','.pkl')
        with open(os.path.join(anno_savedir, syn_anno_file), 'wb') as fh:
            pickle.dump(loc_keypoints, fh)


    # K = opt.get_calibration_matrix_K_from_blender(camObj.data)
    # print(K)
    
if __name__ == '__main__':
    argv = sys.argv[sys.argv.index("--") + 1:]
    parser = argparse.ArgumentParser(
        description='blender rendering code with keypoints.')
    parser.add_argument('-m', '--shapenet_model_id',
                        type=str, help='Name of the shapenet model')
    parser.add_argument('-p', '--vp_par_file',
                        type=str, help='path to the viewpoint parameter file')
    parser.add_argument('-c', '--config_file', 
                        type=str, help='configuration file for the rendering')
    args = parser.parse_args(argv)
    main(args.shapenet_model_id, args.vp_par_file, args.config_file)
    