#!/bin/sh

# This works using the stock gcc included with the 10.6 Xcode. If you have something else, YMMV.

cd ${0%/*}
gcc -framework carbon -o ../Tools/Activate Activate.c
gcc -framework carbon -o ../Tools/AssistiveDevicesCheck AssistiveDevicesCheck.c
gcc -framework cocoa -o ../Tools/EQGetWID EQGetWID.m
gcc -framework cocoa -o ../Tools/EQGetWIDAll EQGetWIDAll.m
gcc -framework cocoa -o ../Tools/EQPopupDetect EQPopupDetect.m
gcc -framework carbon -o ../Tools/EQWindowRealign EQWindowRealign.c
gcc -framework carbon -o ../Tools/GetCurrentSpace GetCurrentSpace.c
gcc -framework carbon -o ../Tools/MoveWindow MoveWindow.c