import json
import unittest
from photonics.circuit import Point, OpticalPort, PhotonicDevice, PhotonicNet, PhotonicCircuit

class CircuitModelTests(unittest.TestCase):
    def test_port_device_link(self):
        d = PhotonicDevice("wg1", "Straight")
        p = OpticalPort("out", Point(1, 2), 0)
        d.add_port(p)
        self.assertIs(p.device, d)
        self.assertEqual(p.qualified_name, "wg1.out")
        d.add_port(p)
        self.assertEqual(len(d.ports), 1)

    def test_net_and_circuit(self):
        a = OpticalPort("out", Point(0, 0), 0, instance_name="A")
        b = OpticalPort("in", Point(10, 0), 180, instance_name="B")
        d1, d2 = PhotonicDevice("A", "Straight"), PhotonicDevice("B", "Straight")
        d1.add_port(a)
        d2.add_port(b)
        net = PhotonicNet("NET1", [a, b], 10.0)
        circuit = PhotonicCircuit.from_extraction([a, b], {"A": d1, "B": d2}, [net])
        self.assertIs(a.net, net)
        self.assertEqual(circuit.unconnected_ports(), [])
        self.assertEqual(json.loads(json.dumps(circuit.to_dict()))["nets"][0]["length_um"], 10.0)

    def test_unconnected(self):
        p = OpticalPort("in", Point(0, 0), 0)
        c = PhotonicCircuit()
        c.add_port(p)
        self.assertEqual(c.unconnected_ports(), [p])

    def test_reject_double_connection(self):
        p = OpticalPort("in", Point(0, 0), 0)
        PhotonicNet("N1", [p])
        with self.assertRaises(ValueError):
            PhotonicNet("N2", [p])

if __name__ == "__main__":
    unittest.main()
