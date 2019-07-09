# -*- coding=utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import unittest
import copy

from chemfiles import Atom, ChemfilesError
from _utils import remove_warnings


class TestAtom(unittest.TestCase):
    def test_repr(self):
        self.assertEqual(Atom("He").__repr__(), "Atom('He')")
        self.assertEqual(Atom("He-3", "He").__repr__(), "Atom('He-3', 'He')")

    def test_copy(self):
        atom = Atom("He")
        cloned = copy.copy(atom)

        self.assertEqual(atom.name, "He")
        self.assertEqual(cloned.name, "He")

        atom.name = "Zn"
        self.assertEqual(atom.name, "Zn")
        self.assertEqual(cloned.name, "He")

    def test_very_long_name(self):
        atom = Atom("He" * 128)
        self.assertEqual(atom.name, "He" * 128)

    def test_name(self):
        atom = Atom("He")
        self.assertEqual(atom.name, "He")
        self.assertEqual(atom.full_name, "Helium")

        atom.name = "Zn"
        self.assertEqual(atom.name, "Zn")

    def test_type(self):
        atom = Atom("He")
        self.assertEqual(atom.type, "He")
        self.assertEqual(atom.full_name, "Helium")

        atom.type = "Zn"
        self.assertEqual(atom.type, "Zn")
        self.assertEqual(atom.full_name, "Zinc")

        atom = Atom("He2", "H")
        self.assertEqual(atom.name, "He2")
        self.assertEqual(atom.type, "H")

    def test_mass(self):
        atom = Atom("He")
        self.assertAlmostEqual(atom.mass, 4.002602, 6)
        atom.mass = 1.0
        self.assertEqual(atom.mass, 1.0)

    def test_charge(self):
        atom = Atom("He")
        self.assertEqual(atom.charge, 0.0)
        atom.charge = -1.5
        self.assertEqual(atom.charge, -1.5)

    def test_radii(self):
        self.assertAlmostEqual(Atom("He").vdw_radius, 1.4, 2)
        self.assertAlmostEqual(Atom("He").covalent_radius, 0.32, 3)

        self.assertEqual(Atom("H1").vdw_radius, 0)
        self.assertEqual(Atom("H1").covalent_radius, 0)

    def test_atomic_number(self):
        self.assertEqual(Atom("He").atomic_number, 2)
        self.assertEqual(Atom("H1").atomic_number, 0)

    def test_property(self):
        atom = Atom("He")

        atom["foo"] = 3
        self.assertEqual(atom["foo"], 3.0)

        atom["foo"] = False
        self.assertEqual(atom["foo"], False)

        with remove_warnings:
            with self.assertRaises(ChemfilesError):
                _ = atom["bar"]

            with self.assertRaises(TypeError):
                atom[3] = "test"

            with self.assertRaises(TypeError):
                _ = atom[3]

        # Check that enabling indexing/__getitem__ did not enable iteration
        with self.assertRaises(TypeError):
            for i in atom:
                pass

        atom["bar"] = "baz"
        self.assertEqual(set(atom.list_properties()), {"bar", "foo"})


if __name__ == "__main__":
    unittest.main()
