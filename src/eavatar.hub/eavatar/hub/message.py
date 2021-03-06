# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
"""
Module for message manipulation.
"""

import ujson as json
import falcon
from cqlengine import columns
from cqlengine.models import Model

from eavatar.hub.views import ResourceBase
from eavatar.hub.managers import BaseManager


class Message(Model):
    """
    Represents messages received by an avatar. A message consists of:
    * a command
      Indicates if the message is a request or a response.
      For a response, 'ERR' is used for reporting error, 'RES' is to return successful result.
      Some commands from HTTP/1.1 are defined.
      - 'GET': The result of a GET request might be cached by the hub.
      - 'POST':
      - 'PUT':
      - 'DELETE':
      The URI part is designated as 'Destination' header.

    * a headers
      Contains metadata regarding the payload. Some well-known headers are:
      - 'Content-type': the content type of the payload, e.g. 'application/json'.
      - 'Content-length': the length in bytes of the payload
      - 'Destination': the resource intended to be the receiver on final target.
    * a payload(optional)
      The content to be sent as is. That is, the hub doesn't interpret or modify the payload.

    """
    avatar_xid = columns.Text(primary_key=True, partition_key=True)
    message_id = columns.TimeUUID(primary_key=True, clustering_order="DESC")
    command = columns.Text(default='POST')
    headers = columns.Text()
    payload = columns.Text(default=None)


class MessageManager(BaseManager):
    model = Message

    def __init__(self):
        super(MessageManager, self).__init__(Message)


class MessageStore(ResourceBase):

    def on_get(self, req, resp, avatar_xid):
        """
        Gets last N messages of the specified avatar.

        :param req:
        :param resp:
        :param avatar_xid: the avatar's XID.
        :return:
        """
        qs = Message.objects(avatar_xid=avatar_xid).limit(10)
        result = []
        for m in qs:
            result.append(m)

        resp.body = json.dumps(result)
        resp.status = falcon.HTTP_200

