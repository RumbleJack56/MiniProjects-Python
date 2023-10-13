import tkinter as tk
from PIL import Image,ImageTk

root = tk.Tk()


frame = tk.Frame(root,width=1200,height=640)
frame.grid(row=0,column=0,sticky="NSEW")
canvas1 = tk.Canvas(frame, height=640,width=1200)

img = Image.open("qwindow.png")
img = ImageTk.PhotoImage(img.resize((1200,640),Image.BICUBIC))
img2 = ImageTk.PhotoImage(Image.open(r"PyKBC(2023)\blueimg.png").resize((1195,80),Image.BICUBIC))
button=tk.Button(frame,text="hi",image=img2,
                anchor="nw",compound="center")

a = canvas1.create_text(500,480,text="Hi",font=("Impact",30),anchor='nw')

canvas1.create_image(0,0,image=img,anchor="nw")

canvas1.create_window(5,440,window=button,anchor='nw')
canvas1.pack(fill="both",anchor="nw")
root.mainloop()