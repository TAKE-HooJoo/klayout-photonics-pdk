import math
from photonics.circuit.geometry import Point

def mod2pi(a):
    return a % (2*math.pi)

def words(alpha,beta,d):
    out=[]
    v=d+math.sin(alpha)-math.sin(beta)
    p2=2+d*d-2*math.cos(alpha-beta)+2*d*(math.sin(alpha)-math.sin(beta))
    if p2>=0:
        t0=math.atan2(math.cos(beta)-math.cos(alpha),v)
        out.append(('LSL',mod2pi(-alpha+t0),math.sqrt(p2),mod2pi(beta-t0)))
    v=d-math.sin(alpha)+math.sin(beta)
    p2=2+d*d-2*math.cos(alpha-beta)+2*d*(-math.sin(alpha)+math.sin(beta))
    if p2>=0:
        t0=math.atan2(math.cos(alpha)-math.cos(beta),v)
        out.append(('RSR',mod2pi(alpha-t0),math.sqrt(p2),mod2pi(-beta+t0)))
    p2=-2+d*d+2*math.cos(alpha-beta)+2*d*(math.sin(alpha)+math.sin(beta))
    if p2>=0:
        p=math.sqrt(p2)
        t0=math.atan2(-math.cos(alpha)-math.cos(beta),d+math.sin(alpha)+math.sin(beta))-math.atan2(-2,p)
        out.append(('LSR',mod2pi(-alpha+t0),p,mod2pi(-beta+t0)))
    p2=d*d-2+2*math.cos(alpha-beta)-2*d*(math.sin(alpha)+math.sin(beta))
    if p2>=0:
        p=math.sqrt(p2)
        t0=math.atan2(math.cos(alpha)+math.cos(beta),d-math.sin(alpha)-math.sin(beta))-math.atan2(2,p)
        out.append(('RSL',mod2pi(alpha-t0),p,mod2pi(beta-t0)))
    return out

def sample_arc(x,y,heading,turn,radius,angle,n):
    sign=1 if turn=='L' else -1
    cx=x-sign*radius*math.sin(heading)
    cy=y+sign*radius*math.cos(heading)
    a0=math.atan2(y-cy,x-cx)
    pts=[]
    for i in range(1,n+1):
        a=a0+sign*angle*i/n
        pts.append(Point(cx+radius*math.cos(a),cy+radius*math.sin(a)))
    return pts,pts[-1].x,pts[-1].y,heading+sign*angle

def candidate(start,end,src_dir,arrival_dir,radius,word,t,p,q,steps=36):
    x,y=start.x,start.y
    h=math.atan2(src_dir[1],src_dir[0])
    pts=[start]
    if t>1e-10:
        arc,x,y,h=sample_arc(x,y,h,word[0],radius,t,steps)
        pts.extend(arc)
    slen=p*radius
    x+=slen*math.cos(h); y+=slen*math.sin(h)
    if slen>1e-10: pts.append(Point(x,y))
    if q>1e-10:
        arc,x,y,h=sample_arc(x,y,h,word[2],radius,q,steps)
        pts.extend(arc)
    if math.hypot(x-end.x,y-end.y)>max(.02,.005*radius):
        return None
    h1=math.atan2(arrival_dir[1],arrival_dir[0])
    if abs(math.atan2(math.sin(h-h1),math.cos(h-h1)))>math.radians(1):
        return None
    if len(pts)<2: return None
    pts[-1]=end
    return tuple(pts)
