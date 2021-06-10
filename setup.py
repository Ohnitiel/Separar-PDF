import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

executables = [Executable('main.py', base=base,
                          target_name='Separar PDF')]

setup(
    name='Separar PDF',
    version='1.0',
    description='Separa arquivos PDF',
    executables=executables,
    options={"build_exe": {
        "packages": ["multiprocessing", "PySide2"],
        "build_exe": r"C:\Users\Qualifisio\Documents\Utilidades\Separar PDF",
        "includes": "atexit",
    }},
)
