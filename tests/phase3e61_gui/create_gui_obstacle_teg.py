"""KLayout 0.30.x batch script: create an unrouted two-port GUI test GDS.
Run: klayout -b -r create_gui_obstacle_teg.py
"""
import os
import pya

DBU = 0.001
WG = pya.LayerInfo(1, 0)
PIN = pya.LayerInfo(2, 0)
OBS = pya.LayerInfo(90, 0)

def um(value):
    return int(round(value / DBU))

def pt(x, y):
    return pya.Point(um(x), um(y))

def path(cell, layer, coords, width):
    cell.shapes(layer).insert(pya.Path([pt(x, y) for x, y in coords], um(width)))

def main():
    layout = pya.Layout()
    layout.dbu = DBU
    top = layout.create_cell('PHOTONICS_GUI_OBSTACLE_TEG')
    wg = layout.layer(WG)
    pin = layout.layer(PIN)
    obs = layout.layer(OBS)

    # Two separate WG stubs: no waveguide between the two optical ports.
    path(top, wg, [(-8.0, 0.0), (0.0, 0.0)], 0.5)
    path(top, wg, [(80.0, 0.0), (88.0, 0.0)], 0.5)

    # Native PIN-layer paths and labels. v6.3/v6.4 collect_ports() detects
    # labels at the path endpoints and derives outward directions.
    # Source outward = +X; destination outward = -X.
    path(top, pin, [(-2.0, 0.0), (0.0, 0.0)], 0.5)
    top.shapes(pin).insert(pya.Text('opt1', pya.Trans(pt(0.0, 0.0))))
    path(top, pin, [(82.0, 0.0), (80.0, 0.0)], 0.5)
    top.shapes(pin).insert(pya.Text('opt2', pya.Trans(pt(80.0, 0.0))))

    # Explicit obstacle layer 90/0; do not put this rectangle on WG 1/0.
    top.shapes(obs).insert(pya.Box(um(37), um(-3), um(43), um(3)))

    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, 'gui_obstacle_2ports.gds')
    layout.write(out_path)
    print('GDS created:', out_path)
    print('Top cell:', top.name)
    print('WG: 1/0; PIN: 2/0; obstacle: 90/0')
    print('Port positions: opt1=(0,0), opt2=(80,0) um')
    print('Obstacle: x=37..43, y=-3..3 um')
    print('Unrouted GUI TEG: PASS')

if __name__ == '__main__':
    main()
