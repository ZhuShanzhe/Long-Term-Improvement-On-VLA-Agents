"""Packing fixtures attached to the existing native Panda/OSC environment.

All manipulation after reset is MuJoCo dynamics. Mark/lot tags are object-local
visual geometry. No camera mask, visibility toggle, or action-time teleport.
"""
import xml.etree.ElementTree as ET
import numpy as np
SURFACE=.424
ITEM_STARTS=[(.12,-.30,SURFACE),(.12,-.12,SURFACE),(.12,.06,SURFACE)]
LAYOUTS={
 'partition_tray':[(-.12,-.02,SURFACE),(-.12,.29,SURFACE)],
 'opaque_carton':[(-.12,-.02,SURFACE),(-.12,.29,SURFACE)],
 'handover_tote':[(-.12,-.02,SURFACE),(.11,.32,SURFACE)],
}
SIZES=[(.095,.110),(.120,.130)]
HEIGHTS={'partition_tray':.080,'opaque_carton':.120,'handover_tote':.140}
KINDS=['cream_cheese','butter','cookies']
COLORS={'red':(.85,.08,.06,1),'green':(.06,.70,.12,1),'blue':(.06,.15,.88,1)}
BATCH_COLORS={'A':(.95,.85,.06,1),'B':(.06,.80,.85,1),'C':(.85,.06,.65,1),'D':(.95,.40,.05,1),'E':(.40,.10,.75,1),'F':(.55,.55,.55,1)}
LETTERS={'A':'abcefg','B':'cdefg','C':'adef','D':'bcdeg','E':'adefg','F':'aefg'}
SEGMENTS={'a':(0,.010,.007,.0015),'g':(0,0,.007,.0015),'d':(0,-.010,.007,.0015),
 'f':(-.007,.005,.0015,.005),'b':(.007,.005,.0015,.005),'e':(-.007,-.005,.0015,.005),'c':(.007,-.005,.0015,.005)}
def vec(x):return ' '.join(str(float(v)) for v in x)
def box(parent,name,size,pos=(0,0,0),rgba=(.55,.43,.30,1),mass='.03',collide=True):
    if collide:ET.SubElement(parent,'geom',name=name+'_collision',type='box',group='0',size=vec(size),pos=vec(pos),rgba=vec(rgba),mass=mass,friction='.8 .005 .0001')
    return ET.SubElement(parent,'geom',name=name,type='box',group='1',size=vec(size),pos=vec(pos),rgba=vec(rgba),mass='0',contype='0',conaffinity='0')
def tag(parent,item,field,z):
    # Tiny protrusion beyond the original bounding surface avoids z fighting.
    root=ET.SubElement(parent,'body',name=f'pack_{item}_{field}_tag',pos=vec((0,0,z)))
    if z<0:root.set('quat','0 1 0 0')
    box(root,f'pack_{item}_{field}_base',(.030,.028,.0005),rgba=(.95,.95,.95,1),collide=False)
    if field=='mark':box(root,f'pack_{item}_mark',(.025,.023,.0006),(0,0,.0007),COLORS['red'],collide=False)
    else:
        for k,(x,y,sx,sy) in SEGMENTS.items():box(root,f'pack_{item}_lot_{k}',(sx*1.8,sy*1.8,.0006),(x*1.8,y*1.8,.0008),(.02,.02,.02,1),collide=False)
    return root
def inject(model,carrier):
    from libero.libero.envs.objects import get_object_fn
    objects={};fixtures={};w=model.worldbody
    for i,kind in enumerate(KINDS):
        name='pack_i'+str(i);obj=get_object_fn(kind)(name=name);model.merge_assets(obj);body=obj.get_obj();w.append(body)
        bottom=float(obj.bottom_offset[2]);top=float(obj.top_offset[2])
        tag(body,'i'+str(i),'mark',top+.0015);tag(body,'i'+str(i),'lot',bottom-.0015)
        objects['i'+str(i)]={'joint':obj.joints[0],'body':obj.root_body,'kind':kind,'bottom':bottom,'top':top}
    h=HEIGHTS[carrier]
    for i,(sx,sy) in enumerate(SIZES):
        name='pack_c'+str(i);body=ET.SubElement(w,'body',name=name,pos=vec(LAYOUTS[carrier][i]));ET.SubElement(body,'freejoint',name=name+'_joint')
        box(body,name+'_floor',(sx,sy,.004),mass='.10')
        for j,(size,pos) in enumerate([((.004,sy,h/2),(-sx,0,h/2)),((.004,sy,h/2),(sx,0,h/2)),((sx,.004,h/2),(0,-sy,h/2)),((sx,.004,h/2),(0,sy,h/2))]):box(body,name+'_wall'+str(j),size,pos,mass='.02')
        # An actual sliding opaque lid with a public protruding push handle.
        lid=ET.SubElement(body,'body',name=name+'_lid',pos=vec((0,0,h+.010)))
        ET.SubElement(lid,'joint',name=name+'_lid_joint',type='slide',axis='0 -1 0' if i==0 else '0 1 0',range='0 .24',damping='.3',frictionloss='1.0',armature='.001')
        box(lid,name+'_cover',(sx+.007,sy+.007,.004),mass='.04')
        box(lid,name+'_handle',(.015,.03,.008),(sx+.012,0,.012),rgba=(.8,.8,.8,1),mass='.008')
        for bar in range(i+1):box(body,name+'_label'+str(bar),(.002,.009,.018),(sx+.004,-.013+bar*.026,h*.6),rgba=(1,1,1,1),collide=False)
        if carrier=='partition_tray':
            box(body,name+'_partition',(sx,.002,.013),(0,0,.017),rgba=(.45,.45,.45,1),mass='.005')
        elif carrier=='handover_tote':
            for side in [-1,1]:box(body,name+'_rim'+str(side),(sx+.007,.009,.009),(0,side*(sy+.004),h),rgba=(.18,.32,.48,1),mass='.01')
        fixtures['c'+str(i)]={'joint':name+'_joint','body':name,'lid_joint':name+'_lid_joint','size':[sx,sy],'height':h}
        cx,cy,cz=LAYOUTS[carrier][i]
        for j,(dx,dy,ax,ay) in enumerate([(-sx,0,.002,sy),(sx,0,.002,sy),(0,-sy,sx,.002),(0,sy,sx,.002)]):
            box(w,f'pack_station_{i}_{j}',(ax,ay,.0007),(cx+dx,cy+dy,SURFACE+.0009),rgba=(.9,.9,.9,1),collide=False)
    # Large neutral transit and handover pads. Their roles do not reveal answers.
    pads={'transit':(.10,-.48,SURFACE),'handover0':(.25,-.18,SURFACE),'handover1':(.25,.24,SURFACE)}
    for name,p in pads.items():box(w,'pack_pad_'+name,(.07,.065,.0008),p,rgba=(.15,.75,.75,1) if name=='transit' else (.95,.82,.08,1),collide=False)
    return objects,fixtures,pads
