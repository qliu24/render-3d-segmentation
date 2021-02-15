import os, sys, tempfile, shutil, glob
import os.path as osp

# import blender configuration
BASE_DIR = osp.dirname(osp.abspath(__file__))
sys.path.append(BASE_DIR)

blender_executable_path = '/mnt/1TB_SSD/qing/blender-2.79b-linux-glibc219-x86_64/blender'
# blank_file = osp.join(BASE_DIR, 'sky.blend')
blank_file = osp.join(BASE_DIR, 'blank.blend')
render_code = 'blender_manual_anno_kp2.py'
    

def render(img_savedir, anno_savedir, model_id, model_dir, anno_dir, par_file, vcolor='random'):
    # run code
    render_cmd = '%s %s --background --python %s -- %s %s %s %s %s %s %s' % (
        blender_executable_path, 
        blank_file, 
        render_code,
        vcolor,
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
    save_root_dir = '/mnt/1TB_SSD/qing/blender_scripts/render_test/'
#     save_root_dir = '/mnt/4TB_b/qing/synthetic_images/car_models/trial_1_041920'
    
#     anno_savedir = osp.join(save_root_dir, 'kp')
    
#     model_dic={'sedan':'6710c87e34056a29aa69dfdc5532bb13',
#                'truck':'42af1d5d3b2524003e241901f2025878',
#                'minivan':'4ef6af15bcc78650bedced414fad522f',
#                'suv':'473dd606c5ef340638805e546aa28d99',
#                'race':'d4251f9cf7f1e0a7cac1226cb3e860ca',
#                'wagon':'bad0a52f07afc2319ed410a010efa019'}
    
#     model_color = {'sedan':['red','blue'], 'suv':['blue','green'], 'wagon':['green','black'], 'truck':['black','red']}
#     for model_key in model_color.keys():
#         for vcolor in model_color[model_key]:
#             img_savedir = osp.join(save_root_dir, 'image_{}'.format(vcolor))
            
#             model_id = model_dic[model_key]
#             model_dir = '/mnt/4TB_b/qing/dataset/shapenet/ShapeNetCore.v2/02958343/'
#             anno_dir = osp.join(project_root_dir, 'car_models')
#             par_file = osp.join(project_root_dir, 'viewpoints', 'trial_1.txt')
#         #     par_file = osp.join(project_root_dir, 'viewpoints', 'round.txt')
#         #     par_file = osp.join(project_root_dir, 'viewpoints', 'hand_anno_parts_vp.txt')
#             render(img_savedir, anno_savedir, model_id, model_dir, anno_dir, par_file, vcolor)

    anno_savedir = osp.join(save_root_dir, 'kp')
    model_dic={'motor1':'6ea0a49bd27fa58b2279b76b11a9a16c',
               'motor2':'3837c8ef573c2a7b360cf6eb12fae4',
               'motor3':'2ff252507b18ce60cd4bec905df51d1d',
               'motor4':'a70eb1b6321022e260e00ef7af003fee',
               'motor5':'9cb038f61be71ed0cca5d7fbf4f17f56',
               'motor6':'db5b6c2f64fefe5b448c90b3a2fec4b8',}

    for model_key in model_dic.keys():
        img_savedir = osp.join(save_root_dir, model_key)
        model_id = model_dic[model_key]
        model_dir = '/mnt/4TB_b/qing/dataset/shapenet/ShapeNetCore.v2/03790512/'
        anno_dir = osp.join(project_root_dir, 'car_models')
        par_file = osp.join(project_root_dir, 'viewpoints', 'round.txt')
        render(img_savedir, anno_savedir, model_id, model_dir, anno_dir, par_file, 'plain')
        
        

