#!/usr/bin/env python3

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

from tkinter import *
import tkinter.messagebox as messagebox
from PIL import Image,ImageTk
import os

from cropping_funcs import *

def process_and_display_image():
    filepath = inp.get()
    int_if_not_empty = lambda s,empty=0 : int(s) if s else empty
    if filepath and os.path.exists(filepath):
        processed_img = process_image(filepath,working_scale=working_scale_slider.get(),
                                      post_working_scale=processing_scale_slider.get(),
                                      param1=int_if_not_empty(param1_entry.get()),param2=int_if_not_empty(param2_entry.get()),
                                      output_border_width=int_if_not_empty(border_width_entry.get(),None))
        if processed_img is not None:
            root.processed_img = processed_img
            w = int(0.9*canv.winfo_width())
            img = ImageTk.PhotoImage(image=Image.fromarray(processed_img).resize((w,w)))
            msgs.itemconfig(text_placeholder,text="")
            canv.itemconfig(img_placeholder,image=img)
            root.image = img # prevent garbage collection
        else:
            msgs.itemconfig(text_placeholder,text="Error: a Hough Circle could not be found\nwith the current parameter combination.\nPossible reasons:\n-One of both of the scales are too small\n-Min radius is too high\n-Param2 is too high\n-The image is too small")
            canv.itemconfig(img_placeholder,image=[])
    elif filepath:
        msgs.itemconfig(text_placeholder,text="Error: Invalid input filepath")
        canv.itemconfig(img_placeholder,image=[])
    else:
        msgs.itemconfig(text_placeholder,text="Notice: Please type in a filepath")
        canv.itemconfig(img_placeholder,image=[])

def keypress_return(event=None):
    process_and_display_image()

def stack_widgets(widget_list,base=0):
    for i,w in enumerate(widget_list):
        w.grid(column=0,row=base+i)

def do_save():
    output_filename = out.get()
    if os.path.exists(os.path.dirname(output_filename)) or len([e for e in os.path.split(output_filename) if e])==1:
        if output_filename.endswith(".png"):
            Image.fromarray(root.processed_img).save(output_filename)
            msgs.itemconfig(text_placeholder,text="Notice: Cropped image saved to %s" % output_filename)
        else:
            msgs.itemconfig(text_placeholder,text="Error: output format must be PNG")
    else:
        msgs.itemconfig(text_placeholder,text="Error: Save-to folder does not exist\nor no output filepath has been provided")

def cancel_save():
    msgs.itemconfig(text_placeholder,text="Notice: save cancelled")

def check_save():
    try:
        root.processed_img
        output_filename = out.get()
        if os.path.exists(output_filename):
            popup = Toplevel(root)
            close_popup = lambda : popup.destroy()
            popup.geometry("500x250")
            popup.title("File Warning")
            warning_msg = Label(popup,text="Warning: file already exists with that name. Do you want to overwrite it?")
            warning_msg.pack(padx=3,pady=1,side=TOP)
            btn_yes = Button(popup,text="Yes",command=lambda : [do_save(),close_popup()])
            btn_yes.pack(padx=0,pady=1,side=TOP)
            btn_no = Button(popup,text="No",command=lambda : [cancel_save(),close_popup()])
            btn_no.pack(padx=0,pady=1,side=TOP)
        else:
            do_save()
    except AttributeError:
        msgs.itemconfig(text_placeholder,text="Error: No image to save")

root = Tk()

root.geometry("700x700")

root.bind("<Return>",keypress_return)

inputs_frame = Frame(root,bg="lightgrey",borderwidth=5)
inputs_frame.columnconfigure(0,weight=1)
inputs_frame.columnconfigure(0,weight=3)
inputs_frame.place(relheight=1,relwidth=0.3,relx=0.7,y=0)

l_input = Label(inputs_frame,text="Input Filepath:",font=("bold"))
inp = Entry(inputs_frame)

btn = Button(inputs_frame,text="Process image",width=10,height=5,command=process_and_display_image)

processing_options = Label(inputs_frame,text="Processing Params",font=("bold"))

l_working_scale = Label(inputs_frame,text="Working Scale:")
working_scale_slider = Scale(inputs_frame,from_=0.05,to=1,resolution=0.05,orient=HORIZONTAL)
working_scale_slider.set(0.2)

l_processing_scale = Label(inputs_frame,text="Processing Scale\n(times working scale):")
processing_scale_slider = Scale(inputs_frame,from_=0.05,to=1,resolution=0.05,orient=HORIZONTAL)
processing_scale_slider.set(0.6)

allow_only = lambda allow : (lambda char : all([c in list(allow) for c in char]))
allow_int_only = (root.register(allow_only("1234567890")),"%S")

l_border_width = Label(inputs_frame,text="Output Border Width (px):")
border_width_entry = Entry(inputs_frame,validate="key",vcmd=allow_int_only)
border_width_entry.insert(0,"4")

advanced_options = Label(inputs_frame,text="Advanced",font=("bold"))

l_param1 = Label(inputs_frame,text="Hough Circle Param1:")
param1_entry = Entry(inputs_frame,validate="key",vcmd=allow_int_only)
param1_entry.insert(0,"5")

l_param2 = Label(inputs_frame,text="Hough Circle Param2:")
param2_entry = Entry(inputs_frame,validate="key",vcmd=allow_int_only)
param2_entry.insert(0,"50")

l_output = Label(inputs_frame,text="Output Filepath:",font=("bold"))
out = Entry(inputs_frame)

btn_out = Button(inputs_frame,text="Save image",width=10,height=5,command=check_save)

stack_widgets([l_input,inp,btn,processing_options,l_working_scale,working_scale_slider,l_processing_scale,processing_scale_slider,l_border_width,border_width_entry,advanced_options,l_param1,param1_entry,l_param2,param2_entry,l_output,out,btn_out])

outputs_frame = Frame(root,bg="lightblue",borderwidth=5)
outputs_frame.columnconfigure(0,weight=1)
outputs_frame.columnconfigure(0,weight=3)
outputs_frame.place(relheight=1,relwidth=0.7,relx=0,y=0)

l_output = Label(outputs_frame,text="Output",bg="lightblue")
l_output.grid(column=0,row=0)
root.update_idletasks()
w,h = outputs_frame.winfo_width(),outputs_frame.winfo_height()
canv = Canvas(outputs_frame,width=0.9*w,height=0.6*h,bg="white")
canv.grid(column=0,row=1)

l_msgs = Label(outputs_frame,text="Messages",bg="lightblue")
l_msgs.grid(column=0,row=2)
msgs = Canvas(outputs_frame,width=0.9*w,height=0.2*h,bg="white")
msgs.grid(column=0,row=3)

root.update_idletasks()
wc,hc = canv.winfo_width(),canv.winfo_height()
img_placeholder = canv.create_image(wc/2,hc/2,anchor=CENTER)
wm,hm = msgs.winfo_width(),msgs.winfo_height()
text_placeholder = msgs.create_text(wm/2,hm/2,anchor=CENTER)

root.mainloop()
