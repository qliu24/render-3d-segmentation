import os, sys, tempfile, shutil, glob
import os.path as osp

# import blender configuration
BASE_DIR = osp.dirname(osp.abspath(__file__))
sys.path.append(BASE_DIR)

blender_executable_path = '/mnt/1TB_SSD/qing/blender-2.79b-linux-glibc219-x86_64/blender'
blank_file = osp.join(BASE_DIR, 'sky.blend')
render_code = 'blender_manual_anno_kp.py'
    

def render(img_savedir, anno_savedir, model_id, model_dir, anno_dir, par_file):
    # run code
    render_cmd = '%s %s --background --python %s -- %s %s %s %s %s %s %s' % (
        blender_executable_path, 
        blank_file, 
        render_code,
        'random_color',
        img_savedir,
        anno_savedir,
        model_id,
        model_dir,
        anno_dir,
        par_file
    )
    try:
        print(render_cmd)
        os.system(render_cmd)
    except Exception as e:
        print(e)
        print('render failed. render_cmd: %s' % (render_cmd))
        

if __name__ == '__main__':
    project_root_dir = '/mnt/1TB_SSD/qing/blender_scripts/'
    save_root_dir = '/mnt/4TB_b/qing/synthetic_images/car_models/dataset'
    
    model_dic={'sedan':'6710c87e34056a29aa69dfdc5532bb13',
               'truck':'42af1d5d3b2524003e241901f2025878',
               'minivan':'4ef6af15bcc78650bedced414fad522f',
               'suv':'473dd606c5ef340638805e546aa28d99',
               'race':'d4251f9cf7f1e0a7cac1226cb3e860ca',
               'wagon':'bad0a52f07afc2319ed410a010efa019'}
    
    model_dir = '/mnt/4TB_b/qing/dataset/shapenet/ShapeNetCore.v2/02958343/'
    anno_dir = osp.join(project_root_dir, 'car_models')
    for model_key in model_dic.keys():
        model_id = model_dic[model_key]
        img_savedir = osp.join(save_root_dir, 'image2', model_key)
        anno_savedir = osp.join(save_root_dir, 'kp2', model_key)
        par_file = osp.join(project_root_dir, 'viewpoints', 'dataset_{}_p.txt'.format(model_key))
        render(img_savedir, anno_savedir, model_id, model_dir, anno_dir, par_file)
