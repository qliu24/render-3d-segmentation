#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
blender_hand_anno_parts.py
brief:
    render projections of a 3D model and its hand annotated parts from viewpoints specified by an input parameter file
usage:
	blender blank.blend --background --python blender_hand_anno_parts.py -- <anno_savedir> <model_id> <model_dir> <anno_dir> <par_file>

inputs:
       <anno_savedir>: path to save the depth maps
       <model_id>: shapenet model id
       <model_dir>: path to shapenet model files
       <anno_dir>: path to hand annotated part .obj files
       <par_file>: txt file - each line is '<azimith angle> <elevation angle> <in-plane rotation angle> <distance>'
author: Qing Liu
'''

import os
import bpy
import bpy_extras
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

def main():
    # Input parameters
    anno_savedir = sys.argv[-5]
    model_id = sys.argv[-4]
    model_dir = sys.argv[-3]
    anno_dir = sys.argv[-2]
    par_file = sys.argv[-1]

    # part_list_file = '/mnt/1TB_SSD/qing/blender_scripts/car_models/part_list.txt'
    # part_list = [line.strip() for line in open(part_list_file).readlines()]

    if not os.path.exists(anno_savedir):
        os.mkdir(anno_savedir)

    view_params = [[float(x) for x in line.strip().split(' ')] for line in open(par_file).readlines()]

    bpy.context.scene.render.alpha_mode = 'TRANSPARENT'
    bpy.data.scenes['Scene'].render.resolution_percentage = 100
    #switch on nodes
    scene = bpy.data.scenes['Scene']
    scene.render.use_compositing = True
    scene.use_nodes = True
    tree = scene.node_tree
    links = tree.links

    # clear default nodes
    for n in tree.nodes:
        tree.nodes.remove(n)

    # create input render layer node
    rl = tree.nodes.new('CompositorNodeRLayers')
    comp = tree.nodes.new('CompositorNodeComposite')
    links.new(rl.outputs[2], comp.inputs[0])
    
    scene.render.image_settings.file_format = 'OPEN_EXR' # set the format. the extension should be exr?
    
    # render the depth maps of the whole object
    shape_file = os.path.join(anno_dir,'car_models_hand_annotated', model_id, 'model_normalized.obj')
    syn_image_file_template = os.path.join(anno_savedir, model_id+'_a{:03d}_e{:03d}_t{:03d}_d{:03d}.exr')
    render_obj(view_params, shape_file, syn_image_file_template)
    
    # render the depth map of the annotated parts
    # for part_idx in range(len(part_list)):
    #     shape_file = os.path.join(anno_dir, 'car_models_hand_annotated','{}_{}.obj'.format(model_id, part_list[part_idx]))
    #     syn_image_file_template = os.path.join(anno_savedir, model_id+'_a{:03d}_e{:03d}_t{:03d}_d{:03d}_'+str(part_idx)+'.exr')
    #     render_obj(view_params, shape_file, syn_image_file_template)


# function for rendering depth maps
def render_obj(view_params, shape_file, syn_image_file_template):
    # import object
    bpy.ops.import_scene.obj(filepath=shape_file,use_split_groups=False,use_split_objects=False)
    camObj = bpy.data.objects['Camera']
    
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
        #bpy.context.space_data.context = 'WORLD'
        opt.setup_lighting(use_sun_light=1, use_additional_light=False, loc=(cx, cy, cz-0.2))

        # ** multiply tilt by -1 to match pascal3d annotations **
        theta_deg = (-1*theta_deg)%360

        # render depth map of the object
        syn_image_file = syn_image_file_template.format(round(azimuth_deg), round(elevation_deg), round(theta_deg), round(rho*100))
        bpy.data.scenes['Scene'].render.filepath = syn_image_file
        bpy.ops.render.render(write_still=True)

    # delete the object
    obj_name = os.path.basename(shape_file).split('.')[0]
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[obj_name].select = True
    bpy.ops.object.delete() 
    
    
if __name__ == '__main__':
    main()
