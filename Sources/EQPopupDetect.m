#import <Cocoa/Cocoa.h>

// compile as such:
// 	gcc -framework cocoa -o EQPopupDetect EQPopupDetect.m

int main(int argc, char **argv) {
	int pid;
	NSAutoreleasePool *pool = [[NSAutoreleasePool alloc] init];
	CFArrayRef windowList;
	NSString* windowOwnerName;
	BOOL result;
	CGRect bounds;
	NSString* sizeString;
	NSInteger windowOwnerPID;

	if (argc != 1) {
		printf("usage: %s\n", argv[0]);
		exit(1);
	}

	windowList = CGWindowListCopyWindowInfo(kCGWindowListExcludeDesktopElements, kCGNullWindowID);

	for (NSMutableDictionary* entry in (NSArray*)windowList) {
		windowOwnerName = [entry objectForKey:(id)kCGWindowOwnerName];
		result = [windowOwnerName isEqualToString:@"EverQuest"];
		if (result) {
			CGRectMakeWithDictionaryRepresentation((CFDictionaryRef)[entry objectForKey:(id)kCGWindowBounds], &bounds);
			sizeString = [NSString stringWithFormat:@"%.0f*%.0f", bounds.size.width, bounds.size.height];
			[entry setObject:sizeString forKey:@"windowSize"];			
			result = [sizeString isEqualToString:@"416*204"];
			if (result) {
				windowOwnerPID = [[entry objectForKey:(id)kCGWindowOwnerPID] integerValue];
				printf("%ld\n", windowOwnerPID);
			}
		}
	}

	CFRelease(windowList);
	[pool drain];
}