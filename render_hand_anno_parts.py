import os, sys, tempfile, shutil, glob
import os.path as osp

# import blender configuration
BASE_DIR = osp.dirname(osp.abspath(__file__))
sys.path.append(BASE_DIR)

blender_executable_path = '/mnt/1TB_SSD/qing/blender-2.79b-linux-glibc219-x86_64/blender'
blank_file = osp.join(BASE_DIR, 'blank.blend')
render_code = 'blender_hand_anno_parts.py'
    

def render(img_savedir, anno_savedir, model_id, model_dir, anno_dir, par_file):
    # run code
    render_cmd = '%s %s --background --python %s -- %s %s %s %s %s %s' % (
        blender_executable_path, 
        blank_file, 
        render_code,
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
    img_savedir = osp.join(project_root_dir, 'car_models','dataset','images')
    anno_savedir = osp.join(project_root_dir, 'car_models','dataset','depth')
    model_id = '6710c87e34056a29aa69dfdc5532bb13'
    model_dir = '/mnt/4TB_b/qing/dataset/shapenet/ShapeNetCore.v2/02958343/'
    anno_dir = osp.join(project_root_dir, 'car_models')
    par_file = osp.join(project_root_dir, 'viewpoints', 'hand_anno_parts_vp.txt')
    render(img_savedir, anno_savedir, model_id, model_dir, anno_dir, par_file)
