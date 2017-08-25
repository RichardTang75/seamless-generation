#Written by Richard Tang, 15-112
#mouse motion off of 15-112 tkinter demos
#http://www.cs.cmu.edu/~112/notes/notes-tkinter-demos.html
#Initial idea of placing numbers and growing numbers comes from 
#http://www.pixelenvy.ca/wa/river.html
#Pathfinding based on A* 15-112 lecture I attended as well as 
#https://www.raywenderlich.com/4946/introduction-to-a-pathfinding
#RGB String taken from 15-112
#http://www.cs.cmu.edu/~112/notes/notes-graphics.html
#RGB String and the mouse motion template are the parts I have not written.
#This is incredibly slow to start. Please wait until the output reads 9.
#Fun fact: The title image was an early attempt at map generation, which
#failed due to extending in a downwards diagonal fashion. Looks hella cool tho.
from tkinter import *
import PIL.Image
import PIL.ImageTk
import random
import heapq
#fun functions
#########
def boutSame(uno,dos):
    acceptable=10**-5
    return (abs(uno-dos)<acceptable)
def distance(x1,y1,x2,y2):
    return ((x1-x2)**2+(y1-y2)**2)**.5
def rgbString(red, green, blue): 
    return "#%02x%02x%02x" % (red, green, blue)
#Debugging purposes only
######
def display(board):
    global count
    count+=1
    im=PIL.Image.new('L',(len(board[0]),len(board)))
    for row in range(len(board)):
        for col in range(len(board[0])):
            color=int((128*(board[row][col])))
            im.putpixel((col,row),color)
    im.save('%d.gif'%(count))
##############
#FUN GLOBALS
stored=dict()
#Will replace gBoard when I finish
#Also replace created
boards=dict()
thick=24
width=512
height=512
player=1
gBoard=[]
gSize=5
#####REMOVE DESE YO
viewBoard=(0,0)
kills=1
numBoss=1
#note to self, x is columns aka board[0] whereas y is rows
#Directions are in relation to wantX,wantY
def generate(data):
    if (data.currentX,data.currentY) not in data.visitedMaps:
        uno,dos=data.currentX,data.currentY
        for choice in [(-1,-1),(-1,1),(1,1),(1,-1)]:
        # for choice in [(-1,-1),(-1,1)]:
            dx,dy=choice
            #want deals with if already created,also already deals with diags
            wantedX,wantedY=uno+dx,dos+dy
            want(uno,dos,wantedX,wantedY)
        data.visitedMaps.add((data.currentX,data.currentY))
    pass
def want(fromX,fromY,wantX,wantY):
    #NESW,0-3
    directions=[None,None,None,None]
    if (wantX,wantY) not in boards:
        #these xs and ys are in relation to origin, not graphical x,y
        sides=[(wantX+1,wantY,'West'),(wantX-1,wantY,'East'),
        (wantX,wantY-1,'North'),(wantX,wantY+1,'South')]
        if abs(fromX-wantX)==1 and abs(fromY-wantY)==1:
            want(fromX,fromY,wantX,fromY)
            want(fromX,fromY,fromX,wantY)
        for take in sides:
            existX,existY,direct=take
            if (existX,existY,direct) in stored:
                #Feed it in right, the directions were in relation to want
                if direct=='North':
                    directions[2]=stored[existX,existY,direct]
                elif direct=='East':
                    directions[3]=stored[existX,existY,direct]
                elif direct=='South':
                    directions[0]=stored[existX,existY,direct]
                elif direct=='West':
                    directions[1]=stored[existX,existY,direct]
        drawGrassland(wantX,wantY,directions[0],directions[1],directions[2],
                        directions[3])
        print(len(boards))
def makeTerrain(width,height):
    final=[]
    for x in range(height):
        final+=[[0]*width]
    return final
def putTerrain(board,percentage=.0001):
    for y in range(len(board)):
        for x in range(len(board[0])):
            if (random.random()<percentage):
                board[x][y]=1+(random.randint(0,1)+random.randint(0,1))
#global tgt should have wraparound
#tgt1 has wraparound, tgt does not
#To reiterate, 1 is wraparound, 2 is bounds
def tgt1(tgtY,tgtX,value,board):
    if (tgtY)<0: tgtY=len(board)-1
    elif (tgtY)>=len(board):tgtY=0
    if (tgtX)<0: tgtX=len(board)-1
    elif (tgtX)>=len(board):tgtX=0
    return tgtY,tgtX
#USE 2 FOR SEAMLESS
#Gotta fix tgtX before putting into list
#Creates the directions in relation to the board being processed
def tgt2(tgtY,tgtX,value,board,putX=None,putY=None):
    newX,newY=tgtX,tgtY
    if (tgtY)<0: 
        newY=0
        #Needed in case tgtX is out of bounds,bounded X is okay for this
        if (tgtX)<0: newX=0
        elif (tgtX)>=len(board[0]):newX=len(board[0])-1
        if putX != None and putY != None:
            if (putX,putY,'North') not in stored:
                stored[(putX,putY,'North')]=makeTerrain(512,thick)
            stored[(putX,putY,'North')][thick-1][newX]=value
    ####DONESO 4 NOW
    elif (tgtY)>=len(board):
        newY=len(board)-1
        if (tgtX)<0: newX=0
        elif (tgtX)>=len(board[0]):newX=len(board[0])-1
        if putX != None and putY != None:
            if (putX,putY,'South') not in stored:
                stored[(putX,putY,'South')]=makeTerrain(512,thick)
            stored[(putX,putY,'South')][0][newX]=value
    if (tgtX)<0: 
        newX=0
        if putX != None and putY != None:
            if (putX,putY,'West') not in stored:
                stored[(putX,putY,'West')]=makeTerrain(thick,512)
            stored[(putX,putY,'West')][newY][thick-1]=value
    elif (tgtX)>=len(board[0]):
        newX=len(board[0])-1
        if putX != None and putY != None:
            if (putX,putY,'East') not in stored:
                stored[(putX,putY,'East')]=makeTerrain(thick,512)
            stored[(putX,putY,'East')][newY][0]=value
    return newY,newX
def snaking(board,per=.2,mode=2,putX=None,putY=None):
    visited=set()
    for y in range(len(board)):
        for x in range(len(board[0])):
            if (board[y][x] != 0 and (x,y) not in visited):
                tgtY,tgtX=y,x
                for times in range(random.randint(2,5)):
                    dx,dy=random.choice([(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),
                                            (1,-1),(1,0),(1,1)])
                    for tLen in range(random.randint(5,40)):
                        tgtY+=dy
                        tgtX+=dx
                        if mode==1:
                            tgtY,tgtX=tgt1(tgtY,tgtX,board[y][x],board)
                        else:
                            tgtY,tgtX=tgt2(tgtY,tgtX,board[y][x],
                                            board,putX,putY)
                        visited.add((tgtX,tgtY))
                        change=random.random()*per-per/2
                        board[tgtY][tgtX]=board[y][x]+(change)                                    
def randTerrain(board,visited2,per=.2,mode=2,putX=None,putY=None):
    visited=set()
    per=per
    for y in range(len(board)):
        for x in range(len(board[0])): 
            #visited hits each pixel only once
            if (board[y][x] != 0 and (x,y) not in visited and 
                (x,y) not in visited2):
                visited2.add((x,y))
                for dy in range(-1,2):
                    for dx in range(-1,2):
                        tgtY,tgtX=y+dy,x+dx
                        if mode==1:
                            tgtY,tgtX=tgt1(tgtY,tgtX,board[y][x],board)
                        else:
                            tgtY,tgtX=tgt2(tgtY,tgtX,board[y][x],board,
                                    putX,putY)
                        if (random.random()<.25 and 
                            ((tgtX,tgtY)) not in visited):
                            #so you can't extend on an added piece
                            visited.add((tgtX,tgtY))
                            if board[y][x]<2.9:
                                change=random.random()*per-per/2
                            else:
                                change=random.random()*per-per/1.5
                            board[tgtY][tgtX]=board[y][x]+(change)    
def fillTerrain(board,visited2,water=True,per=.2,putX=None,putY=None):
    def fillTerrain80(board,y,x,per):
        nonlocal visited
        nonlocal putX,putY
        for z in range(random.randint(2,4)):
            dx,dy=random.choice([(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),
                                (1,0),(1,1)])
            #if (x+dx,y+dy) not in visited:
            tgtY,tgtX=y+dy,x+dx
            visited.add((tgtX,tgtY))
            tgtY,tgtX=tgt2(tgtY,tgtX,board[y][x],board,putX,putY)
            if board[y][x]<2.9:
                change=random.random()*per-per/2
            else:
                change=random.random()*per-per/1.5
            board[tgtY][tgtX]=board[y][x]+(change)
    def fullFillTerrain80(board,y,x,per):
        nonlocal visited
        nonlocal putX,putY
        for dy in range(-1,2):
            for dx in range(-1,2):
                tgtY,tgtX=y+dy,x+dx
                visited.add((tgtX,tgtY))
                tgtY,tgtX=tgt2(tgtY,tgtX,board[y][x],board,putX,putY)
                change=random.random()*per-per/1.5
                board[tgtY][tgtX]=board[y][x]+(change)
    visited=set()
    per=per
    for y in range(len(board)):
        for x in range(len(board[0])):
            #visited hits each pixel only once
            if (board[y][x] != 0 and (x,y) not in visited and 
            (x,y) not in visited2):
                if board[y][x]<1.2 and water==True:
                    fullFillTerrain80(board,y,x,per)
                fillTerrain80(board,y,x,per)
                visited2.add((x,y))
def makeBigMap(width=512,height=512,countries=5):
    width,height=width,height
    minD=200
    liquid=set()
    positions=[]
    countries=countries
    def putCountries(board):
        nonlocal minD
        nonlocal positions
        positions.append((random.randint(10,width),random.randint(10,height)))
        #first one was appended before loop, so countries-1
        for country in range(countries-1): 
            good=False
            while good==False:
                x,y=random.randint(10,width),random.randint(10,height)
                good=True
                for position in positions:
                    if distance(x,y,*position)<minD:
                        good=False
                if good==True:
                    positions+=[(x,y)]
        print (positions)
        for position in positions:
            sX,sY=position
            board[sY][sX]=(positions.index(position)+1)
    #modFullFill seemed to be easier than applying fullfill to polity
    def modFullFill(board):
        visited=set()
        for y in range(len(board)):
            for x in range(len(board[0])):
                if (board[y][x] != 0 and (x,y) not in visited and 
                (x,y) not in visited2):
                    for dy in range(-1,2):
                        for dx in range(-1,2):
                            tgtY,tgtX=y+dy,x+dx
                            if (tgtX,tgtY) not in liquid:
                                visited.add((tgtX,tgtY))
                                tgtY,tgtX=tgt1(tgtY,tgtX,board[y][x],board)
                                board[tgtY][tgtX]=board[y][x]
    polities,big=makeTerrain(width,height),makeTerrain(width,height)
    putTerrain(big,.005)
    putCountries(polities)
    for p in range(3):
        snaking(polities,0)
    visited2=set()
    for n in range(30):
        randTerrain(polities,visited2,0,1)
    visited2=set()
    for m in range(10):
        modFullFill(polities)
        visited=set()
    visited2=set()
    #Make big map tend to put liquid in middle, ice on top and bottom
    return big,polities
#ligate
#Attach East and West first, then North and South
#Reversals are less intensive than repeated inserts
def ligate(board,N,E,S,W):
    E=E[thick:512-thick]
    W=W[thick:512-thick]
    for row in range(len(board)):
        board[row]=board[row][::-1]
        board[row].extend(W[row])
        board[row]=board[row][::-1]
        board[row].extend(E[row])
    board=board[::-1]
    board.extend(N)
    board=board[::-1]
    board.extend(S)
    return board
def makeBoard(width,height,N,E,S,W,coordX,coordY):
    width,height=width,height
    No,Ea,So,We=N,E,S,W
    if N==None:
        No=makeTerrain(512,thick)
    if E==None:
        Ea=makeTerrain(thick,512)
    if S==None:
        So=makeTerrain(512,thick)
    if W==None:
        We=makeTerrain(thick,512)
    visited2=set()
    ####100% DONE
    #creates nextmaps
    #backdrop
    board=makeTerrain(width,height)
    #base should always be 512,512
    base=makeTerrain(512,512)
    putTerrain(base,.005)
    for rB in range(8):
        randTerrain(base,visited2)
    visited2=set()
    fillTerrain(base,visited2,False)
    visited2=set()
    ###start of board
    putTerrain(board)
    snaking(board,.2,2,coordX,coordY)
    if (width,height)==(512-2*thick,512-2*thick):
        board=ligate(board,No,Ea,So,We)
    print(len(board),len(board[0]))
    for r in range(30):
        randTerrain(board,visited2,.2,2,coordX,coordY)
    visited2=set()
    for f in range(4):
        fillTerrain(board,visited2,True,.2,coordX,coordY)
    visited2=set()
    return board,base   #Nextmaps
##drawing happens here
def drawGrassland(coordX=0,coordY=0,N=None,E=None,S=None,W=None):
    global boards
    if (coordX,coordY)==(0,0):
        board,base=makeBoard(512,512,N,E,S,W,coordX,coordY)
    else:
        board,base=makeBoard(512-2*thick,512-2*thick,N,E,S,W,coordX,coordY)
    boards[(coordX,coordY)]=board
    temp,mod=0,0
    im=PIL.Image.new('RGB',(512,512))
    for row in range(len(board)):
        for col in range(len(board[0])):
            if board[row][col]==0:
                #Adds colors
                if base[row][col]==0:
                    temp=230
                else:
                    temp=(base[row][col])*200
                color=(int(temp)//4,int(temp),0)
            #water
            elif board[row][col]<1.5:
                temp=153*(board[row][col]-.5)
                color=(0,int(temp)//2,int(temp))
            #forest, 76-153 and down
            elif board[row][col]<2.5:
                temp=int(153*(board[row][col]-1.5))
                color=(temp//2,temp,0)
            #hills
            elif board[row][col]<2.9:
                temp=int(100*(board[row][col]-2.5))
                color=(255,255-temp//2,255-temp)
            #mountains, 153-76 and down
            else:
                mod=153*(board[row][col]-2.9)
                temp=153-int(mod)
                #nice brown
                color=(temp,temp//2,0)
            im.putpixel((col,row),color)
    im.save('test%d,%d.gif'%(coordX,coordY))
def drawBigMap():
    bigMap,polMap=makeBigMap()
    count=0
    im=PIL.Image.new('RGB',(512,512))
    for row in range(len(polMap)):
        for col in range(len(polMap[0])):
            if polMap[row][col]==0:
                color=(120,120,120)
            elif polMap[row][col]==1:
                color=(153,255,153)
            elif polMap[row][col]==2:
                color=(255,255,153)
            elif polMap[row][col]==3:
                color=(255,153,153)
            elif polMap[row][col]==4:
                color=(153,255,255)
            elif polMap[row][col]==5:
                color=(255,153,255)
            elif polMap[row][col]==6:
                color=(255,204,229)
            elif polMap[row][col]==7:
                color=(153,204,255)
            elif polMap[row][col]==8:
                color=(153,153,255)
            else: color=(0,0,0)
            im.putpixel((col,row),color)
    im.save('political.png')
############
#Don't need this later on
def isLegalPF(nx,ny,board):
    if nx<0 or ny<0 or nx>=len(board[0]) or ny>=len(board):
        return False
    return True
#Update this part if I update pathfinding
##################
def filled():
    colFilled=dict()
    for test in tests:
        for col in range(-2*gSize,2*gSize):
            for row in range(-2*gSize,2*gSize):
                x,y=test.x,test.y
                colFilled[(row+y,col+x)]=colFilled.get((row+y,col+x),0)+5
    return colFilled
#Make everything in relation to globalX,globalY which are in
#relation to 0,0
def pfTransfer(globalX,globalY):
    whichX=(globalX//512)
    whichY=-(globalY//512)
    accessX=globalX-whichX*512
    accessY=globalY-whichY*-512
    return whichX,whichY,accessX,accessY
#Every coordinate should be based on the global system, accessing should
#be based on pfTransfer
def pathfinding(x,y,tx,ty):
    oL=[]
    heapq.heapify(oL)
    cL=set()
    cL.add((x,y))
    d=dict()
    colFill=filled()
    count=0
    tBoardX,tBoardY,txBoard,tyBoard=pfTransfer(tx,ty)
    whichB=boards[(tBoardX,tBoardY)]
    if whichB[tyBoard][txBoard]!=0 and whichB[tyBoard][txBoard]<1.5:
        return 0
    def findin(mx,my,tx,ty,pastCost=0):
        nonlocal count
        for choices in [(-1,-1),(-1,0),(-1,1),(0,1),(0,-1),(1,1),(1,0),(1,-1)]:
            dx,dy=choices
            nx,ny=mx+dx,my+dy
            #handles when reaching
            if (nx,ny) == (tx,ty):
                d[tx,ty]=(mx,my)
                return True
            boardX,boardY,accessX,accessY=pfTransfer(nx,ny)
            if (boardX,boardY) in boards:
                usingB=boards[(boardX,boardY)]
            else:
                #return statement does nothing, prevents pushing though and
                #adds to closed List
                cL.add((nx,ny))
                return False
            if isLegalPF(accessX,accessY,usingB):
                terrain=usingB[accessY][accessX]
                if ((terrain==0 or terrain > 1.5) and (nx,ny) not in cL):
                    dist=distance(nx,ny,tx,ty)
                    newCost=terrain+1+pastCost
                    if (ny,nx) in colFill:
                        if count>5:
                            newCost+=colFill[(ny,nx)]
                        count+=1
                    estCost=dist+newCost
                    heapq.heappush(oL,(estCost,nx,ny,newCost))
                    d[(nx,ny)]=(mx,my)
                    cL.add((nx,ny))
                continue
            continue
    while True:
        #start
        if len(oL)==0:
            findin(x,y,tx,ty)
            #Stuck yo
            if len(oL)==0:
                return None
        blah,mx,my,cost=heapq.heappop(oL)
        if findin(mx,my,tx,ty,cost)==True:
            break
    final=[(tx,ty)]
    counter=0
    #gotta avoid dat recursion depth
    def path(px,py):
            nonlocal final
            final+=[d[px,py]]
            return d[px,py]
    while True:
        if counter==0:
            counter+=1
            next=path(tx,ty)
        next=path(*next)
        if next==(x,y):
            break
    return final
##############
#Do i understand how the cX and cY variables work? not a chance.
def clickety(x,y,data):
    x-=data.cX
    y-=data.cY
    global selected
    selected=[]
    two=2*gSize
    decent=[]
    for test in tests:
        if test.team==player:
            dist=distance(test.x,test.y,x,y)
            if dist<two:
                decent.append((dist,test))
    if len(decent)>0:
        blah,select=min(decent)
        selected.append(select)
def clicketyRight(x,y,data):
    x-=data.cX
    y-=data.cY
    two=2*gSize
    decent=[]
    for test in tests:
        dist=distance(test.x,test.y,x,y)
        if dist<two:
            decent.append((dist,test))
    if len((decent))>0:
        blah,target=min(decent)
    else:
        target=(x,y)
    return target
def setEventInfo(event, data, eventName):
    ctrl  = ((event.state & 0x0004) != 0)
    shift = ((event.state & 0x0001) != 0)    
    if ctrl:  pass
    if shift: pass
def mouseMotion(event, data):
    pass
def leftPressed(event, data):
    if data.gameWon==0 and data.gameLost==0:
        clickety(event.x,event.y,data)
    data.boxStartX,data.boxStartY=event.x,event.y
def leftMoved(event, data):
    setEventInfo(event, data, "leftMoved")
    data.leftPosn = (event.x, event.y)
    data.boxTempX,data.boxTempY=event.x,event.y
def leftReleased(event, data):
    setEventInfo(event, data, "leftReleased")
    data.leftPosn = (event.x, event.y)
    if data.gameWon==0 and data.gameLost==0:
        if data.boxTempX!=None and data.boxTempY!=None:
            left=min(data.boxTempX,data.boxStartX)
            right=max(data.boxTempX,data.boxStartX)
            top=min(data.boxTempY,data.boxStartY)
            bottom=max(data.boxTempY,data.boxStartY)
            #modify the x and ys here 
            for test in tests:
                if (test.x>left-data.cX and test.x<right-data.cX and 
                    test.y>top-data.cY and test.y<bottom-data.cY and 
                    test.team==player):
                    selected.append(test)
            data.boxTempX,data.boxTempY=None,None
def rightPressed(event, data):
    global test     #what does this line do again
    dy=0
    num=0
    if data.gameWon==0 and data.gameLost==0:
        if len(selected)>0:
            target=clicketyRight(event.x,event.y,data)
            if isinstance(target,test):
                #had to change name to allow isinstance to work
                for testy in selected:
                    testy.target=target
            else:
                if len(selected)==1:
                    selected[0].move(*target)
                else:
                    moveX,moveY=target
                    dist=distance(data.cX,data.cY,moveX,moveY)
                # uVectorX,uVectorY=(moveX-data.cX)/dist,(moveY-data.cY)/dist
                    while True:
                        for dx in range(-5,6):
                            if num>=len(selected):
                                break
                            #Originally had shiftX,shiftY multiplied by the
                            #unit vectors for angling. Didn't work and I
                            #realized that it didn't really matter.
                            shiftX = int(dx*10)
                            shiftY = int(dy*10)
                            bX,bY,aX,aY=pfTransfer(moveX+shiftX,moveY+shiftY)
                            if (boards[(bX,bY)][aY][aX]==0 or 
                                boards[(bX,bY)][aY][aX]<1.5):
                            #gotta do something to avoid the water
                                selected[num].move(moveX+shiftX,moveY+shiftY)
                                num+=1
                        dy+=1
                        #dy will be added to, but that's okay
                        if num>=len(selected): 
                            break
def rightMoved(event, data):
    pass
def rightReleased(event, data):
    pass
def drawHelper(data):
    drawThese=set()
    data.currentX,data.currentY=data.cX//-512,data.cY//512
    for key in boards:
        mapX,mapY=key
        if mapX<data.minMX: data.minMX=mapX
        elif mapX>data.maxMX:   data.maxMX=mapX
        if mapY>data.maxMY: data.maxMY=mapY
        elif mapY<data.minMY:   data.minMY=mapY
    for dx in range(-1,2):
        for dy in range(-1,2):
            addX,addY=data.currentX+dx,data.currentY+dy
            drawThese.add((addX,addY))
            if(addX,addY) not in data.mapImages:
                if (addX,addY) in boards:
                    data.mapImages[(addX,addY)]=(PIL.ImageTk.PhotoImage(
                                            file="test%d,%d.gif"%(addX,addY)))
    return drawThese
#camera x,y are the opposite of offsetX, offsetY
#Gotta remember that map x,ys are in standard quadrant coords
def drawMaps(canvas,data):
    drawThese=drawHelper(data)
    for drawMap in drawThese:
        if drawMap in boards:
            x,y=drawMap
            x0,y0=x*512,y*-512
            x0+=data.cX
            y0+=data.cY
            canvas.create_image(x0,y0,anchor=NW,image=data.mapImages[x,y])
def drawIntro(canvas,data):
    top=10
    canvas.create_image(0,0,anchor=NW,image=data.background)
    if data.intro==0:
        canvas.create_text(width//2,height//4,text="BARBAROS",
            font=("Brush Script MT", 90, "bold"),fill="tomato")
    elif data.intro==1:            
        text01="""
            You awake in an unfamiliar location. You've tried walking 
            around,but it appears that this place is effectively endless, 
            stretching out in an sea of mountains, hills, forests, and 
            lakes. 
            """
        text02="""
            A voice appears in your mind. "100". And the voice is 
            gone again...
            """
        canvas.create_text(width//2,height//4,text=text01,
            font=("Arial 14 bold"))    
        canvas.create_text(width//2,height//2,text=text02,
            font=("Arial 14 bold"))   
    elif data.intro==2:
        text11="""
            You realize that you're surrounded by the din of battle.
            You motion at a few of the units fighting. Some respond. 
            Most don't.
            It appears that only those clad in green will fight for you.
            """
        text12="""
            Furthermore, it appears more units suddenly appear 
            somewhat randomly. 
            You suppose you yourself were brought in in the 
            same fashion.
            """
        canvas.create_text(width//2,height//4,text=text11,
            font=("Arial 14 bold"))    
        canvas.create_text(width//2,height//2,text=text12,
            font=("Arial 14 bold"))   
    elif data.intro==3:
        text21="""
            As you motion towards a unit of a different color, you 
            watch as your troops cut down the enemy. 
            The voice reappears. 
            "1".
            """
        text22="""
            Without any other leads, you've no choice but to kill 
            another 99...
            """
        canvas.create_text(width//2,height//4,text=text21,
            font=("Arial 14 bold"))    
        canvas.create_text(width//2,height//2,text=text22,
            font=("Arial 14 bold"))   
    elif data.intro==4:
        text31="""
            Welcome to Barbaros. Basic commands are WASD for camera
            movement. 
            Click on a unit to select it. 
            Clicking on another unit
            deselects the original unit and selects the new unit. 
            Right-clicking sends the selected units orders. 
            More units will automatically appear as you explore. 
            Please have patience if the game freezes. This is to 
            be expected as the game is generating an infinite world
            piece by piece. Have fun getting those 100 kills!
            """
        text32="""
            In the game ahead you will be controlling small units of dots
            to minimize your own losses and maximize everyone else's.
            Blue is water, which no unit can walk upon. Green is forest,
            beige is hill, and brown is mountain. 
            """
        canvas.create_text(width//2,height//4,text=text31,
            font=("Arial 14 bold"))    
        canvas.create_text(width//2,3*height//4,text=text32,
            font=("Arial 14 bold"))
    canvas.create_text(width//2,height-top,
            text="Press any key to continue",font=("Arial 14 bold"))
def drawHelpScreen(canvas,data):
    top=10
    canvas.create_image(0,0,anchor=NW,image=data.background)
    text31="""
        Welcome to Barbaros. Basic commands are WASD for camera
        movement. 
        Click on a unit to select it. 
        Clicking on another unit
        deselects the original unit and selects the new unit. 
        Right-clicking sends the selected units orders. 
        More units will automatically appear as you explore. 
        Please have patience if the game freezes. This is to 
        be expected as the game is generating an infinite world
        piece by piece. Have fun getting those 100 kills!
        """
    text32="""
        In the game ahead you will be controlling small units of dots
        to minimize your own losses and maximize everyone else's.
        Blue is water, which no unit can walk upon. Green is forest,
        beige is hill, and brown is mountain. If the game is too slow, try
        parking all your units next to any new maps you create. This will reduce
        the pathfinding spike.
        """
    canvas.create_text(width//2,height//4,text=text31,
        font=("Arial 14 bold"))    
    canvas.create_text(width//2,3*height//4,text=text32,
        font=("Arial 14 bold"))
    canvas.create_text(width//2,height-top,
        text="Press any key to return",font=("Arial 14 bold"))
def drawSideBar(canvas,data):
    #coordinate systems collide.
    #I did the tiles in normal coordinates, I did drawing in computer coords
    #witness the results of coordinate system collision.
    num=3
    canvas.create_rectangle(width-100,23,width,height,fill="lemonchiffon",
        width=5)
    locX,locY=-data.cX+256,data.cY+256
    canvas.create_text(width-50,25,
        text="Your location=%d,%d"%(locX,locY),
        font="Arial 8 bold",anchor=N)
    canvas.create_text(width-50,40,text="Your Unit Locations:",anchor=N,
        font="Arial 8 bold")
    for test in tests:
        if test.team==player:
            num+=1
            canvas.create_text(width-50,9+num*12,
                text="%d,%d"%(test.x,-test.y+512),font="Arial 8 bold",anchor=N)

def redrawAll(canvas,data):
    top=10
    if data.intro<5:
        drawIntro(canvas,data)
    else:
        if data.help==1:
            drawHelpScreen(canvas,data)
        elif data.gameLost==0 and data.gameWon==0:
            #canvas.create_image(0,0,anchor=NW,image=data.map)
            drawMaps(canvas,data)
            for test in tests:
                test.draw(canvas,data.cX,data.cY)
                if test.team==player:
                    canvas.create_text(test.x+data.cX,test.y-top+data.cY,
                        text=int(test.hp),font="Arial 8 bold",fill="violet")
            canvas.create_rectangle(0,0,width,2*top,fill="violet")
            canvas.create_text(50,top,text=("Kills:%d"%kills),
                        font="Arial 15 bold",anchor=W)
            canvas.create_text(50+width//3,top,text=("Allied:%d"%data.onTeam),
                        font="Arial 15 bold",anchor=W)
            canvas.create_text(50+ 2*width//3,top,
                text=("Enemy:%d"%data.otherTeam),font="Arial 15 bold",anchor=W)
            drawSideBar(canvas,data)
            canvas.create_text(width//2,height-top,
                        text=("Press 'h' for help"),font="Arial 15 bold",
                                            fill="beige")
            canvas.create_text(width//2,height-2*top,
                        text=("%d,%d"%(data.currentX,data.currentY)),font="Arial 15 bold",
                                            fill="beige")
            #Orange the ones inside the box.
            if data.boxTempX!=None and data.boxTempY!=None:
                canvas.create_rectangle(data.boxStartX,data.boxStartY,
                    data.boxTempX,data.boxTempY)
        elif data.gameLost==1:
            canvas.create_image(0,0,anchor=NW,image=data.background)
            canvas.create_text(width//2,height//2,text="You Lost", 
                font=("Brush Script MT", 90, "bold"),fill="tomato")
        elif data.gameWon==1:
            canvas.create_image(0,0,anchor=NW,image=data.background)
            canvas.create_text(width//2,height//2,text="You Won", 
                font=("Brush Script MT", 90, "bold"),fill="tomato")
def createEnemies(data):
    otherX,otherY=(data.cX-400)//-512,(data.cY+400)//512
    if (data.currentX,data.currentY) not in data.alreadyCreated:
        data.pastX,data.pastY=data.currentX,data.currentY
        data.alreadyCreated.add((data.currentX,data.currentY))
        startX,startY=data.currentX*512,data.currentY*-512
        #A group at each corner, about 60 in?
        #distance in starts is too far for a simple loop for all 4
        for number in range(random.randint(1,4)):
            new=test(startX+206+random.randint(-15,15),
                startY+206+random.randint(-15,15),
                random.randint(0,8))
            tests.append(new)
        for number in range(random.randint(1,4)):
            new=test(startX+306+random.randint(-15,15),
                startY+306+random.randint(-15,15),
                random.randint(0,8))
            tests.append(new)
        for number in range(random.randint(1,4)):
            new=test(startX+206+random.randint(-15,15),
                startY+306+random.randint(-15,15),
                random.randint(0,8))
            tests.append(new)
        for number in range(random.randint(1,4)):
            new=test(startX+306+random.randint(-15,15),
                startY+206+random.randint(-15,15),
                random.randint(0,8))
            tests.append(new)
    elif (otherX,otherY) not in data.alreadyCreated:
        data.alreadyCreated.add((otherX,otherY))
        startX,startY=otherX*512,otherY*-512
        for number in range(random.randint(1,4)):
            new=test(startX+206+random.randint(-15,15),
                startY+206+random.randint(-15,15),
                random.randint(0,8))
            tests.append(new)
        for number in range(random.randint(1,4)):
            new=test(startX+306+random.randint(-15,15),
                startY+306+random.randint(-15,15),
                random.randint(0,8))
            tests.append(new)
        for number in range(random.randint(1,4)):
            new=test(startX+206+random.randint(-15,15),
                startY+306+random.randint(-15,15),
                random.randint(0,8))
            tests.append(new)
        for number in range(random.randint(1,4)):
            new=test(startX+306+random.randint(-15,15),
                startY+206+random.randint(-15,15),
                random.randint(0,8))
            tests.append(new)
def cBound(data):
    for test in tests:
        if test.team==player:
            if test.x>data.right:
                data.right=test.x
            elif test.x<data.left:
                data.left=test.x
            if test.y>data.down:
                data.down=test.y
            elif test.y<data.up:
                data.up=test.y
def init(data):
    data.leftPosn = (data.width//4, data.height//2)
    data.rightPosn = (data.width*3//4, data.height//2)
    data.motionPosn = (data.width//2, data.height//2)
    data.gameLost=0
    data.gameWon=0
    drawGrassland()
    data.mapImages=dict()
    data.mapImages[(0,0)]=(PIL.ImageTk.PhotoImage(file="test0,0.gif"))
    data.map=PhotoImage(file="test0,0.gif")
    #where to create map 0,0
    data.cX,data.cY=0,0
    # data.marginX,data.marginY=20,20
    data.left,data.right,data.up,data.down=0,0,0,0
    data.minMX,data.minMY,data.maxMX,data.maxMY=0,0,0,0
    data.currentX,data.currentY=0,0
    data.pastX,data.pastY=None,None
    data.visitedMaps=set()
    data.intro=0
    data.boss=0
    data.background=PIL.ImageTk.PhotoImage(file="test.png")
    data.help=0
    data.onTeam,data.otherTeam=0,0
    data.alreadyCreated=set()
    data.boxTempX,data.boxTempY=None,None
    data.boxStartX,data.boxStartY=0,0
# self,x,y,team=1,strength=2,hp=100,point=1,speed=5,range=50,
                                # ROF=5):
def timerFired(data):
    generate(data)
    boss=test(data.cX,data.cY,9,45,1000,100,10,60,3)
    if data.intro>4:
        trafficCop()
        cBound(data)
        createEnemies(data)
        data.onTeam=0
        data.otherTeam=0
        if kills>=100 and data.boss==0:
            tests.append(boss)
            data.boss=1
        for testy in tests:
            testy.update()
            if testy.team==player:
                data.onTeam+=1
            else:
                data.otherTeam+=1
        if data.onTeam<1:
            data.gameLost=1
        elif data.boss==1 and numBoss<1:
            data.gameWon=1
def keyPressed(event, data):
    global kills
    if data.intro<5:
        data.intro+=1
    elif data.help==1:
        data.help=0
    else:
        # if event.keysym=="Up":
        #     newtest=test(0+random.randint(15,50),0+random.randint(15,50),0)
        #     tests.append(newtest)
        # elif event.keysym=="Down":
        #     newtest=test(250-random.randint(15,50),250-random.randint(15,50))
        #     tests.append(newtest)
        if event.keysym=="d":
            data.cX-=10
        elif event.keysym=="a":
            data.cX+=10
        elif event.keysym=="w":
            data.cY+=10
        elif event.keysym=="s":
            data.cY-=10
        elif event.keysym=="h":
            data.help=1
        elif event.keysym=="bar":
            kills+=99

####################################
# use the run function as-is
####################################

def run(width=width, height=height):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()    

    # Note changes #1:
    def mouseWrapper(mouseFn, event, canvas, data):
        mouseFn(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        # redrawAllWrapper(canvas, data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    data.readyForDeltaDraw = False
    # create the root and the canvas
    root = Tk()
    init(data)
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events

    # Note changes #2:
    root.bind("<Button-1>", lambda event:
                            mouseWrapper(leftPressed, event, canvas, data))
    root.bind("<Button-2>", lambda event:
                            mouseWrapper(rightPressed, event, canvas, data))
    canvas.bind("<Motion>", lambda event:
                            mouseWrapper(mouseMotion, event, canvas, data))
    canvas.bind("<B1-Motion>", lambda event:
                            mouseWrapper(leftMoved, event, canvas, data))
    canvas.bind("<B2-Motion>", lambda event:
                            mouseWrapper(rightMoved, event, canvas, data))
    root.bind("<B1-ButtonRelease>", lambda event:
                            mouseWrapper(leftReleased, event, canvas, data))
    root.bind("<B2-ButtonRelease>", lambda event:
                            mouseWrapper(rightReleased, event, canvas, data))

    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")
#Make group movement, make pathfinding optimization grid
#INPUT EFFECTIVE SPEED
#Put in pursuit
#Better collision resolution
#One chosen stops instead of previous where chosen moves
def trafficCop():
    seen=set()
    for i1,test in enumerate(tests):
        for i2,other in enumerate(tests):
            if (i1,i2) not in seen and test != other:
                #one stopped should remain stopped
                if distance(test.x,test.y,other.x,other.y)<int(gSize*1.5):
                    if test.stopCount>0 or other.stopCount>0:
                        pass
                    elif test.moveComplete==0 or test.continousMove==1:
                        #both moving
                        if other.moveComplete==0 or other.continousMove==1:
                            who=random.choice([test,other])
                            who.stopCount=1
                        #test is moving, other is stopped
                        else:
                            test.moveComplete,test.continousMove=1,0
                            test.stopCount=1
                    else:
                        #test is stopped,other is moving
                        if other.moveComplete==0 or other.continousMove==1:
                            other.moveComplete,other.continousMove=1,0
                            other.stopCount=1
                        #can't do anything, one should move, but making a 
                        #a move requires a x,y which I don't want to do rn
                        else:
                            pass
            seen.add((i1,i2))
class test(object):
    def __init__(self,x,y,team=1,strength=2,hp=100,point=1,speed=5,range=50,
                                ROF=5):
        self.team,self.strength,self.hp,self.point=team,strength,hp,point
        self.speed,self.range=speed,range
        self.atk,self.retreat,self.rePo,self.defend=1,0,0,0
        self.x,self.y=x,y
        if self.team!=9:
            self.size=gSize
        else:
            self.size=3*gSize
        self.attackers=0
        self.atklist=[]
        self.ROF=ROF
        self.fireTimer=0
        self.dict=dict()
        #Target should be closest/weakest/closest to death?
        self.target=self.closest()
        self.range=50
        self.timeOut=0
        self.movere=[]
        self.moveComplete=1
        self.movePos=1
        self.continousMove=0
        self.stopCount=0
        self.atkMoves=0
        #target location
        self.end=(0,0)
        self.resetCount=10
        self.hitByPlayer=0
    def __eq__(self,other):
        if isinstance(other,test):
            return (boutSame(self.hp, other.hp) and
            self.team==other.team and self.strength==other.strength
            and self.x==other.x and self.y==other.y and
            self.speed==other.speed and self.ROF==other.ROF)
        return False
    def draw(self,canvas,offsetX,offsetY):
        x0,y0=self.x-self.size+offsetX,self.y-self.size+offsetY
        x1,y1=self.x+self.size+offsetX,self.y+self.size+offsetY
        if self.team==0:
            color=120,120,120
        elif self.team==1:
            color=153,255,153
        elif self.team==2:
            color=255,255,153
        elif self.team==3:
            color=255,153,153
        elif self.team==4:
            color=153,255,255
        elif self.team==5:
            color=255,153,255
        elif self.team==6:
            color=255,204,229
        elif self.team==7:
            color=153,204,255
        elif self.team==8:
            color=153,153,255
        else: color=0,0,0
        if self in selected:
            outline="yellow"
        else:
            outline="black"
        color=rgbString(*color)
        canvas.create_oval(x0,y0,x1,y1,fill=color,width=2,outline=outline)
    def closest(self):
        closest,closestD="",width+height
        temp=0
        for target in tests:
            temp=distance(self.x,self.y,target.x,target.y)
            if temp<closestD and (self.team != target.team):
                closest=target
                closestD=temp
        return closest
    #Contains the entirety of the AI
    def update(self):
        global kills
        global numBoss
        friendlies=0
        enemies=0
        if self.resetCount==0:
            self.attackers=len(self.atklist)
            self.atk,self.retreat,self.rePo,self.defend=1,0,0,0
            self.resetCount=10
        self.resetCount-=1
        if self.target not in tests:
            self.target=self.closest()
        order=max(self.atk,self.retreat,self.rePo,self.defend)
        if self.hp<0:
            if self.team==9:
                numBoss-=1
            if self.hitByPlayer==1 and self.team!=player:
                kills+=1
            if self in tests:
                tests.remove(self)
        if self.continousMove==1:
            self.contMove()
        else:
            #just shoot at a random one, staying still. defense yo
            if self.defend==order and self.attackers>0 and len(self.atklist)>0:
                for enemy in self.atklist:
                    if distance(self.x,self.y,enemy.x,enemy.y)<self.range:
                        self.attack(enemy)
                        if self not in enemy.atklist:
                            enemy.atklist.append(self)
                        break
            #I need to work on this later
            elif self.retreat==order:
                scary = self.target
                scaryX,scaryY=self.target.x,self.target.y
                vectorScary=scaryX,scaryY
            elif self.atk==order:
                if isinstance(self.target,test):
                    if self not in self.target.atklist:
                        self.target.atklist.append(self)
                self.attack(self.target)
            for other in tests:
                if ((isinstance(other,test) and 
                    (distance(self.x,self.y,other.x,other.y))<50)):
                    if self.team != other.team:
                        enemies+=1
                    else: friendlies +=1
            if friendlies>enemies and self.attackers>=3:
                self.defend+=1
            elif friendlies>enemies and self.attackers<3:
                self.atk+=1
            elif enemies>friendlies and self.attackers>=2:
                self.retreat+=1
            elif enemies>friendlies and self.attackers<2:
                self.atk+=1
        #Distance, attacking, direction,friendlies,number
        #Attack, regroup, retreat, move
        #Reset after 10 secs? regroup goes to 1
    #if one is moving and one stopped, the moving one should always go
    #if both are moving, one should stop
    #if both are moving, you don't need to recalculate pathfinding
    #This is bad and ugly. Called for both when moving, should be able to
    #communicate who moves
    # def tooclose(self):
    #     for test in tests:
    #         if self != test:
    #             if distance(self.x,self.y,test.x,test.y)<5:
    #                 if self.contMove==0 and test.contMove==0:
    #                     who=random.choice([test,self])
    #                     return (None,who)
    #                 elif self.contMove==0 and test.contMove!=0:
    #                     return(None,test)
    #                 elif test.contMove==0:
    #                     return(None,self)
    #                 else:
    #                     return random.choice([test,self])
    #     return False
    def moveTilAttack(self,x,y):
        global numBoss
        if self.stopCount<1:
            if self.moveComplete==1 and self.continousMove==0:
                self.movere=pathfinding(self.x,self.y,x,y)
                if self.movere==None:
                    if self in tests:
                        if self.team==9:
                            numBoss-=0
                        tests.remove(self)
                    self.movere=[(0,0)]*100
                elif self.movere==0:
                    self.target=self.closest()
                else:
                    self.movePos=1
                    indexio=self.movePos*self.speed
                    #negative because pathfinding returns stuff backwards
                    self.x,self.y=self.movere[-indexio]
                    self.moveComplete=0
            elif self.moveComplete==0:
                self.movePos+=1
                indexio=self.movePos*self.speed
                if self.movere==0:
                    pass
                elif indexio>=len(self.movere):
                    self.moveComplete=1
                    self.movePos=0
                else:
                    self.x,self.y=self.movere[-indexio]
                    #recalculates path if collision
                    # if self.tooclose()==self:
                    #     #You get to move!
                    #     pass
                    # elif self.tooclose()==(None,self):
                    #     #you have to recalculate
                    #     self.moveComplete=1
                    #     self.x,self.y=self.movere[(-indexio+self.speed)]
                    #     self.movePos=0
                    # elif self.tooclose() != False:
                    #     #You don't do nothin this time
                    #     self.x,self.y=self.movere[(-indexio+self.speed)]
                    #     self.movePos-=1
        else:
            self.stopCount-=1
    def move(self,x,y):
        global numBoss
        self.movere=pathfinding(self.x,self.y,x,y)
        self.target=self.closest()
        if self.movere==None:
            if self in tests:
                if self.team==9:
                    numBoss-=1
                tests.remove(self)
            self.movere=[(0,0)]*100
        elif self.movere==0:
            pass
        else:
            self.movePos=1
            indexio=self.movePos*self.speed
            if indexio>=len(self.movere):
                self.movePos,indexio=0
            #negative because pathfinding returns stuff backwards
            else:
                self.x,self.y=self.movere[-indexio]
                self.continousMove=1
    def contMove(self):
        if self.stopCount<1:
            if self.continousMove==1:
                self.movePos+=1
                indexio=self.movePos*self.speed
                if self.movere==0:
                    pass
                elif indexio>=len(self.movere):
                    self.continousMove=0
                    self.movePos=0
                    self.moveComplete=1
                else:
                    self.x,self.y=self.movere[-indexio]
                    # if self.tooclose()==self:
                    #     pass
                    # elif self.tooclose()!=False:
                    #     print(5)
                    #     self.x,self.y=self.movere[(-indexio+self.speed)]
                    #     self.movePos-=1
                    #     self.stopCount=3
        else:
            self.stopCount-=1
    def attack(self,other):
        if self.continousMove==0:
            if isinstance(other,test) and other.hp>0:
                if distance(self.x,self.y,other.x,other.y)<self.range:
                    if self.fireTimer==self.ROF:
                        if self.team==player:
                            other.hitByPlayer=1
                        self.atkMoves=0
                        self.moveComplete=1
                        other.hp-=int(self.strength)
                        if distance(self.x,self.y,other.x,other.y)<other.range:
                            self.hp-=other.strength/((other.attackers+1))
                        self.fireTimer=0
                    self.fireTimer+=1
                else:
                    self.moveTilAttack(other.x,other.y)
                    self.atkMoves+=1
                    if self.atkMoves>=10:
                        self.target=self.closest()
tests=[]
test2=test(256,256)
test1=test(266,266)
test3=test(246,246)
test4=test(246,266)
test5=test(266,246)
test6=test(120,120)
test7=test(396,120)
test8=test(396,396)
test9=test(120,396)
tests.append(test2)
tests.append(test1)
tests.append(test3)
tests.append(test4)
tests.append(test5)
tests.append(test6)
tests.append(test7)
tests.append(test8)
tests.append(test9)
selected=[]
#Check number of tests
run()