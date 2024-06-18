from serial import *
import struct
from math import *
import pygame
import keyboard


#serial write function
def swrite(s,number):
    number=struct.pack('B',number)
    s.write(number)

#convert 3d to 2d with the bryce secret equation
def convert(info,theta,obsx,obsy,obsz):
    dd=10**-200
    tot=tan(theta)
    proj=[]
    for i in range(len(info)):
        proj.append([0,0])
    for i in range(len(info)):
        use=info[i]
        
        #y
        dxz=((obsx-use[0])**2+(obsz-use[2])**2)**.5
        yp=(use[1]-obsy)/(2*(dxz+dd))*tot+.5
        proj[i][1]=yp

        #x
        dyz=((obsy-use[1])**2+(obsz-use[2])**2)**.5
        xp=(use[0]-obsx)/(2*dyz+dd)*tot+.5
        proj[i][0]=xp
        
    return proj


#setup serial on USB-C port COM3
s = Serial("COM3",baudrate=9600,bytesize=8)

print("starting")

#send 244 to start
swrite(s,244)


cont1=1
data=[]


first=1
while cont1==1:
    
    

    #receive data
    a=[]
    res=int(str(s.read().hex()),16)
    a.append(res*2*pi/200) #got theta out of 200

    #receive data
    res=int(str(s.read().hex()),16)
    a.append(res*4) #got vertical out of 34. should be close to 15 cm with 4mm leead

    #receive data
    res=int(str(s.read().hex()),16)
    distance=75-(14650*(res)**-1.396)  #in mm
    a.append(distance)

    #this is to stop the scanning process
    if floor(a[0])==8:
        if a[1]==1020:
            if floor(a[2])==68:
                cont1=0

    #this is to record the data to a tuple          
    if len(a)==3:
        if first==0:
            if cont1==1:
                if a[2]>0:
                    data.append(a)
        time.sleep(.005)
        print(100*a[0]/(2*pi),"percent done")
        swrite(s,245)

    #this never happens
    if len(a)!=3:
        print("Error. didnt get 3")

    first=0
    
#prints out all 3d coordinates
print(data)

#put the information in the correct indices for easy use later
cylindrical=[]
for i in range(len(data)):
    a=data[i]
    cylindrical.append([a[2],a[0],-a[1]])

#convert cylindrical to cartesian coordinates
coords=[]
for i in range(len(cylindrical)):
        r=cylindrical[i][0]
        angle=cylindrical[i][1]
        z=cylindrical[i][2]
        x=r*cos(angle)
        y=r*sin(angle)
        coords.append([x,z,y])


#open a text file
f = open("x-y-z.txt", "a")
f.truncate

#write to the text file
for i in range(len(coords)):
    use=coords[i]
    a=use[0]
    b=use[1]
    c=use[2]
    string=str(a)+" "+str(-b)+" "+str(c)+"\n"
    f.writelines(string)

f.close()
#close the text file

#create canvas to plot points onto
screenwidth=3200/2 #put your screenwidth and then divide by half
screenheight=1800/2

#start the pygame canvas
pygame.init()
screen = pygame.display.set_mode((screenwidth, screenheight))
#put a name on the window
pygame.display.set_caption("3d scanner")


ox,oy,oz=0,0,-200 #initial observer coordinates
obspeed = .5 #observer speed
t=0
text=0
string=""


flip=1
spinspeed=.0005
go=True
while go:

    #this is to make it able to close the pygame window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #press q to quit the window and program
    if keyboard.is_pressed('q'):
        go=0
            
    #convert cylindrical to cartesian coords
    coords=[]
    for i in range(len(cylindrical)):
        r=cylindrical[i][0]
        angle=cylindrical[i][1]+t #spin the object around
        z=cylindrical[i][2]
        x=r*cos(angle)
        y=r*sin(angle)

        #able to flip axes with keyboard later
        if flip==1:
            coords.append([x,z,y])
        if flip==2:
            coords.append([x,y,z])

    #rotate the object around
    t+=spinspeed
    if t>=360:
        t=0

    #the arrow keys and "w" and "s" will move the observer around in all 3 axes
    if keyboard.is_pressed('up arrow'):
        oy-=obspeed
    if keyboard.is_pressed('down arrow'):
        oy+=obspeed
    if keyboard.is_pressed('right arrow'):
        ox+=obspeed
    if keyboard.is_pressed('left arrow'):
        ox-=obspeed
    if keyboard.is_pressed('w'):
        oz+=obspeed
    if keyboard.is_pressed('s'):
        oz-=obspeed

    #keyboard presses of "a" and "d" will change the rotate speed
    if keyboard.is_pressed('a'):
        spinspeed-=.001
    if keyboard.is_pressed('d'):
        spinspeed+=.001

    #keyboard presses of "u" and "i" will flip the model over to switch between axes
    if keyboard.is_pressed('u'):
        flip=1
    if keyboard.is_pressed('i'):
        flip=2

    #convert 3d to 2d
    proj=convert(coords,20,ox,oy,oz)

    #make a black background
    screen.fill((0,0,0))

    #plot all the points according to the converted list of points
    for i in range(len(proj)):
        x,y=screenwidth*proj[i][0],screenheight*proj[i][1] #scale up to size of screen
        pygame.draw.circle(screen, (200,0,255), (x,y), 5) #draw particles

    pygame.display.flip()

pygame.quit()


s











