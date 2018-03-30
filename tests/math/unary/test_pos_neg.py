from tests.wrappers.unary_func import fwdprop_test_factory, backprop_test_factory
from mygrad import positive, negative
import numpy as np


@fwdprop_test_factory(mygrad_func=positive, true_func=np.positive)
def test_positive_fwd(): pass


@backprop_test_factory(mygrad_func=positive)
def test_positive_backward(): pass


@fwdprop_test_factory(mygrad_func=negative, true_func=np.negative)
def test_negative_fwd(): pass


@backprop_test_factory(mygrad_func=negative)
def test_negative_backward(): pass