#include <Carbon/Carbon.h>
#include "CGSPrivate.h"

// compile as such:
// 	gcc -framework carbon -o MoveWindow MoveWindow.c

int main(int argc, char **argv) {
	int wid;
	int space;
	CGSConnection connection;

    if (argc != 3) {
        printf("usage: %s <wid> <space>\n", argv[0]);
        exit(1);
    } else {
        wid = atoi(argv[1]);
        space = atoi(argv[2]);
    }

	connection = _CGSDefaultConnection();
	CGSWindow wids[] = {wid};
	CGSMoveWorkspaceWindowList(connection, wids, 1, space);
	return 0;
}