#include <Carbon/Carbon.h>

// compile as such:
//  gcc -framework carbon -o EQWindowRealign EQWindowRealign.c

static bool amIAuthorized () {
    if (AXAPIEnabled() != 0) {
        return true;
    }
    if (AXIsProcessTrusted() != 0) {
        return true;
    }
    return false;
}

static void EQResize (int pid) {
    ProcessSerialNumber psn;
    GetProcessForPID(pid, &psn);
    SetFrontProcessWithOptions(&psn, kSetFrontProcessFrontWindowOnly);

    AXValueRef temp;
    CGPoint windowPosition;
    AXUIElementRef frontMostApp;
    AXUIElementRef frontMostWindow;
    frontMostApp = AXUIElementCreateApplication(pid);
    AXUIElementSetAttributeValue(frontMostApp, kAXFrontmostAttribute, kCFBooleanTrue); // make application frontmost

    AXUIElementCopyAttributeValue(frontMostApp, kAXFocusedWindowAttribute, (CFTypeRef *)&frontMostWindow);
    AXUIElementSetAttributeValue(frontMostWindow, kAXMainAttribute, kCFBooleanTrue); // make window frontmost

    AXUIElementCopyAttributeValue(frontMostWindow, kAXPositionAttribute, (CFTypeRef *)&temp);
    AXValueGetValue(temp, kAXValueCGPointType, &windowPosition);
    CFRelease(temp);
    windowPosition.x = 0;
    windowPosition.y = -33;
    temp = AXValueCreate(kAXValueCGPointType, &windowPosition);
    AXUIElementSetAttributeValue(frontMostWindow, kAXPositionAttribute, temp);
    CFRelease(temp);

    CFRelease(frontMostWindow);
    CFRelease(frontMostApp);
}

int main (int argc, char ** argv) {
    int pid;

    if (argc != 2) {
        printf("usage: %s <pid>\n", argv[0]);
        exit(1);
    } else
        pid = atoi(argv[1]);

    if (!amIAuthorized()) {
        printf("Can't use accessibility API!\n");
        return 1;
    }

    EQResize(pid);
    return 0;
}