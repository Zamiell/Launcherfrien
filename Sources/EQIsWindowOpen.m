#import <Cocoa/Cocoa.h>

// compile as such:
// 	gcc -framework cocoa -o EQIsWindowOpen EQIsWindowOpen.m

int main(int argc, char **argv) {
	int pid;
	NSAutoreleasePool *pool = [[NSAutoreleasePool alloc] init];
	CFArrayRef windowList;
	NSString* windowName;
	BOOL result;
	NSInteger windowOwnerPID;
	NSInteger windowNumber;
	NSInteger windowWorkspace;

	if (argc != 2) {
		printf("usage: %s <pid>\n", argv[0]);
		exit(1);
	} else {
		pid = atoi(argv[1]);
	}

	windowList = CGWindowListCopyWindowInfo(kCGWindowListExcludeDesktopElements, kCGNullWindowID);

	for (NSMutableDictionary* entry in (NSArray*)windowList) {
		windowName = [entry objectForKey:(id)kCGWindowName];
		result = [windowName isEqualToString:@"EverQuest - 1.2.8"];
		if (result) {
			windowOwnerPID = [[entry objectForKey:(id)kCGWindowOwnerPID] integerValue];
			if (windowOwnerPID == pid) {
				return 0;
			}
		}
	}

	return 1;
}
