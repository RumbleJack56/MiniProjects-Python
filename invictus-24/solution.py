import numpy as np
import hashlib
import cv2
import matplotlib.pyplot as plt
from functools import reduce

class Crypt_Image():
    def __init__(self,filepath: str):
        self.orig = cv2.imread(filepath)
        self.img = self.orig
        self.b,self.g,self.r = cv2.split(self.orig)
        self.ENABLE_RED = True
        self.ENABLE_GREEN = True
        self.ENABLE_BLUE = True
        self.IS_GRAYSCALE = False
        self.NUM_ROWS = 1
        self.NUM_COLS = 1
        self.matSize = self.img.shape[:2]
    def view_original(self):
        plt.close('all')
        plt.imshow(cv2.cvtColor(self.orig,cv2.COLOR_BGR2RGB))
        plt.title("Original Image")
        plt.axis("off")
    def preview(self):
        plt.close('all')
        plt.imshow(cv2.cvtColor(self.img,cv2.COLOR_BGR2RGB))
        plt.title("Preview of Current Settings")
        plt.axis("off")
    def getSegmentedImgs(self):
        segments = []
        for y in range(self.NUM_ROWS):
            for x in range(self.NUM_COLS):
                segments.append(Segment_Image(self.img[
                    int(y*1080/self.NUM_ROWS):int(1080/self.NUM_ROWS*(y+1)),
                    int(x*1080/self.NUM_COLS):int(1080/self.NUM_COLS*(x+1)),
                    :]))
        return segments
    def SegShow(self,segArr):
        fig, ax = plt.subplots(self.NUM_ROWS,self.NUM_COLS)
        for num,segment in enumerate(segArr):
            if self.NUM_COLS == 1 == self.NUM_ROWS: ax.imshow(cv2.cvtColor(segment.img,cv2.COLOR_BGRA2RGB)) ; ax.axis('off') ; continue
            ax[num//self.NUM_ROWS,num%self.NUM_ROWS].imshow(cv2.cvtColor(segment.img,cv2.COLOR_BGRA2RGB))
            ax[num//self.NUM_ROWS,num%self.NUM_ROWS].axis('off')


                
    

    ## Transformations and properties:
    def setRed(self,val):
        if val==True: self.img[:,:,2] = self.r
        else :
            self.img[:,:,2] = np.zeros(np.multiply(*self.matSize)).reshape(self.matSize)
        return val
    

    def setGreen(self,val):
        if val==True: self.img[:,:,1] = self.g
        else : 
            self.img[:,:,1] = np.zeros(np.multiply(*self.matSize)).reshape(self.matSize)
        return val

    def setBlue(self,val):
        if val==True: self.img[:,:,0] = self.b
        else :
            self.img[:,:,0] = np.zeros(np.multiply(*self.matSize)).reshape(self.matSize)
        return val
    
    def setGray(self,val):
        if val==True: self.img = cv2.cvtColor(cv2.cvtColor(self.orig,cv2.COLOR_BGR2GRAY),cv2.COLOR_GRAY2BGR)
        else: self.img=self.orig
        return val

    ENABLE_BLUE = property(fset=setBlue)
    ENABLE_GREEN = property(fset=setGreen)
    ENABLE_RED= property(fset=setRed)
    IS_GRAYSCALE=property(fset=setGray)


class Segment_Image():
    def __init__(self,img):
        self.orig = img
        self.img = self.orig
        self.b,self.g,self.r = cv2.split(self.orig)
        self.ENABLE_RED = True
        self.ENABLE_GREEN = True
        self.ENABLE_BLUE = True
    ## Transformations and properties:
    def setRed(self,val):
        if val==True: self.img[:,:,2] = self.r
        else :
            self.img[:,:,2] = np.zeros(np.multiply(*self.matSize)).reshape(self.matSize)
        return val
    

    def setGreen(self,val):
        if val==True: self.img[:,:,1] = self.g
        else : 
            self.img[:,:,1] = np.zeros(np.multiply(*self.matSize)).reshape(self.matSize)
        return val

    def setBlue(self,val):
        if val==True: self.img[:,:,0] = self.b
        else :
            self.img[:,:,0] = np.zeros(np.multiply(*self.matSize)).reshape(self.matSize)
        return val

    ENABLE_BLUE = property(fset=setBlue)
    ENABLE_GREEN = property(fset=setGreen)
    ENABLE_RED= property(fset=setRed)

    def avgColor(self)->list[int]:
        b,g,r = cv2.split(self.img)
        b=np.mean(b.reshape(np.multiply(*b.shape),-1))//1
        g=np.mean(g.reshape(np.multiply(*g.shape),-1))//1
        r=np.mean(r.reshape(np.multiply(*r.shape),-1))//1
        return b,g,r



def test_solution(output_array: np.ndarray)->bool:
    hashsol = hashlib.sha256(str(sum([16**i *x for i,x in enumerate(output_array.flatten())])).encode('utf-8')).hexdigest()
    soln = '7918f3f87a52acb1ac038db6924a5b5d32a1298a0d1da518d0ada717da4c2b8b'
    
    return hashsol , hashsol==soln
test_solution(np.array([1]))
