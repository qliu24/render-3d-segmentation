import numpy as np
import os
import cv2
import matplotlib.pyplot as plt


def read_depth_img(file_name, alpha=False):
    img = cv2.imread(file_name)
    img_filtered = img[:,:,0] # depth
    if alpha:
        alpha_channel = img_filtered!=255 # upper bound of depth
        img_filtered = img_filtered*alpha_channel
        return img_filtered, alpha_channel
        
    return img_filtered

project_root_dir = '/mnt/1TB_SSD/qing/blender_scripts/'
file_dir = os.path.join(project_root_dir, 'car_models', 'dataset', 'depth')
model_id = '6710c87e34056a29aa69dfdc5532bb13'
par_file = os.path.join(project_root_dir, 'viewpoints', 'hand_anno_parts_vp.txt')
view_params = [[float(x) for x in line.strip().split(' ')] for line in open(par_file).readlines()]

for param in view_params:
    azimuth_deg = param[0]
    elevation_deg = param[1]
    theta_deg = param[2]
    rho = param[3]
    
    # ** multiply tilt by -1 to match pascal3d annotations **
    theta_deg = (-1*theta_deg)%360
    img_file_whole = '%s_a%03d_e%03d_t%03d_d%03d.png' % (model_id, round(azimuth_deg), round(elevation_deg), round(theta_deg), round(rho))
    img_whole, img_alpha = read_depth_img(os.path.join(file_dir, img_file_whole), alpha=True)
    img_whole = img_whole.astype(float)
    depth_map_list = [img_whole]
    seg_map_list = [img_alpha]
    for part_idx in range(31):
        img_file = img_file_whole.replace('.png','_{}.png'.format(part_idx))
        img_part = read_depth_img(os.path.join(file_dir, img_file))
        img_part = img_part.astype(float)
        depth_map_list.append(img_part)
        seg_map = np.logical_and((img_part - img_whole)<=0, img_alpha!=0)
        seg_map_list.append(seg_map)
        
    save_file = img_file_whole.replace('.png','.npz')
    np.savez(os.path.join(file_dir, save_file), depth_map = depth_map_list, seg_map = seg_map_list)
    