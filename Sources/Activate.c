#include <Carbon/Carbon.h>

// compile as such:
//  gcc -framework carbon -o Activate Activate.c

static bool amIAuthorized () {
    if (AXAPIEnabled() != 0) {
        return true;
    }
    if (AXIsProcessTrusted() != 0) {
        return true;
    }
    return false;
}

static void EQActivate (int pid) {
    ProcessSerialNumber psn;
    GetProcessForPID(pid, &psn);
    SetFrontProcessWithOptions(&psn, kSetFrontProcessFrontWindowOnly);

    AXUIElementRef frontMostApp;
    AXUIElementRef frontMostWindow;
    frontMostApp = AXUIElementCreateApplication(pid);
    AXUIElementSetAttributeValue(frontMostApp, kAXFrontmostAttribute, kCFBooleanTrue); // make application frontmost

    AXUIElementCopyAttributeValue(frontMostApp, kAXFocusedWindowAttribute, (CFTypeRef *)&frontMostWindow);
    AXUIElementSetAttributeValue(frontMostWindow, kAXMainAttribute, kCFBooleanTrue); // make window frontmost
    
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

    EQActivate(pid);
    return 0;
}