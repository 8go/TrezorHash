#!/bin/bash

echo "Requires Python and pip to be installed"
echo "Read: http://www.pyinstaller.org/"
echo "Something similar should work on Windows as well"
echo "Read: https://mborgerson.com/creating-an-executable-from-a-python-script"

su -c "pip install pyinstaller" root
pyinstaller --hidden-import pkgutil --windowed --icon=icons/TrezorHash.ico --onefile TrezorHash.py
echo "Single file executable is: ./dist/TrezorHash"
ls -lh ./dist/TrezorHash
