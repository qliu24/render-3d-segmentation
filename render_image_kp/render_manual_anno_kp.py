import os, sys, shutil, glob
import os.path as osp
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--blender_executable_path', type=str, 
                    default='/mnt/1TB_SSD/qing/blender-2.79b-linux-glibc219-x86_64/blender')
parser.add_argument('--obj_cls', type=str, default='car',
                    help='object class (car, motorbike, etc.)')
parser.add_argument('--model_id', type=str, default='6710c87e34056a29aa69dfdc5532bb13',
                    help='shapenet model id')
parser.add_argument('--vp_file', type=str, default='round.txt',
                    help='filename for viewpoint parameters')
parser.add_argument('--bg_file', type=str, default='blank.blend',
                    help='filename for blender environment file')
args = parser.parse_args()

# import blender configuration
BASE_DIR = osp.dirname(osp.abspath(__file__))
sys.path.append(BASE_DIR)
blank_file = osp.join(BASE_DIR, '../env/', args.bg_file)
render_code = 'blender_manual_anno_kp.py'

def render(model_id, par_file, cfg_path):
    # run code
    render_cmd = '%s %s --background --python %s -- -m %s -p %s -c %s' % (
        args.blender_executable_path, 
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
    cfg_path = osp.join(BASE_DIR, 'config_{}.ini'.format(args.obj_cls))
    par_file = osp.join(BASE_DIR, '../viewpoints/', args.vp_file)
    render(args.model_id, par_file, cfg_path)