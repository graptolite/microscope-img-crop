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

from PIL import Image,ImageDraw

def crop_to_circle(working_img,circle):
    cx,cy,r = circle

    n_rows,n_cols,_ = working_img.shape

    # Crop to just the region of interest.
    working_img = Image.fromarray(working_img).crop([cx-r,cy-r,cx+r,cy+r])

    # New image for mask.
    size = [2*r,2*r]
    circle_mask = Image.new("1",size,0)
    # Draw circle filling the mask image.
    ImageDraw.Draw(circle_mask).ellipse([0,0] + size,fill=1)

    # Set circle mask as alpha.
    processed_img = np.dstack([working_img,255*np.asarray(circle_mask)])
    return processed_img

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
        c = [circ[0],circ[1]]
        r = circ[2]

        if output_border_width:
            cv2.circle(working_img,c,r,(0,0,0),output_border_width*2) # multiply border width by 2 as half of thickness lies outside fitted circle
        r = r + output_border_width

        processed_img = crop_to_circle(working_img,c + [r])
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
