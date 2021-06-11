# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe

__version__ = '2.0.0'

def console(*data):
    frappe.publish_realtime('out_to_console', data, user=frappe.session.user)

connect = frappe.connect

def custom_connect(*args, **kwargs):
    out = connect(*args, **kwargs)
    if frappe.conf.auto_commit_on_many_writes:
        frappe.db.auto_commit_on_many_writes = 1

    return out

frappe.connect = custom_connect
