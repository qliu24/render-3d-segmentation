import os, sys, tempfile, shutil, glob
import os.path as osp

# import blender configuration
BASE_DIR = osp.dirname(osp.abspath(__file__))
sys.path.append(BASE_DIR)

blender_executable_path = '/mnt/1TB_SSD/qing/blender-2.79b-linux-glibc219-x86_64/blender'
blank_file = osp.join(BASE_DIR, 'sky.blend')
render_code = 'blender_script.py'
    

def render(model_file, viewpoint_file, syn_images_folder):
    # image_name = model_file.split('/')[-3] + '.png'
    image_name = model_file.split('/')[-1].replace('.off','.png')
    print(model_file, image_name)
    if not osp.exists(syn_images_folder):
        os.mkdir(syn_images_folder)

    # run code

    render_cmd = '%s %s --background --python %s -- %s %s %s' % (
        blender_executable_path, 
        blank_file, 
        render_code, 
        model_file,
        viewpoint_file, 
        syn_images_folder
    )
    try:
        print(render_cmd)
        os.system(render_cmd)
    except Exception as e:
        print(e)
        print('render failed. render_cmd: %s' % (render_cmd))
        

if __name__ == '__main__':
    # List models
    
    # model_dir = 'ShapeNetCore.v1/02691156/*/model.obj'
    # 02691156 is the id for airplane
    # * is the md5 id?
    
    # model_dir = '/mnt/1TB_SSD/qing/vc-shapenet/examples/car/*/models/model_normalized.obj'
    # model_dir = '/mnt/1TB_SSD/qing/blender_scripts/PASCAL3D+_obj/01r.obj'
    model_dir = '/mnt/1TB_SSD/qing/blender_scripts/PASCAL3D+_obj/01.off'
    print(model_dir)
    models = glob.glob(model_dir)
    print(len(models))
    
    # viewpoint
    for model_file in models:
        model_name = model_file.replace('.off','').split('/')[-1]
        
        viewpoint_file = './viewpoints/azi8r10ele1r5_{}.txt'.format(model_name) 
        syn_images_folder = osp.join(BASE_DIR, 'images')
        render(model_file, viewpoint_file, syn_images_folder)
