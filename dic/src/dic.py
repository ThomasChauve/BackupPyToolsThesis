# -*- coding: utf-8 -*-
'''
Created on 21 août 2015

.. py:module:: dic

Toolbox for data obtained using 7D software create by Pierre Vacher
7D software is software to perform Digital Image Correlation (DIC). This toolbox is used to analysed the data export from 7D software by using the exportation by 'txt>>gdr'

.. warning:: In 7D version 0.9.5.178 there is a mistake during the expoprtation using 'txt>>gdr' dy=-dy and exy=-exy. Use 'correct7Dgdr.py' before using this toolbox
.. note:: if you want reduce the error due to the DIC process by doing the mean of multiple output, please refers to 'mean7Dgdr.py'

@author: Thomas Chauve
@contact: thomas.chauve@lgge.obs.ujf-grenoble.fr
@license: CC-BY-CC
'''

import aita
import image2d as im2d
import micro2d as mi2d
import symetricTensorMap as sTM

import numpy as np
from skimage import io
import os
import pylab
import matplotlib.pyplot as plt
from moviepy.video.io.bindings import mplfig_to_npimage
import moviepy.editor as mpy
import matplotlib.cm as cm
import matplotlib.patches as patches

class dic(object):
    '''
    'dic' is a python class to analyse data from 2D digital image correlation
    
    .. note:: this toolbox is build to work with the output from 7D using txt>>gdr export   
    '''
    pass


    def __init__(self, adr_data, resolution, time_step, adr_micro=0):
        '''
        :param adr_data: folder path where the 7D output are store
        :type adr_data: str
        :param resolution: pixel size of the image used for DIC (millimeters)
        :type resolution: float
        :param time_step: time step between the picture (seconds)
        :type time_step: float
        :param adr_micro: path for the black and white skeleton of the microstructure (bmp format) (default 0 - no microstructure)
        :type adr_micro: str
        '''
        
        # include time_step in the object
        self.time=time_step
                
        # find out file from 7D
        output=os.listdir(adr_data)
        output.sort()
        # loop on all the output
        self.u=[]
        self.v=[]
        self.strain=[]
        #self.exx=[]
        #self.eyy=[]
        #self.exy=[]
        #self.eeq=[]
        self.oxy=[]
        for i in list(range(len(output))):
            # load the file
            data=np.loadtxt(adr_data + '/' + output[i])
            # find not indexed point
            id=np.where(data[:,4]!=0.0)
            # replace not indexed point by NaN value
            data[id,2:4]=np.NaN
            data[id,5:8]=np.NaN
            # for the first step it extract size sx,sy and window correlation value used in 7D
            if (i==0):
                n_dic=np.abs(data[0,1]-data[1,1])
                nb_pix=np.size(data[:,0])
                sx=np.int32(np.abs(data[0,0]-data[nb_pix-1,0])/n_dic+1)
                sy=np.int32(np.abs(data[0,1]-data[nb_pix-1,1])/n_dic+1)
            # Build image at time t=i
            self.u.append(im2d.image2d(np.transpose(np.reshape(data[:,2]*resolution,[sx,sy])),n_dic*resolution))
            self.v.append(im2d.image2d(np.transpose(np.reshape(data[:,3]*resolution,[sx,sy])),n_dic*resolution))
            #self.exx.append(im2d.image2d(np.transpose(np.reshape(data[:,5],[sx,sy])),n_dic*resolution))
            #self.eyy.append(im2d.image2d(np.transpose(np.reshape(data[:,6],[sx,sy])),n_dic*resolution))
            #self.exy.append(im2d.image2d(np.transpose(np.reshape(data[:,7],[sx,sy])),n_dic*resolution))
            #slef.eeq.append((self.exx[i].pow(2)+self.eyy[i].pow(2)+self.exy[i].pow(2)*2.)*(2./3.).pow(1/2))
            exx=im2d.image2d(np.transpose(np.reshape(data[:,5],[sx,sy])),n_dic*resolution)
            eyy=im2d.image2d(np.transpose(np.reshape(data[:,6],[sx,sy])),n_dic*resolution)
            exy=im2d.image2d(np.transpose(np.reshape(data[:,7],[sx,sy])),n_dic*resolution)
            if i==0:
                eaz=im2d.image2d(np.zeros([sy,sx]),n_dic*resolution)
                
            self.strain.append(sTM.symetricTensorMap(exx,eyy,eaz,exy,eaz,eaz))
            self.oxy.append((self.u[i].diff('y')-self.v[i].diff('x'))*.5)
        
        minx=np.int32(np.min(data[:,0])/n_dic)-1
        maxx=np.int32(np.max(data[:,0])/n_dic)
        miny=np.int32(np.min(-data[:,1])/n_dic)-1
        maxy=np.int32(np.max(-data[:,1])/n_dic)
        
        # open the microstructure
        if adr_micro==0:
            self.micro=mi2d.micro2d(np.zeros([sy,sx]),n_dic*resolution)
        else:
            micro_bmp = io.imread(adr_micro)
            self.micro=mi2d.micro2d(micro_bmp[miny:maxy,minx:maxx,0]/np.max(micro_bmp),n_dic*resolution)
        
        self.grains=self.micro.grain_label()
        
        # replace grains boundary with NaN number
        self.grains.field=np.array(self.grains.field,float)
        idx=np.where(self.micro.field==1)
        self.grains.field[idx]=np.nan
        
    def crop(self):
        '''
        Crop function to select the area of interest
        
        :return: crop dic object
        :rtype: dic
        :Exemple: >>> data.crop()
        
        .. note:: clic on the top left corner and bottom right corner to select the area
        '''
        
        # plot the data
        h=self.strain[len(self.u)-1].t22.plot()
        self.micro.plotBoundary()
        # select top left and bottom right corner for crop
        print('Select top left and bottom right corner for crop :')
        x=np.array(pylab.ginput(2))/self.u[1].res
        plt.close("all")
        # create x and Y coordinate
        
        xx=[x[0][0],x[1][0]]
        yy=[x[0][1],x[1][1]]
        # size of the initial map
        ss=np.shape(self.u[0].field)
        # find xmin xmax ymin and ymax
        xmin=np.ceil(np.min(xx))
        xmax=np.floor(np.max(xx))
        ymin=ss[0]-np.ceil(np.max(yy))
        ymax=ss[0]-np.floor(np.min(yy))
        
        for i in list(range(len(self.strain))):
            # crop the map
            self.u[i].field=self.u[i].field[ymin:ymax, xmin:xmax]
            self.v[i].field=self.v[i].field[ymin:ymax, xmin:xmax]
            #
            ss=np.shape(self.u[i].field)
            #self.exx[i].field=self.exx[i].field[ymin:ymax, xmin:xmax]
            #self.eyy[i].field=self.eyy[i].field[ymin:ymax, xmin:xmax]
            #self.exy[i].field=self.exy[i].field[ymin:ymax, xmin:xmax]
            #self.eeq[i].field=self.eeq[i].field[ymin:ymax, xmin:xmax]
            self.strain[i].t11.field=self.strain[i].t11.field[ymin:ymax, xmin:xmax]
            self.strain[i].t22.field=self.strain[i].t22.field[ymin:ymax, xmin:xmax]
            #self.strain[i].t33.field=self.strain[i].t33.field[ymin:ymax, xmin:xmax]
            self.strain[i].t12.field=self.strain[i].t12.field[ymin:ymax, xmin:xmax]
            #self.strain[i].t13.field=self.strain[i].t13.field[ymin:ymax, xmin:xmax]
            #self.strain[i].t23.field=self.strain[i].t23.field[ymin:ymax, xmin:xmax]
            self.strain[i].t33.field=np.zeros(ss)
            self.strain[i].t13.field=np.zeros(ss)
            self.strain[i].t23.field=np.zeros(ss)
            
            self.oxy[i].field=self.oxy[i].field[ymin:ymax, xmin:xmax]
            
        self.micro.field=self.micro.field[ymin:ymax, xmin:xmax]
        self.grains=self.micro.grain_label()
        
        # replace grains boundary with NaN number
        self.grains.field=np.array(self.grains.field,float)
        idx=np.where(self.micro.field==1)
        self.grains.field[idx]=np.nan
        
    def strain_macro(self,nb_line=3):
        '''
        Compute the macroscopic strain along the y-axis (vertical) using 2 methods :
        
        (1)-mean of eyy \n
        (2)-dic line (see Fanny Grennerat Thesis)
            
        :param nb_line: number of line skip at the top and bottom part of the picture during (2) evalutation
        :type nb_line: int
        :return: macro_eyy, method (1)
        :rtype: array
        :return: macro_line, method (2)
        :rtype: array
        :return: time, time of each point (seconds)
        :rtype: array
        :Exemple:
            >>> [time,macro_eyy,macro_line]=data.strain_macro()
            >>> plt.plot(time,macro_eyy)
            >>> plt.show()
            
        .. warning:: If you have macro_eyy~=-macro_line, it is because you did not correct the gdr output 
        '''
        
        time=np.zeros(len(self.u))
        macro_eyy=np.zeros(len(self.u))
        macro_line=np.zeros(len(self.u))
        # number of line along y
        nby=np.shape(self.v[0].field)[0]-1
        for i in list(range(len(self.u))):
            time[i]=(i+1)*self.time
            macro_eyy[i]=np.nanmean(self.strain[i].t22.field)
            macro_line[i]=(np.nanmean(self.v[i].field[nb_line,:])-np.nanmean(self.v[i].field[nby-nb_line,:]))/((nby-2*nb_line)*self.v[i].res)
            
            
        return time,macro_eyy,macro_line
    
    def find_pic(self,strain_step=0.001,minst=0):
        '''
        Find picture number as between 2 picture the increment of deformation is macro_strain
        
        :param strain_step: macroscopic strain between 2 picture.
        :type strain_step: float
        :return: nb_img
        :rtype: array
        '''
        
        # extract macroscopic strain from the data
        [time,macro_eyy,macro_line]=self.strain_macro()
        
        nb_img=[]
        
        id=np.isnan(macro_line)
        macro_line[id]=0
        
        #last strain record
        if minst==0:
            minstrain=macro_line[len(macro_line)-1]
        else:
            minstrain=minst
        
        
        #number of iteration
        it=np.int32(minstrain/strain_step)

        for i in list(range(-it)):
            # find where the macro strain is higher that the step
            idx=np.where(macro_line>-1.*np.float(i+1)*strain_step)
            # take the minimum
            label=np.where(macro_line==np.min(macro_line[idx]))
            nb_img.append(list(label[0]))
            
            
        res=np.array(nb_img)    
        #np.savetxt('wanted_image.txt',res,fmt='%i')
            
        return res
    
    def noise_map(self):
        '''
        compute the variance of a set of map for u, v, exx, eyy, exy, eeq
        :return su,sv,sexx,seyy,sexy,seeq:
        :rtype su,sv,sexx,seyy,sexy,seeq: im2d.image2d
        '''
        l, c = np.shape(self.u[0].field)
        st11 = np.zeros((l, c, len(self.u)))
        st22 = np.zeros((l, c, len(self.u)))
        st12 = np.zeros((l, c, len(self.u)))
        steq = np.zeros((l, c, len(self.u)))
        su = np.zeros((l, c, len(self.u)))
        sv = np.zeros((l, c, len(self.u)))
        
        for i in list(range(len(self.u))):
            st11[:,:,i]=self.strain[i].t11.field
            st22[:,:,i]=self.strain[i].t22.field
            st12[:,:,i]=self.strain[i].t12.field
            su[:,:,i]=self.u[i].field
            sv[:,:,i]=self.v[i].field
            steq[:,:,i]=self.strain[i].eqVonMises().field
            
        return im2d.image2d(np.nanstd(su,axis=2),self.micro.res), im2d.image2d(np.nanstd(sv,axis=2),self.micro.res), im2d.image2d(np.nanstd(st11,axis=2),self.micro.res), im2d.image2d(np.nanstd(st22,axis=2),self.micro.res), im2d.image2d(np.nanstd(st12,axis=2),self.micro.res), im2d.image2d(np.nanstd(steq,axis=2),self.micro.res)
        
        
    def movie(self,name,optdic=1,tl_img=0,vmin=np.NaN,vmax=np.NaN,vmin_i=np.NaN,vmax_i=np.NaN,colorbarcenter=False,colorbar=cm.brg,fps=5.,nb_line=3,subarea=False):
        '''
        :param name: name of the output file ###.mp4
        :type optdic: str
        :param optdic: 1=eqVonMises, 2=twod princitipal_strain, 3=eyy
        :type optdic: int
        :param tl_img: top left image 
        :type tl_img: aita or dic
        :param vmin: c axis minimum fig1 
        :type vmin: float
        :param vmax: c axis maximum fig1 
        :type vmax: float
        :param vmin_i: c axis minimum fig2 
        :type vmin_i: float
        :param vmax_i: c axis maximum fig2
        :type vmax_i: float
        :param colorbarcenter: do you want center the colorbar
        :type colorbarcenter: bool
        :param colorbar: color of the colorbar
        :type colorbar: matplotlib.cm
        :param fps: frame per second
        :type fps: int
        :param nb_line: number of line for the dic line (see function strain_macro)
        :type nb_line: int
        :param subarea: Do you want select a sub area
        :type subarea: bool
        
        :return: movie
        :rtype: .mp4
        
       
        '''
        
        if (subarea==True and type(tl_img)==dic):
            plt.close('all')
            tl_img.strain[len(self.u)-1].eqVonMises().plot(vmin=vmin_i,vmax=vmax_i,colorbarcenter=colorbarcenter,colorbar=colorbar)
            xl=np.array(plt.ginput(2))
            plt.close('all')
            
        [tt,eyy,dl]=self.strain_macro(nb_line=nb_line)
        
        if type(tl_img)==aita.aita:
            h,img=tl_img.plot()
            plt.close('all')
       
        def make_frame(t):
            plt.close('all')
            fig, ax = plt.subplots(1, figsize=(10, 10), facecolor=(1,1,1))
            #fig=plt.subplot(2,1,1)
            id=np.int32(t*fps)
            ax.clear()
            ax.axis('off')
            #ax.set_title("DIC", fontsize=16)
            if optdic==1:
                self.strain[id].eqVonMises().plot(vmin=vmin,vmax=vmax,colorbarcenter=colorbarcenter,colorbar=colorbar)
                self.micro.plotBoundary()
            elif optdic==2:
                self.strain[id].principal_tensor(scale=100/(t+1),space=3,twod=True,absolutemax=False,colorbarcenter=True,plotmin=True)
            elif optdic==3:
                self.strain[id].t22.plot(vmin=vmin,vmax=vmax,colorbarcenter=colorbarcenter,colorbar=colorbar)
            if subarea==True:
                ax.add_patch(patches.Rectangle((np.min(xl[:,0]), np.min(xl[:,1])),np.max(xl[:,0])-np.min(xl[:,0]),np.max(xl[:,1])-np.min(xl[:,1]),fill=False))
                        
            return mplfig_to_npimage(fig)
        
        def make_strain(t):
            plt.close('all')
            plt.subplots(1, figsize=(5, 10), facecolor=(1,1,1))
            id=np.int32(t*fps)
            plt.subplot(2,1,1)#, figsize=(5, 10), facecolor=(1,1,1))
            if type(tl_img)==aita.aita:
                nx=np.shape(tl_img.phi.field)
                plt.imshow(img,extent=(0,nx[1]*tl_img.phi.res,0,nx[0]*tl_img.phi.res))                
            else:
                plt.axis('off')
            plt.subplot(2,1,2)#, figsize=(5, 10), facecolor=(1,1,1))
            plt.plot(tt[0:id]/3600.,dl[0:id],'-b')
            plt.xlabel('Time (h)')
            plt.ylabel('Strain')
            plt.xlim([0,np.max(tt)/3600.])
            plt.ylim([np.min(dl),np.max(dl)])
            plt.grid('on')
            plt.title(id, fontsize=16)
            return mplfig_to_npimage(plt.gcf())
        
        def make_increment(t):
            plt.close('all')
            fig, ax = plt.subplots(1, figsize=(10, 10), facecolor=(1,1,1))
            id=np.int32(t*fps)
            plt.axis('off')
            #plt.title("Increment", fontsize=16)
            #if optdic==1:
            #    tl_img.strain[id].eqVonMises().plot(vmin=vmin_i,vmax=vmax_i,colorbarcenter=colorbarcenter,colorbar=colorbar)
            #elif optdic==2:
            bg=tl_img.strain[0].t11
            bg.field[:,:]=0;
            tl_img.strain[id].principal_tensor(scale=10,space=2,twod=True,absolutemax=False,colorbarcenter=True,plotmin=True,vmax=vmax_i)
            ax.add_patch(patches.Rectangle((np.min(xl[:,0]), np.min(xl[:,1])),np.max(xl[:,0])-np.min(xl[:,0]),np.max(xl[:,1])-np.min(xl[:,1]),fill=False))
            #elif optdic==3:
            #   tl_img.strain[id].t22.plot(vmin=vmin_i,vmax=vmax_i,colorbarcenter=colorbarcenter,colorbar=colorbar)
            if subarea==True:
                plt.xlim([np.min(xl[:,0]),np.max(xl[:,0])])
                plt.ylim([np.min(xl[:,1]),np.max(xl[:,1])])
            return mplfig_to_npimage(fig)
        
        strainfig =mpy.VideoClip(make_frame, duration=len(self.strain)/fps)            
        straincurvefig =mpy.VideoClip(make_strain, duration=len(self.strain)/fps)
        
        
        if type(tl_img)==dic:
            straininc =mpy.VideoClip(make_increment, duration=len(self.strain)/fps)
            animation = mpy.clips_array([[strainfig,straininc ,straincurvefig]]) 
        else:
            animation = mpy.clips_array([[strainfig, straincurvefig]])
        # animation.write_gif("sinc_mpl.gif", fps=5)
        animation.write_videofile(name, fps=fps)


        
        return   
