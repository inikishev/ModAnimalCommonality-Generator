import tkinter, os
import xml.etree.ElementTree as ET


def get_Defs(folder,Def_types:list=[],blacklist_nodes:list=[], whitelist_nodes:list=[]):
    mod_Defs,mod_names,mod_packageIds,mod_index,n=[],[],[],[],0
    for root, folders, files in os.walk(folder):
        if 'About' in folders:
            #mod_Defs=[]
            try: about=ET.parse(root+'/About/About.xml')
            except FileNotFoundError: pass
            mod_name=about.find('name').text
            #print(name.text)
            mod_packageId=about.find('packageId').text
            mod_names.append(mod_name)
            mod_packageIds.append(mod_packageId)
            mod_index.append(n)
            #print(mod_packageId)
        #print(root)
        if '/Defs' in root.replace('\\', '/'):
            for file in files:
                if file.lower().endswith('.xml'):
                    file=ET.parse(root+'/'+file)
                    for Def in file.getroot():
                        #print (Def.tag)
                        if len(Def_types)>0 and Def.tag not in Def_types: continue
                        for node in blacklist_nodes:
                            if Def.find(node) is not None: 
                                continue
                        for node in whitelist_nodes:
                            if Def.find(node) is None: 
                                continue
                        mod_Defs.append(Def)
                        #print(len(mod_Defs))
                        #print (Def.tag)
                        n+=1
    return mod_Defs,mod_names,mod_packageIds,mod_index

def Def_get_type(Def):
    if Def.find('race') is not None: 
        Def_type='pawn'
    elif Def.find('stuffProps') is not None: 
        Def_type='stuff'
    elif Def.find('plant') is not None: 
        Def_type='plant'
    elif Def.find('filth') is not None: 
        Def_type='filth'
    elif Def.find('ingestible') is not None: 
        Def_type='food'
    elif Def.find('projectile') is not None: 
        Def_type='projectile'
    elif Def.find('apparel') is not None: 
        Def_type='apparel'
    elif Def.find('weaponTags') is not None or Def.find('weaponClasses') is not None or Def.find('verbs') is not None or Def.find('tools') is not None: 
        Def_type='weapon'
    elif Def.find('soundInteract') is not None or Def.find('soundDrop') is not None or Def.find('stackLimit') is not None or Def.find('allowedArchonexusCount') is not None: 
        Def_type='resource'
    elif Def.find('castEdgeShadows') is not None or Def.find('size') is not None or Def.find('building') is not None or Def.find('fillPercent') is not None or Def.find('staticSunShadowHeight') is not None: 
        Def_type='building'
    else: Def_type='idk'
    return Def_type

def Def_remove(Def, blacklist:list):
    for node in blacklist:
        if Def.find(node) is not None: Def.remove(node)

def Def_whitelist(Def, whitelist:list):
    for node in Def:
        print(node.tag)
        if node.tag not in whitelist: 
            print('deleted')
            Def.remove(node)

def Def_add(Def, nodes:list, values:list):
    if type(nodes[0]) == list or type(nodes[0]) == tuple: nodes, values = nodes[0], nodes[1]
    for i in range(len(nodes)):
        if Def.find(nodes[i]) is None:
            node=ET.SubElement(Def, nodes[i])
            if values[i] is not None: node.text = values[i]

def Def_replace(Def, old, new, new_value = None):
    if Def.find(old) is not None: 
        Def.remove(old)
        node=ET.SubElement(Def, new)
        if new_value is not None: node.text = new_value

def Def_add_or_replace(Def, old, new, new_value = None):
    if Def.find(old) is not None: 
        Def.remove(old)
    node=ET.SubElement(Def, new)
    if new_value is not None: node.text = new_value

def Def_propify(Def):
    try: Def.attrib.pop("ParentName")
    except KeyError: pass
    try: Def.attrib.pop("Name")
    except KeyError: pass
    Def.set("ParentName","tmerge2_props")
    Def_whitelist(Def, ('defName','label', 'description', 'graphicData', 'altitudeLayer', 'passability', 'fillPercent', 'rotatable', 'defaultPlacingRot', 'size', 'uiIconScale'))
    return Def

def output(start:str, end:str, mod_start:str, mod_middle:str, mod_end:str, each_start:str, each_end:str, each_after:str, lines:list, mod_names=['None'],mod_packageIds=['None'],mod_index=[0]) -> str:
    """
    start
        mod_start {label} mod_middle {packageID} mod_end
            each_start {line} each_end
        each_after
    end
    """
    text=start
    for i in range(len(mod_index)):
        text+=mod_start+mod_names[i]+mod_middle+mod_packageIds[i]+mod_end
        #print(len(mod_index), i)
        amongus=range(mod_index[i], mod_index[i+1]) if i+1<len(mod_index) else range(mod_index[i], len(lines))
        for j in amongus: 
            #print(j, len(lines))
            text+=each_start+lines[j]+each_end
        text+=each_after
    text+=end
    return text

def propifier(folder):
    mod_props=[]
    mod_Defs,mod_names,mod_packageIds,mod_index=get_Defs(folder,Def_types=['ThingDef'])
    if not os.path.isdir('P '+mod_names[0]): os.mkdir('P '+mod_names[0])
    if not os.path.isdir('P '+mod_names[0]+'/Defs'): os.mkdir('P '+mod_names[0]+'/Defs')
    with open('P '+mod_names[0]+'/Defs/'+mod_packageIds[0].replace('.','_')+'_props.xml', "w") as f:
        f.write("""<?xml version="1.0" encoding="UTF-8"?>
    """)
    for i in range(len(mod_Defs)):
        if Def_get_type(mod_Defs[i])=='building' and mod_Defs[i].find('defName') is not None and mod_Defs[i].find('graphicData/texPath') is not None: 
            defName=mod_Defs[i].find('defName').text
            mod_Defs[i].remove(mod_Defs[i].find('defName'))
            node=ET.SubElement(mod_Defs[i], 'defName')
            node.text = defName+'_prop'
            #mod_Defs[i].insert(0, node)
            mod_props.append(Def_propify(mod_Defs[i]))
    text='<Defs>'
    for i in range(len(mod_names)):
        text+=f'\n<!-- {mod_packageIds[i]} - {mod_names[i]} -->'
    #print(type(mod_Defs))
    for i in mod_props:
        text+=ET.tostring(i, encoding='utf8', method='xml').decode('utf-8').replace("<?xml version='1.0' encoding='utf8'?>",'')
    text+='</Defs>'
    with open('P '+mod_names[0]+'/Defs/'+mod_packageIds[0].replace('.','_')+'_props.xml', "a") as f:
        f.write(text)


def scrapper(folder):
    mod_Defs,mod_names,mod_packageIds,mod_index=get_Defs(folder)
    #print(mod_names)
    lines=[]
    #print(len(mod_Defs))
    for Def in mod_Defs:
        #print(Def.tag)
        nl='\n'
        lines.append(f"\n<{Def.tag}>{nl+'<defName>'+Def.find('defName').text+'</defName>' if Def.find('defName') is not None else ''}{nl+'<ParentName>'+Def.attrib['ParentName']+'</ParentName>' if 'ParentName' in Def.attrib else ''}{nl+'<Name>'+Def.attrib['Name']+'</Name>' if 'Name' in Def.attrib else ''}{nl+'<Abstract>'+Def.attrib['Abstract']+'</Abstract>' if 'Abstract' in Def.attrib else ''}{nl+'<label>'+Def.find('label').text+'</label>' if Def.find('label') is not None else ''}{nl+'<description>'+Def.find('description').text+'</description>' if Def.find('description') is not None else ''}\n<type>{Def_get_type(Def)}</type>\n</{Def.tag}>")
    text=output(start='<Defs>\n', end='\n</Defs>', mod_start='\n\n<Mod>\n<label>', mod_middle='</label>\n<packageId>', mod_end='</packageId>\n<Nodes>', each_start='', each_end='', each_after='\n</Nodes>\n</Mod>', lines=lines, mod_names=mod_names,mod_packageIds=mod_packageIds,mod_index=mod_index)
    with open('scrapper.xml', "w") as f:
        f.write(text)

def scrapper_compact(folder):
    mod_Defs,mod_names,mod_packageIds,mod_index=get_Defs(folder)
    #print(mod_names)
    lines=[]
    #print(len(mod_Defs))
    for Def in mod_Defs:
        #print(Def.tag)
        nl='\n'
        lines.append(f"""\n<li>{Def.tag}/{Def.find('defName').text if Def.find('defName') is not None else (('@'+Def.attrib['Name']) if 'Name' in Def.attrib else '?')}</li> <!--{(' @ParentName="'+Def.attrib['ParentName'] +'"  ') if 'ParentName' in Def.attrib else ''}{('@Name="'+Def.attrib['Name'] +'"  ') if 'Name' in Def.attrib and Def.find('defName') is None else ''}{('label="'+Def.find('label').text +'"  ') if Def.find('label') is not None else ''}{'  type='+Def_get_type(Def)} -->""")
    text=output(start='<Defs>\n', end='\n</Defs>', mod_start='\n\n<Mod>\n<label>', mod_middle='</label>\n<packageId>', mod_end='</packageId>\n<Nodes>', each_start='', each_end='', each_after='\n</Nodes>\n</Mod>', lines=lines, mod_names=mod_names,mod_packageIds=mod_packageIds,mod_index=mod_index)
    with open('scrapper_compact.xml', "w") as f:
        f.write(text)

def scrapper_CherryPicker(folder):
    mod_Defs,mod_names,mod_packageIds,mod_index=get_Defs(folder)
    #print(mod_names)
    lines=[]
    #print(len(mod_Defs))
    for Def in mod_Defs:
        #print(Def.tag)
        nl='\n'
        if Def.find('defName') is not None:
            lines.append(f"""\n<li>{Def.tag}/{Def.find('defName').text}</li>""")
    text=output(start='<Defs>\n', end='\n</Defs>', mod_start='\n\n<!-- ', mod_middle=' ', mod_end=' -->\n<CherryPicker.DefList MayRequire="owlchemist.cherrypicker">\n<defName>CHANGE_THIS_TO_SOMETHING_UNIQUE</defName>\n<label>CHANGE THIS TO LABEL</label>\n<defs>', each_start='', each_end='', each_after='\n</defs>\n</CherryPicker.DefList>', lines=lines, mod_names=mod_names,mod_packageIds=mod_packageIds,mod_index=mod_index)
    with open('scrapper_CherryPicker.xml', "w") as f:
        f.write(text)

from tkinter import filedialog

folder = tkinter.filedialog.askdirectory()
#propifier(folder)
scrapper_CherryPicker(folder)