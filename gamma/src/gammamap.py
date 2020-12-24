'''
.. py:module:: gammarun
Created on 27 jan. 2016
This class is build to build gamma map

@author: Thomas Chauve
@contact: thomas.chauve@lgge.obs.ujf-grenoble.fr
@license: CC-BY-CC
'''

import image2d
import numpy as np
import symetricTensorMap
import TensorMap

class gammamap(object):
    '''
    This toolbox is building a gamma map
    
    This toolbox is running on python and need various packages :
    
    :library: image2d  
    '''
    pass


    def __init__(self, map,burger,plane):
        '''
        :param map: output map from CraFT
        :type map: image2d
        :param burger: burger vector of the slip system
        :type burger: array
        :param plane: normal vector of the plane of the slip system
        :type plane: array
        
        :return: gammamap object with '.map' (output from CraFT), '.b' burger vector '.plane' planver vector of the slip system
        :rtype: gammamap
        '''
        self.map=map
        self.b=burger
        self.plane=plane
        
    def schmidtensor(self,sTM=False):
        '''
        Compute the schmidtensor 1/2*(b*plane+plane*b)
        
        :param sTM: if you want the schmid tensor return under a symetric tensor map
        :type sTM: bool 
        :return: array 3*3
        :rtype: array or symetricTensorMap
        '''
        
        
        if sTM:
            st= 0.5*(np.tensordot(self.plane,self.b,axes=0)+np.tensordot(self.b,self.plane,axes=0))
            
            ss=self.map.field.shape
            res=self.map.res
            
            t11=image2d.image2d(np.zeros(ss),res)
            t12=image2d.image2d(np.zeros(ss),res)
            t13=image2d.image2d(np.zeros(ss),res)
            t22=image2d.image2d(np.zeros(ss),res)
            t23=image2d.image2d(np.zeros(ss),res)
            t33=image2d.image2d(np.zeros(ss),res)
        
            t11.field[:,:]=st[0,0]
            t12.field[:,:]=st[0,1]
            t13.field[:,:]=st[0,2]
            t22.field[:,:]=st[1,1]
            t23.field[:,:]=st[1,2]
            t33.field[:,:]=st[2,2]
            
            res=symetricTensorMap.symetricTensorMap(t11,t22,t33,t12,t13,t23)
        else :
            res= 0.5*(np.tensordot(self.plane,self.b,axes=0)+np.tensordot(self.b,self.plane,axes=0))
        
        return res
        
    def bdotn(self,TM=False):
        '''
        Compute the dyadic product ou b time n
        
        :param TM: if you want the b X n return under a tensor map
        :type TM: bool 
        :return: array 3*3
        :rtype: array or TensorMap
        '''
        if TM:
            st= np.tensordot(self.b,self.plane,axes=0)
            
            ss=self.map.field.shape
            res=self.map.res
            
            t11=image2d.image2d(np.zeros(ss),res)
            t12=image2d.image2d(np.zeros(ss),res)
            t13=image2d.image2d(np.zeros(ss),res)
            
            t21=image2d.image2d(np.zeros(ss),res)
            t22=image2d.image2d(np.zeros(ss),res)
            t23=image2d.image2d(np.zeros(ss),res)
            
            t31=image2d.image2d(np.zeros(ss),res)
            t32=image2d.image2d(np.zeros(ss),res)
            t33=image2d.image2d(np.zeros(ss),res)
        
            t11.field[:,:]=st[0,0]
            t12.field[:,:]=st[0,1]
            t13.field[:,:]=st[0,2]
            
            t21.field[:,:]=st[1,0]
            t22.field[:,:]=st[1,1]
            t23.field[:,:]=st[1,2]
            
            t31.field[:,:]=st[2,0]
            t32.field[:,:]=st[2,1]
            t33.field[:,:]=st[2,2]
            
            res=TensorMap.TensorMap(t11,t12,t13,t21,t22,t23,t31,t32,t33)
        else :
            res= np.tensordot(self.b,self.plane,axes=0)  
            
        return res 
        
    
    def vpstrain(self):
        '''        
        :return: viscoplastic strain of the slip system
        :rtype: symetricTensorMap
        '''
        return self.map*self.schmidtensor(sTM=True)
    
    def Lpi(self):
        '''
        Compute L^p the plastic portion. (see Le et al. 2016)
        '''
        
        Lpi=self.map*self.bdotn(TM=True)
        
        return Lpi