from wand.image import Image
from tkinter import filedialog
import tkinter
import base64

window = tkinter.Tk()

input_preview_canvas = tkinter.Canvas(window, width=500, height=500)
output_preview_canvas = tkinter.Canvas(window, width=500, height=500)

def generate_preview(img):
    img.transform(resize='500x500>')
    img.format = 'gif'

    img_in_binary = img.make_blob()
    img_in_base64 = base64.b64encode(img_in_binary).decode('ascii')
    img_tk = tkinter.PhotoImage(data=img_in_base64)

    # Just to avoid being garbage-collected
    img_label = tkinter.Label(window)
    img_label.image = img_tk

    return img_tk

def generate_output_preview(img, threshold=0.5):
    img.threshold(threshold)
    return generate_preview(img)

def show_input_preview(img):
    input_preview_canvas.create_image(0, 0, image=generate_preview(img), anchor=tkinter.NW)

def show_output_preview(img):
    global image_on_canvas
    image_on_canvas = output_preview_canvas.create_image(0, 0, image=generate_output_preview(img), anchor=tkinter.NW)

def on_open():
    open_dialog = filedialog.Open(window, filetypes=[('All Files', '*.*')])
    filepath = open_dialog.show()

    if filepath != '':
        global image
        image = Image(filename=filepath)
        img = image.clone()
        show_input_preview(img)
        show_output_preview(img)

def on_change(val):
    threshold = float(val)/100
    img_tk = generate_output_preview(image.clone(), threshold)
    output_preview_canvas.itemconfig(image_on_canvas, image=img_tk)

open_btn = tkinter.Button(window, text='Open')
open_btn.configure(command=on_open)

threshold_slider = tkinter.Scale(window, from_=25, to=75, orient=tkinter.HORIZONTAL)
threshold_slider.set(50)
threshold_slider.configure(command=on_change)

open_btn.pack()
threshold_slider.pack()
input_preview_canvas.pack(side=tkinter.LEFT)
output_preview_canvas.pack(side=tkinter.LEFT)


window.mainloop()
