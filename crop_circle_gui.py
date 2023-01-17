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

class GUI(Tk):
    def __init__(self):
        super().__init__()
        self.geometry("700x700")
        self.title("Microscope Image Circle Crop")
        self.tk.call("wm","iconphoto",self._w,PhotoImage(file="icon.png"))

        # bind enter/return key to
        self.bind("<Return>",lambda event=None : self.process_and_display_image())

        self.inputs_frame = Frame(self,bg="lightgrey",borderwidth=5)
        self.inputs_frame.columnconfigure(0,weight=1)
        self.inputs_frame.columnconfigure(0,weight=3)
        self.inputs_frame.place(relheight=1,relwidth=0.3,relx=0.7,y=0)

        self.l_input = Label(self.inputs_frame,text="Input Filepath:",font=("bold"))
        self.inp = Entry(self.inputs_frame)

        self.btn = Button(self.inputs_frame,text="Process image",width=10,height=5,command=self.process_and_display_image)

        self.processing_options = Label(self.inputs_frame,text="Processing Params",font=("bold"))

        self.l_working_scale = Label(self.inputs_frame,text="Working Scale:")
        self.working_scale_slider = Scale(self.inputs_frame,from_=0.05,to=1,resolution=0.05,orient=HORIZONTAL)
        self.working_scale_slider.set(0.2)

        self.l_processing_scale = Label(self.inputs_frame,text="Processing Scale\n(times working scale):")
        self.processing_scale_slider = Scale(self.inputs_frame,from_=0.05,to=1,resolution=0.05,orient=HORIZONTAL)
        self.processing_scale_slider.set(0.6)

        allow_only = lambda allow : (lambda char : all([c in list(allow) for c in char]))
        allow_int_only = (self.register(allow_only("1234567890")),"%S")

        self.l_border_width = Label(self.inputs_frame,text="Output Border Width (px):")
        self.border_width_entry = Entry(self.inputs_frame,validate="key",vcmd=allow_int_only)
        self.border_width_entry.insert(0,"4")

        self.advanced_options = Label(self.inputs_frame,text="Advanced",font=("bold"))

        self.l_param1 = Label(self.inputs_frame,text="Hough Circle Param1:")
        self.param1_entry = Entry(self.inputs_frame,validate="key",vcmd=allow_int_only)
        self.param1_entry.insert(0,"5")

        self.l_param2 = Label(self.inputs_frame,text="Hough Circle Param2:")
        self.param2_entry = Entry(self.inputs_frame,validate="key",vcmd=allow_int_only)
        self.param2_entry.insert(0,"50")

        self.l_output = Label(self.inputs_frame,text="Output Filepath:",font=("bold"))
        self.out = Entry(self.inputs_frame)

        self.btn_out = Button(self.inputs_frame,text="Save image",width=10,height=5,command=self.check_save)

        input_widget_list = [self.l_input,self.inp,self.btn,self.processing_options,self.l_working_scale,self.working_scale_slider,self.l_processing_scale,self.processing_scale_slider,self.l_border_width,self.border_width_entry,self.advanced_options,self.l_param1,self.param1_entry,self.l_param2,self.param2_entry,self.l_output,self.out,self.btn_out]
        self.stack_widgets(input_widget_list)

        self.outputs_frame = Frame(self,bg="lightblue",borderwidth=5)
        self.outputs_frame.columnconfigure(0,weight=1)
        self.outputs_frame.columnconfigure(0,weight=3)
        self.outputs_frame.place(relheight=1,relwidth=0.7,relx=0,y=0)

        self.l_output = Label(self.outputs_frame,text="Output",bg="lightblue")
        self.update_idletasks()
        w,h = self.outputs_frame.winfo_width(),self.outputs_frame.winfo_height()
        self.canv = Canvas(self.outputs_frame,width=0.9*w,height=0.6*h,bg="white")

        self.l_msg = Label(self.outputs_frame,text="Messages",bg="lightblue")
        self.msg = Canvas(self.outputs_frame,width=0.9*w,height=0.2*h,bg="white")

        output_widget_list = [self.l_output,self.canv,self.l_msg,self.msg]
        self.stack_widgets(output_widget_list)

        self.update_idletasks()
        wc,hc = self.canv.winfo_width(),self.canv.winfo_height()
        self.img_placeholder = self.canv.create_image(wc/2,hc/2,anchor=CENTER)
        wm,hm = self.msg.winfo_width(),self.msg.winfo_height()
        self.text_placeholder = self.msg.create_text(wm/2,hm/2,anchor=CENTER)

        self.protocol("WM_DELETE_WINDOW",self.destroy)

    def process_and_display_image(self):
        filepath = self.inp.get()
        int_if_not_empty = lambda s,empty=0 : int(s) if s else empty
        if filepath and os.path.exists(filepath):
            processed_img = process_image(filepath,working_scale=self.working_scale_slider.get(),
                                          post_working_scale=self.processing_scale_slider.get(),
                                          param1=int_if_not_empty(self.param1_entry.get()),param2=int_if_not_empty(self.param2_entry.get()),
                                          output_border_width=int_if_not_empty(self.border_width_entry.get(),None))
            if processed_img is not None:
                self.processed_img = processed_img
                w = int(0.9*self.canv.winfo_width())
                self.img = ImageTk.PhotoImage(image=Image.fromarray(processed_img).resize((w,w)))
                self.update_msg("")
                self.update_canv(self.img)
            else:
                self.update_msg("Error: a Hough Circle could not be found\nwith the current parameter combination.\nPossible reasons:\n-One of both of the scales are too small\n-Min radius is too high\n-Param2 is too high\n-The image is too small")
                self.update_canv(None)
        elif filepath:
            self.update_msg("Error: Invalid input filepath")
            self.update_canv(None)
        else:
            self.update_msg("Notice: Please type in a filepath")
            self.update_canv(None)

    def stack_widgets(self,widget_list):
        for i,w in enumerate(widget_list):
            w.grid(column=0,row=0+i)

    def do_save(self):
        output_filename = self.out.get()
        if os.path.exists(os.path.dirname(output_filename)) or len([e for e in os.path.split(output_filename) if e])==1:
            if output_filename.endswith(".png"):
                Image.fromarray(self.processed_img).save(output_filename)
                self.update_msg("Notice: Cropped image saved to %s" % output_filename)
            else:
                self.update_msg("Error: output format must be PNG")
        else:
            self.update_msg("Error: Save-to folder does not exist\nor no output filepath has been provided")

    def cancel_save(self):
        self.update_msg("Notice: save cancelled")

    def check_save(self):
        try:
            self.processed_img
            output_filename = self.out.get()
            if os.path.exists(output_filename):
                popup = Toplevel(self)
                close_popup = lambda : popup.destroy()
                popup.geometry("500x250")
                popup.title("File Warning")
                warning_msg = Label(popup,text="Warning: file already exists with that name. Do you want to overwrite it?")
                warning_msg.pack(padx=3,pady=1,side=TOP)
                btn_yes = Button(popup,text="Yes",command=lambda : [self.do_save(),close_popup()])
                btn_yes.pack(padx=0,pady=1,side=TOP)
                btn_no = Button(popup,text="No",command=lambda : [self.cancel_save(),close_popup()])
                btn_no.pack(padx=0,pady=1,side=TOP)
            else:
                self.do_save()
        except AttributeError:
            self.update_msg("Error: No image to save")

    def update_msg(self,text):
        self.msg.itemconfig(self.text_placeholder,text=text)

    def update_canv(self,img):
        self.canv.itemconfig(self.img_placeholder,image=img)


if __name__=="__main__": # writing and testing in emacs so had to remove whitespaces: https://stackoverflow.com/a/73388122 by https://stackoverflow.com/users/19555485/donald-duck
    root = GUI()
    root.mainloop()
