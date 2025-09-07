# Dyploma
## This is code and some files for my bachelor's work. This code works with photos, making masks to teach NNs, and creates 3D model (kinda) out of .ply file with OpenGL

First part takes medical pictures with different body parts (mostly limbs, diabetical feet) that contains markups from our colleagues from medical univercity. Using .json files with polygon coordinates, it generates two monochrome masks: one represents body part, the other represents wound. We used them to teach two NN, where the first one finds the tissue in the image, and the other one, respectively, the wound surface.

Second part transforms .ply file from specific camera (intel realsense, if I recall correctly) into raw point cloud. It contains primitive UI to give user ability to manipulate "model" in viewport.

This code is part of bigger system so it could look strange without context. Feel free to contact me if there are any further questions.
