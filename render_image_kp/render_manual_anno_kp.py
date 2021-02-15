import os, sys, shutil, glob
import os.path as osp

# import blender configuration
BASE_DIR = osp.dirname(osp.abspath(__file__))
sys.path.append(BASE_DIR)

blender_executable_path = '/mnt/1TB_SSD/qing/blender-2.79b-linux-glibc219-x86_64/blender'
blank_file = osp.join(BASE_DIR, '../env/sky.blend')
render_code = 'blender_manual_anno_kp.py'
    

def render(model_id, par_file, cfg_path):
    # run code
    render_cmd = '%s %s --background --python %s -- -m %s -p %s -c %s' % (
        blender_executable_path, 
        blank_file, 
        render_code,
        model_id,
        par_file,
        cfg_path
    )
    try:
        print(render_cmd)
        os.system(render_cmd)
    except Exception as e:
        print(e)
        print('render failed. render_cmd: %s' % (render_cmd))
        

if __name__ == '__main__':
    obj_class = 'aeroplane'
    cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'config_{}.ini'.format(obj_class))
    project_root_dir = '/mnt/1TB_SSD/qing/blender_scripts/'
    
#     model_dic={'sedan':'6710c87e34056a29aa69dfdc5532bb13',
#                'truck':'42af1d5d3b2524003e241901f2025878',
#                'minivan':'4ef6af15bcc78650bedced414fad522f',
#                'suv':'473dd606c5ef340638805e546aa28d99',
#                'race':'d4251f9cf7f1e0a7cac1226cb3e860ca',
#                'wagon':'bad0a52f07afc2319ed410a010efa019'}
    
#     model_dic={'cruiser':'6ea0a49bd27fa58b2279b76b11a9a16c',
#            'chopper':'3837c8ef573c2a7b360cf6eb12fae4',
#            'scooter':'5131b742dad94f6175dadc997718614d',
#            'dirtbike':'db5b6c2f64fefe5b448c90b3a2fec4b8'}

    model_dic={'airliner':'10e4331c34d610dacc14f1e6f4f4f49b',
               'jet':'5cf29113582e718171d03b466c72ce41',
               'fighter':'b0b164107a27986961f6e1cef6b8e434',
               'biplane':'17c86b46990b54b65578b8865797aa0'}
    
    for model_key in model_dic.keys():
        model_id = model_dic[model_key]
        par_file = osp.join(project_root_dir, 'viewpoints', 'dataset', 'dataset_{}_p.txt'.format(model_key))
        render(model_id, par_file, cfg_path)
        
