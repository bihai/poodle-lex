# Copyright (c) 1995-2014 by Fredrik Lundh
# By obtaining, using, and/or copying this software and/or its associated 
# documentation, you agree that you have read, understood, and will comply with
# the following terms and conditions:
#
# Permission to use, copy, modify, and distribute this software and its 
# associated documentation for any purpose and without fee is hereby granted, 
# provided that the above copyright notice appears in all copies, and that both 
# that copyright notice and this permission notice appear in supporting 
# documentation, and that the name of Secret Labs AB or the author not be used 
# in advertising or publicity pertaining to distribution of the software 
# without specific, written prior permission.
#
# SECRET LABS AB AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS 
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN 
# NO EVENT SHALL SECRET LABS AB OR THE AUTHOR BE LIABLE FOR ANY SPECIAL, 
# INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM 
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR 
# PERFORMANCE OF THIS SOFTWARE.

import xml.etree.cElementTree as ET
import functools

# Utility 
class _E(object):
    def __call__(self, tag, *children, **attrib):
        elem = ET.Element(tag, attrib)
        for item in children:
            if isinstance(item, dict):
                elem.attrib.update(item)
            elif isinstance(item, basestring):
                if len(elem):
                    elem[-1].tail = (elem[-1].tail or "") + item
                else:
                    elem.text = (elem.text or "") + item
            elif ET.iselement(item):
                elem.append(item)
            else:
                raise TypeError("bad argument: %r" % item)
        return elem
    def __getattr__(self, tag):
        return functools.partial(self, tag)