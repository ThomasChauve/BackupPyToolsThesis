import multiruncraft
import matplotlib.pyplot as plt
import pickle

adr_folder='/home/tchauve/lachouf/CI_columnar_ice/CI02_manip/nb_ori_197/CI02_ng2'
adr_init='/home/tchauve/lachouf/CI_columnar_ice/CI02_manip/nb_ori_197/CI02_true'
time_data='09.20000000e+04'

# ng1=multiruncraft.multiruncraft(adr_folder,time_data,adr_init)
ng1 = pickle.load( open( "ng1.craft", "rb"))

plt.figure()
plt.subplot(131)
ng1.plotpdf('strain_energie()',mask=mask)
plt.title('Strain Energy')
plt.subplot(132)
ng1.plotpdf('strain.t22',mask=mask)
plt.title('Eyy')
plt.subplot(133)
ng1.plotpdf('strain.eqtensor2d()',mask=mask)
plt.title('Eeq')


#
plt.figure()
plt.subplot(131)
map0.plot()
plt.title('Initial micro')

plt.subplot(132)
map1.plot()
plt.title('New grain : min strain_energie, mask newgrain')

plt.subplot(133)
map2.plot()
plt.title('New grain : min strain_energie, mask circle around triple junction 7mm')

# test
X=[]
Y=[]
U=[]
V=[]
ss=np.shape(sTM.t11.field)
k=5
for i in list(range(ss[0]/5)):
    for j in list(range(ss[1]/5)):
        ii=k*i
        jj=k*j
        # first arrow
        X.append(ii*sTM.t11.res)
        Y.append(jj*sTM.t11.res)
        U.append(a[0,ii,jj]*v[0,0,ii,jj])
        V.append(a[0,ii,jj]*v[1,0,ii,jj])
        #symetric arrow
        X.append(ii*sTM.t11.res)
        Y.append(jj*sTM.t11.res)
        U.append(-a[0,ii,jj]*v[0,0,ii,jj])
        V.append(-a[0,ii,jj]*v[1,0,ii,jj])
        #second arrow
        X.append(ii*sTM.t11.res)
        Y.append(jj*sTM.t11.res)
        U.append(a[2,ii,jj]*v[0,2,ii,jj])
        V.append(a[2,ii,jj]*v[1,2,ii,jj])
        #symetric arrow
        X.append(ii*sTM.t11.res)
        Y.append(jj*sTM.t11.res)
        U.append(-a[2,ii,jj]*v[0,2,ii,jj])
        V.append(-a[2,ii,jj]*v[1,2,ii,jj])
        
X=np.array(X)
Y=np.array(Y)
U=np.array(U)
V=np.array(V)
        

        
