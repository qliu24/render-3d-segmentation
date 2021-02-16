import numpy as np


# get randomized vp files
           
# # car
# model_dic={'sedan':'6710c87e34056a29aa69dfdc5532bb13',
#            'truck':'42af1d5d3b2524003e241901f2025878',
#            'minivan':'4ef6af15bcc78650bedced414fad522f',
#            'suv':'473dd606c5ef340638805e546aa28d99',
#            'race':'d4251f9cf7f1e0a7cac1226cb3e860ca',
#            'wagon':'bad0a52f07afc2319ed410a010efa019'}
# azi_range = np.arange(360) # uniform
# ele_range = np.arange(0,81) # biased to lower than 30
# ele_weight = np.concatenate([np.repeat(95,31),np.repeat(4,30),np.repeat(1,20)])
# ele_weight = ele_weight/np.sum(ele_weight)
# dis_bin = np.arange(2,4.25,0.25) # uniform
# per_model_n = 4000

# # motorbike
# model_dic={'cruiser':'6ea0a49bd27fa58b2279b76b11a9a16c',
#            'chopper':'3837c8ef573c2a7b360cf6eb12fae4',
#            'scooter':'5131b742dad94f6175dadc997718614d',
#            'dirtbike':'db5b6c2f64fefe5b448c90b3a2fec4b8'}
# azi_range = np.arange(360) # uniform
# ele_range = np.arange(0,81) # biased to lower than 30
# ele_weight = np.concatenate([np.repeat(20,31),np.repeat(2,30),np.repeat(1,20)])
# ele_weight = ele_weight/np.sum(ele_weight)
# dis_bin = np.arange(1,4.25,0.25) # uniform
# per_model_n = 4000

# # aeroplane
# model_dic={'airliner':'10e4331c34d610dacc14f1e6f4f4f49b',
#            'jet':'5cf29113582e718171d03b466c72ce41',
#            'fighter':'b0b164107a27986961f6e1cef6b8e434',
#            'biplane':'17c86b46990b54b65578b8865797aa0'}
# azi_range = np.arange(360) # uniform
# ele_range = np.arange(-50,81) # biased to lower than 30
# ele_weight = np.concatenate([np.repeat(1,20),np.repeat(4,30),np.repeat(40,31),np.repeat(2,30),np.repeat(1,20)])
# ele_weight = ele_weight/np.sum(ele_weight)
# dis_bin = np.arange(1.5,4.25,0.25) # uniform
# per_model_n = 4000

# bus
model_dic={'school':'79e32e66bbf04191afe1d4530f4c6e24',
           'regular':'4ead9b28515b97fdc0e2e9e9ade4d03b',
           'double':'3080d86e8424187d4d44f5db04bf14b8',
           'articulated':'1821df0ce1bf2cea52470de2774d6099'}
azi_range = np.arange(360) # uniform
ele_range = np.arange(0,81) # biased to lower than 20
ele_weight = np.concatenate([np.repeat(95,21),np.repeat(4,40),np.repeat(1,20)])
ele_weight = ele_weight/np.sum(ele_weight)
dis_bin = np.arange(1.5,4.25,0.25) # uniform
per_model_n = 4000


for model in model_dic.keys():
    azi_ls = np.random.choice(azi_range, size=(per_model_n,))
    ele_ls = np.random.choice(ele_range, size=(per_model_n,), p=ele_weight)
    dis_ls = np.random.choice(dis_bin, size=(per_model_n,))

    vp_file = '/mnt/1TB_SSD/qing/blender_scripts/viewpoints/dataset/dataset_{}.txt'.format(model)
    
    par_ls = list(zip(azi_ls, ele_ls, dis_ls))
    par_ls = list( dict.fromkeys(par_ls) )
    
    with open(vp_file, 'w') as fh:
        for nn in range(len(par_ls)):
            fh.write('{} {} 0 {}\n'.format(par_ls[nn][0], par_ls[nn][1], par_ls[nn][2]))