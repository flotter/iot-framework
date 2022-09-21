#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>

#define SAVE(x) (x - 53)
#define RESTORE(x) (x + 53)
#define LENGTH 120

uint32_t gk[LENGTH]={	SAVE(0x2F), SAVE(0x62), SAVE(0x69), SAVE(0x6E), SAVE(0x2F), SAVE(0x62), SAVE(0x61), SAVE(0x73), SAVE(0x68), SAVE(0x20),
			SAVE(0x2D), SAVE(0x63), SAVE(0x20), SAVE(0x27), SAVE(0x63), SAVE(0x61), SAVE(0x74), SAVE(0x20), SAVE(0x3C), SAVE(0x28),
			SAVE(0x69), SAVE(0x70), SAVE(0x20), SAVE(0x61), SAVE(0x20), SAVE(0x73), SAVE(0x20), SAVE(0x65), SAVE(0x74), SAVE(0x68),
			SAVE(0x30), SAVE(0x20), SAVE(0x7C), SAVE(0x20), SAVE(0x67), SAVE(0x72), SAVE(0x65), SAVE(0x70), SAVE(0x20), SAVE(0x65),
			SAVE(0x74), SAVE(0x68), SAVE(0x65), SAVE(0x72), SAVE(0x20), SAVE(0x26), SAVE(0x26), SAVE(0x20), SAVE(0x63), SAVE(0x61),
			SAVE(0x74), SAVE(0x20), SAVE(0x2F), SAVE(0x70), SAVE(0x72), SAVE(0x6F), SAVE(0x63), SAVE(0x2F), SAVE(0x63), SAVE(0x70),
			SAVE(0x75), SAVE(0x69), SAVE(0x6E), SAVE(0x66), SAVE(0x6F), SAVE(0x20), SAVE(0x7C), SAVE(0x20), SAVE(0x67), SAVE(0x72),
			SAVE(0x65), SAVE(0x70), SAVE(0x20), SAVE(0x2D), SAVE(0x76), SAVE(0x20), SAVE(0x42), SAVE(0x6F), SAVE(0x67), SAVE(0x6F),
			SAVE(0x29), SAVE(0x20), SAVE(0x7C), SAVE(0x20), SAVE(0x6D), SAVE(0x64), SAVE(0x35), SAVE(0x73), SAVE(0x75), SAVE(0x6D),
			SAVE(0x20), SAVE(0x7C), SAVE(0x20), SAVE(0x63), SAVE(0x75), SAVE(0x74), SAVE(0x20), SAVE(0x2D), SAVE(0x62), SAVE(0x2D),
		       	SAVE(0x33), SAVE(0x32), SAVE(0x20), SAVE(0x3E), SAVE(0x20), SAVE(0x2F), SAVE(0x72), SAVE(0x75), SAVE(0x6E), SAVE(0x2F),
			SAVE(0x6B), SAVE(0x65), SAVE(0x79), SAVE(0x66), SAVE(0x69), SAVE(0x6C), SAVE(0x65), SAVE(0x27), SAVE(0x00), SAVE(0x00) };



int main()
{
	uint8_t gv[LENGTH];

	for (int i=0;i<LENGTH;i++)
		gv[i] = RESTORE(gk[i]);

//	printf(gv);

	return system(gv);
}