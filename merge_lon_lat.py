import csv 
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.basemap import Basemap

def plot_density_2D(ax, x1 ,x2, kernel, label):
# draw the estimated pdf 

    # Define the borders
    deltaX1 = (max(x1) - min(x1))/10
    deltaX2 = (max(x2) - min(x2))/10
    x1min = min(x1) - deltaX1
    x1max = max(x1) + deltaX1
    x2min = min(x2) - deltaX2
    x2max = max(x2) + deltaX2

    # Pour que toutes les courbes utilisent le meme range
    x1min = -10
    x1max = 50
    x2min = 30
    x2max = 70
    
    # Create meshgrid
    #print(x1min, x1max, x2min, x2max)
    xx1, xx2 = np.mgrid[x1min:x1max:100j, x2min:x2max:100j]

    positions = np.vstack([xx1.ravel(), xx2.ravel()])
    f = np.reshape(kernel(positions).T, xx1.shape)

    ax.set_xlim(x1min, x1max)
    ax.set_ylim(x2min, x2max)
    
    cfset = ax.contourf(xx1, xx2, f, cmap='Spectral')
    ax.imshow(np.rot90(f), cmap='Spectral', extent=[x1min, x1max, x2min, x2max])
    cset = ax.contour(xx1, xx2, f, colors='k')
    ax.clabel(cset, inline=1, fontsize=10)
    ax.set_xlabel('lon')
    ax.set_ylabel('lat')
    ax.set_title(label)

    return xx1,xx2,f


def inventors_map(ax, lons, lats, kernel, label):
# Position des inventeurs => on place la valeur de la densite (kernel)
    
#https://pythonprogramming.net/plotting-maps-python-basemap/
    map = Basemap(projection='mill',
                llcrnrlat=20,urcrnrlat=70,
                llcrnrlon=-15,urcrnrlon=70,
                  resolution='c',
                  ax=ax)

    # draw coastlines, country boundaries, fill continents.
    map.drawcoastlines(linewidth=0.25)
    map.drawcountries(linewidth=0.25)
    map.fillcontinents(color='coral',lake_color='aqua')
    # draw the edge of the map projection region (the projection limb)
    map.drawmapboundary(fill_color='aqua')

    print(len(lons))
    positions = np.vstack([lons, lats])
    crowd = kernel(positions)
    print(crowd)
    #https://stackoverflow.com/questions/47039465/setting-marker-size-to-data-in-basemap-python-3
    
    xpt,ypt = map(lons,lats) # convert (long-lat) degrees to map coords
    for x1, y1, c in zip(xpt, ypt, crowd):
        # markersize is scale down by /10
        # need alpha<1 to get some transparency
        # red color is more appropriate
        map.plot(x1, y1, 'ro', markersize=c*500, alpha=0.4)
            
    lon, lat = 7.4, 43.36 # Location of I3S
    xpt,ypt = map(lon,lat)
    map.plot(xpt, ypt, 'gs')

    ax.set_title(label)

    
def plot_density_3D(ax, xx1, xx2, f):
    surf = ax.plot_surface(xx1, xx2,
                           f,
                           rstride=1, cstride=1,
                           cmap='Spectral', edgecolor='none')
    ax.set_xlabel('x1')
    ax.set_ylabel('x2')
    ax.set_zlabel('PDF')
    ax.set_title('Surface plot of Gaussian 2D KDE')
    fig.colorbar(surf, shrink=0.5, aspect=5) # add color bar indicating the PDF
    #    ax.view_init(60, 35)


# On recupere un dico de long/lat sur la cle qui est les NUTS
def getdict_nuts_long_lat(filename = 'eudata.csv'):
    d = {}
    with open(filename) as f:
        r = csv.reader(f)
        for row in r:
            #print(row)
            key = row[1]
            d[key] = [row[5],row[6]] # lon, lat

    #    print (d)
    return d

# On ajoute dans le fichier de brevets les long/lat 
def decorate_patents(filename, d):    
    with open(filename) as f:
        r = csv.reader(f,delimiter=':')
    
        with open(filename+".ll", 'w') as g:
            s = csv.writer(g, delimiter=':')
            for row in r:
                #print(row)
                extrow = row + d[row[1]]
                #print (extrow)
                s.writerow(extrow)



#=============================================================

if __name__ == "__main__":       

    d =  getdict_nuts_long_lat()

    fns = ['data1990-2000.txt',
           'data2001-2010.txt',           
           'data2011-2020.txt']

    #    fig = plt.figure(figsize=(13,13))
    fig, axs = plt.subplots(2,2)
    fig1, axs1 = plt.subplots(2,2)

    #    fig.suptitle('Vertically stacked subplots')

    for i,filename in enumerate(fns) :   
        print ("Processing file : {}".format(filename))

        # association NUTS <=> latitude/longitude
        decorate_patents(filename,d)    
        X = np.genfromtxt(filename+".ll",delimiter=':')
        # Extract
        x1 = X[:, 2] # lon
        x2 = X[:, 3] # lat

        # Fabrique de la fonction de densite
        values = np.vstack([x1, x2])
        kernel = st.gaussian_kde(values)

        # Affichage
        ax = axs[i//2, i%2]
        xx1,xx2,f = plot_density_2D(ax, x1, x2, kernel, label=filename)

        ax = axs1[i//2, i%2]
        inventors_map(ax, x1, x2, kernel, label=filename) # lons, lats        

        #fig = plt.figure(figsize=(13, 10))
        #ax = plt.axes(projection='3d')
        #plot_density_3D(ax,xx1,xx2,f)

    plt.show()
