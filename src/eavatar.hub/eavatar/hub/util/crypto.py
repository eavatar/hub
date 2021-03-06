# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import hashlib
import base58
from Crypto.Hash import RIPEMD
import libnacl.public
import libnacl.secret

# The public key used for verifying peer tokens which are the identify certificates.
TOKEN_PUBLIC_KEY = ''

XID_PREFIX = b'\xea'
FINGER_PREFIX = b'\xef'


def generate_keypair(sk=None):
    """
    Generate a random key pair.
    :return:
    """
    if sk:
        keypair = libnacl.public.SecretKey(sk=sk)
    else:
        keypair = libnacl.public.SecretKey()

    return keypair.pk, keypair.sk


def generate_symmetric_key():
    """
    Generate a random key for symmetric encryption.

    :return:
    """
    box = libnacl.secret.SecretBox()
    return box.sk


def key_to_xid(key):
    """
    Generate an address from a public key.
    :param key: the 32-byte byte string.
    :return:
    """
    sha256 = hashlib.sha256()
    sha256.update(XID_PREFIX)
    sha256.update(key)
    sum = sha256.digest()
    addr = XID_PREFIX + key + sum[:2]

    return base58.b58encode(addr)


def xid_to_key(xid):
    """
    Retrieve the key from an XID.

    :param xid:
    :return:
    """
    val = base58.b58decode(xid)

    if len(val) != 35:
        return None

    prefix = val[0]
    if prefix != XID_PREFIX:
        return None

    key = val[1:33]
    sha256 = hashlib.sha256()
    sha256.update(XID_PREFIX)
    sha256.update(key)
    sum = sha256.digest()

    if val[-2:] != sum[:2]:
        return None

    return key


def validate_xid(addr):
    """
    Check if the provided address is valid or not.

    :param addr: address in base58 string.
    :return:
    """
    val = base58.b58decode(addr)
    #assert len(val) == 35

    if len(val) != 35:
        return False

    prefix = val[0]
    if prefix != XID_PREFIX:
        return False

    sha256 = hashlib.sha256()
    sha256.update(XID_PREFIX)
    sha256.update(val[1:33])
    sum = sha256.digest()

    if val[-2:] != sum[:2]:
        return False

    return True


def key_to_fingerprint(key):
    """
    Fingerprint is used to uniquely identify an entity without exposing extra information.
    :param key: the public key
    :return:
    """
    #assert len(key) == 32

    sha256 = hashlib.sha256()
    sha256.update(key)
    key_hash = sha256.digest()

    #print('%r' % key_hash)

    #assert len(key_hash) == 32

    ripemd = RIPEMD.new(key_hash)
    key_hash = ripemd.digest()

    #assert len(key_hash) == 20

    sha256 = hashlib.sha256()
    sha256.update(FINGER_PREFIX)
    sha256.update(key_hash)
    checksum = sha256.digest()
    result = FINGER_PREFIX+key_hash+checksum[:4]
    return base58.b58encode(result)


def validate_fingerprint(fingerprint):
    val = base58.b58decode(fingerprint)
    #print("Length: %d" % len(val) )
    if len(val) != 25:
        return False

    prefix = val[0]
    if prefix != FINGER_PREFIX:
        return False

    key_hash = val[1:21]
    sha256 = hashlib.sha256()
    sha256.update(FINGER_PREFIX)
    sha256.update(key_hash)
    given_checksum = sha256.digest()[:4]
    expected_checksum = val[-4:]
    if expected_checksum != given_checksum:
        return False

    return True


def xid_to_fingerprint(address):
    key = xid_to_key(address)
    if key:
        return key_to_fingerprint(key)
    else:
        return None


def key_to_peer_id(key):
    sha256 = hashlib.sha256()
    sha256.update(key)
    key_hash = sha256.digest()

    #print('%r' % key_hash)

    #assert len(key_hash) == 32

    ripemd = RIPEMD.new(key_hash)
    return ripemd.digest()


def calc_session_key(pk, sk):
    """
    Calculate the session key from a public key and secret key.

    :param pk: the counterpart's public key.
    :param sk: the own private key
    :return:
    """
    return libnacl.crypto_box_beforenm(pk, sk)


def secret_key_encrypt(sk, plaindata):
    """
    Encrypt a chunk of data with secret key symmetric encryption.

    :param sk:
    :param plaindata:
    :return:
    """
    box = libnacl.secret.SecretBox(sk)
    return box.encrypt(plaindata)


def secret_key_decrypt(sk, encrypted):
    box = libnacl.secret.SecretBox(sk)
    return box.decrypt(encrypted)


def secret_key_box(sk):
    return libnacl.secret.SecretBox(sk)


def public_key_encrypt(sender_sk, receiver_pk, plaintext):
    sender_box = libnacl.public.Box(sender_sk, receiver_pk)
    return sender_box.encrypt(plaintext)


def public_key_decrypt(receiver_sk, sender_pk, ciphertext):
    receiver_box = libnacl.public.Box(receiver_sk, sender_pk)
    return receiver_box.decrypt(ciphertext)


def public_key_box(sk, pk):
    return libnacl.public.Box(sk, pk)

