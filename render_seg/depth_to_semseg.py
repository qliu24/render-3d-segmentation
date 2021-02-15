import numpy as np
import os
import cv2
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--obj_class', type=str, default='aeroplane',
                    help='name of the object class (car, motorbike, etc.)')
parser.add_argument('--model_key', type=str, default='airliner',
                    help='name of the subtype key (sedan, SUV, etc.)')
parser.add_argument('--suffix', type=str, default='')
args = parser.parse_args()


def read_depth_img(file_name, alpha=False):
    depth_map = cv2.imread(file_name, cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)
    depth_map_filtered = depth_map[:,:,0] # depth
    if alpha:
        alpha_channel = depth_map_filtered<1e10 # upper bound of depth
        depth_map_filtered = depth_map_filtered*alpha_channel
        return depth_map_filtered, alpha_channel
        
    return depth_map_filtered

def main():
#     part_num=31
    if args.obj_class == 'car':
        part_idxs = np.arange(31).reshape(31,1)
        model_dic={'sedan':'6710c87e34056a29aa69dfdc5532bb13',
               'truck':'42af1d5d3b2524003e241901f2025878',
               'minivan':'4ef6af15bcc78650bedced414fad522f',
               'suv':'473dd606c5ef340638805e546aa28d99', # 'race':'d4251f9cf7f1e0a7cac1226cb3e860ca',
               'wagon':'bad0a52f07afc2319ed410a010efa019'}
    if args.obj_class == 'motorbike':
        # merge some parts
        part_idxs = [[0], [1], [2], [3], [4,5,6,14,27,28,29,30], # wheel_front, wheel_back, fender_front, fender_back, frame
                    [7], [8], [9], # mirror_left, mirror_right, windscreen
                    [10], [11], [12], [13], # license_plate, seat, seat_back, gas_tank
                    [15], [16], [17,18,19], # handle_left, handle_right, headlight
                    [20,21,22], [23,24], # taillight, exhaust_left
                    [25,26], # exhaust_right
                    [31], [32], [33,34]] # engine, cover_front, cover_body
        model_dic={'cruiser':'6ea0a49bd27fa58b2279b76b11a9a16c',
           'chopper':'3837c8ef573c2a7b360cf6eb12fae4',
           'scooter':'5131b742dad94f6175dadc997718614d',
           'dirtbike':'db5b6c2f64fefe5b448c90b3a2fec4b8'}
    if args.obj_class == 'aeroplane':
        # merge some parts
        part_idxs = [[0], [1,2,3,4,5,6,7,8,9], # propeller, cockpit
                    [10], [11], [12], # wing_left, wing_right, fin
                    [13], [14], [15], [16], # tailplane_left, tailplane_right, wheel_front, landing_gear_front
                    [17], [18], [19], [20], # wheel_back_left, gear_back_left, wheel_back_right, gear_back_right
                    [21], [22], [23,24,25,26], [27,28,29,30], # engine_left, engine_right, door_left, door_right
                    [31], [32], # bomb_left, bomb_right
                    [33,34], [35,36], [37,38]] # window_left, window_right, body

        model_dic={'airliner':'10e4331c34d610dacc14f1e6f4f4f49b',
                   'jet':'5cf29113582e718171d03b466c72ce41',
                   'fighter':'b0b164107a27986961f6e1cef6b8e434',
                   'biplane':'17c86b46990b54b65578b8865797aa0'}
        
    project_root_dir = '/mnt/1TB_SSD/qing/blender_scripts/'
    data_root_dir = '/mnt/4TB_b/qing/3DComputerGraphicsPart/'
    
    file_dir = os.path.join(data_root_dir, 'synthetic_images', args.obj_class, 'depth{}'.format(args.suffix))
    save_dir = os.path.join(data_root_dir, 'synthetic_images', args.obj_class, 'seg{}'.format(args.suffix))
    
    model_key = args.model_key
    assert model_key in model_dic.keys()
    model_id = model_dic[model_key]
    print('processing model: {}, suffix: {}'.format(model_key, args.suffix))
    if args.suffix=='2':
        lsfile = 'dataset_{}_p.txt'
    else:
        lsfile = 'dataset_{}.txt'
    
    par_file = os.path.join(project_root_dir, 'viewpoints', 'dataset', lsfile.format(model_key))
    view_params = [[float(x) for x in line.strip().split(' ')] for line in open(par_file).readlines()]

    os.makedirs(os.path.join(save_dir, model_id), exist_ok=True)

    for pi,param in enumerate(view_params):
        if (pi+1)%500==0:
            print('{}/{}...'.format(pi+1, len(view_params)))

        azimuth_deg = param[0]
        elevation_deg = param[1]
        theta_deg = param[2]
        rho = param[3]
        
        # aeroplane
        if elevation_deg<=-25 and rho>=3:
            rho -= 1

        # ** multiply tilt by -1 to match pascal3d annotations **
        theta_deg = (-1*theta_deg)%360
        depth_file_whole = '%s_a%03d_e%03d_t%03d_d%03d.exr' % (model_id, round(azimuth_deg), round(elevation_deg), round(theta_deg), round(rho*100))
        depth_file_whole_p = os.path.join(file_dir, model_id, depth_file_whole)
        assert os.path.exists(depth_file_whole_p),depth_file_whole_p
        depth_whole, alpha_whole = read_depth_img(depth_file_whole_p, alpha=True)
        depth_map_list = []
        for part_idx_ls in part_idxs:
            depth_part = np.ones_like(depth_whole)*np.inf
            for part_idx in part_idx_ls:
                depth_file_p = depth_file_whole_p.replace('.exr','_{}.exr'.format(part_idx))
                if not os.path.exists(depth_file_p):
#                     print('no exist depth file: '+os.path.join(file_dir, depth_file))
                    continue
                else:
                    _dd = read_depth_img(depth_file_p)
                    depth_part = np.minimum(depth_part, _dd)

            depth_map_list.append(depth_part)

        seg_mask = np.argmin(depth_map_list, axis=0)+1
    #     uncertain_mask = np.min(depth_map_list, axis=0)==np.max(depth_whole)
    #     uncertain_mask = np.greater(np.min(depth_map_list, axis=0), depth_whole+100)
    #     uncertain_mask = np.logical_and(alpha_whole==1, uncertain_mask)
    #     print('sum of uncertain_mask: {}'.format(np.sum(uncertain_mask)))
        target = np.zeros_like(seg_mask)
        target[alpha_whole==1] = seg_mask[alpha_whole==1]
    #     target[uncertain_mask] = 255

        save_file = depth_file_whole.replace('.exr','.png')
        cv2.imwrite(os.path.join(save_dir, model_id, save_file), target.astype(np.uint8))
    
if __name__ == '__main__':
    main()