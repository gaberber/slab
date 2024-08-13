/* AD5791.h
 * Created by Larry Chen
 * Modified by Chunyang Ding
 */

#ifndef AD5791_h
#define AD5791_h

#include <Arduino.h>
#include <SPI.h>

/* Read and write bits */
#define READ    0x8
#define WRITE   0x0

/* Register codes */
#define DAC     0x1
#define CTRL    0x2
#define CLR     0x3
#define SCTRL   0x4

#define INIT_CODE0      BITCODE(((WRITE|CTRL)<<4),0x0,0x16) //Clamps output to GND
/* Writes 0 010 0000 | 00000000 | 00010110 ?? 
SDODIS = 0 -> SDO pin is enabled
BIN/2sC = 1 -> Dac register uses offset binary coding
DACTRI = 0 -> DAC in normal operational mode
OPGND = 1 -> DAC in tristate mode - DAC output clamped to ground through 6kOhm resistor. 	
RBUF = 1 -> internal amp powered down
*/
#define INIT_CODE       BITCODE(((WRITE|CTRL)<<4),0x0,0x12)
/* Writes 0 010 0000 | 00000000 | 00010010 OPGND 0-> 1, DAC output clamp to ground is removed */ 

/* Given a value to write to the DAC register (0-1048576), constructs the 24 bit code to send to the device */
#define DAC_CODE(val)   ((((long)(WRITE|DAC)<<20)&0xF00000)|DAC_TO_BITCODE(val))
/* Writes the value 0 | 001 | 11000011010100000 (dac value in 20 bits) */

/* These macros return the first, second, and third bytes of a 24 bit code */
#define BYTE1(b)   (byte)((b>>16)&0xFF)
#define BYTE2(b)   (byte)((b>>8)&0xFF)
#define BYTE3(b)   (byte)((b&0xFF))


/* Concatenates three bytes into one 24 bit code*/
#define BITCODE(b1, b2, b3) ((((long)b1<<16)|((long)b2<<8)|(long)b3)&0xFFFFFF)
/* Given a 24 bit code, returns the value read from or written to the DAC register (0-1048576)*/
#define BITCODE_TO_DAC(b)   (b&0xFFFFF)
#define DAC_TO_BITCODE(d)   ((long)d&0xFFFFF)


class AD5791
{
    public:
        AD5791(int sync);
        void initialize_DAC();
        
        long set_value(long bitcode);
        void set_gcurrval(long input);
        void ramp(long bitcode, long step_size, int delta_t);
        long read_CTRL_register();
        long read_DAC_register();
        long read_CLR_register();
        long read_SCTRL_register();
    private:
        int _sync;
        long _dac_reg;
        long currval;
        long gcurrval = 524288;

};

#endif
