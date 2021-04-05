## Render Synthetic Images with Part Segmentation Annotations Using CGPart
CGPart is a comprehensive part segmentation dataset that provides detailed annotations on 3D CAD models, synthetic images, and real test images. It involves 5 vehicle categories: *car*, *motorbike*, *aeroplane*, *bus*, and *bicycle*. Below are some example segmentation annotations from the dataset. You can find more information about CGPart from this [page](https://qliu24.github.io/cgpart/) or from our [paper](https://arxiv.org/abs/2103.14098).  
  
<img src="https://qliu24.github.io/cgpart/images/cgpart_overview.jpg" alt="cgpart_overview" width="750"/>

### Requirements

* Blender 2.79b
* Python 3, opencv-python 
  
### Usage

#### Step1: Download the annotated 3D CAD models and setup the config files
* Download the annotated 3D CAD models from [here](https://cs.jhu.edu/~qliu24/CGPart/cgpart_3d.zip)
* Edit the config files in *render_image_kp* folder to have correct data locations

#### Step2: Render the images (with keypoint annotations)
* Run the *render_image_kp/render_manual_anno_kp.py* with proper arguments to generate the synthetic images, for example:
```
cd render_image_kp
python render_manual_anno_kp.py --obj_cls car --model_id 6710c87e34056a29aa69dfdc5532bb13
```
* To randomize the render parameters:
  * Generate randomized viewpoint parameter files and put it in the *viewpoints* folder, then use it through the *--vp_file* argument.
  * Modify the config files and use *surface = random_pic* or *surface = random_color* to randomize the object surface/texture.
  * Set *--bg_file sky.blend* and uncomment the related lines in *render_image_kp/blender_manual_anno_kp.py* (L66-67, L117-118, L121-122, L142-145) to randomize the background.
  * Uncomment *render_image_kp/blender_manual_anno_kp.py* L165 and comment the L167-168 to randomize the lighting.

#### Step3: Render the depth maps and convert them into segmentation maps
* Run the *render_seg/render_manual_anno_parts.py* with proper arguments to generate the depth maps, for example:
```
cd render_seg
python render_manual_anno_parts.py --obj_cls car --model_id 6710c87e34056a29aa69dfdc5532bb13
```

Then run the *render_seg/depth_to_semseg.py* with proper arguments to generate the segmentation maps, for example:
```
python depth_to_semseg.py --obj_cls car --model_key sedan
```

#### Step4 (optional): Visualize the results
Example code is given in the *visualization.ipynb* notebook.

### Citation
If you find this project helpful, please consider citing our paper.
```
@article{liu2019semantic,
  author    = {Liu, Qing and Kortylewski, Adam and Zhang, Zhishuai and Li, Zizhang and Guo, Mengqi and Liu, Qihao and Yuan, Xiaoding and Mu, Jiteng and Qiu, Weichao and Yuille, Alan},
  title     = {CGPart: A Part Segmentation Dataset Based on 3D Computer Graphics Models},
  journal   = {arXiv preprint arXiv:2103.14098},
  year      = {2021},
}
```
