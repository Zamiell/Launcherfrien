#import <Cocoa/Cocoa.h>

// compile as such:
// 	gcc -framework cocoa -o EQGetWID EQGetWID.m

int main(int argc, char **argv) {
	int pid;
	NSAutoreleasePool *pool = [[NSAutoreleasePool alloc] init];
	CFArrayRef windowList;
	NSString* windowOwnerName;
	BOOL result;
	NSInteger windowOwnerPID;
	NSInteger windowNumber;
	NSInteger windowWorkspace;

	if (argc != 2) {
		printf("usage: %s <pid>\n", argv[0]);
		exit(1);
	} else
		pid = atoi(argv[1]);

	windowList = CGWindowListCopyWindowInfo(kCGWindowListExcludeDesktopElements, kCGNullWindowID);

	for (NSMutableDictionary* entry in (NSArray*)windowList) {
		windowOwnerName = [entry objectForKey:(id)kCGWindowOwnerName];
		result = [windowOwnerName isEqualToString:@"EverQuest"];
		if (result) {
			windowOwnerPID = [[entry objectForKey:(id)kCGWindowOwnerPID] integerValue];
			if (windowOwnerPID == pid) {
				windowNumber = [[entry objectForKey:(id)kCGWindowNumber] integerValue];
				windowWorkspace = [[entry objectForKey:(id)kCGWindowWorkspace] integerValue];
				printf("%ld %ld\n", windowNumber, windowWorkspace);
			}
		}
	}

	CFRelease(windowList);
	[pool drain];
}