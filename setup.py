#!/usr/bin/env python
import sys
import subprocess
from subprocess import call
from setuptools import setup

PHANTOMJS_EXEC = 'phantomjs'
NVM_EXEC = 'nvm'

def cmd_exists(cmd):
    return call("type " + cmd, shell=True, 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

if not cmd_exists(PHANTOMJS_EXEC):
    install_cmd = ["npm", "install", "-g", "phantomjs"]
    if cmd_exists(NVM_EXEC):
        install_cmd = ["nvm", "use", "0.10"] + install_cmd
    npm_result = call(install_cmd, shell=True, 
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if npm_result != 0:
        print "Please install PhantomJS first."
        sys.exit(1)

setup(name='pgyer-grab',
      version='1.0',
      description='Pgyer .ipa files grabbing utility',
      author='Vladimir Ignatev',
      author_email='ya.na.pochte@gmail.com',
      url='https://www.python.org/',
      packages=['pgyergrab'],
      scripts=['pgyergrab/bin/pgyer-grab'],
      install_requires=['requests==2.5.1']
     )