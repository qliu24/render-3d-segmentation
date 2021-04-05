import os, sys, random, math
import bpy
import numpy as np
import bpy_extras
from mathutils import Matrix

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# function for projecting 3d keypoints to 2d img
def project_by_object_utils(cam, point):
    scene = bpy.context.scene
    co_2d = bpy_extras.object_utils.world_to_camera_view(scene, cam, point)
    render_scale = scene.render.resolution_percentage / 100
    render_size = (
            int(scene.render.resolution_x * render_scale),
            int(scene.render.resolution_y * render_scale),
            )
    return (co_2d.x * render_size[0], render_size[1] - co_2d.y * render_size[1], co_2d.z)


def get_calibration_matrix_K_from_blender(camd):
    f_in_mm = camd.lens
    scene = bpy.context.scene
    resolution_x_in_px = scene.render.resolution_x
    resolution_y_in_px = scene.render.resolution_y
    scale = scene.render.resolution_percentage / 100
    sensor_width_in_mm = camd.sensor_width
    sensor_height_in_mm = camd.sensor_height
    pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y
    if (camd.sensor_fit == 'VERTICAL'):
        # the sensor height is fixed (sensor fit is horizontal), 
        # the sensor width is effectively changed with the pixel aspect ratio
        s_u = resolution_x_in_px * scale / sensor_width_in_mm / pixel_aspect_ratio 
        s_v = resolution_y_in_px * scale / sensor_height_in_mm
    else: # 'HORIZONTAL' and 'AUTO'
        # the sensor width is fixed (sensor fit is horizontal), 
        # the sensor height is effectively changed with the pixel aspect ratio
        pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y
        s_u = resolution_x_in_px * scale / sensor_width_in_mm
        s_v = resolution_y_in_px * scale * pixel_aspect_ratio / sensor_height_in_mm

    # Parameters of intrinsic calibration matrix K
    alpha_u = f_in_mm * s_u
    alpha_v = f_in_mm * s_v
    u_0 = resolution_x_in_px*scale / 2
    v_0 = resolution_y_in_px*scale / 2
    skew = 0 # only use rectangular pixels

    K = Matrix(
        ((alpha_u, skew,    u_0),
        (    0  ,  alpha_v, v_0),
        (    0  ,    0,      1 )))
    return K


# function for adding image to object surface
def add_image_to_obj(obj, image_file_path):    
    obj_name = obj.name
    img = bpy.data.images.load(image_file_path)
    tex = bpy.data.textures.new("tex_"+obj_name, 'IMAGE')
    tex.image=img

    mat = bpy.data.materials.new("mat_"+obj_name)
    tslot = mat.texture_slots.add()
    tslot.texture = tex
    
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def camPosToQuaternion(cx, cy, cz):
    camDist = math.sqrt(cx * cx + cy * cy + cz * cz)
    cx = cx / camDist
    cy = cy / camDist
    cz = cz / camDist
    axis = (-cz, 0, cx)
    angle = math.acos(cy)
    a = math.sqrt(2) / 2
    b = math.sqrt(2) / 2
    w1 = axis[0]
    w2 = axis[1]
    w3 = axis[2]
    c = math.cos(angle / 2)
    d = math.sin(angle / 2)
    q1 = a * c - b * d * w1
    q2 = b * c + a * d * w1
    q3 = a * d * w2 + b * d * w3
    q4 = -b * d * w2 + a * d * w3
    return (q1, q2, q3, q4)

def quaternionFromYawPitchRoll(yaw, pitch, roll):
    c1 = math.cos(yaw / 2.0)
    c2 = math.cos(pitch / 2.0)
    c3 = math.cos(roll / 2.0)    
    s1 = math.sin(yaw / 2.0)
    s2 = math.sin(pitch / 2.0)
    s3 = math.sin(roll / 2.0)    
    q1 = c1 * c2 * c3 + s1 * s2 * s3
    q2 = c1 * c2 * s3 - s1 * s2 * c3
    q3 = c1 * s2 * c3 + s1 * c2 * s3
    q4 = s1 * c2 * c3 - c1 * s2 * s3
    return (q1, q2, q3, q4)


def camPosToQuaternion(cx, cy, cz):
    q1a = 0
    q1b = 0
    q1c = math.sqrt(2) / 2
    q1d = math.sqrt(2) / 2
    camDist = math.sqrt(cx * cx + cy * cy + cz * cz)
    cx = cx / camDist
    cy = cy / camDist
    cz = cz / camDist    
    t = math.sqrt(cx * cx + cy * cy) 
    tx = cx / t
    ty = cy / t
    yaw = math.acos(ty)
    if tx > 0:
        yaw = 2 * math.pi - yaw
    pitch = 0
    tmp = min(max(tx*cx + ty*cy, -1),1)
    #roll = math.acos(tx * cx + ty * cy)
    roll = math.acos(tmp)
    if cz < 0:
        roll = -roll    
    print("%f %f %f" % (yaw, pitch, roll))
    q2a, q2b, q2c, q2d = quaternionFromYawPitchRoll(yaw, pitch, roll)    
    q1 = q1a * q2a - q1b * q2b - q1c * q2c - q1d * q2d
    q2 = q1b * q2a + q1a * q2b + q1d * q2c - q1c * q2d
    q3 = q1c * q2a - q1d * q2b + q1a * q2c + q1b * q2d
    q4 = q1d * q2a + q1c * q2b - q1b * q2c + q1a * q2d
    return (q1, q2, q3, q4)

def camRotQuaternion(cx, cy, cz, theta): 
    theta = theta / 180.0 * math.pi
    camDist = math.sqrt(cx * cx + cy * cy + cz * cz)
    cx = -cx / camDist
    cy = -cy / camDist
    cz = -cz / camDist
    q1 = math.cos(theta * 0.5)
    q2 = -cx * math.sin(theta * 0.5)
    q3 = -cy * math.sin(theta * 0.5)
    q4 = -cz * math.sin(theta * 0.5)
    return (q1, q2, q3, q4)

def quaternionProduct(qx, qy): 
    a = qx[0]
    b = qx[1]
    c = qx[2]
    d = qx[3]
    e = qy[0]
    f = qy[1]
    g = qy[2]
    h = qy[3]
    q1 = a * e - b * f - c * g - d * h
    q2 = a * f + b * e + c * h - d * g
    q3 = a * g - b * h + c * e + d * f
    q4 = a * h + b * g - c * f + d * e    
    return (q1, q2, q3, q4)


def obj_centened_camera_pos(dist, azimuth_deg, elevation_deg):
    phi = float(elevation_deg) / 180 * math.pi
    theta = float(azimuth_deg) / 180 * math.pi
    x = (dist * math.cos(theta) * math.cos(phi))
    y = (dist * math.sin(theta) * math.cos(phi))
    z = (dist * math.sin(phi))
    return (x, y, z)


def use_sun_light(energy, loc=None):
    if not(loc is None):
        bpy.ops.object.lamp_add(type='SUN', view_align = False, location=loc)
    else:
        bpy.ops.object.lamp_add(type='SUN', view_align = False, location=(0, 0, 1))
        
    bpy.data.objects['Sun'].data.energy = energy
    
def use_point_light(energy, loc=None):
    if isinstance(loc[0], (list, tuple)):
        for ll in loc:
            bpy.ops.object.lamp_add(type='POINT', view_align = False, location=ll)
    else:
        bpy.ops.object.lamp_add(type='POINT', view_align = False, location=loc)
        
    for ob in bpy.context.scene.objects:
        if not ob.type == 'LAMP':
            continue
        lamp = ob.data
        if lamp.name.lower().startswith("point"):
            lamp.energy = energy
    
    
def setup_random_lighting(camera_loc):
    bpy.context.scene.world.light_settings.use_environment_light = False
    
    # setup sun
    bpy.ops.object.lamp_add(type='SUN', view_align = False, location=camera_loc)
    bpy.data.objects['Sun'].data.energy = np.random.uniform(0.3,1.0)
    
    # setup point light
    light_num_lowbound = 0
    light_num_highbound = 4
    
#     light_elevation_degree_lowbound = 20
    light_elevation_degree_lowbound = -20
    light_elevation_degree_highbound = 60

    light_energy_mean = 0.5
    light_energy_std = 0.1
        
    num_of_light = np.random.randint(light_num_lowbound,light_num_highbound)
    if num_of_light>0:
        binsize = 360/num_of_light
        start_azimuth_degree = 0
        for _ in range(num_of_light):
            light_azimuth_degree_lowbound = start_azimuth_degree
            light_azimuth_degree_highbound = start_azimuth_degree+binsize
            light_azimuth_deg = np.random.uniform(light_azimuth_degree_lowbound, light_azimuth_degree_highbound)
            light_elevation_deg  = np.random.uniform(light_elevation_degree_lowbound, light_elevation_degree_highbound)
            light_dist = 4
            lx, ly, lz = obj_centened_camera_pos(light_dist, light_azimuth_deg, light_elevation_deg)
            bpy.ops.object.lamp_add(type='POINT', view_align = False, location=(lx, ly, lz))
            bpy.data.objects['Point'].data.energy = np.random.normal(light_energy_mean, light_energy_std)
            start_azimuth_degree = start_azimuth_degree+binsize
    
    
    
def setup_lighting(use_environment_light = None, use_sun_light = 0.5, use_additional_light = True, use_point_light = False, loc=None):
    
    bpy.context.scene.world.light_settings.use_environment_light = False
    
    if use_environment_light:
        # use_environment_light = [0.9, 0.3]
        light_environment_energy_lowbound = use_environment_light[0]
        light_environment_energy_highbound = use_environment_light[1]
        
        bpy.context.scene.world.light_settings.use_environment_light = True
        env_lighting = np.random.uniform(light_environment_energy_lowbound, light_environment_energy_highbound)
        bpy.context.scene.world.light_settings.environment_energy = env_lighting
        bpy.context.scene.world.light_settings.environment_color = 'PLAIN'
    
    if use_sun_light:
        # Add a sky lighting
        # use_sun_light = 0.7
        if loc:
            bpy.ops.object.lamp_add(type='SUN', view_align = False, location=loc)
        else:
            bpy.ops.object.lamp_add(type='SUN', view_align = False, location=(0, 0, 1))
            
        bpy.data.objects['Sun'].data.energy = use_sun_light
        
    if use_additional_light:
        light_num_lowbound = 3
        light_num_highbound = 3
        light_dist_lowbound = 4
        light_dist_highbound = 4
        
        light_elevation_degree_lowbound = 20
        light_elevation_degree_highbound = 50
        
        light_energy_mean = 0.01
        light_energy_std = 0.001
        
        num_of_light = random.randint(light_num_lowbound,light_num_highbound)
        binsize = 360/num_of_light
        start_azimuth_degree = 0
        for _ in range(num_of_light):
            light_azimuth_degree_lowbound = start_azimuth_degree
            light_azimuth_degree_highbound = start_azimuth_degree+binsize
            light_azimuth_deg = np.random.uniform(light_azimuth_degree_lowbound, light_azimuth_degree_highbound)
            
            light_elevation_deg  = np.random.uniform(light_elevation_degree_lowbound, light_elevation_degree_highbound)
            light_dist = np.random.uniform(light_dist_lowbound, light_dist_highbound)
            lx, ly, lz = obj_centened_camera_pos(light_dist, light_azimuth_deg, light_elevation_deg)
            bpy.ops.object.lamp_add(type='POINT', view_align = False, location=(lx, ly, lz))
            bpy.data.objects['Point'].data.energy = np.random.normal(light_energy_mean, light_energy_std)
            start_azimuth_degree = start_azimuth_degree+binsize

    if use_point_light:
        light_num_lowbound = 2
        light_num_highbound = 2
        light_dist_lowbound = 2
        light_dist_highbound = 4
        
        light_azimuth_degree_lowbound = 0
        light_azimuth_degree_highbound = 360
        light_elevation_degree_lowbound = 20
        light_elevation_degree_highbound = 80

        light_energy_mean = 0.1
        light_energy_std = 0.03
        # set point lights
        for i in range(random.randint(light_num_lowbound,light_num_highbound)):
            light_azimuth_deg = np.random.uniform(light_azimuth_degree_lowbound, light_azimuth_degree_highbound)
            light_elevation_deg  = np.random.uniform(light_elevation_degree_lowbound, light_elevation_degree_highbound)
            light_dist = np.random.uniform(light_dist_lowbound, light_dist_highbound)
            lx, ly, lz = obj_centened_camera_pos(light_dist, light_azimuth_deg, light_elevation_deg)
            bpy.ops.object.lamp_add(type='POINT', view_align = False, location=(lx, ly, lz))
            bpy.data.objects['Point'].data.energy = np.random.normal(light_energy_mean, light_energy_std)
