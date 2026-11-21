"""npy -- the npython command line tool.

npy is the CLI of npython, the Python-compatible interpreter that is
meant to be "python, but better".

    npy run file.py [args...]   run file.py with npython
    npy install pkg [pkg...]    install packages into npython (via pip)
    npy uninstall pkg [...]     uninstall packages from npython
    npy list [args...]          list packages installed for npython
    npy shell                   start the npython interactive interpreter
    npy --version                 show the npy / npython version

Any other invocation (``npy``, ``npy file.py``, ``npy -c ...``) falls
back to a regular Python interpreter: with npy, only ``npy run`` is
npython, everything else is Python.

The file extension stays ``.py``: npython runs the same Python code as
Python, and every Python library -- standard library or external --
works natively with npython.
"""

__version__ = "1.1"
