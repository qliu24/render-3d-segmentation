import os, sys, tempfile, shutil, glob
import os.path as osp

# set debug mode
debug_mode = 0
if debug_mode:
    io_redirect = ''
else:
    io_redirect = ' > /dev/null 2>&1'

# import blender configuration
BASE_DIR = osp.dirname(osp.abspath(__file__))
sys.path.append(BASE_DIR)

blender_executable_path = '/mnt/1TB_SSD/qing/blender-2.79b-linux-glibc219-x86_64/blender'
blank_file = osp.join(BASE_DIR, 'sky.blend')
render_code = 'blender_script.py'
    

def render(model_file, viewpoints, syn_images_folder):
    # image_name = model_file.split('/')[-3] + '.png'
    image_name = model_file.split('/')[-1].replace('.off','.png')
    print(model_file, image_name)
    if not osp.exists(syn_images_folder):
        os.mkdir(syn_images_folder)

    # run code
    for v in viewpoints:
        print(">> Selected view: ", v)
        azimuth,elevation,tilt,distance=v
        output_img = osp.join(syn_images_folder, '{}_{}_{}'.format(azimuth, elevation, image_name))
        
        temp_dirname = tempfile.mkdtemp()
        view_file = osp.join(temp_dirname, 'view.txt')
        view_fout = open(view_file,'w')
        view_fout.write('{} {} {} {}'.format(azimuth, elevation, tilt, distance))
        view_fout.close()
        
        render_cmd = '%s %s --background --python %s -- %s %s %s %s %s' % (
            blender_executable_path, 
            blank_file, 
            render_code, 
            model_file, 
            'xxx', 
            'xxx', 
            view_file, 
            temp_dirname
        )
        try:
            print(render_cmd)
            os.system('%s %s' % (render_cmd, io_redirect))
            imgs = glob.glob(temp_dirname+'/*.png')
            shutil.move(imgs[0], output_img)
        except Exception as e:
            print(e)
            print('render failed. render_cmd: %s' % (render_cmd))

        # CLEAN UP
        shutil.rmtree(temp_dirname)
        

if __name__ == '__main__':
    # List models
    
    # model_dir = 'ShapeNetCore.v1/02691156/*/model.obj'
    # 02691156 is the id for airplane
    # * is the md5 id?
    
    # model_dir = '/mnt/1TB_SSD/qing/vc-shapenet/examples/car/*/models/model_normalized.obj'
    # model_dir = '/mnt/1TB_SSD/qing/blender_scripts/PASCAL3D+_obj/01r.obj'
    model_dir = '/mnt/1TB_SSD/qing/blender_scripts/PASCAL3D+_obj/*.off'
    print(model_dir)
    models = glob.glob(model_dir)
    print(len(models))
    
    # viewpoint
    for model_file in models:
        model_name = model_file.replace('.off','').split('/')[-1]
        
        viewpoint_file = './viewpoints/azi8r10ele1r5_{}.txt'.format(model_name) 
        viewpoints = [[float(x) for x in line.rstrip().split(' ')] for line in open(viewpoint_file,'r')]
        syn_images_folder = osp.join(BASE_DIR, 'images_{}'.format(model_name))

        render(model_file, viewpoints, syn_images_folder)
