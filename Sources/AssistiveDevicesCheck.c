#include <stdio.h>

// compile as such:
//  gcc -framework carbon -o AssistiveDevicesCheck AssistiveDevicesCheck.c

int main (int argc, char ** argv) {
	int test = AXAPIEnabled();
	printf("%d\n", test);
}