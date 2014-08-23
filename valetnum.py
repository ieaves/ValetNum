#Although this is clearly a sub-optimal solution the basic idea is to follow a greedy strategy.
#Cars will be picked up at the specified times and always returned to the closest garage.
#The solver then iterates forward in time through subsequent 'events' (someone either needing 
#their car picked up or returned). A single valet is assigned to pick up the first car at the first 
#event. At each following event the solver attempts to minimize the amount of time a valet spends idle
#by finding the valet with the most free time who is able to accomplish the event (whether its picking
#up or dropping off) and assigning them to that task. If no valets are able to do so a new valet is added.

import numpy
import random
import operator

def distance(xo,yo,xi,yi):
	return ((xo-xi)**(2.0)+(yo-yi)**(2.0))**(.5)

def min_time_index(valets,tn):
	#-1 weirdness basically guarantees I'll find the smallest positive number when calling the
	#min function. If the output of min is positive then the difference was negative and none
	#of the valets are actually in range.
	amin_time=-1*(valets[0][2]-tn[0])
	min_time=amin_time
	mindex=0
	for j in range(len(valets)):
		min_time=-1*(valets[j][2]-tn[j])
		if min_time < amin_time:
			amin_time=min_time
			mindex=j
			
	return [mindex, amin_time]
	
nclients=10000
ngarages=10
vw=6.0
vc=30.0

tarr=[]
tleave=[]
tinitloc=numpy.zeros((nclients,2))
garages=numpy.zeros((ngarages,2))

tlist=numpy.zeros((2*nclients,6))

#SF is ~121 km^2 so lets make a box that is 11km by 11km (in meters) and place our garages
#and client initial locations randomly.
dx=11*1000
dy=dx

for i in range(ngarages):
	garages[i,0]=random.uniform(0,dx)
	garages[i,1]=random.uniform(0,dy)
	
for i in range(nclients):
	tarr.append(random.uniform(0,24*60**2))
	tleave.append(random.uniform(tarr[i],24*60**2))
	tinitloc[i,0]=random.uniform(0,dx)
	tinitloc[i,1]=random.uniform(0,dy)

#tlist=[event time,pickup/dropoff tag, closest garage [x,y] coord, distance to garage, client number]
tlist[0:(nclients),0]=tarr
tlist[(nclients):,0]=tleave
tlist[(nclients):,1]=tlist[(nclients):,1]+1
tlist[0:nclients,5]=range(nclients)
tlist[nclients:,5]=tlist[0:nclients,5]

#find the closest garage to each starting person. First pass we will send all cars there
#this is NOT optimal but a reasonable starting place
dists=numpy.zeros(ngarages)

for i in range(nclients):
	for j in range(ngarages):
		dists[j]=distance(garages[j,0],garages[j,1],tinitloc[i,0],tinitloc[i,1])
	min_index, min_dist = min(enumerate(dists), key=operator.itemgetter(1))
	tlist[i,2]=garages[min_index,0]
	tlist[i,3]=garages[min_index,1]
	tlist[i,4]=min_dist
	tlist[i+nclients,2:5]=tlist[i,2:5]

#sort the tlist in order of event occurrences
t=numpy.argsort(tlist[:,0])
stlist=tlist[t,:]

#list valet travel time as negative (traveling to garage) and starting location at closest garage
valets=[]
#valets tracks the valets last position and elapsed time since arriving there (in other words
#that would be how long they've been waiting at the garage)
valets.append([stlist[0,2],stlist[0,3],-stlist[0,4]/vc])

#iterate over the sorted tlist of events
for i in range(1,2*nclients-1):
	dt=stlist[i,0]-stlist[i-1,0]	#elapsed time since last event
	for j in range(len(valets)):
		valets[j][2]=valets[j][2]+dt	#updates the time valets have been waiting

	tn=numpy.zeros((len(valets),1))
	
	#Handles the logic for pickups and drop offs separately. 
	if stlist[i][1] == 0:	#pickup
		for j in range(len(valets)):
			#time for valet to go from his current location to the pickup location
			tn[j]=distance(valets[j][0],valets[j][1],tinitloc[stlist[i,5],0],tinitloc[stlist[i,5],1])/vw
		
		#since the valet is picking up their last position will be at the closest nearby garage
		#and it will cost them the driving time to get there (hence the negative time)
		mindex, min_time=min_time_index(valets,tn)
		if min_time > 0:
			valets.append([stlist[i,2],stlist[i,3],-stlist[i,4]/vc])
		else:
			valets[mindex][:]=[stlist[i,2],stlist[i,3],-stlist[i,4]/vc]
	else:	#dropoff
		for j in range(len(valets)):
			#time for valet to go from his current location to the garage with the clients car
			#and time to drive the car to the person
			tn[j]=distance(valets[j][0],valets[j][1],stlist[i,2],stlist[i,3])/vw + stlist[i,4]/vc

		#since the valet is dropping off their last position will be at the clients pick up point
		#and their idle time will be set to zero
		mindex, min_time=min_time_index(valets,tn)
		if min_time > 0:
			valets.append([tinitloc[stlist[i,5],0],tinitloc[stlist[i,5],1],0])
		else:
			valets[mindex][:]=[tinitloc[stlist[i,5],0],tinitloc[stlist[i,5],1],0]
		
print len(valets)