import unittest
from types import SimpleNamespace as Obj
from photonics.integration import from_router_v61


def port(name, inst, x):
    return Obj(name=name, position=Obj(x=x, y=0), direction=0, width=0.5,
               instance_name=inst, cell_name="Straight")


class RouterAdapterTests(unittest.TestCase):
    def test_conversion_and_independence(self):
        a, b, c = port("o1", "A", 0), port("o1", "B", 10), port("o1", "C", 20)
        da = Obj(name="A", cell_name="Straight", ports=[a])
        db = Obj(name="B", cell_name="Straight", ports=[b])
        dc = Obj(name="C", cell_name="Straight", ports=[c])
        net = Obj(name="NET1", ports=[a, b], length=10.0)
        circuit = from_router_v61([a, b, c], {"A": da, "B": db, "C": dc}, [net])
        self.assertEqual(len(circuit.devices), 3)
        self.assertEqual(circuit.nets[0].length, 10)
        self.assertEqual([p.qualified_name for p in circuit.unconnected_ports()], ["C.o1"])
        self.assertIs(circuit.devices["A"].ports[0], circuit.nets[0].ports[0])
        self.assertFalse(hasattr(a, "net"))

    def test_shared_port_rejected(self):
        a, b, c = port("o1", "A", 0), port("o1", "B", 10), port("o1", "C", 20)
        devices = {p.instance_name: Obj(name=p.instance_name, cell_name="Straight", ports=[p])
                   for p in (a, b, c)}
        nets = [Obj(name="N1", ports=[a, b], length=10),
                Obj(name="N2", ports=[a, c], length=20)]
        with self.assertRaisesRegex(ValueError, "already belongs to a net"):
            from_router_v61([a, b, c], devices, nets)

    def test_unknown_port_rejected(self):
        a, b = port("o1", "A", 0), port("o1", "B", 10)
        with self.assertRaisesRegex(ValueError, "unknown port"):
            from_router_v61([a], {}, [Obj(name="N1", ports=[a, b], length=10)])

if __name__ == "__main__":
    unittest.main()
