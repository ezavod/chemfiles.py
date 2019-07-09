# -*- coding=utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from ctypes import c_double, c_uint64, c_char_p

from .utils import CxxPointer, _call_with_growing_buffer, string_type
from .misc import ChemfilesError
from .property import Property


class Atom(CxxPointer):
    """
    An :py:class:`Atom` is a particle in the current :py:class:`Frame`. It
    stores the atom name, type, mass, and charge.

    The atom name is usually an unique identifier (``'H1'``, ``'C_a'``) while
    the atom type will be shared between all particles of the same type:
    ``'H'``, ``'Ow'``, ``'CH3'``.

    Parameters
    ----------
    name: str
        Name of the atom.
    type: str, optional
        Type of the atom, default to the same as ``name``

    Examples
    --------

    >>> # Create an atom with same name and type
    >>> atom = Atom('F')
    >>> atom.name
    'F'
    >>> atom.type
    'F'

    >>> # Create an atom with different name and type
    >>> atom = Atom('F2', 'F')
    >>> atom.name
    'F2'
    >>> atom.type
    'F'
    """

    def __init__(self, name, type=None):
        ptr = self.ffi.chfl_atom(name.encode('utf8'))
        super(Atom, self).__init__(ptr, is_const=False)
        if type:
            self.type = type

    def __copy__(self):
        return Atom.from_mutable_ptr(self.ffi.chfl_atom_copy(self.ptr))

    def __repr__(self):
        name = self.name
        type = self.type
        if type == name:
            return "Atom('{}')".format(name)
        else:
            return "Atom('{}', '{}')".format(name, type)

    @property
    def mass(self):
        """
        The atom mass, in atomic mass units.

        Examples
        --------

        >>> atom = Atom('F')
        >>> atom.mass
        18.9984032
        >>> atom.mass = 19.5
        >>> atom.mass
        19.5
        """
        mass = c_double()
        self.ffi.chfl_atom_mass(self.ptr, mass)
        return mass.value

    @mass.setter
    def mass(self, mass):
        self.ffi.chfl_atom_set_mass(self.mut_ptr, c_double(mass))

    @property
    def charge(self):
        """
        The atom charge, in number of the electron charge *e*.

        Examples
        --------

        >>> atom = Atom('F')
        >>> atom.charge
        0.0
        >>> atom.charge = -1
        >>> atom.charge
        -1.0
        """
        charge = c_double()
        self.ffi.chfl_atom_charge(self.ptr, charge)
        return charge.value

    @charge.setter
    def charge(self, charge):
        self.ffi.chfl_atom_set_charge(self.mut_ptr, c_double(charge))

    @property
    def name(self):
        """
        The atom name.

        Examples
        --------

        >>> atom = Atom('F')
        >>> atom.name
        'F'
        >>> atom = Atom('F2', 'F')
        >>> atom.name
        'F2'
        """
        return _call_with_growing_buffer(
            lambda buffer, size: self.ffi.chfl_atom_name(self.ptr, buffer, size),
            initial=32
        )

    @name.setter
    def name(self, name):
        self.ffi.chfl_atom_set_name(self.mut_ptr, name.encode('utf8'))

    @property
    def type(self):
        """
        The atom type.

        Examples
        --------

        >>> atom = Atom('F')
        >>> atom.type
        'F'
        >>> atom = Atom('F2', 'F')
        >>> atom.type
        'F'
        """
        return _call_with_growing_buffer(
            lambda buffer, size: self.ffi.chfl_atom_type(self.ptr, buffer, size),
            initial=32
        )

    @type.setter
    def type(self, type):
        self.ffi.chfl_atom_set_type(self.mut_ptr, type.encode('utf8'))

    @property
    def full_name(self):
        """
        The full name of the atom, as guessed from its type.

        For example, the full name for ``'He'`` is ``'Helium'``. If the name can
        not be found, this will be an empty string.

        Examples
        --------

        >>> atom = Atom('F')
        >>> atom.full_name
        'Fluorine'
        >>> atom = Atom('Wat', 'Wat')
        >>> atom.full_name
        ''
        """
        return _call_with_growing_buffer(
            lambda buffer, size: self.ffi.chfl_atom_full_name(self.ptr, buffer, size),
            initial=64,
        )

    @property
    def vdw_radius(self):
        """
        The Van der Waals radius of the atom, as guessed from its type.

        If the radius can not be found, this will be 0.

        Examples
        --------

        >>> atom = Atom('F')
        >>> atom.vdw_radius
        1.5
        >>> atom = Atom('Wat', 'Wat')
        >>> atom.vdw_radius
        0.0
        """
        radius = c_double()
        self.ffi.chfl_atom_vdw_radius(self.ptr, radius)
        return radius.value

    @property
    def covalent_radius(self):
        """
        The covalent radius of the atom, as guessed from its type.

        If the radius can not be found, this will be 0.

        Examples
        --------

        >>> atom = Atom('F')
        >>> atom.covalent_radius
        0.71
        >>> atom = Atom('Wat', 'Wat')
        >>> atom.covalent_radius
        0.0
        """
        radius = c_double()
        self.ffi.chfl_atom_covalent_radius(self.ptr, radius)
        return radius.value

    @property
    def atomic_number(self):
        """
        The atomic number of the atom, as guessed from its type.

        If the atomic number can not be found, this will be 0.

        Examples
        --------

        >>> atom = Atom('F')
        >>> atom.atomic_number
        9
        >>> atom = Atom('Wat', 'Wat')
        >>> atom.atomic_number
        0
        """
        number = c_uint64()
        self.ffi.chfl_atom_atomic_number(self.ptr, number)
        return number.value

    def __iter__(self):
        # Disable automatic iteration from __getitem__
        raise TypeError("can not iterate over an atom")

    def __getitem__(self, name):
        """
        Get a property of this atom with the given ``name``.

        Parameters
        ----------
        name: str
            The name of the property.

        Raises
        ------
        ChemfilesError
            If the property does not exists in this atom.

        Examples
        --------
        >>> atom = Atom('F')
        >>> atom['is_hetatm'] = False
        >>> atom['is_hetatm']
        False
        >>> # Non-existing property
        >>> atom['not here']
        Traceback (most recent call last):
        ...
        chemfiles.misc.ChemfilesError: can not find a property named 'not here' in this atom
        """
        if not isinstance(name, string_type):
            raise TypeError(
                "Invalid type {} for an atomic property name".format(type(name))
            )
        ptr = self.ffi.chfl_atom_get_property(self.ptr, name.encode('utf8'))
        return Property.from_mutable_ptr(ptr).get()

    def __setitem__(self, name, value):
        """
        Set a property of this atom, with the given ``name`` and ``value``.

        The new value overwrite any pre-existing property with the same name.

        Parameters
        ----------
        name: str
            The name of the property.
        value: bool or float or str or 3D vector
            The value of the property.

        Examples
        --------
        >>> atom = Atom('F')
        >>> atom['pdb_icode'] = 'A'
        >>> atom['pdb_icode']
        'A'
        """
        if not isinstance(name, string_type):
            raise TypeError(
                "invalid type {} for a property name".format(type(name))
            )
        property = Property(value)
        self.ffi.chfl_atom_set_property(
            self.mut_ptr, name.encode('utf8'), property.ptr
        )

    def list_properties(self):
        """
        Get the name of all properties in this atom.

        Examples
        --------
        >>> atom = Atom('F')
        >>> atom['pdb_icode'] = 'A'
        >>> atom['is_hetatm'] = False
        >>> sorted(atom.list_properties())
        ['is_hetatm', 'pdb_icode']
        """
        count = c_uint64()
        self.ffi.chfl_atom_properties_count(self.ptr, count)
        count = count.value

        StringArray = c_char_p * count
        names = StringArray()
        self.ffi.chfl_atom_list_properties(self.ptr, names, count)
        return list(map(lambda n: n.decode('utf8'), names))
