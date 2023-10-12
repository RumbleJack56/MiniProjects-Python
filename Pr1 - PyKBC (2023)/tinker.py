import tkinter as tk
from PIL import Image,ImageTk

root = tk.Tk()


frame = tk.Frame(root,width=1200,height=640)
frame.grid(row=0,column=0,sticky="NSEW")
canvas1 = tk.Canvas(frame, height=640,width=1200)

img = Image.open("qwindow.png")
img = ImageTk.PhotoImage(img.resize((1200,640),Image.BICUBIC))


canvas1.create_image(0,0,image=img,anchor="nw")
canvas1.pack(fill="both",anchor="nw")
root.mainloop()