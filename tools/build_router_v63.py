#!/usr/bin/env python3
"""Build v6.3 GUI macro from existing refined v6.2 macro, preserving legacy port discovery."""
import argparse
from pathlib import Path
import xml.etree.ElementTree as ET

GUI = r'''
class Router(pya.Plugin):
    """Two-click GUI backed by the independent Phase 3C RoutingEngine."""
    def __init__(self):
        super(Router, self).__init__()
        self.first = None

    def activated(self):
        self.first = None
        self._status('Photonics Router v6.3: click source optical port')

    def deactivated(self):
        self.first = None

    @staticmethod
    def _status(message):
        try:
            pya.MainWindow.instance().message(message, 4000)
        except Exception:
            print(message)

    @staticmethod
    def _warning(message):
        print(message)
        try:
            pya.MessageBox.warning('Photonics Router v6.3', message, pya.MessageBox.Ok)
        except Exception:
            pass

    def mouse_click_event(self, p, buttons, prio):
        if prio:
            return False
        view = pya.LayoutView.current()
        if view is None:
            return False
        cv = view.active_cellview()
        if cv is None or not cv.is_valid():
            return False
        layout, cell = cv.layout(), cv.cell
        port = nearest_port(cell, layout, pya.DPoint(p.x, p.y))
        if port is None:
            self._status('No optical port within %.1f um' % SNAP_RADIUS)
            return True
        if self.first is None:
            self.first = port
            self._status('Source %s selected: click destination' % port.qualified_name)
            return True
        source, destination = self.first, port
        self.first = None
        try:
            from photonics.pdk.cross_section import WaveguideCrossSection
            from photonics.pdk.design_rules import DesignRules
            from photonics.integration.router_v62 import route_between_ports
            width = float(source.width)
            if abs(width - float(destination.width)) > 1e-6:
                self._warning('PORT_WIDTH_MISMATCH: %.4f vs %.4f um' %
                              (width, float(destination.width)))
                return True
            xs = WaveguideCrossSection('strip', width, MIN_BEND_RADIUS)
            rules = DesignRules(0.4, 0.5, MIN_BEND_RADIUS)
            result = route_between_ports(cell, layout, source, destination,
                                         xs, rules, WG_LAYER)
        except Exception as exc:
            self._warning('Routing error: %s' % exc)
            return True
        if not result.valid:
            self._warning('No route created: %s' % result.reason)
            return True
        try:
            view.add_missing_layers()
        except Exception:
            pass
        msg = ('%s -> %s\nTopology: %s\nLength: %.3f um\n'
               'Designed radius: %.3f um\nSampled radius: %s\n'
               'Source tangent error: %.3f deg\n'
               'Destination tangent error: %.3f deg' %
               (source.qualified_name, destination.qualified_name,
                result.variant, result.length_um,
                result.designed_radius_um,
                format_bend_radius(result.measured_radius_um),
                result.tangent_error_source_deg,
                result.tangent_error_destination_deg))
        print('[Photonics Router v6.3]\n' + msg)
        self._status('Route created: %.3f um (%s)' %
                     (result.length_um, result.variant))
        try:
            pya.MessageBox.info('Photonics Router v6.3', msg, pya.MessageBox.Ok)
        except Exception:
            pass
        return True

class RouterFactory(pya.PluginFactory):
    def __init__(self):
        super(RouterFactory, self).__init__()
        self.register(-1000, 'photonics_router_v6_3', 'Photonics Router v6.3')

    def create_plugin(self, manager, root, view):
        return Router()

RouterFactory()
'''

def build(source, target, root):
    tree = ET.parse(source)
    xmlroot = tree.getroot()
    text_node = xmlroot.find('text')
    if text_node is None or not text_node.text:
        raise ValueError('Missing Python source in KLayout XML macro')
    original = text_node.text
    marker = '\nclass Router(pya.Plugin):'
    if original.count(marker) != 1:
        raise ValueError('Expected exactly one Router plugin class')
    prefix = original.split(marker, 1)[0]
    # Import from checkout, not ~/.klayout/pymacros. This is explicit for reliability.
    bootstrap = ("\nimport sys\n_PDK_ROOT = %r\n"
                 "if _PDK_ROOT not in sys.path:\n    sys.path.insert(0, _PDK_ROOT)\n" % str(root))
    text_node.text = prefix + bootstrap + '\n' + GUI
    target.parent.mkdir(parents=True, exist_ok=True)
    tree.write(target, encoding='utf-8', xml_declaration=True)
    # Ensure the macro's Python content is syntactically valid.
    compile(text_node.text, str(target), 'exec')
    return target

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='.', help='PDK checkout directory')
    args = parser.parse_args()
    root = Path(args.root).expanduser().resolve()
    source = root / 'pymacros/photonics_router_v6_2_refined_cscsc.lym'
    target = root / 'pymacros/photonics_router_v6_3.lym'
    print('Generated:', build(source, target, root))

if __name__ == '__main__':
    main()
