import math
from photonics.circuit.geometry import Point
from .dubins import words,candidate,mod2pi
from .geometry import unit,length,min_radius,tangent_errors
from .result import RouteResult

class RoutingEngine:
    def __init__(self, cross_section, design_rules, tangent_tolerance_deg=5.0, samples_per_arc=36):
        if not design_rules.validate_cross_section(cross_section):
            raise ValueError('Cross section violates design rules')
        if not 0<tangent_tolerance_deg<90 or samples_per_arc<4:
            raise ValueError('Invalid routing configuration')
        self.cross_section=cross_section
        self.rules=design_rules
        self.tangent_tolerance_deg=tangent_tolerance_deg
        self.samples_per_arc=samples_per_arc

    def route(self,start,end,source_outward,destination_outward):
        if not all(math.isfinite(v) for v in (start.x,start.y,end.x,end.y)):
            raise ValueError('Coordinates must be finite')
        src=unit(source_outward)
        dst=unit(destination_outward)
        arrival=(-dst[0],-dst[1])
        dx=end.x-start.x;dy=end.y-start.y
        D=math.hypot(dx,dy)
        if D<1e-9:
            return self._failure('COINCIDENT_PORTS')
        # Exact straight line, with strict native outward-port directions.
        chord=(dx/D,dy/D)
        if (chord[0]*src[0]+chord[1]*src[1]>1-1e-12 and
            chord[0]*arrival[0]+chord[1]*arrival[1]>1-1e-12):
            return RouteResult((start,end),D,math.inf,math.inf,0.,0.,True,'STRAIGHT')
        radius=max(self.cross_section.min_bend_radius_um,self.rules.min_bend_radius_um)*1.25
        theta=math.atan2(dy,dx)
        alpha=mod2pi(math.atan2(src[1],src[0])-theta)
        beta=mod2pi(math.atan2(arrival[1],arrival[0])-theta)
        valid=[]
        for word,t,p,q in words(alpha,beta,D/radius):
            if math.degrees(t+q)>240: continue
            pts=candidate(start,end,src,arrival,radius,word,t,p,q,self.samples_per_arc)
            if pts is None: continue
            err0,err1=tangent_errors(pts,src,dst)
            if max(err0,err1)>self.tangent_tolerance_deg: continue
            # The sampled circumcircle radius is diagnostic only; at straight/arc
            # junctions a three-point estimate is not an exact curvature bound.
            plen=length(pts)
            if plen>2.2*D: continue
            valid.append(RouteResult(pts,plen,radius,min_radius(pts),err0,err1,True,word))
        if not valid:
            return self._failure('NO_LEGAL_CSC_ROUTE')
        return min(valid,key=lambda r:r.length_um)

    @staticmethod
    def _failure(reason):
        return RouteResult((),0.,0.,math.inf,180.,180.,False,'NONE',reason)
