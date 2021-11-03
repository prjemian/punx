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
        d = f.create_dataset("bytearray/data", data=[])
        d.attrs['axes'] = np.array("Words are these things".split(), dtype='S')
        d = f.create_dataset("stringarray/data", data=[])
        d.attrs['axes'] = "Words are these things".split()
        d = f.create_dataset("string/data", data=[])
        d.attrs['axes'] = "Words are these things"

    report = h5tree.Hdf5TreeView('test.h5').report()
    print("\n".join(report))

    reference = [
        'test.h5',
        '  bytearray',
        '    data:float64[0] = []',
        '      @axes = ["Words", "are", "these", "things"]',
        '  string',
        '    data:float64[0] = []',
        '      @axes = ["W", "o", "r", "d", "s", " ", "a", "r", "e", " ", "t",'
        ' "h", "e", "s", "e", " ", "t", "h", "i", "n", "g", "s"]',
        '  stringarray',
        '    data:float64[0] = []',
        '      @axes = ["Words", "are", "these", "things"]',
    ]

    assert "\n".join(report) == "\n".join(reference)
