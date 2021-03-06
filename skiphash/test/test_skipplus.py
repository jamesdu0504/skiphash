import logging
import time

import pytest
import pytest_twisted
from pytest_mock import mocker
from twisted.internet import defer, reactor
from twisted.python import log

from skiphash.core import sleep
from skiphash.skipplus import SkipNode, SkipNodeFactory, SkipNodeReference

observer = log.PythonLoggingObserver()
observer.start()

# pylint: disable=maybe-no-member

@pytest_twisted.inlineCallbacks
def test_local_graph(caplog, mocker):
    caplog.set_level(logging.DEBUG, logger='vaud.core')
    caplog.set_level(logging.DEBUG, logger='vaud.skip')
    caplog.set_level(logging.INFO, logger='twisted')
    
    # This test does not check for correctness!
    # It only tries to run some skip+ nodes ;)

    factory = SkipNodeFactory(33000)

    for _ in range(10):
        factory.newNode()
    
    yield sleep(5)

    yield factory.shutdown()
