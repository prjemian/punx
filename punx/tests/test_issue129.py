import h5py
import numpy as np
from punx import h5tree


def test_render_muliple_axes_attribute():
    """Ensure axes attributes are rendered as list of double quoted strings.

    @axes should be saved as an array of byte strings or an array of object
    strings because the NeXus standard says so. Single strings separated by
    whitespace or other charachters will not be rendered correctly.
    """
    with h5py.File('test.h5', 'w') as f:

        print()

        d = f.create_dataset("zero-term-byte-array/data", data=[])
        d.attrs['axes'] = np.array("zero terminated byte array".split(), dtype='S')
        print(f"{d.name} is converted to {type(d.attrs['axes'])} of {type(d.attrs['axes'][0])}")

        # HDF5 does not support unicode strings
        # d = f.create_dataset("unicode-array/data", data=[])
        # d.attrs['axes'] = np.array("unicode numpy array".split(), dtype='U')

        d = f.create_dataset("pystring-list/data", data=[])
        d.attrs['axes'] = "python native string list".split()
        print(f"{d.name} is converted to {type(d.attrs['axes'])} of {type(d.attrs['axes'][0])}")

        d = f.create_dataset("pystring/data", data=[])
        d.attrs['axes'] = "python native string"
        print(f"{d.name} is converted to {type(d.attrs['axes'])} of {type(d.attrs['axes'][0])}")

    report = h5tree.Hdf5TreeView('test.h5').report()
    print("\n".join(report))

    reference = [
        'test.h5',
        '  pystring',
        '    data:float64[0] = []',
        '      @axes = "python native string"',
        '  pystring-list',
        '    data:float64[0] = []',
        '      @axes = ["python", "native", "string", "list"]',
        '  zero-term-byte-array',
        '    data:float64[0] = []',
        '      @axes = ["zero", "terminated", "byte", "array"]',
    ]

    assert "\n".join(report) == "\n".join(reference)
