import tkinter, os, re
import xml.etree.ElementTree as ET
from tkinter import filedialog
mods = tkinter.filedialog.askdirectory()
defNames=[]
patch = open("tests_scrapper.xml", "w")
patch.write("""<?xml version="1.0" encoding="UTF-8"?>
<Mods>""")
patch.close()
patch = open("tests_scrapper.xml", "a", encoding="utf8")
def stuff(name, packageId, list_of_Defs):
    print(packageId)
    global patch
    list_of_Defs.sort(key = lambda x: x[0])
    patch.write(f'''   
<!-- {name} -->
    <Mod>
        <name>{name}</name>
        <packageId>{packageId}</packageId>
        <Defs>
''')
    for i in list_of_Defs:
        if i[2] is not None:
            patch.write(f'''<li>{i[0]}/{i[2]}</li>
        ''')
    patch.write(f'''</Defs>
    </Mod>


''')
        


list_of_Defs=[]
stop=False
for root, folders, files in os.walk(mods):
    if 'About' in folders:
        if len(list_of_Defs)>0: 
            stuff(name, packageId, list_of_Defs)
        list_of_Defs=[]
        try: about=ET.parse(root+'/About/About.xml')
        except FileNotFoundError: pass
        name=about.find('name').text
        #print(name.text)
        packageId=about.find('packageId').text
    if '/Defs' in root.replace('\\', '/'):
        for file in files:
            if file.lower().endswith('.xml'):
                file=ET.parse(root+'/'+file)
                for Def in file.getroot():
                    if Def.find('race') is not None: DefType='Pawn'
                    elif Def.find('stuffProps') is not None: DefType='Material'
                    else: DefType='Unknown'
                    defName, label=Def.find('defName'), Def.find('label')
                    try: 
                        defName=defName.text
                        for i in list_of_Defs:
                            if defName in i: 
                                stop=True
                                break
                    except AttributeError: pass
                    if stop is True: 
                        stop=False
                        continue
                    try: label=label.text
                    except AttributeError: pass
                    list_of_Defs.append((Def.tag, Def.attrib, defName, label, DefType))

stuff(name, packageId, list_of_Defs)
patch.write('</Mods>')
patch.close()