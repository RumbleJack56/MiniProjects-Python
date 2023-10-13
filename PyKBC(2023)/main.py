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

        for num , window in enumerate([MainWindow]+[QWindow]*15 +[LossWindow]+[WinWindow]):
            frame = window(rootbox,self,questions=questions,qnum=num)
            if window == QWindow:
                self.windows[num] = frame
            else: 
                self.windows[window] = frame
            frame.grid(row=0,column=0,sticky="NSEW")
        
        print(self.windows)
        self.setWindow(MainWindow)

    def ActiveWindow(self,windowname):
        soundsystem.music.stop()
        self.setWindow(windowname)

    def setWindow(self,windowname):
        print(windowname)
        self.windows[windowname].tkraise()
        if windowname in range(1,16):
            soundsystem.music.load(r"PyKBC(2023)\nextques.mp3")
            soundsystem.music.play()
    def nextwin(self,qnum):
        if qnum == 15:
            self.ActiveWindow(WinWindow)
        else:
            self.ActiveWindow(qnum+1)

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


class QWindow(tk.Frame):
    def __init__(self,parent,ControlWin,**kwargs):
        tk.Frame.__init__(self,parent)
        self.quesNum = kwargs['qnum']
        genre,qs = kwargs['questions'][self.quesNum -1]
        q,a,b,c,d,ans = random.choice(qs)
        tempOptionList = [a,b,c,d]
        canvas = tk.Canvas(self, width=1200,height=640,borderwidth=0)
        canvas.pack(side='top',fill='both',expand=True)
        
        canvas.im1 = ImageTk.PhotoImage(Image.open(r"PyKBC(2023)\qwindow.png").resize((1200,640),Image.BICUBIC))
        canvas.create_image(0,0,image=canvas.im1,anchor='nw')

        canvas.im2 = ImageTk.PhotoImage(Image.open(r"PyKBC(2023)\quit.png").resize((100,100),Image.BICUBIC))
        quitbutton = tk.Button(self,width=100,height=100,anchor='nw',image=canvas.im2,command=lambda: ControlWin.ActiveWindow(WinWindow))
        canvas.create_window(0,0,window=quitbutton,anchor='nw')

        canvas.im3 = ImageTk.PhotoImage(Image.open(r"PyKBC(2023)\opta.png").resize((520,53),Image.BICUBIC))
        canvas.im4 = ImageTk.PhotoImage(Image.open(r"PyKBC(2023)\optb.png").resize((520,53),Image.BICUBIC))
        canvas.im5 = ImageTk.PhotoImage(Image.open(r"PyKBC(2023)\optc.png").resize((520,50),Image.BICUBIC))
        canvas.im6 = ImageTk.PhotoImage(Image.open(r"PyKBC(2023)\optd.png").resize((520,50),Image.BICUBIC))

        options = []
        for x in range(4):
            options.append(tk.StringVar())
        for n,x in enumerate([a,b,c,d]):
            options[n].set(x)
        
        buttons = []
        for x,im in zip(options,[canvas.im3,canvas.im4,canvas.im5,canvas.im6]):
            if x.get() == ans:
                buttons.append(tk.Button(self,width=520,height=53,anchor='nw',image=im,compound="center",fg="#ffa646",
                                         font=("Calibri",20),textvariable=x,command=lambda: ControlWin.nextwin(self.quesNum)))
            else:
                buttons.append(tk.Button(self,width=520,height=53,anchor='nw',image=im,compound="center",fg="#ffa646",
                                         font=("Calibri",20),textvariable=x,command=lambda: ControlWin.ActiveWindow(LossWindow)))

        canvas.create_text(610,480,text=str(q),font=("Calibri",20),fill="#ffa646")
        canvas.create_window(100,520,window=buttons[0],anchor='nw')
        canvas.create_window(620,520,window=buttons[1],anchor='nw')
        canvas.create_window(100,580,window=buttons[2],anchor='nw')
        canvas.create_window(620,580,window=buttons[3],anchor='nw')

        
        # print(genre,qs)
        
        print(genre,q,a,b,c,d,ans)

class LossWindow(tk.Frame):
    def __init__(self,parent,root,**kwargs):
        tk.Frame.__init__(self,parent)

class WinWindow(tk.Frame):
    def __init__(self,parent,root,**kwargs):
        tk.Frame.__init__(self,parent)


def main():
    questions = [[key,val] for key,val in webscrape.question_set().items()]
    random.shuffle(questions)
    print(questions)
    app = KbcApp(questions)
    app.mainloop()
if __name__=="__main__":
    main()