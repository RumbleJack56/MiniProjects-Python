import tkinter as tk
import time, webscrape, pygame.mixer as soundsystem
from tkinter import ttk
from PIL import Image,ImageTk

soundsystem.init()

class KbcApp(tk.Tk):
    def __init__(self,*args,**kwargs):
        tk.Tk.__init__(self,*args,**kwargs)
        self.geometry("1200x640")
        self.title("Kaun Banega Crorepati")

        rootbox = tk.Frame(self, width=1200,height=640)
        rootbox.rowconfigure(0,weight=1)
        rootbox.columnconfigure(0,weight=1)
        rootbox.pack(side="top",fill="both",expand=True)

        self.windows= {}

        for num , window in enumerate([MainWindow]+[QWindow]*15+[LossWindow,WinWindow]):
            frame = window(rootbox,self,qnum=num)
            if window == QWindow: 
                self.windows[num] = frame
            else: 
                self.windows[window] = frame
            frame.grid(row=0,column=0,sticky="NSEW")
        
        self.ActiveWindow(MainWindow)

    def ActiveWindow(self,windowname):
        self.windows[windowname].tkraise()


class MainWindow(tk.Frame):
    def __init__(self,parent,root,**kwargs):
        tk.Frame.__init__(self,parent)
        canvas = tk.Canvas(self, width=1200,height=640,borderwidth=0)
        canvas.pack(side='top',fill='both',expand=True)
        soundsystem.music.load("Pr1 - PyKBC (2023)\intro.mp3")
        soundsystem.music.play()
        canvas.background = ImageTk.PhotoImage(Image.open("Title Window.png").resize((1200,640),Image.LANCZOS))
        canvas.create_image(0,0,image=canvas.background,anchor="nw")
        canvas.bg2 = ImageTk.PhotoImage(Image.open(r"Pr1 - PyKBC (2023)\blueimg.png").resize((1193,90),Image.BILINEAR))
        startbutton = tk.Button(self,image=canvas.bg2,text = "Lets Play",
                                borderwidth=0,width=1193,height=90,relief="sunken")
        canvas.create_window(0,473,window=startbutton,anchor="nw")
        # canvas.create_text(550,490,text="Lets Play",anchor="nw",font=("Impact",30))


class QWindow(tk.Frame):
    def __init__(self,parent,root,**kwargs):
        tk.Frame.__init__(self,parent)
        self.quesNum = kwargs['qnum']   
        text = tk.Label(self,text=str(self.quesNum))
        text.pack(side = 'top',fill="both",anchor="center",expand=True)
class LossWindow(tk.Frame):
    def __init__(self,parent,root,**kwargs):
        tk.Frame.__init__(self,parent)

class WinWindow(tk.Frame):
    def __init__(self,parent,root,**kwargs):
        tk.Frame.__init__(self,parent)


def main():
    app = KbcApp()
    app.mainloop()
if __name__=="__main__":
    main()
