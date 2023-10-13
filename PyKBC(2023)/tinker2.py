import tkinter as tk
import webscrape
import time
import playsound
from tkinter import ttk
from PIL import Image,ImageTk

class testclass(tk.Tk):
    def __init__(self,*args,**kwargs):
        
        tk.Tk.__init__(self,*args,**kwargs)
        
        self.wm_title("Kaun Banega Crorepati")
        self.geometry("1200x640")
        
        
        overallframe = tk.Frame(self)
        overallframe.pack(side="top",fill="both",expand=True)
        overallframe.grid_columnconfigure(0,weight=1)
        overallframe.grid_rowconfigure(0,weight=1)


        self.frames = {}
        for F in (MainPage,SidePage,CompletionScreen):
            frame = F(overallframe,self)
            self.frames[F] = frame
            frame.grid(row=0,column=0,sticky="NSEW")


        
        self.show_frame(MainPage)


    def show_frame(self,container):
        frame = self.frames[container]
        # raises the current frame to the top
        frame.tkraise()

class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        

        kbctitle = Image.open("qwindow.png").resize((1200,640),Image.BICUBIC)
        kbctitle = ImageTk.PhotoImage(kbctitle)
        base = tk.Canvas(self,width=1200,height=640)
        base.pack(fill="both",expand=True)
        base.create_image(0,0,image=kbctitle,anchor='nw')
        
        
        

        button1 = tk.Button(
            self,
            text="Go to the Side Page",
            command=lambda: controller.show_frame(SidePage)
        )
        button1_canvas = base.create_window(540,600,anchor="nw",window=button1)


class SidePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="This is the Side Page")
        label.pack(padx=10, pady=10)

        switch_window_button = tk.Button(
            self,
            text="Go to the Completion Screen",
            command=lambda: controller.show_frame(CompletionScreen),
        )
        switch_window_button.pack(side="bottom", fill=tk.X)


class CompletionScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Completion Screen, we did it!")
        label.pack(padx=10, pady=10)
        switch_window_button = ttk.Button(
            self, text="Return to menu", command=lambda: controller.show_frame(MainPage)
        )
        switch_window_button.pack(side="bottom", fill=tk.X)






def main():
    testobj = testclass()
    testobj.mainloop()

if __name__ == "__main__":
    main()