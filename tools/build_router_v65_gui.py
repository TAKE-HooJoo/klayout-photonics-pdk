#!/usr/bin/env python3
"""Build a standalone v6.5 GUI macro from the user's installed v6.4 macro.
The original v6.4 file is never modified. Standard-library only.
"""
from pathlib import Path
import argparse
import re

START = 'class Router(pya.Plugin):'
END = 'RouterFactory()'
GUI = '''# Shared activation owner across all three v6.5 plugin instances.
_v65_active_router = None

class HybridRouter(pya.Plugin):
    """Two-click hybrid router. Mode is selected by activating a tool."""
    def __init__(self, mode):
        super(HybridRouter, self).__init__()
        self.mode = mode
        self.first = None

    def activated(self):
        global _v65_active_router
        _v65_active_router = self
        self.first = None
        print('[v6.5 ACTIVATED] mode=%s instance=%s' % (self.mode, id(self)), flush=True)
        self._status('Photonics Router v6.5 [%s]: click source optical port' % self.mode)

    def deactivated(self):
        global _v65_active_router
        if _v65_active_router is self:
            _v65_active_router = None
        print('[v6.5 DEACTIVATED] mode=%s instance=%s' % (self.mode, id(self)), flush=True)
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
            pya.MessageBox.warning('Photonics Router v6.5', message, pya.MessageBox.Ok)
        except Exception:
            pass

    def mouse_click_event(self, p, buttons, prio):
        print('[v6.5 CLICK] mode=%s instance=%s prio=%s x=%.3f y=%.3f' %
              (self.mode, id(self), prio, p.x, p.y), flush=True)
        # In KLayout prio=True may belong to the selected plugin.
        # Never let inactive plugins steal the click when prio=False.
        if _v65_active_router is not self:
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
            self._status('[%s] Source %s: click destination' %
                         (self.mode, port.qualified_name))
            return True
        source, destination = self.first, port
        self.first = None
        print('[v6.5 ROUTE] mode=%s source=%s destination=%s' %
              (self.mode, source.qualified_name, destination.qualified_name), flush=True)
        if source.qualified_name == destination.qualified_name:
            self._warning('SAME_PORT_SELECTED')
            return True
        try:
            from photonics.pdk.cross_section import WaveguideCrossSection
            from photonics.pdk.design_rules import DesignRules
            from photonics.integration.router_hybrid_v65 import route_between_ports_hybrid
            width = float(source.width)
            xs = WaveguideCrossSection('strip', width, MIN_BEND_RADIUS)
            rules = DesignRules(0.4, 0.5, MIN_BEND_RADIUS)
            result = route_between_ports_hybrid(
                cell, layout, source, destination, xs, rules,
                mode=self.mode, waveguide_layer=WG_LAYER,
                obstacle_layer=OBSTACLE_LAYER)
        except Exception as exc:
            print('[v6.5 EXCEPTION] mode=%s error=%r' % (self.mode, exc), flush=True)
            self._warning('Routing rejected [%s]: %s' % (self.mode, exc))
            return True
        print('[v6.5 RESULT] mode=%s valid=%s variant=%s reason=%s' %
              (self.mode, result.valid, result.variant, result.reason), flush=True)
        if not result.valid:
            self._warning('No route created [%s]: %s' %
                          (self.mode, result.reason))
            return True
        try:
            view.add_missing_layers()
        except Exception:
            pass
        msg = ('%s -> %s\\nMode: %s\\nTopology: %s\\nLength: %.3f um\\n'
               'Designed radius: %.3f um\\nSampled radius: %s\\n'
               'Source tangent error: %.3f deg\\n'
               'Destination tangent error: %.3f deg' %
               (source.qualified_name, destination.qualified_name,
                self.mode, result.variant, result.length_um,
                result.designed_radius_um,
                format_bend_radius(result.measured_radius_um),
                result.tangent_error_source_deg,
                result.tangent_error_destination_deg))
        print('[Photonics Router v6.5]\\n' + msg)
        self._status('Route created [%s]: %.3f um (%s)' %
                     (self.mode, result.length_um, result.variant))
        try:
            pya.MessageBox.info('Photonics Router v6.5', msg, pya.MessageBox.Ok)
        except Exception:
            pass
        return True


class HybridRouterFactory(pya.PluginFactory):
    def __init__(self, mode, plugin_id, priority):
        super(HybridRouterFactory, self).__init__()
        self.mode = mode
        self.register(priority, plugin_id,
                      'Photonics Router v6.5 ' + mode)

    def create_plugin(self, manager, root, view):
        return HybridRouter(self.mode)


# Three independent toolbar tools provide explicit, persistent mode selection.
# Keep factory objects alive for the lifetime of the macro.
_hybrid_router_factories = [
    HybridRouterFactory('AUTO', 'photonics_router_v6_5_auto', -1011),
    HybridRouterFactory('CSC', 'photonics_router_v6_5_csc', -1012),
    HybridRouterFactory('EULER', 'photonics_router_v6_5_euler', -1013),
]
'''

def build(source: Path, dest: Path):
    raw = source.read_text(encoding='utf-8')
    if raw.count(START) != 1 or raw.count(END) != 1:
        raise ValueError('v6.4 GUI markers not found exactly once; no output written')
    if '<klayout-macro>' not in raw or '</klayout-macro>' not in raw:
        raise ValueError('Input is not a KLayout macro')
    before, tail = raw.split(START, 1)
    _, after = tail.split(END, 1)
    out = before + GUI + after
    out = out.replace('Photonics Router v6.4 - experimental obstacle-aware waypoint GUI',
                      'Photonics Router v6.5 - hybrid CSC Euler AUTO GUI', 1)
    out = out.replace('<version>6.4</version>', '<version>6.5</version>', 1)
    if 'route_between_ports_v64' in out or 'class RouterFactory(' in out:
        raise ValueError('Unexpected v6.4 GUI code remains; no output written')
    if dest.resolve() == source.resolve():
        raise ValueError('Refusing to overwrite v6.4')
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(out, encoding='utf-8')
    print('Created:', dest)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', default='pymacros/photonics_router_v6_4.lym')
    parser.add_argument('--output', default='pymacros/photonics_router_v6_5.lym')
    args = parser.parse_args()
    build(Path(args.source), Path(args.output))
