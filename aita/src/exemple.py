'''
Exemple of script
'''

def example():
	'''	
	>>> # load aita function
	>>> import aita
	>>> # load image2d function used to manipulate 2D image
	>>> import image2d as im
	>>> # load matplotlib for plot
	>>> import matplotlib.pylab as plt
	>>> # load pickle to save data
	>>> import pickle
	>>> # load loadData_aita where different function to create aita object are available
	>>> import loadData_aita as lda
	
	>>> ####################################################################
	>>> ############################### Help ###############################
	>>> ####################################################################
	>>> help(aita)
	
	>>> ####################################################################
	>>> ############## open the data from G50 analyseur#####################
	>>> ####################################################################
	>>> # the inputs come from G50 analyseur
	>>> adr_data='orientation_test.dat'
	>>> adr_micro='micro_test.bmp'
	>>> # create data where all the data are include
	>>> data=lda.aita5col(adr_data,adr_micro)
		
	>>> ####################################################################
	>>> ####Correct the analysis position with the experiment position######
	>>> ####################################################################
	>>> # select a restricted area
	>>> data.crop()
	>>> # rotate of 180 degree the data
	>>> #data.rot180()
	>>> # Horizontal mirror on the data
	>>> #data.fliplr()
	>>> # remove data with quality under 75
	>>> data.filter(75)
	>>> # As creating this object can be time consuming you prefer reload it. So this is a way to save data
	>>> #pickle.dump(data, open('data_py.G50',"wb"))
	>>> # And to load the data
	>>> #data = pickle.load( open( "data_py.G50", "rb"))
		
	
	>>> # we can know visualized the phi1 value
	>>> data.phi1.plot()
	>>> plt.show()
		
	>>> # or grains
	>>> data.grains.plot()
	>>> plt.show()
		
	>>> # colormap
	>>> data.plot()
	>>> plt.show()
		
	>>> # plot pole figure with eigen -vectors and -values of the second order orientation tensor
	>>> data.plotpdf(peigen=True)
	>>> plt.show()
	'''
	
	
	# load aita function
	import aita
	# load image2d function used to manipulate 2D image
	import image2d as im
	# load matplotlib for plot
	import matplotlib.pylab as plt
	# load pickle to save data
	import pickle
	# load loadData_aita where different function to create aita object are available
	import loadData_aita as lda
	
	####################################################################
	############################### Help ###############################
	####################################################################
	help(aita)
	
	####################################################################
	############## open the data from G50 analyseur#####################
	####################################################################
	# the inputs come from G50 analyseur
	adr_data='orientation_test.dat'
	adr_micro='micro_test.bmp'
	# create data where all the data are include
	data=lda.aita5col(adr_data,adr_micro)
		
	####################################################################
	####Correct the analysis position with the experiment position######
	####################################################################
	# select a restricted area
	data.crop()
	# rotate of 180 degree the data
	#data.rot180()
	# Horizontal mirror on the data
	#data.fliplr()
	# remove data with quality under 75
	data.filter(75)
	# As creating this object can be time consuming you prefer reload it. So this is a way to save data
	#pickle.dump(data, open('data_py.G50',"wb"))
	# And to load the data
	#data = pickle.load( open( "data_py.G50", "rb"))
		
	
	# we can know visualized the phi1 value
	data.phi1.plot()
	plt.show()
		
	# or grains
	data.grains.plot()
	plt.show()
		
	# colormap
	data.plot()
	plt.show()
		
	# plot pole figure with eigen -vectors and -values of the second order orientation tensor
	data.plotpdf(peigen=True)
	plt.show()
