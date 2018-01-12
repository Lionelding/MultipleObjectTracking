import sys
import numpy as np
from sklearn import mixture
#import itertools
import math
import heapq
import random 

Graph=0
Org=0
extremeClipping=0


if(Graph):
    import matplotlib.pyplot as plt
    import matplotlib.mlab as mlab


modelName="GaussianMixture"
modelComponent=1
initial='kmeans'

#from collections import Counter

sys.path.insert(0, "/home/liqiang/AI_not_smart3/lightnet4/yolo4/src")
#color_iter = itertools.cycle(['navy', 'c', 'cornflowerblue', 'gold', 'darkorange'])

def multiply(a):
    print "Will compute", a, "times", a
    c=a*a
    return c


def showHistogram(inString):
    ## Initialization
    inString=list(inString)
    inString.sort()
    listFloat=inString
    print "\t"+str(listFloat)
    #listFloat=map(float, inString)

    if(Graph and Org):
        fig, (ax00, ax01, ax10, ax11) = plt.subplots(ncols=4, figsize=(8, 4))

        ## ax00: Plot the Histogram    
        ax00.hist(listFloat, bins=len(listFloat),facecolor='b', histtype='bar')
        ax00.set_title("Histogram in x direction")
        ax00.grid(True)

    ## Fit data to the Gaussian Mixture Model

    if(Org):
        meanlist,covarlist=gaussianMixtureModel(listFloat, modelName, modelComponent, initial)


    if(Graph or Org):
        ## ax01: Plot the Normalized Histogram
        #weights=np.ones_like(listFloat)/len(listFloat)
        ax01.hist(listFloat, bins=len(listFloat), normed=1, facecolor='b', histtype='bar')
        ax01.set_title("Normalized Histogram")
        plotGaussian(ax01, len(listFloat), meanlist, covarlist)


    # Perform Maximum Clipping
    listFloat, bigmean=maximumClipping(listFloat, 3);
    if(bigmean==2):
        ##fg is stationary, no need to compute GMM
        print ""
        return 0;

    ## Fit the modified data to Gaussian Mixture Model
    meanlist,covarlist=gaussianMixtureModel(listFloat, modelName, modelComponent, initial)

    if(Graph):
        ## ax10: Plot the Histogram after maximum clipping
        ax10.hist(listFloat, bins=len(listFloat), facecolor='b', histtype='bar')
        ax10.set_title("Maximum Clipping")
        ax10.grid(True)
    
    
        ## ax11: Plot the Normalized Histogram after maximum clipping
        #weights=np.ones_like(listFloat)/len(listFloat)
        n, bins, patches =ax11.hist(listFloat, bins=len(listFloat), normed=1, facecolor='b', histtype='bar')
        ax11.set_title("Normalized & Maximum Clipping")
        plotGaussian(ax11, len(listFloat), meanlist, covarlist)

        ## Show the Graph
        plt.suptitle(str(modelName)+" Model "+" Component Number: "+str(modelComponent))
        plt.show()


    meanValue=findMaxMin(meanlist, bigmean)
    #print meanValue
    print ""
    return meanValue   

def findMaxMin(meanlist, bigmean):

    absmin=10000
    absmax=0
    for x in range(len(meanlist[0])):
        if(abs(meanlist[0][x])>abs(absmax)):
            absmax=meanlist[0][x]
        if(abs(meanlist[0][x])<abs(absmin)):
            absmin=meanlist[0][x]

    if(bigmean):
        return absmax
    return absmin 


def plotGaussian(axx, bins, meanlist, covarlist):

    for i in range(len(meanlist[0])):    
        mu = meanlist[0][i]
        variance = covarlist[0][i]
        sigma = math.sqrt(variance)
        x = np.linspace(mu-7*variance,mu+7*variance, bins)
        p, =axx.plot(x, mlab.normpdf(x, mu, sigma), 'r', alpha=10)
    axx.grid(True)
    axx.legend([p], ["Best Fitting"], fontsize=15, loc=1)
    return 

def maximumClipping(listFloat, diff):

    ## Create the an Hashmap to store the occurance frequency of each key
    dictionary={}
    for i in range(0, len(listFloat)):
        key=listFloat[i]
        if key in dictionary:
            dictionary[key]=dictionary[key]+1
        else:
            dictionary[key]=1


    ## If the maximum value of key AA is larger than key BB by 10 or more, 
    ## then we assign the value of key AA with value in BB + diff (user input)
    ## if extremeClipping, we assign the value of key AA with value of 1
    max3=heapq.nlargest(2, dictionary, key=dictionary.get)
    oldMax0=dictionary[max3[0]]


    ## Case 1 or Case 3: Completely stop or Completely Moving 
    if(oldMax0==len(listFloat)):
        if(max3[0]==0):
            print "\tCompletely Stops"
            return listFloat, 2
        else: 
            print "\tIn Motion"
            return listFloat, 0

    ## Case 4: Foreground stops and background moves
    if((oldMax0*1.0/len(listFloat))>0.7 and max3[0]==0):
        print "\tFg stops and Bg moves"
        return listFloat, 2

    oldMax1=dictionary[max3[1]]
    print "\tLargest Two Elements with Values: "
    print "\t"+str(max3[0])+": "+str(oldMax0)+", "+str(max3[1])+": "+str(oldMax1)


    ## Case 2: Foreground move and background stops
    if (max3[0]==0 and (dictionary[max3[0]]-dictionary[max3[1]])>diff):
        if(extremeClipping):
            dictionary[max3[0]]=1
        else:
            dictionary[max3[0]]=dictionary[max3[1]]+diff
        newMax0=dictionary[max3[0]]
    
        print "\tClipped Largest Two Elements with Values: "
        print "\t"+str(max3[0])+": "+str(newMax0)+", "+str(max3[1])+": "+str(oldMax1)

    else:
        print "\tThe Largest Value is not zero, No need to clip"
        # ii=0
        # while (listFloat[ii]!=0):
        #     ii=ii+1
        # del listFloat[(ii):(3+ii)]  
        return listFloat, 1

    ## Find the starting point of 0
    ii=0
    while (listFloat[ii]!=0):
        ii=ii+1

    del listFloat[(ii+newMax0):(oldMax0+ii)]  
    print "\tFg moves and Bg stops"
    return listFloat, 1

def gaussianMixtureModel(inList, modelName, modelComponent, initial):

    arrayFloat=np.asarray(inList)
    X=arrayFloat.reshape(-1,1)
    meanlist=[]
    covarlist=[]

    ## Uncomment to debug
    if(modelName=="GaussianMixture"):

        # print "Shape of Input: "+str(arrayFloat.shape)
        # print arrayFloat
        gmm = mixture.GaussianMixture(n_components=modelComponent, init_params=initial, covariance_type='full', tol=1e-3, max_iter=50)
        #print gmm

        warning=gmm.fit(X) 

        # print "Means:"
        # print "\t"+str([float(x) for x in gmm.means_])
        # print "Covariance: "
        # print "\t"+str([float(x) for x in gmm.covariances_])
        # print "Converged: "
        # print "\t"+str(gmm.converged_)
        # print "Iterations: "
        # print "\t"+str(gmm.n_iter_)
        # print ""
        temp=gmm

    if(modelName=="BayesianGM"):
        dpgmm1 = mixture.BayesianGaussianMixture(
        n_components=modelComponent, covariance_type='full', weight_concentration_prior=1e-2,
        weight_concentration_prior_type='dirichlet_process',
        mean_precision_prior=1e-2, covariance_prior=1e0 * np.eye(1),
        init_params="random", max_iter=100, random_state=2).fit(X)
        print "Means:"
        print "\t"+str([float(x) for x in dpgmm1.means_])
        print "Covariance: "
        print "\t"+str([float(x) for x in dpgmm1.covariances_])
        print "Converged: "
        print "\t"+str(dpgmm1.converged_)
        print "Iterations: "
        print "\t"+str(dpgmm1.n_iter_)
        print ""
        temp=dpgmm1


    if(modelName=="BayesianGM2"):
        dpgmm2 = mixture.BayesianGaussianMixture(
        n_components=modelComponent, covariance_type='full', weight_concentration_prior=1e+2,
        weight_concentration_prior_type='dirichlet_process',
        mean_precision_prior=1e-2, covariance_prior=1e0 * np.eye(1),
        init_params="kmeans", max_iter=100, random_state=2).fit(X)
        print "Means:"
        print "\t"+str([float(x) for x in dpgmm2.means_])
        print "Covariance: "
        print "\t"+str([float(x) for x in dpgmm2.covariances_])
        print "Converged: "
        print "\t"+str(dpgmm2.converged_)
        print "Iterations: "
        print "\t"+str(dpgmm2.n_iter_)
        print ""
        temp=dpgmm2

    
    meanlist.append([float(x) for x in temp.means_])
    covarlist.append([float(x) for x in temp.covariances_])
    return meanlist, covarlist 

    #return 1

def testGaussianMixture():
    mu, sigma = 0, 0.3 # mean and standard deviation
    s = np.random.normal(mu, sigma, 1000)
    s=s.reshape(-1,1)
    print np.shape(s)

    gmm = mixture.GaussianMixture(n_components=1, covariance_type='full', init_params='random', max_iter=100).fit(s)
    print "Means:"
    print "\t"+str([float(x) for x in gmm.means_])
    print "Covariance: "
    print "\t"+str([float(x) for x in gmm.covariances_])
    print "Converged: "
    print "\t"+str(gmm.converged_)
    print "Iterations: "
    print "\t"+str(gmm.n_iter_)
    print ""

    count, bins, ignored = plt.hist(s, 30, normed=True)
    p1, = plt.plot(bins, 1/(sigma * np.sqrt(2 * np.pi)) *np.exp( - (bins - mu)**2 / (2 * sigma**2) ),linewidth=2, color='r')
    
    mu = gmm.means_[0][0]
    variance = gmm.covariances_[0][0][0]
    sigma = math.sqrt(variance)
    p2, = plt.plot(bins, 1/(sigma * np.sqrt(2 * np.pi)) *np.exp( - (bins - mu)**2 / (2 * sigma**2) ),linewidth=2, color='k')

    # mu = gmm.means_[1][0]
    # print gmm.covariances_
    # variance = gmm.covariances_[1][0][0]
    # sigma = math.sqrt(variance)
    # p2, = plt.plot(bins, 1/(sigma * np.sqrt(2 * np.pi)) *np.exp( - (bins - mu)**2 / (2 * sigma**2) ),linewidth=2, color='k')

    l2 = plt.legend([p1, p2], ["Ground Truth", "Predicted"], fontsize=10, loc=1)
    plt.title('Test of Gaussian Model Fitting with Random Initialization')
    plt.grid(True)
    plt.show()



#o1=(0, 0, 0, 0, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 3)
# t=(0, 0, 0, 3, 4, 4, 3, 4, 0, 0, 0, 0, 0, 0, 4, 3, 4, 4, 6, 6, 5, 6, 2, 0, 0, 0, 1, 3, 4, 4, 5, 6, 6, 6, 4, 5, 6, 0, 0, 0, 3, 4, 4, 5, 7, 7, 4, 2, 6, 6, 7, 4, 0, 4, 5, 2, 6, 7, 7, 7, 7, 0, 0, 8, 7, 0, 1, 4, 3, 2, 1, 8, 8, 8, 9, 8, 1, -3, 0, 0, 0, 0, 0, 4, 7, 7, 8, 8, 9, -1, -3, 0, 0, 0, 0, 0, 0, 8, 8, 8, 8, 8, 7, 4)
# x=(0, 0, 0, 0, 0, 1, 2, 1, 3, 1, 0, 0, 0, 0, 0, 0, 1, 1, 2, 1, 1, 1, 0, 0, 0,0,0,0,0,0,0,0,0,328, 326, 327, 329, 330, 331, 326, 325, 335, 320, 331, 330, 340, 342, 338, 339, 354, 330, 330)
# y=(0, 0, 0, 0, 0, 0 ,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3,3,3,3,3,  3,3,3,3,3,  3,3,3,3,3,3,  3)
# z=(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1)
# zz=(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,1,1)

# s1x=(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)

# s2x=(0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12,12, -1, -1, -1, -1, 0, 0, 0, 12, 12, 10, 10, 11, 12, 13, 13, 13, 14, 14, 12, 12, 11, 0, 0, 0, 1, 1, 1, 2)
# s2y=(0, 0, 0, 8, 9, 8, 8, 0, 0, 0, 9, 10, 8, 0, 0, 0, 0, 0, 0, 0, 0, 7, 7, 6, 6, 9, 9, 9, 10, 8, 8, 0, 0, 0, 10, 8, 0, 0, 0, 10, 0, 1, 1, -1, -1, 2, 2, 0, 0, 1, -2, -2)


# s3x0=(15, 16, 10, 15, 1, 0, 15, 15, -1, -1, -1, -1, 0, 16, 14, 11, 15, 13, 13, 15, 15, 14, 14, 0, 15, 11, 1, 1, 1, 2, 0, 15, 0, 15, 10, 0, 0, 11, 12, 15, 16, 17, 16)
# s3y0=(12, 11, 9, 12, 1, 0, 0, 0, 12, 12, -1, -1, -1, -1, 0, 12, 10, 12, 12, 10, 10, 11, 12, 13, 12, 12, 14, 14, 0, 12, 11, 1, 1, 1, 2, 0, 12, 0, 12, 10, 12, 0, 0, 13)

# s3x1=(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 4, 5, 5, 3, 0, 6, 4, 5, 5, -1, -1, -1, -1, 0, 5, 6, 5, 5, 4, 3, 2, 3, 5, 6, 0, 4, 4, 5, 2, 5, 0, 5, 1, 1, 1, 2, 0, 2, 0, 5, 5, 0, 0, 6, 7, 0, 0, 0, 0, 0, 0, 0, 0)

# s4x=(8, 9, 8, 8, 9, 10, 8, 7, 7, 6, 6, 9, 9, 9, 10, 8, 8, 8, 9, 10, 8, 10, 8,8)
# s4y=(5, 6, 5, 7, 4, 5, 3, 2, 5, 6, 6, 5, 3, 2, 1, 5, 5, 6, 7, 6, 3, 2, 5,5)


# o21=(1,  0,1,0,1,0,1,2)
# o22=(1,1,0,0,1,1,0,2)
# o3=(-1, -1, 0, 0, 1, 1, 1, 1)
# o4=(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1)
#o5=(0, 0, 1, 1, 1, 1, 1, 1)
# o6=(-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 5, 5, 5, 6, 6, 6, 7, 7, 7, 7, 8, 8, 8, 9, 9, 9, 9, 9, 10, 10, 11, 11, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13, 13, 13, 13, 13, 13, 13, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 18, 18, 18, 18, 19, 19)

# [0, -2, -1, -1, 1, 2, 1, 2]
# o7=(1, 0, 1, 0, 1, 1, 0, 2)
#showHistogram(s1x)
#testGaussianMixture()

# plt.hist(s1x, bins=len(s1x),facecolor='b', histtype='bar')
# plt.title("Histogram in y direction")
# plt.grid(True)
# plt.show()