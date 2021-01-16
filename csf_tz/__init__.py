# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe

<<<<<<< HEAD
__version__ = '1.7.3'
=======
__version__ = '1.7.2'
>>>>>>> a221704909c9ffb67abd68a6982d694198409c1d

def console(*data):
	frappe.publish_realtime('out_to_console', data, user=frappe.session.user)
