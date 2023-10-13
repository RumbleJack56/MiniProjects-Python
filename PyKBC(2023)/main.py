import tkinter as tk
import time,random, webscrape, pygame.mixer as soundsystem
from tkinter import ttk
from PIL import Image,ImageTk

soundsystem.init()

class KbcApp(tk.Tk):
    def __init__(self,questions,*args,**kwargs):
        tk.Tk.__init__(self,*args,**kwargs)
        self.geometry("1200x640")
        self.title("Kaun Banega Crorepati")
        self.resizable(False,False)
        rootbox = tk.Frame(self, width=1200,height=640)
        rootbox.rowconfigure(0,weight=1)
        rootbox.columnconfigure(0,weight=1)
        rootbox.pack(side="top",fill="both",expand=True)

        self.windows= {}

        for num , window in enumerate([MainWindow]+[QWindow]*2+[LossWindow,WinWindow]):
            frame = window(rootbox,self,questions=questions,qnum=num)
            if window == QWindow:

                self.windows[num] = frame
            else: 
                self.windows[window] = frame
            frame.grid(row=0,column=0,sticky="NSEW")
        
        self.setWindow(MainWindow)

    def ActiveWindow(self,windowname):
        soundsystem.music.stop()
        self.setWindow(windowname)

    def setWindow(self,windowname):
        self.windows[windowname].tkraise()
        if windowname in range(1,16):
            soundsystem.music.load(r"PyKBC(2023)\nextques.mp3")
            soundsystem.music.play()


class MainWindow(tk.Frame):
    def __init__(self,parent,ControlWin,**kwargs):
        tk.Frame.__init__(self,parent)
        canvas = tk.Canvas(self, width=1200,height=640,borderwidth=0)
        canvas.pack(side='top',fill='both',expand=True)
        soundsystem.music.load("PyKBC(2023)\intro.mp3")
        soundsystem.music.play()
        canvas.background = ImageTk.PhotoImage(Image.open("Title Window.png").resize((1200,640),Image.LANCZOS))
        canvas.create_image(0,0,image=canvas.background,anchor="nw")
        canvas.bg2 = ImageTk.PhotoImage(Image.open(r"PyKBC(2023)\blueimg.png").resize((1193,90),Image.BICUBIC))
        startbutton = tk.Button(self,image=canvas.bg2,text = r"  Lets Play",font=("Impact",45),fg="#8b714f",compound="center",
                                borderwidth=0,width=1193,height=90,
                                command=lambda: ControlWin.ActiveWindow(1))
        canvas.create_window(0,473,window=startbutton,anchor="nw")
        # canvas.create_text(550,490,text="Lets Play",anchor="nw",)


class QWindow(tk.Frame):
    def __init__(self,parent,ControlWin,**kwargs):
        tk.Frame.__init__(self,parent)
        self.quesNum = kwargs['qnum']
        genre,qs = kwargs['questions'][self.quesNum -1]
        q,a,b,c,d,ans = random.choice(qs)

        canvas = tk.Canvas(self, width=1200,height=640,borderwidth=0)
        canvas.pack(side='top',fill='both',expand=True)
        
        canvas.im1 = ImageTk.PhotoImage(Image.open(r"PyKBC(2023)\qwindow.png").resize((1200,640),Image.BICUBIC))
        canvas.create_image(0,0,image=canvas.im1,anchor='nw')

        canvas.im2 = ImageTk.PhotoImage(Image.open(r"PyKBC(2023)\quit.png").resize((100,100),Image.BICUBIC))
        button = tk.Button(self,width=100,height=100,anchor='nw',image=canvas.im2,command=lambda: ControlWin.ActiveWindow(WinWindow))
        canvas.create_window(0,0,window=button,anchor='nw')

        canvas.im3 = ImageTk.PhotoImage(Image.open(r"PyKBC(2023)\opta.png").resize((520,53),Image.BICUBIC))
        canvas.im4 = ImageTk.PhotoImage(Image.open(r"PyKBC(2023)\optb.png").resize((520,53),Image.BICUBIC))
        canvas.im5 = ImageTk.PhotoImage(Image.open(r"PyKBC(2023)\optc.png").resize((520,50),Image.BICUBIC))
        canvas.im6 = ImageTk.PhotoImage(Image.open(r"PyKBC(2023)\optd.png").resize((520,50),Image.BICUBIC))

        opta,optb,optc,optd = [tk.StringVar()]*4
        buttonA = tk.Button(self,width=520,height=53,anchor="nw",image=canvas.im3,compound="center",fg='#ffa646',font=("Calibri",25),textvariable=opta)
        buttonB = tk.Button(self,width=520,height=53,anchor="nw",image=canvas.im4,compound="center")
        buttonC = tk.Button(self,width=520,height=50,anchor="nw",image=canvas.im5,compound="center")
        buttonD = tk.Button(self,width=520,height=50,anchor="nw",image=canvas.im6,compound="center")
        
        opta= "wow"
        canvas.create_window(100,520,window=buttonA,anchor='nw')
        canvas.create_window(620,520,window=buttonB,anchor='nw')
        canvas.create_window(100,580,window=buttonC,anchor='nw')
        canvas.create_window(620,580,window=buttonD,anchor='nw')

        
        # print(genre,qs)
        
        print(genre,q,a,b,c,d,ans)








        # text = tk.Label(self,text=str(self.quesNum))
        # text.pack(side = 'top',fill="both",anchor="center",expand=True)
class LossWindow(tk.Frame):
    def __init__(self,parent,root,**kwargs):
        tk.Frame.__init__(self,parent)

class WinWindow(tk.Frame):
    def __init__(self,parent,root,**kwargs):
        tk.Frame.__init__(self,parent)


def main():
    questions = [[key,val] for key,val in webscrape.question_set().items()]
    random.shuffle(questions)

    
    app = KbcApp(questions)
    app.mainloop()
if __name__=="__main__":
    main()
