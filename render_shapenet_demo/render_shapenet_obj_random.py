import os, sys, tempfile, shutil, glob
import os.path as osp
import numpy as np

# import blender configuration
BASE_DIR = osp.dirname(osp.abspath(__file__))
sys.path.append(BASE_DIR)

blender_executable_path = '/mnt/1TB_SSD/qing/blender-2.79b-linux-glibc219-x86_64/blender'
# blank_file = osp.join(BASE_DIR, 'sky.blend')
blank_file = osp.join(BASE_DIR, 'blank.blend')
render_code = 'blender_shapenet_obj.py'
    

def render(img_savedir, model_id, model_dir, par_file):
    # run code
    render_cmd = '%s %s --background --python %s -- %s %s %s %s' % (
        blender_executable_path, 
        blank_file, 
        render_code,
        img_savedir,
        model_id,
        model_dir,
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
    save_root_dir = '/mnt/1TB_SSD/qing/blender_scripts/render_test/bicycle'
    shapenet_root = '/mnt/4TB_b/qing/dataset/shapenet/ShapeNetCore.v2/'
    obj_class = '02834778'
    model_ls = glob.glob(os.path.join(shapenet_root, obj_class, '*'))
    model_ls = [os.path.basename(mm) for mm in model_ls]
    model_ls_selected = model_ls
#     model_ls_selected = np.random.choice(model_ls, size=(100,), replace=False)
    
#     model_ls_selected = ['a4678e6798e768c3b6a66ea321171690',
#                 '8de793e2e964f40a26c713777861983a',
#                 'b2bb5a56b3d805b298b8c800ae001b66',
#                 'd8a43017132c210cc1006ed55bc1a3fc',
#                 '17c86b46990b54b65578b8865797aa0',
#                 'd1e3bba19cb9447dcf6c095014f481a4',
#                 'a1017765200c668c6ecd5ddc73f570a8'
#                ]
    
    for model_index, model_id in enumerate(model_ls_selected):
        img_savedir = osp.join(save_root_dir, obj_class+'_'+str(model_index))
        model_dir = os.path.join(shapenet_root, obj_class)
        par_file = osp.join(project_root_dir, 'viewpoints', 'round.txt')
        render(img_savedir, model_id, model_dir, par_file)
        
        


