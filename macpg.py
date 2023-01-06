import tkinter, os, re
from tkinter import filedialog
mods = tkinter.filedialog.askdirectory()
defNames=[]
patch = open("tests_macautogen.xml", "w")
patch.write("""<?xml version="1.0" encoding="UTF-8"?>
<Patch>""")
patch.close()
patch = open("tests_macautogen.xml", "a", encoding="utf8")
def stuff(name, packageId, defNames):
    print(packageId)
    global patch
    defNames = list(dict.fromkeys(defNames))
    key=packageId.replace('.','')
    patch.write(f'''   
<!-- {name} -->
<Operation Class="XmlExtensions.ApplyPatch">
    <patchName>testspatches_act</patchName>
    <arguments>
        <li>{name}</li>
        <li>{packageId}</li>
        <li>{key}</li>
    </arguments>
</Operation>

<Operation Class="XmlExtensions.OptionalPatch">
    <modId>tests.ModAnimalCommonality</modId>
    <key>testsMAC_{key}</key>
    <defaultValue>false</defaultValue>
    <caseTrue>
        <Operation Class="XmlExtensions.UseSetting">
        <modId>tests.ModAnimalCommonality</modId>
        <key>testsMAC_{key}k</key>
        <defaultValue>1</defaultValue>
        <apply>
            <Operation Class="XmlExtensions.PatchOperationMath">
                <success>Always</success>
                <xpath>Defs/ThingDef[
''')
    for i in defNames[:-1]:
        patch.write(f'defName="{i}" or \n')
    patch.write(f'''defName="{defNames[-1]}"
        ]/race/wildBiomes/*</xpath>
                <value>{{testsMAC_{key}k}}</value>
                <operation>*</operation>
            </Operation>
            <Operation Class="XmlExtensions.PatchOperationMath">
                <success>Always</success>
                <xpath>
        ''')
    for i in defNames[:-1]:
        patch.write(f'Defs/BiomeDef/wildAnimals/{i} | \n')
    patch.write(f'''Defs/BiomeDef/wildAnimals/{defNames[-1]}
            </xpath>
                <value>{{testsMAC_{key}k}}</value>
                <operation>*</operation>
            </Operation>
            </apply>
        </Operation>
    </caseTrue>
    <caseFalse></caseFalse>
</Operation>

''')

for root, folders, files in os.walk(mods):
    #print(root, folders, files)
    if 'About' in folders:
        if len(defNames)>0: 
            stuff(name, packageId, defNames)
        defNames=[]
        try: 
            with open(root+'/About/About.xml', 'r', encoding="utf8") as f:
                about=f.read()
        except FileNotFoundError: pass
        about=about.split('<modDependencies>')[0]+about.split('</modDependencies>')[-1]
        name=about[about.find('<name>')+6:about.find('</name>')]
        packageId=about[about.find('<packageId>')+11:about.find('</packageId>')]
    if '/Defs' in root.replace('\\', '/'):
        for file in files:
            if file.lower().endswith('.xml'):
                with open(root+'/'+file, 'r', encoding="utf8") as f:
                    file=f.read()
                    if '<ThingDef' not in file or '</ThingDef>' not in file: continue
                file=file.split('<ThingDef')
                for i in file: 
                    if '</ThingDef>' in i:
                        i = i.split('</ThingDef>')[0]
                        if '<defName>' in i and (('<race>' in i and '</race>' in i) or 'ParentName="AnimalThingBase"' in i):
                            defNames.append(i[i.find('<defName>')+9:i.find('</defName>')])
stuff(name, packageId, defNames)
patch.write('</Patch>')
patch.close()