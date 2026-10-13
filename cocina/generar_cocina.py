# Modelo 3D de la cocina a partir del plano "Medidas_cocina.pdf".
# Unidades: mm. Origen: esquina interior inferior-izquierda de la cocina.
# Eje X = ancho (izq -> der), eje Y = fondo (abajo -> arriba en el plano).
import os, math
import FreeCAD as App, Part, Mesh

OUT = os.path.dirname(os.path.abspath(__file__))

# ---- Medidas leidas del plano (m -> mm) -------------------------------
ANCHO   = 6230   # 6,23 interior
FONDO   = 6250   # 6,25 interior
ALTO    = 2600   # altura de muros (SUPUESTA, no viene en el plano)
MURO    = 150    # espesor de muro (aprox. por el achurado)
ALTO_BARRA = 1100  # altura de la barra curva (SUPUESTA)

# Muro superior: 0,81 + 0,67 + 3,90 = 5,38 y luego pilar 0,87 x 0,45
# Muro izquierdo con pilar de 0,54 x 0,44 a 2,85 del muro superior
# Muro inferior: vano 0,94 + muro 2,57 + machon 0,13
# Muro derecho: 2,74 + pilar 0,40; abajo abierto hacia el salon
# Barra curva: cuarto de anillo R2,65 - R3,10, centro a 3,59 del muro izq
#              y 2,83 del muro inferior (calculado del dibujo a escala)
BARRA_CX, BARRA_CY, BARRA_RI, BARRA_RE = 3590, 2830, 2650, 3100
MURO_DER_DESDE = FONDO - 3700 + 450  # el muro derecho baja 3,70 desde arriba

doc = App.newDocument("Cocina")

def caja(nombre, x, y, lx, ly, h=ALTO, z=0):
    o = doc.addObject("Part::Box", nombre)
    o.Length, o.Width, o.Height = lx, ly, h
    o.Placement.Base = App.Vector(x, y, z)
    return o

# Piso
caja("Piso", -MURO, -MURO, ANCHO + 2*MURO, FONDO + 2*MURO, h=50, z=-50)

# Muros
caja("Muro_superior", -MURO, FONDO, 5380 + MURO, MURO)
caja("Pilar_sup_der", ANCHO - 870, FONDO - 450, 870 + MURO, 450 + MURO)
Y_PILAR_IZQ = FONDO - 2850 - 440
caja("Muro_izquierdo", -MURO, Y_PILAR_IZQ, MURO, FONDO - Y_PILAR_IZQ)  # abierto bajo el pilar
caja("Pilar_izquierdo", 0, Y_PILAR_IZQ, 540, 440)
caja("Muro_inferior", 940, -MURO, 2570, MURO)
caja("Machon_inferior", 940 + 2570, -300, 130, 300)
caja("Muro_derecho", ANCHO, MURO_DER_DESDE, MURO, FONDO - MURO_DER_DESDE)
caja("Pilar_der", ANCHO - 400, MURO_DER_DESDE - 400, 400 + MURO, 400)

# Barra curva (cuarto de anillo entre -90 y 0 grados)
ext = Part.makeCylinder(BARRA_RE, ALTO_BARRA, App.Vector(BARRA_CX, BARRA_CY, 0), App.Vector(0,0,1), 90)
inn = Part.makeCylinder(BARRA_RI, ALTO_BARRA, App.Vector(BARRA_CX, BARRA_CY, 0), App.Vector(0,0,1), 90)
anillo = ext.cut(inn)
anillo.rotate(App.Vector(BARRA_CX, BARRA_CY, 0), App.Vector(0,0,1), -90)
barra = doc.addObject("Part::Feature", "Barra_curva"); barra.Shape = anillo

doc.recompute()
objs = [o for o in doc.Objects if hasattr(o, "Shape")]
doc.saveAs(os.path.join(OUT, "cocina.FCStd"))
Part.export(objs, os.path.join(OUT, "cocina.step"))
Mesh.export(objs, os.path.join(OUT, "cocina.stl"))

# ---- Vista en planta (SVG) cortando a 1,0 m de altura ------------------
s = 0.1  # 1 px = 10 mm
pad = 60
minx, miny = -800, -800
W, H = (ANCHO + 1600) * s + 2*pad, (FONDO + 1600) * s + 2*pad
def P(x, y): return (pad + (x - minx) * s, H - pad - (y - miny) * s)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" '
       f'viewBox="0 0 {W:.0f} {H:.0f}" style="background:#fff">']
for o in objs:
    if o.Name == "Piso": continue
    sec = o.Shape.slice(App.Vector(0,0,1), 1000 if o.Name != "Barra_curva" else 500)
    for w in sec:
        pts = [P(v.x, v.y) for v in w.discretize(Distance=50)]
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"
        col = "#c0703a" if o.Name == "Barra_curva" else "#555"
        svg.append(f'<path d="{d}" fill="{col}" fill-opacity="0.35" stroke="{col}" stroke-width="1.5"/>')
def cota(x1, y1, x2, y2, txt, off=(0, 0)):
    (a, b), (c, d) = P(x1, y1), P(x2, y2)
    svg.append(f'<line x1="{a:.1f}" y1="{b:.1f}" x2="{c:.1f}" y2="{d:.1f}" stroke="#1565c0" stroke-width="1" marker-start="url(#m)" marker-end="url(#m)"/>')
    svg.append(f'<text x="{(a+c)/2+off[0]:.1f}" y="{(b+d)/2+off[1]:.1f}" font-family="sans-serif" font-size="14" fill="#1565c0" text-anchor="middle">{txt}</text>')
svg.insert(1, '<defs><marker id="m" markerWidth="8" markerHeight="8" refX="4" refY="4"><circle cx="4" cy="4" r="2" fill="#1565c0"/></marker></defs>')
cota(0, FONDO - 1200, ANCHO, FONDO - 1200, "6,23 m", (0, -6))
cota(670, 0, 670, FONDO, "6,25 m", (32, 40))
cota(BARRA_CX, BARRA_CY, BARRA_CX + BARRA_RE*math.cos(math.radians(-45)), BARRA_CY + BARRA_RE*math.sin(math.radians(-45)), "R3,10", (30, 0))
x, y = P(ANCHO/2, FONDO*0.62)
svg.append(f'<text x="{x:.0f}" y="{y:.0f}" font-family="sans-serif" font-size="22" text-anchor="middle" fill="#333">Cocina</text>')
x, y = P(BARRA_CX + 1500, BARRA_CY - 2300)
svg.append(f'<text x="{x:.0f}" y="{y:.0f}" font-family="sans-serif" font-size="14" fill="#c0703a">Barra curva</text>')
svg.append("</svg>")
open(os.path.join(OUT, "cocina_planta.svg"), "w").write("\n".join(svg))
print("OK", len(objs), "objetos")
