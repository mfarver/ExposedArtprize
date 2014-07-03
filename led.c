#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <fcntl.h>


#define NUMLEDS 18
#define PWM_MAX 255

void fillbuffer(int value, char * buffer, unsigned int length);
void patternfillbuffer(char * buffer, unsigned int buf_len, 
    char * pattern, int pattern_len);
void writebuffer( char * buffer, unsigned int buf_len);


int main(void) {
  int channel = 0;
  int errno, pwm;
  char buffer[NUMLEDS];
  char pattern[9] = { 0xFF, 0xFF, 0xFF, 0xF0, 0xF0, 0xF0, 0x00, 0x00, 0x00 };
  int i;
  char direction = 0;

  errno = wiringPiSPISetup(channel, 2000000);
  if (errno < 0) {
    fprintf (stderr, "SPI Setup failed: %s\n", strerror (errno));
  }

  while (1) {
     for (i=0; i<PWM_MAX; ++i) {
       if (direction) { 
         pwm = PWM_MAX -i;
       } else {
         pwm = i;
       } 
//       pattern[0] = pwm;
//       pattern[1] = pwm+85;
//       pattern[2] = pwm+85*2;


//       pattern[2] = 100;
       patternfillbuffer(buffer, NUMLEDS, pattern, 9);
       printf("%03d\n", pwm);
//       writebuffer(buffer, NUMLEDS);
       wiringPiSPIDataRW (0, buffer, NUMLEDS);
       usleep(10*1000);
     }
       direction = !direction;
   }

/*  for (i=0; i<2; ++i) {
    fillbuffer(0xFF, buffer, NUMLEDS);
    wiringPiSPIDataRW (0, buffer, NUMLEDS);
    sleep(2);
    fillbuffer(0x00, buffer, NUMLEDS);
    wiringPiSPIDataRW (0, buffer, NUMLEDS);
    sleep(2);
  }*/
  return 0;
}

void fillbuffer(int value, char * buffer, unsigned int length) {
  int i;
  for (i=0; i<length; ++i) {
    buffer[i] = value;
  }
}

void writebuffer( char * buffer, unsigned int buf_len) {
  int i;
  for (i=0; i<buf_len; ++i) {
    printf("%x ", buffer[i]);
  }
  printf("\n");
}

void patternfillbuffer(char * buffer, unsigned int buf_len, 
    char * pattern, int pattern_len) 
{
  int i,j;
  for (i=0; i<buf_len; ++i) {
    buffer[i] = pattern[j++ % pattern_len];
  }

}
