import os
import stat
import logging
import mimetypes

from fluentcore import date
from fluentcore import log
from fluentcore import fs
from fluentcore.system import disk

from openstack import client



LOG = log.getLogger(__name__)


class OpenstackManager:

    def __init__(self) -> None:
        self.openstack = client.OpenstackClient.create_instance()
