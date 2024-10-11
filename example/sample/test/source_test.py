from src.source import Progbar
import numpy as np

def test_progbar_neg1():
    n = 2
    input_arr = np.random.random((n, n, n))

    bar = Progbar(None, interval=1)
    for i, arr in enumerate(input_arr):
        bar.update(i, list(arr))

def test_progbar_neg2():
    n = 2
    input_arr = np.random.random((n, n, n))

    bar = Progbar(None, interval=1)
    for i, arr in enumerate(input_arr):
        bar.add(i, list(arr))

def test_progbar_pos1():
    n = 2
    input_arr = np.random.random((n, n, n))

    bar = Progbar(n)
    for i, arr in enumerate(input_arr):
        bar.update(i, list(arr))

def test_progbar_pos2():
    n = 2
    input_arr = np.random.random((n, n, n))

    bar = Progbar(n, verbose=2)
    for i, arr in enumerate(input_arr):
        bar.update(i, list(arr))

def test_progbar_pos3():
    n = 2
    input_arr = np.random.random((n, n, n))

    bar = Progbar(n, verbose=2, width=0)
    for i, arr in enumerate(input_arr):
        bar.update(i, list(arr))

def test_progbar_pos4():
    n = 2
    input_arr = np.random.random((n, n, n))

    bar = Progbar(n)
    for i, arr in enumerate(input_arr):
        bar.update(i, list(arr))

def test_progbar_pos5():
    n = 2
    input_arr = np.random.random((n, n, n))

    bar = Progbar(n, width=0)
    for i, arr in enumerate(input_arr):
        bar.update(i, list(arr))

def test_progbar_pos6():
    n = 2
    input_arr = np.random.random((n, n, n))

    bar = Progbar(n, interval=0.01)
    for i, arr in enumerate(input_arr):
        bar.add(i, list(arr))

def test_progbar_pos7():
    n = 2
    input_arr = np.random.random((n, n, n))

    bar = Progbar(n, verbose=2, interval=0.01)
    for i, arr in enumerate(input_arr):
        bar.add(i, list(arr))

def test_progbar_pos8():
    n = 2
    input_arr = np.random.random((n, n, n))

    bar = Progbar(n, width=0, verbose=2, interval=0.01)
    for i, arr in enumerate(input_arr):
        bar.add(i, list(arr))


