# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
"""
Avatar-specific functionality.
"""

import json
import falcon
from datetime import datetime
from cqlengine import columns
from cqlengine.models import Model

from eavatar.hub import views
from eavatar.hub import managers


# models #
class Avatar(Model):
    """
    Represents anything with an identity that can send or receive messages.
    """
    xid = columns.Text(primary_key=True, partition_key=True)
    owner_xid = columns.Text(default=None)  # the avatar who owns this one.
    parent_xid = columns.Text(default=None)  # the containment relationship.
    supervisor_xid = columns.Text(default=None)  # the avatar who can manage this one.
    kind = columns.Text(default='thing')
    created_at = columns.DateTime(default=datetime.utcnow())
    modified_at = columns.DateTime(default=datetime.utcnow())


class AvatarOwner(Model):
    """
    Represents relationship between an avatar and its owner.
    """
    owner_xid = columns.Text(primary_key=True)
    avatar_xid = columns.Text(primary_key=True, clustering_order="ASC")


# managers #
class AvatarManager(managers.BaseManager):
    model = Avatar

    def __init__(self):
        super(AvatarManager, self).__init__(self.model)


# views #
class AvatarCollection(views.ResourceBase):
    def on_get(self, req, resp):
        resp.body = views.EMPTY_LIST
        resp.status = falcon.HTTP_200

    def on_put(self, req, resp):
        try:
            data = json.load(req.stream, encoding=views.ENCODING)
            avatar = Avatar(xid=data.get('xid'), kind=data.get('kind'))
            avatar.save()
            resp.body = views.RESULT_OK
            resp.status = falcon.HTTP_200
        except:
            raise


class AvatarResource(views.ResourceBase):

    def on_get(self, req, resp, avatar_xid):
        rs = Avatar.objects(xid=avatar_xid).limit(1)
        if len(rs) == 0:
            raise falcon.HTTPNotFound

        resp.body = json.dumps(rs[0])
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp, avatar_xid):
        pass


