"""Phase 18: distinguish exact CSC parameters from polyline proxies."""
import math

def analytic_csc_energy(radius_um, arc1_rad, arc2_rad, straight_um):
    vals=(radius_um,arc1_rad,arc2_rad,straight_um)
    if any(not math.isfinite(float(v)) for v in vals) or radius_um<=0 or straight_um<0 or arc1_rad<0 or arc2_rad<0:
        raise ValueError('invalid CSC geometry')
    return {'arc_length_um':radius_um*(arc1_rad+arc2_rad),
            'length_um':radius_um*(arc1_rad+arc2_rad)+straight_um,
            'analytic_energy_inv_um':(arc1_rad+arc2_rad)/radius_um,
            'ideal_jump_inv_um':1/radius_um}

def parameter_status(obj):
    """Return exact parameters only if explicitly exposed, never infer them."""
    fields=('arc1_rad','arc2_rad','straight_um')
    if all(hasattr(obj,k) for k in fields):
        return {k:float(getattr(obj,k)) for k in fields}
    return None

def audit_source(module):
    import inspect
    out=[]
    for name in ('route_between_ports_hybrid','route_with_waypoints'):
        f=getattr(module,name,None)
        if f is None:
            out.append((name,'NOT_EXPOSED',''))
        else:
            try:
                src=inspect.getsourcefile(f) or ''
                line=inspect.getsourcelines(f)[1]
                out.append((name,'FOUND',f'{src}:{line}'))
            except (OSError,TypeError):
                out.append((name,'FOUND_SOURCE_UNAVAILABLE',''))
    return out
