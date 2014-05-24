# -*- coding: utf-8 -*-

import hashlib


def generate_password_hash(value):
    return hashlib.sha256(value).hexdigest()
