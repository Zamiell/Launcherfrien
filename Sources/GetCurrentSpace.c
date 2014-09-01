#include "CGSPrivate.h"

// compile as such:
//  gcc -framework carbon -o GetCurrentSpace GetCurrentSpace.c

int main(int argc, char **argv) {
	CGSConnection connection;
	int space;

    if (argc != 1) {
        printf("usage: %s\n", argv[0]);
        exit(1);
    }

	connection = _CGSDefaultConnection();
	CGSGetWorkspace(connection, &space);
	printf("%d\n", space);
	return 0;
}