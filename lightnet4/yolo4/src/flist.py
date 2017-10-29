import sys
import numpy as np
from sklearn import mixture
#import itertools
import math
import heapq

Graph=0
Org=0
extremeClipping=0


if(Graph):
    import matplotlib.pyplot as plt
    import matplotlib.mlab as mlab


modelName="GaussianMixture"
modelComponent=3
initial='random'

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
    print listFloat
    #listFloat=map(float, inString)

    if(Graph and Org):
        fig, (ax00, ax01, ax10, ax11) = plt.subplots(ncols=4, figsize=(8, 4))

        ## ax00: Plot the Histogram    
        ax00.hist(listFloat, bins=len(listFloat),facecolor='b', histtype='bar')
        ax00.set_title("Histogram")
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


    ## Perform Maximum Clipping
    listFloat, bigmean=maximumClipping(listFloat, 0);


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
    print meanValue
    return int(round(meanValue))   

def findMaxMin(meanlist, bigmean):

    absmin=0
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
        x = np.linspace(mu-3*variance,mu+3*variance, bins)
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
    ## then we assign the value of key AA with value in BB + 10
    max3=heapq.nlargest(2, dictionary, key=dictionary.get)
    oldMax0=dictionary[max3[0]]


    ## Case 1 or Case 3: Completely stop or Completely Moving 
    if(oldMax0==len(listFloat)):
        if(oldMax0==0):
            print "Completely Stops"
        else: 
            print "In Motion"
        return listFloat, 0

    ## Case 4: Foreground stops and background moves
    if((oldMax0*1.0/len(listFloat))>0.7 and max3[0]==0):
        print "Fg stops and Bg moves"
        return listFloat, 0 

    oldMax1=dictionary[max3[1]]
    print "\nLargest Two Elements with Values: "
    print "\t"+str(max3[0])+": "+str(oldMax0)+", "+str(max3[1])+": "+str(oldMax1)


    ## Case 2: Foreground move and background stops
    if (max3[0]==0 and (dictionary[max3[0]]-dictionary[max3[1]])>diff):
        if(extremeClipping):
            dictionary[max3[0]]=0
        else:
            dictionary[max3[0]]=dictionary[max3[1]]+diff
        newMax0=dictionary[max3[0]]
    
        print "\nClipped Largest Two Elements with Values: "
        print "\t"+str(max3[0])+": "+str(newMax0)+", "+str(max3[1])+": "+str(oldMax1)

    else:
        print "The Largest Value is not zero, No need to clip"
        return listFloat, 1


    ## Find the starting point of 0
    ii=0
    while (listFloat[ii]!=0):
        ii=ii+1

    del listFloat[(ii+newMax0):(oldMax0+ii)]  
    print "Fg moves and Bg stops"
    return listFloat, 1

def gaussianMixtureModel(inList, modelName, modelComponent, initial):

    arrayFloat=np.asarray(inList)
    X=arrayFloat.reshape(-1,1)
    meanlist=[]
    covarlist=[]

    if(modelName=="GaussianMixture"):

        print "Shape of Input: "+str(arrayFloat.shape)
        print arrayFloat
        gmm = mixture.GaussianMixture(n_components=modelComponent, init_params=initial, covariance_type='full', max_iter=50).fit(X)
        
        print "Means:"
        print "\t"+str([float(x) for x in gmm.means_])
        print "Covariance: "
        print "\t"+str([float(x) for x in gmm.covariances_])
        print "Converged: "
        print "\t"+str(gmm.converged_)
        print "Iterations: "
        print "\t"+str(gmm.n_iter_)
        print ""
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


# def calculateDegree(xTuple,yTuple):
#     xComponent=showHistogram(xTuple)
#     yComponent=-(showHistogram(yTuple))


# xString="0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.01 0.01 0.01 0.01 0.01 0.01 0.02 0.02 0.05 0.05 0.08 0.11 0.11 0.13 0.13 0.14 0.15 0.17 0.17 0.17 0.18 0.18 0.21 0.21 0.21 0.21 0.21 0.21 0.23 0.23 0.23 0.23 0.23 0.23 0.23 0.23 0.24 0.24 0.24 0.24 0.24 0.24 0.25 2.20 2.21 2.22 2.22 2.22 2.23 2.23 2.23 2.24 2.24 2.24 2.24 2.24 3.17 3.18 3.19 3.19 3.19 4.13 4.13 4.23 5.10 5.21 7.15 8.19 9.06 9.06 10.21 11.05 11.05 11.15 11.15 12.09 12.13 14.04 15.07 15.11 15.14 17.16 18.06 18.15 19.14 21.10 21.16 23.09 23.15 24.12 24.12 26.02 26.04 26.06 26.08 26.17 28.12 29.08 30.05 30.11 30.11 33.03 36.05 37.11 45.01 45.07 48.10 48.13 50.07 51.06 60.08 63.02 63.06 63.06 68.10 71.03 71.06 71.09 81.07 90.01 90.03 90.03 90.04 98.08 105.12 135.07 144.05 150.05 161.11 162.09 171.06 180.01 198.09 215.08 215.08 225.01 225.01 225.01 225.01 225.01 225.01 229.17 231.06 231.06 243.02 245.12 251.03 251.03 251.03 270.01 270.01 270.01 270.02 270.02 285.04 292.10 315.04 334.02 334.04 339.05 339.13 340.08 340.17 342.03 342.12 344.10 344.17 346.04 348.13 348.13 349.05 349.05 349.05 350.11 350.16 351.18 352.07 352.13 353.08 353.16 354.09 355.10 355.10 355.21 355.21 356.12 356.12 356.24 356.24 356.24 357.15 357.16 358.23 358.24 358.24 358.24 358.24 358.24"
# yString="-12.00 -11.00 -10.00 -10.00 -10.00 -9.00 -8.00 -8.00 -8.00 -8.00 -8.00 -8.00 -7.00 -7.00 -7.00 -7.00 -6.00 -6.00 -6.00 -6.00 -6.00 -6.00 -5.00 -5.00 -5.00 -5.00 -5.00 -4.00 -4.00 -4.00 -4.00 -4.00 -4.00 -3.00 -3.00 -3.00 -3.00 -3.00 -3.00 -3.00 -3.00 -3.00 -3.00 -3.00 -3.00 -3.00 -3.00 -2.00 -2.00 -2.00 -2.00 -2.00 -2.00 -2.00 -2.00 -2.00 -2.00 -2.00 -2.00 -2.00 -2.00 -2.00 -2.00 -2.00 -2.00 -2.00 -2.00 -2.00 -2.00 -2.00 -2.00 -1.00 -1.00 -1.00 -1.00 -1.00 -1.00 -1.00 -1.00 -1.00 -1.00 -1.00 -1.00 -1.00 -1.00 -1.00 -1.00 -1.00 -1.00 -1.00 -1.00 -1.00 -1.00 -1.00 -1.00 -1.00 -1.00 -1.00 -1.00 -1.00 -1.00 -1.00 -1.00 -1.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 2.00 2.00 2.00 2.00 2.00 2.00 2.00 2.00 3.00 3.00 3.00 3.00 3.00 4.00 5.00 7.00"
# zString="1.00 2.00 3.00 2.00 3.00 3.00 4.00 5.00 4.00"
# zzString="1 2 3 2 3 3 4 5 4"
# o1=(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1)
# t=(0, 0, 0, 3, 4, 4, 3, 4, 0, 0, 0, 0, 0, 0, 4, 3, 4, 4, 6, 6, 5, 6, 2, 0, 0, 0, 1, 3, 4, 4, 5, 6, 6, 6, 4, 5, 6, 0, 0, 0, 3, 4, 4, 5, 7, 7, 4, 2, 6, 6, 7, 4, 0, 4, 5, 2, 6, 7, 7, 7, 7, 0, 0, 8, 7, 0, 1, 4, 3, 2, 1, 8, 8, 8, 9, 8, 1, -3, 0, 0, 0, 0, 0, 4, 7, 7, 8, 8, 9, -1, -3, 0, 0, 0, 0, 0, 0, 8, 8, 8, 8, 8, 7, 4)
# x=(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4)
# y=(0, 0, 0, 0, 0, 0 ,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3,3,3,3,3,  3,3,3,3,3,  3,3,3,3,3,3,  3)
# z=(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1)
# zz=(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,1,1)
# o2=(0, 0, 0, 1, 1, 1, 1, 2)
# o3=(-1, -1, 0, 0, 1, 1, 1, 1)
# showHistogram(o3)
#testGaussianMixture()
