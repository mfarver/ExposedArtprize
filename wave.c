#include <math.h>
#include <string.h>
#include <stdint.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <fcntl.h>

#include <wiringPiSPI.h>
 
#define CHANNELS 18
#define WAVELENGTH 18
#define FRAMES WAVELENGTH
#define WAIT 40000

uint8_t frame[CHANNELS];
uint8_t animation[FRAMES];

void init(void) 
{
	memset(frame, 0, CHANNELS);
	size_t i;
	for (i = 0; i < FRAMES; i++) 
	{
		animation[i] = (sin(i * 2 * M_PI / ((double)WAVELENGTH)) + 1) * 64;
	}
}

int main(void) {
	size_t i;
	size_t frameno = 0;
	int errno;
	init();

	errno = wiringPiSPISetup(0, 2000000);
	if (errno < 0) {
		fprintf (stderr, "SPI Setup failed: %s\n", strerror (errno));
	}
	
	printf("Starting...\n");
	while (1) {
		if (frameno == 0)
			printf("Top\n");
		for (i = 0; i < CHANNELS; i++) 
		{
			frame[i] = animation[(i + frameno) % FRAMES];
		}
//		printf("%i\t%i\n", frameno, (int)frame[0]);
		wiringPiSPIDataRW(0, frame, CHANNELS);
		frameno = (frameno+1) % FRAMES;
		usleep(WAIT+500);
	 }
	return 0;
}

