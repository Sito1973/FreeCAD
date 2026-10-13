import FreeCAD as App, Part, Mesh, sys
out = "/home/user/FreeCAD/cocina_prueba"
import os; os.makedirs(out, exist_ok=True)
doc = App.newDocument("Cocina")
# medidas en mm: mesón 2400x600x900, nevera 700x700x1800
meson = doc.addObject("Part::Box","Meson"); meson.Length=2400; meson.Width=600; meson.Height=900
nevera = doc.addObject("Part::Box","Nevera"); nevera.Length=700; nevera.Width=700; nevera.Height=1800
nevera.Placement.Base = App.Vector(2450,0,0)
doc.recompute()
doc.saveAs(out+"/cocina_prueba.FCStd")
Part.export([meson,nevera], out+"/cocina_prueba.step")
Mesh.export([meson,nevera], out+"/cocina_prueba.stl")
print("OK", App.Version()[:3])
