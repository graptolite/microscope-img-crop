# Copyright (C) 2022  Yingbo Li
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import numpy as np
import cv2

def zealous_square_crop_circle(r,cx,cy,img):
    n_rows,n_cols,_ = img.shape

    del_rows = []
    upper_crop = 0
    upper_crop_found = False
    for i in range(n_rows):
        dist_min = abs(i - cy)
        if dist_min > r:
            del_rows.append(i)
            if not upper_crop_found:
                if upper_crop != i:
                    upper_crop_found = True
                else:
                    upper_crop += 1
    img = np.delete(img,tuple(del_rows),axis=0)
#    print("vertical cropping complete")

    del_cols = []
    left_crop = 0
    left_crop_found = False
    for j in range(n_cols):
        dist_min = abs(j - cx)
        if dist_min > r:
            del_cols.append(j)
            if not left_crop_found:
                if left_crop != j:
                    left_crop_found = True
                else:
                    left_crop += 1
    img = np.delete(img,tuple(del_cols),axis=1)
#    print("horizontal cropping complete")
    return img

def circle_transparency_crop(img):
    n_rows,n_cols,_ = img.shape
    if n_rows != n_cols:
        print("Warning: Input is not a zealously cropped circle - results may not be great")
    img = np.dstack([img,255*np.ones([n_rows,n_cols,1])])

    r = n_rows/2
    cy = n_rows/2
    cx = n_cols/2

#    print("circular cropping of image with dimensions : %s,%s" % (n_rows,n_cols))
    for i in range(n_rows):
        for j in range(n_cols):
            dist_to_c = np.sqrt((i - cy)**2 + (j - cx)**2)
            if dist_to_c > r:
                img[i][j] = [0,0,0,0]
#    print("circular cropping finished")
    return img

def process_image(image,working_scale:float=0.2,post_working_scale:float=0.6,param1:int=5,param2:int=50,output_border_width:int=4):
    basic_img = cv2.imread(image,cv2.IMREAD_UNCHANGED)
    basic_img = cv2.cvtColor(basic_img, cv2.COLOR_BGR2RGB)
    working_img = cv2.resize(basic_img,(0,0),fx=working_scale,fy=working_scale)
    processing_img = working_img
    processing_scale = post_working_scale * working_scale
    processing_img = cv2.resize(basic_img,(0,0),fx=processing_scale,fy=processing_scale)

    greyscale = cv2.cvtColor(processing_img,cv2.COLOR_RGB2GRAY)
    greyscale = cv2.Canny(greyscale, 50, 100)

    n_rows = greyscale.shape[0]
    min_dim = min(greyscale.shape)
    circles = cv2.HoughCircles(greyscale,cv2.HOUGH_GRADIENT,1,n_rows,
                              param1=param1,param2=param2,
                              minRadius=int(.1*min_dim),maxRadius=0)

    if circles is not None:
        if len(circles) > 1:
            print("Warning: Multiple circles detected, just plotting the largest one")
        circles = np.rint(circles)[0]
        circles = np.array(sorted(circles,key=lambda c : c[2],reverse=True))
        circ = np.uint16(circles[0]/(processing_scale/working_scale))
        c = (circ[0],circ[1])
        r = circ[2]

        if output_border_width:
            cv2.circle(working_img,c,r,(0,0,0),output_border_width*2) # multiply border width by 2 as half of thickness lies outside fitted circle

        cx,cy = c

        r = r - 3

        processed_img = zealous_square_crop_circle(r,cx,cy,working_img)
        processed_img = circle_transparency_crop(processed_img)

        processed_img = np.uint8(processed_img)
    else:
        processed_img = None
    return processed_img

def show_img(image):
    cv2.namedWindow("output", cv2.WINDOW_NORMAL)
    cv2.imshow("output",image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return
