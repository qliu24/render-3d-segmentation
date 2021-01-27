import numpy as np

# get randomized vp files
model_dic={'sedan':'6710c87e34056a29aa69dfdc5532bb13',
           'truck':'42af1d5d3b2524003e241901f2025878',
           'minivan':'4ef6af15bcc78650bedced414fad522f',
           'suv':'473dd606c5ef340638805e546aa28d99',
           'race':'d4251f9cf7f1e0a7cac1226cb3e860ca',
           'wagon':'bad0a52f07afc2319ed410a010efa019'}
           
azi_range = np.arange(360) # uniform
ele_range = np.arange(0,81) # biased to lower than 30
ele_weight = np.concatenate([np.repeat(95,31),np.repeat(4,30),np.repeat(1,20)])
ele_weight = ele_weight/np.sum(ele_weight)
dis_bin = np.arange(2,4.25,0.25) # uniform
per_model_n = 4000


for model in model_dic.keys():
    azi_ls = np.random.choice(azi_range, size=(per_model_n,))
    ele_ls = np.random.choice(ele_range, size=(per_model_n,), p=ele_weight)
    dis_ls = np.random.choice(dis_bin, size=(per_model_n,))

    vp_file = '/mnt/1TB_SSD/qing/blender_scripts/viewpoints/dataset_{}_p.txt'.format(model)
    
    par_ls = list(zip(azi_ls, ele_ls, dis_ls))
    par_ls = list( dict.fromkeys(par_ls) )
    
    with open(vp_file, 'w') as fh:
        for nn in range(len(par_ls)):
            fh.write('{} {} 0 {}\n'.format(par_ls[nn][0], par_ls[nn][1], par_ls[nn][2]))