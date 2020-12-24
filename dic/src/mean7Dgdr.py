#!/usr/bin/env python
# -*- coding: utf-8 -*-
''' 

.. py:module:: mean7Dgdr

This program is doing the mean of 7D output.

.. note:: please for each 7D analyses with different initial image create a folder as 'IMG###'
.. note:: the mean data will be export in the folder allIMG

'''

import numpy as np
import os
from signal import pause


# find all the file and folder in the current folder
folder=os.listdir(os.getcwd())
# find the folder contening 7D output IMG###
img_folder=[]
for i in range(len(folder)):
    if (folder[i][0:3]=='IMG'):
        img_folder.append(folder[i])
nb_folder=len(img_folder)

# name of all the output from 7D
if len(img_folder)>1:   
    name=os.listdir(img_folder[0])
    nb_img=len(name)
    
    # create outputfolder
    os.mkdir('allIMG')
    print('allIMG folder created')
    
    # loop on all the image
    for i in list(range(nb_img)):
        for j in list(range(nb_folder)):
            if j==0:
                data=np.loadtxt(img_folder[j] + '/' + name[i])
                x,y,u,v,cor,exx,eyy,exy=np.loadtxt(img_folder[j] + '/' + name[i],dtype='f,f,f,f,f,f,f,f',unpack=True)
            else:
                x1,y1,u1,v1,cor1,exx1,eyy1,exy1=np.loadtxt(img_folder[j] + '/' + name[i],dtype='f,f,f,f,f,f,f,f',unpack=True)
                u=u+u1
                v=v+v1
                cor=cor+cor1
                exx=exx+exx1
                eyy=eyy+eyy1
                exy=exy+exy1
                
        # divide by the number of indexed point
        # for x and y always write 
        data[:,0]=x
        data[:,1]=y
        # for dx dy exx eyy exy, it is 0 when it is not indexed but data[:,4]=-n where n is the number of not indexed point
        div=cor+nb_folder
        pause
        idx=np.where(div>0.)
        data[:,2]=0        
        data[idx,2]=u[idx]/div[idx]
        data[:,2]=0
        data[idx,3]=v[idx]/div[idx]
        data[:,2]=0
        data[idx,5]=exx[idx]/div[idx]
        data[:,2]=0
        data[idx,6]=eyy[idx]/div[idx]
        data[:,7]=0
        data[idx,7]=exy[idx]/div[idx]
        # correct data[:,4]=0 for indexed data and -1 for none
        
        data[:,4]=-1
        data[idx,4]=0
        # write the file
        np.savetxt('allIMG/' + name[i], data)
else:
    print('less than 2 folders')