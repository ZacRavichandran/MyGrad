""" Test `numerical_gradient`, `numerical_derivative`, and `broadcast_check`"""

from tests.utils.numerical_gradient import numerical_gradient, broadcast_check, numerical_derivative

import hypothesis.extra.numpy as hnp
import hypothesis.strategies as st
from hypothesis import given

import numpy as np


def unary_func(x): return x ** 2


def binary_func(x, y): return x * y ** 2


def ternary_func(x, y, z): return z * x * y ** 2


def test_broadcast_check1():
    x = np.empty((3, 1, 4))
    y = np.empty((4,))
    z = np.empty((3, 2, 4))
    x_args, y_args, z_args = broadcast_check(x, y, z)
    assert x_args == dict(new_axes=tuple(), keepdim_axes=(1,))
    assert y_args == dict(new_axes=(0, 1), keepdim_axes=tuple())
    assert z_args == dict(new_axes=tuple(), keepdim_axes=tuple())


def test_broadcast_check2():
    # no broadcasting
    x = np.empty((3,))
    y = np.empty((3,))
    x_args, y_args = broadcast_check(x, y)
    assert x_args == dict(new_axes=tuple(), keepdim_axes=tuple())
    assert y_args == dict(new_axes=tuple(), keepdim_axes=tuple())


def test_broadcast_check3():
    x = np.empty((3, 1, 4))
    y = np.empty((5, 3, 2, 4))
    x_args, y_args = broadcast_check(x, y)
    assert x_args == dict(new_axes=(0,), keepdim_axes=(2,))
    assert y_args == dict(new_axes=tuple(), keepdim_axes=tuple())


@given(x=st.decimals(-100, 100))
def test_numerical_derivative(x):
    num_der = numerical_derivative(unary_func, x)
    assert np.isclose(float(num_der), float(x) * 2.)


@given(st.data())
def test_numerical_gradient_no_broadcast(data):

    x = data.draw(hnp.arrays(shape=hnp.array_shapes(max_side=3, max_dims=3),
                             dtype=float,
                             elements=st.floats(-100, 100)))

    y = data.draw(hnp.arrays(shape=x.shape,
                             dtype=float,
                             elements=st.floats(-100, 100)))

    z = data.draw(hnp.arrays(shape=x.shape,
                             dtype=float,
                             elements=st.floats(-100, 100)))

    grad = data.draw(hnp.arrays(shape=x.shape,
                                dtype=float,
                                elements=st.floats(-100, 100)))


    # check variable-selection
    assert numerical_gradient(unary_func, x, back_grad=grad, vary_ind=[])[0] is None

    # no broadcast
    dx = numerical_gradient(unary_func, x, back_grad=grad)
    assert np.allclose(dx, grad * 2 * x)

    dx, dy = numerical_gradient(binary_func, x, y, back_grad=grad)
    assert np.allclose(dx, grad * y ** 2)
    assert np.allclose(dy, grad * 2 * x * y)

    dx, dy, dz = numerical_gradient(ternary_func, x, y, z, back_grad=grad)
    assert np.allclose(dx, grad * z * y ** 2)
    assert np.allclose(dy, grad * z * 2 * x * y)
    assert np.allclose(dz, grad * x * y ** 2)


@given(st.data())
def test_numerical_gradient_x_broadcast(data):

    x = data.draw(hnp.arrays(shape=(3, 4),
                             dtype=float,
                             elements=st.floats(-100, 100)))

    y = data.draw(hnp.arrays(shape=(2, 3, 4),
                             dtype=float,
                             elements=st.floats(-100, 100)))

    grad = data.draw(hnp.arrays(shape=(2, 3, 4),
                                dtype=float,
                                elements=st.floats(-100, 100)))

    # broadcast x
    dx, dy = numerical_gradient(binary_func, x, y, back_grad=grad)
    assert np.allclose(dx, (grad * y ** 2).sum(axis=0))
    assert np.allclose(dy, grad * 2 * x * y)


@given(st.data())
def test_numerical_gradient_y_broadcast(data):

    y = data.draw(hnp.arrays(shape=(3, 4),
                             dtype=float,
                             elements=st.floats(-100, 100)))

    x = data.draw(hnp.arrays(shape=(2, 3, 4),
                             dtype=float,
                             elements=st.floats(-100, 100)))

    grad = data.draw(hnp.arrays(shape=(2, 3, 4),
                                dtype=float,
                                elements=st.floats(-100, 100)))

    # broadcast x
    dx, dy = numerical_gradient(binary_func, x, y, back_grad=grad)
    assert np.allclose(dx, grad * y ** 2)
    assert np.allclose(dy, (grad * 2 * x * y).sum(axis=0))


@given(st.data())
def test_numerical_gradient_xy_broadcast(data):

    x = data.draw(hnp.arrays(shape=(2, 1, 4),
                             dtype=float,
                             elements=st.floats(-100, 100)))

    y = data.draw(hnp.arrays(shape=(1, 3, 4),
                             dtype=float,
                             elements=st.floats(-100, 100)))

    grad = data.draw(hnp.arrays(shape=(2, 3, 4),
                                dtype=float,
                                elements=st.floats(-100, 100)))

    # broadcast x
    dx, dy = numerical_gradient(binary_func, x, y, back_grad=grad)
    x_grad = (grad * y ** 2).sum(axis=1, keepdims=True)
    y_grad = (grad * 2 * x * y).sum(axis=0, keepdims=True)
    assert np.allclose(dx, x_grad)
    assert np.allclose(dy, y_grad)
