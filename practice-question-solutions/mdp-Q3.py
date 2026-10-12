import sys

v=[0,0,0]

def qa():
   l = .2 * (4 + .5 * v[1]) + .8 * (-10 + .5 * v[2])
   r = .8 * (4 + .5 * v[1]) + .2 * (-10 + .5 * v[2])

   if l >= r:
     return (l,"left")
   else:
     return (r,"right")

def qb():
   l = .8 * (2 + .5 * v[0]) + .2 * (-10 + .5 * v[2])
   r = .2 * (2 + .5 * v[0]) + .8 * (-10 + .5 * v[2])

   if l >= r:
     return (l,"left")
   else:
     return (r,"right")

def qc():
   l = .2 * (2 + .5 * v[0]) + .8 * (4 + .5 * v[1])
   r = .8 * (2 + .5 * v[0]) + .2 * (4 + .5 * v[1])

   if l >= r:
     return (l,"left")
   else:
     return (r,"right")

#=====
print (v)
for i in range (10):
   aa = qa()
   bb = qb()
   cc = qc()
   print (aa[1],bb[1],cc[1])
   v = [aa[0],bb[0],cc[0]]
   print (v)
   
