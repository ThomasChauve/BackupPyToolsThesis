# -*- coding: utf-8 -*-
'''
.. py:module:: multiruncraft
Created on 30 sept. 2015
Toolbox to treat data from multiple run experiment using CraFT

@author: Thomas Chauve
@contact: thomas.chauve@lgge.obs.ujf-grenoble.fr
@license: CC-BY-CC
'''

import os
import runcraft
import numpy as np
import matplotlib.pylab as plt
import plotpdf_craft

class multiruncraft(object):
    '''
    This toolbox need over toolboxs :
    
    :library: os
    :library: runcraft

    '''
    pass
        
    def __init__(self,adr_folder,time_data,folder_init):
        '''
        Build the object multiruncraft
        
        :param adr_folder: path to the folder were all the run are present
        :type adr_folder: str
        :param time_data: suffix of one vtk file you want analyse
        :type time_data: str
        :param folder_init: folder where is the run of the initial state you want campare with
        :type folder_init: str
        :return: multiruncraft object
        :rtype: multiruncraft
        
        symetricTensorMap structure :
        
        :element: *.run : list with n 'runcraft' object (n=number of craft run)
        :element: *.init : the initial craft run you want compare with 
        
        .. warning:: inside adr_folder the structure should be for each run you find a "runi" folder with inside this a 'output' folder were the CraFT output are.
        '''
        #find current folder
        current=os.getcwd()
        # find the folder with 'run' prefix within adr_folder
        folder=os.listdir(adr_folder)
        folder.sort()
        run_folder=[]
        for i in xrange(len(folder)):
            if (folder[i][0:3]=='run'):
                run_folder.append(folder[i])
                
        # loop on each folder (ie. run)
        self.ng_run=[]
        
        for i in xrange(len(run_folder)):
            self.ng_run.append(runcraft.runcraft(adr_folder+'/'+run_folder[i],time_data))
                   
        # return in current folder   
        os.chdir(current)
        
        # open init data
        self.init=runcraft.runcraft(folder_init,time_data)
        
        return
        
        
    def info(self,selectGrain=False,ngId=0):
        '''
        Give info about the number of differents orientations tested. What are these orientations ? And what is the GrainId of the new grain.
        If no option are pass there is two option. 1- If the ngId is equal to the maxId of the init micro + 1, it take it as a new grain. 2- If not, it ask the user which is the ngId.
        
        :param selectGrain: User select the new grain by clic on the microstructure (default False)
        :type selectGrain: bool
        :param ngId: User give the new grainId directly
        :type ngId: int
        :return: ngId: the new grain Id
        :rtype: int
        :return: tested_ori: The orientation for the new grain tested with CraFT
        :rtype: array
        '''
        
        # How many run with new grain ?
        nb_run='Number of orientation tested : '+str(len(self.ng_run))
        print nb_run
        
        # Find what is the grain Id of the new grain
        if ngId==0: # if the grain Id is pass by the user you don't have to look
            maxgId=np.max(self.init.grainId.field)
            ngId=np.max(self.ng_run[0].grainId.field)
        
            if (maxgId!=ngId-1) or selectGrain:
                self.ng_run[0].grainId.plot()
                print('Clic to select the new grain :')
                x=np.int32(np.array(plt.ginput(1))/self.ng_run[0].grainId.res)
                ss=np.shape(self.ng_run[0].grainId.field)
                ngId=self.ng_run[0].grainId.field[ss[0]-x[0,1],x[0,0]]
        # print the new grain Id    
        maxngId='New grainId : '+str(ngId)
        print maxngId
        
        # look for phi1 phi phi2 of the new grain orientation tested
        # where is the new grain in the array
        wid=np.where(self.ng_run[0].orientation[:,0]==ngId)
        tested_ori=np.zeros([len(self.ng_run),3])
       
        for i in xrange(len(self.ng_run)):
            tested_ori[i]=self.ng_run[i].orientation[wid[0]][0,1:4]
            
        return ngId,tested_ori
    
    def plotpdf(self,option,mask=0,selectGrain=False, ngId=0,norm=False,colorbarcenter=True):
        '''
        Plot pole figure data of the option wanted using a mask if necessary
        By default the new grain ID ngId is the maxId(init data)+1 (see .info)
        
        :param option: a runcraft image2d link (exemple : 'strain.t22' or 'stress.t11' or 'strain.eqtensor2d()' or 'strain_energie()')
        :type option: str
        :param mask:
        :type mask: image2d
        :param selectGrain: User select the new grain by clic on the microstructure (default False)
        :type selectGrain: bool
        :param ngId: User give the new grainId directly
        :type ngId: int
        :param norm: normalized value by mean(strain.t22)
        :type norm: bool
        :return: maxori is the line of the orientation output from .info function for which the data plot are maximal
        :rtype: int
        :return: minori is the line of the orientation output from .info function for which the data plot are minimum
        :rtype: int
        '''
        if mask==0:
            opt=option
        else:
            opt=option+'*mask'
        
        # compute the mean of the variable wanted for each run with a new grains
        res=np.zeros(np.int32(len(self.ng_run)))
        for i in range(np.int32(len(self.ng_run))):
            # print(np.float(i)/np.float(len(self.ng_run)))
            res[i]=np.nanmean(eval('self.ng_run[i].'+opt).field)
            
        # compute the mean of the variable wanted for the initial run (without new grain)    
        res_ref=np.nanmean(eval('self.init.'+opt).field)
        
        # load the orientation info
        ngId,ori=self.info(selectGrain, ngId)
        
        # plot the pole figure
        if norm:
            nn=np.zeros(np.int32(len(self.ng_run)))
            for i in range(np.int32(len(self.ng_run))):
                nn[i]=np.nanmean(self.ng_run[i].strain.t22.field)
            ni=np.nanmean(self.init.strain.t22.field)
            color=res/nn-res_ref/ni
        else:
            color=res-res_ref
        plotpdf_craft.plotpdf_craft(ori, color,colorbarcenter=colorbarcenter)
        
        maxori=np.where(color==np.max(color))
        minori=np.where(color==np.min(color))
        
        return maxori, minori
        
    def schmid_grain(self):
        '''
        
        '''
        [nb,ori]=self.info()
        id=np.where(self.ng_run[0].grainId.field==nb)
        gid=list(set(self.init.grainId.field[id]))
        
        ori=plotpdf_craft.ori()
        schmid=[]
        k=0;
        for j in gid:
            id2=np.where((self.ng_run[0].grainId.field==nb) & (self.init.grainId.field==j))
            schmid.append(np.zeros([1,len(ori)]))
            for i in list(range(len(id2[0]))):
                [sigma,tid]=self.init.stress.extract_data(np.array([[id2[1][i],id2[0][i]]]))
                schmid[k]=schmid[k]+plotpdf_craft.schmid(sigma, ori)
            plt.figure()
            plotpdf_craft.plotpdf_craft(ori, schmid[k], colorbarcenter=False)
            plt.title(str(j))
            k=k+1
            plt.show()
        return