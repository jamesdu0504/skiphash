import logging
import time

import pytest
import pytest_twisted
from pytest_mock import mocker
from twisted.internet import defer, reactor
from twisted.internet.address import IPv4Address
from twisted.python import log

from skiphash import thisHost
from skiphash.core import CopyableBitArray, Node, NodeFactory, NodeReference, randomBitArray, remoteMethod

observer = log.PythonLoggingObserver()
observer.start()

# pylint: disable=maybe-no-member

@pytest.fixture(scope="function")
def nodes(caplog, mocker):
    caplog.set_level(logging.DEBUG, logger='vaud.core')
    caplog.set_level(logging.DEBUG, logger='twisted')

    factory = NodeFactory(30000)
    for _ in range(3):
        factory.newNode()

    yield factory.nodes

    return pytest_twisted.blockon(factory.shutdown())

@pytest_twisted.inlineCallbacks
def test_remote_interaction(caplog, mocker, nodes):
    caplog.set_level(logging.DEBUG, logger='vaud.core')
    caplog.set_level(logging.DEBUG, logger='twisted')
    
    n = nodes[0]

    # add a mocked 'test' method
    mocker.patch.object(n, "test", create=True)
    n.test.return_value = "value" # set a return value
    # emulating the @remoteMethod decorator
    n.test.is_remote_method = True
    remoteMethod.methodNames.add("test")

    # call n.test and its remote-alias locally
    assert n.test() == "value"
    assert n.remote_test() == "value"

    # implicitly call n.test remotely via its NodeReference object
    returnValue = yield n.reference.test()
    assert returnValue == "value"

    # explicitly call n.test remotely via its NodeReference object
    n1Remote = yield n.reference.remote
    returnValue = yield n1Remote.callRemote("test")
    assert returnValue == "value"

@pytest_twisted.inlineCallbacks
def test_reference_copying(caplog, mocker, nodes):
    caplog.set_level(logging.DEBUG, logger='vaud.core')
    caplog.set_level(logging.DEBUG, logger='twisted')

    n1, n2 = nodes[0:2]

    # add a mocked 'test' method
    mocker.patch.object(n2, "test", create=True)
    n2.test.return_value = n1.reference # set a reference as the return value
    # emulating the @remoteMethod decorator
    n2.test.is_remote_method = True
    remoteMethod.methodNames.add("test")

    # implicitly call n2.test remotely via its NodeReference object
    returnValue = yield n2.reference.test()
    assert returnValue == n1.reference

@pytest_twisted.inlineCallbacks
def test_bytearray_copying(caplog, mocker, nodes):
    caplog.set_level(logging.DEBUG, logger='vaud.core')
    caplog.set_level(logging.DEBUG, logger='twisted')

    n = nodes[2]

    # add a mocked 'test' method
    mocker.patch.object(n, "test", create=True)
    bitArray = randomBitArray(8)
    print(bitArray)
    n.test.return_value = CopyableBitArray(bitArray) # set a bitarray as the return value
    # emulating the @remoteMethod decorator
    n.test.is_remote_method = True
    remoteMethod.methodNames.add("test")

    # implicitly call n2.test remotely via its NodeReference object
    returnValue = yield n.reference.test()
    assert returnValue == bitArray
