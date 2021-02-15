import pickle
import os, cv2, glob
import numpy as np

dataset_rootdir = '/mnt/4TB_b/qing/3DComputerGraphicsPart/synthetic_images/car'
model_dic={'sedan':'6710c87e34056a29aa69dfdc5532bb13',
               'truck':'42af1d5d3b2524003e241901f2025878',
               'minivan':'4ef6af15bcc78650bedced414fad522f',
               'suv':'473dd606c5ef340638805e546aa28d99',
               'wagon':'bad0a52f07afc2319ed410a010efa019'}

for model_name in model_dic.keys():
    model_id = model_dic[model_name]
    for batch in ['','2']:
        img_dir = os.path.join(dataset_rootdir, 'image{}'.format(batch), model_id)
        anno_dir = os.path.join(dataset_rootdir, 'kp{}'.format(batch), model_id)
        depth_dir = os.path.join(dataset_rootdir, 'depth{}'.format(batch), model_id)
        save_dir = os.path.join(dataset_rootdir, 'kp{}_v'.format(batch), model_id)
        os.makedirs(save_dir, exist_ok=True)
        anno_file_ls = glob.glob(os.path.join(anno_dir,'*'))
        
        for fi,anno_file in enumerate(anno_file_ls):
            if (fi+1)%500==0:
                print('{}/{}...'.format(fi+1, len(anno_file_ls)))
                
            file_name = os.path.basename(anno_file)
            with open(anno_file, 'rb') as fh:
                kp_ls = pickle.load(fh)

            depth_file = os.path.join(depth_dir, file_name.replace('.pkl','.exr'))
            assert os.path.exists(depth_file), depth_file
            depth_map = cv2.imread(depth_file, cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)
            
            kp_ls_vis = dict()

            d_height, d_width = depth_map.shape[0:2]
            for vn,vv in kp_ls.items():
                if round(vv[0])<0 or round(vv[1])<0:
                    kp_ls_vis[vn] = [0.0, 0.0, 0.0]
                elif round(vv[1]) >= d_height or round(vv[0]) >= d_width:
                    kp_ls_vis[vn] = [0.0, 0.0, 0.0]
                elif (depth_map[round(vv[1]),round(vv[0]),0]-vv[2])>-0.01 or depth_map[round(vv[1]),round(vv[0]),0]>1e10:
                    kp_ls_vis[vn] = vv[:2]+[1.0]
                else:
                    kp_ls_vis[vn] = vv[:2]+[0.0]
                    
            with open(os.path.join(save_dir, file_name), 'wb') as fh:
                pickle.dump(kp_ls_vis, fh)