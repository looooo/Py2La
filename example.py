# -*- coding: utf-8 -*-
#!/usr/bin/env python

from __future__ import division
from sympy import *

#L \title{FreeCAD-Doc}
#L \author{open source user}
#L \maketitle

#L \section{simple latex text}

#L text -> on
"""
The idea of this documentation-tool is to use python 
for easy math documentation in latex. So that CAD-Parts and 
the calculation of stress, savetyfactor... can be documented 
and get actualised when something is changed in the cad tool.\\
This example is a test-file and should be updated if new stuff is introduced.
"""
#L text -> off


#L \section{simple latex math}


#L equation -> on
"mm"
"""a description"""
a = 30		#unit#		##short description##
b = a ** 2 	#unit#		##short description##
c = b * a	#unit#		##short description##
d = a / c	#unit#		##short description##
e = Symbol('e')
g = integrate(e**2,(e,0,1))
#L equation -> off

#L text->on
#L \section{todo}
"- Utf-8\\- sympy printing\\- functions\\- matplotlib "