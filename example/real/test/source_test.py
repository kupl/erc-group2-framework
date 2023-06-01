from src.source import Progbar
import numpy as np

def test_progbar_update():
    n = 2
    input_arr = np.random.random((n, n, n))

    bar = Progbar(n)
    for i, arr in enumerate(input_arr):
        bar.update(i, list(arr))

def test_progbar_update_verbose():
    n = 2
    input_arr = np.random.random((n, n, n))

    bar = Progbar(n, verbose=2)
    for i, arr in enumerate(input_arr):
        bar.update(i, list(arr))

def test_progbar_update_no_values():
    n = 2

    bar = Progbar(n)
    for i in range(n):
        bar.update(i)


def test_progbar_add():
    n = 2
    input_arr = np.random.random((n, n, n))

    bar = Progbar(n)
    for i, arr in enumerate(input_arr):
        bar.add(i, list(arr))

def test_progbar_update_error():
    n = 2
    input_arr = np.random.random((n, n, n))

    bar = Progbar(None)
    for i, arr in enumerate(input_arr):
        bar.update(i, list(arr))

def test_progbar_add_error():
    n = 2
    input_arr = np.random.random((n, n, n))

    bar = Progbar(None)
    for i, arr in enumerate(input_arr):
        bar.add(i, list(arr))