#import <Cocoa/Cocoa.h>

// compile as such:
// 	gcc -framework cocoa -o EQGetWIDAll EQGetWIDAll.m

int main(int argc, char **argv) {
	int pid;
	NSAutoreleasePool *pool = [[NSAutoreleasePool alloc] init];
	CFArrayRef windowList;
	NSString* windowOwnerName;
	BOOL result;
	NSInteger windowOwnerPID;
	NSInteger windowNumber;
	NSInteger windowWorkspace;

	if (argc != 1) {
		printf("usage: %s\n", argv[0]);
		exit(1);
	}

	windowList = CGWindowListCopyWindowInfo(kCGWindowListExcludeDesktopElements, kCGNullWindowID);

	for (NSMutableDictionary* entry in (NSArray*)windowList) {
		windowOwnerName = [entry objectForKey:(id)kCGWindowOwnerName];
		result = [windowOwnerName isEqualToString:@"EverQuest"];
		if (result) {
			windowOwnerPID = [[entry objectForKey:(id)kCGWindowOwnerPID] integerValue];
			windowNumber = [[entry objectForKey:(id)kCGWindowNumber] integerValue];
			windowWorkspace = [[entry objectForKey:(id)kCGWindowWorkspace] integerValue];
			printf("%ld %ld %ld\n", windowOwnerPID, windowNumber, windowWorkspace);
		}
	}

	CFRelease(windowList);
	[pool drain];
}