#include <xs1.h>
#include <platform.h>
#include <stdio.h>
#include <print.h>
#include "i2c.h"
#include "ina219.h"

//#define DEBUG_PRINT
//#define CONTINUOUS

#define IIC_ADDRESS_ADC_B  (0x41)
#define IIC_ADDRESS_ADC_A  (0x45)

//#define BIT_RATE 1152000
#define BIT_RATE (115200*4)
//#define BIT_RATE 500000
#define BIT_TIME XS1_TIMER_HZ / BIT_RATE
#define BITS_PER_BYTE 8
#define SET_PARITY 0
#define STOP_BIT 1

#define MIN_DELAY   20000

// UART
// on stdcore[0] :  port rx = PORT_UART_RX;
// on stdcore[0] :  port tx = PORT_UART_TX;

on stdcore[0]: out port rx = XS1_PORT_1P;
on stdcore[0]: out port tx = XS1_PORT_1O;
unsigned baud_rate = BIT_RATE;

// Flash
on stdcore[0] : port led0 = PORT_CLOCKLED_0;
on stdcore[1] : port led1 = PORT_CLOCKLED_1;
on stdcore[2] : port led2 = PORT_CLOCKLED_2;
on stdcore[3] : port led3 = PORT_CLOCKLED_3;
on stdcore[0] : port selg = PORT_CLOCKLED_SELG;
on stdcore[0] : port selr = PORT_CLOCKLED_SELR;

// 3B
// on stdcore[3]: port sdaA_X3B = XS1_PORT_1E;
// on stdcore[3]: port sclA_X3B = XS1_PORT_1F;
on stdcore[3]: port triggerA_X3B = XS1_PORT_4C;

on stdcore[3]: struct r_i2c A_X3B = {XS1_PORT_1F, XS1_PORT_1E, 250, 32};


on stdcore[3]: port sdaB_X3B = XS1_PORT_1G;
on stdcore[3]: port sclB_X3B = XS1_PORT_1H;
on stdcore[3]: port triggerB_X3B = XS1_PORT_4D;

// 3A
//on stdcore[3]: port sdaA_X3A = XS1_PORT_1A;
//on stdcore[3]: port sclA_X3A = XS1_PORT_1B;
on stdcore[3]: port triggerA_X3A = XS1_PORT_4A;

on stdcore[3]: struct r_i2c A_X3A = {XS1_PORT_1B, XS1_PORT_1A, 250};
// on stdcore[3]: struct r_i2c A_X3A = {XS1_PORT_1B, XS1_PORT_1A, 1000};

//on stdcore[3]: port sdaB_X3A = XS1_PORT_1C;
//on stdcore[3]: port sclB_X3A = XS1_PORT_1D;
on stdcore[3]: port triggerB_X3A = XS1_PORT_4B;

on stdcore[3]: struct r_i2c B_X3A = {XS1_PORT_1D, XS1_PORT_1C, 250};
// on stdcore[3]: struct r_i2c B_X3A = {XS1_PORT_1D, XS1_PORT_1C, 1000};

// 1A
on stdcore[1]: port sdaA_X1A = XS1_PORT_1A;
on stdcore[1]: port sclA_X1A = XS1_PORT_1B;
on stdcore[1]: port triggerA_X1A = XS1_PORT_4A;

on stdcore[1]: port sdaB_X1A = XS1_PORT_1C;
on stdcore[1]: port sclB_X1A = XS1_PORT_1D;
on stdcore[1]: port triggerB_X1A = XS1_PORT_4B;

// 2A
on stdcore[2]: port sdaA_X2A = XS1_PORT_1A;
on stdcore[2]: port sclA_X2A = XS1_PORT_1B;
on stdcore[2]: port triggerA_X2A = XS1_PORT_4A;

on stdcore[2]: port sdaB_X2A = XS1_PORT_1C;
on stdcore[2]: port sclB_X2A = XS1_PORT_1D;
on stdcore[2]: port triggerB_X2A = XS1_PORT_4B;

// Bottom row
on stdcore[0]: port sdaA_bottom = XS1_PORT_1A;
on stdcore[0]: port sclA_bottom = XS1_PORT_1B;
on stdcore[0]: port triggerA_bottom = XS1_PORT_1C;

// on stdcore[2]: out port sdaBB = XS1_PORT_1G;
// on stdcore[2]: out port sclBB = XS1_PORT_1H;
// on stdcore[2]: port triggerBB = XS1_PORT_4D;

// if interval == -1, wait for trigger
void test_ina(struct r_i2c &ports, port trigger, chanend send, unsigned int address, unsigned maxuA, unsigned resistor, int pga_range, int interval)
{
    timer t;
    INA219_t ina219;
    int pwr, bus, current, shunt;
    unsigned cfg, ret, trig, delay, now;
    short power_array[50];
    short current_array[50];
    short bus_array[50];
    short shunt_array[50];
    short timestamp_array[50];
    int n_vals, avg, start;
    int cnt, last;
    unsigned long energy;
    unsigned long tottime, pwr_avg=0;

    printf("Init\n");

    cfg = INA219_CFGB_BUSV_RANGE(INA219_CFG_BUSV_RANGE_16)
        | INA219_CFGB_PGA_RANGE(pga_range)
        | INA219_CFGB_BADC_RES_AVG(INA219_CFG_ADC_RES_12)
        | INA219_CFGB_SADC_RES_AVG(INA219_CFG_ADC_RES_12)
        | INA219_CFGB_OPMODE(INA219_CFG_OPMODE_SCBV_CT);
        //| INA219_CFGB_OPMODE(INA219_CFG_OPMODE_SV_CT);
    ret = ina219_init(ina219, t, ports, address);
    if(ret != XMOS_SUCCESS)
        printf("Init error\n");
    ret = ina219_config(ina219, t, ports, cfg);
    if(ret != XMOS_SUCCESS)
        printf("Config error\n");
    ret = ina219_auto_calibrate(ina219, t, ports, maxuA, resistor, 1);

    if(i2c_master_start_high_speed(ports) == 0)
        printf("Couldnt enter high speed mode\n");

    trig = 0;

     while(1)
     {
        if(interval == -1)
        {
            while(trig&1)
            {
                trigger :> trig;
                pwr = ina219_power_uW(ina219,t,ports);
            }
            send <: 1;
        }


        cnt = 0;
        t :> now;
        energy = 0;
        tottime = 0;
        while(!(trig&1))
        {
            last = now;
            t when timerafter(now + MIN_DELAY) :> now;
            // bus = ina219_bus_mV(ina219,ports);
            pwr = ina219_power_uW(ina219,t,ports);
            // current = ina219_current_uA(ina219, t, ports);
            // shunt = ina219_shunt_uV(ina219,ports);
            send <: 2;
            // send <: bus;
            send <: pwr;
            // send <: current;
            // send <: shunt;
            send <: now;
            trigger :> trig;

            if(interval != -1)
            {
                t when timerafter(now + interval) :> now;
                trig = 0;
            }

          // printf("%dmV %duW %duA %duV   %duW\n", bus, pwr, current, shunt, pwr_avg);
            cnt += 1;

            energy += pwr*(now-last)>>10;
            tottime += (now-last);
        }

        if(interval == -1)
            send <:0;

        printf("unTriggered: %d measurements\nEnergy %d\nTime %d\n", cnt, energy/1000*1024, tottime);

    }
    // return;

}

#define CHANS   8

void printer(chanend r[CHANS])
{
    int cur, sht, pwr, bus;
    int i;

    while(1)
    {
        for(i = 0; i < CHANS; ++i)
        {
            r[i] :> bus;
            r[i] :> pwr;
            r[i] :> cur;
            r[i] :> sht;
            // printf("%d: %4duV %5duW %5duA %3duV\t", i, bus, pwr, cur, sht);
        }
        // printf("\n");
    }
}

void flash(port led, chanend prev, chanend next, int start)
{
    timer t;
    unsigned int n;
    int i = 0;

    t :> n;

    if(start)
        next <: 0;

    for(;;)
    {
        led <: 0;
        prev :> int;
        for(i = 3; i < 8 ; ++i)
        {
            t when timerafter(n) :> n;
            n += 4000000;
            led <: 1<<i;
        }

        next <:0;
    }
}

void fadecolours(port selg, port selr)
{
    int high_time, low_time;
    timer t;
    unsigned n;
    int dir = 0;

    high_time = 900;
    low_time = 100;

    t :> n;

    while(1)
    {
        t when timerafter(n) :> n;
        n += high_time*2500;
        selg <: 1;
        selr <: 0;

        t when timerafter(n) :> n;
        n += low_time*1000;
        selg <: 0;
        selr <: 1;

        if(dir == 0)
        {
            high_time += 1;
            low_time -= 1;
            if(low_time <= 0)
            {
                low_time = 0;
                high_time = 1000;
                dir = 1;
            }
        }
        else
        {
            high_time -= 1;
            low_time += 1;
            if(low_time >= 1000)
            {
                low_time = 1000;
                high_time = 0;
                dir = 0;
            }
        }
    }

}

void txByte (out port TXD, int byte) {
    unsigned time;
    timer t;
    int p=0;

    /* input initial time */
    t :> time;

    /* output start bit */
    TXD <: 0;
    time += BIT_TIME;
    t when timerafter (time) :> void;

    /* output data bits */
    for (int i=0; i <8; i++) {
        p ^= (byte&1);
        TXD <: >> byte;
        time += BIT_TIME;
        t when timerafter (time) :> void;
    }

    /* output stop bit */
    TXD <: 1;
    time += BIT_TIME;
    t when timerafter (time) :> void;
}

#define UART_BUF_SIZE   1024

void UART_buffer(chanend from_sense, chanend to_uart)
{
    short buf1[UART_BUF_SIZE];
    int buf2[UART_BUF_SIZE];
    char buf_cmd[UART_BUF_SIZE];
    int head=0, end=0, can_send=0;
    int val;

    while(1)
    {
        select {
            case (((end+1)&(UART_BUF_SIZE-1)) != head) => from_sense :> val:
            {
                buf_cmd[end] = val;

                if(val == 2)
                {
                    from_sense :> val;
                    buf1[end] = val;
                    from_sense :> val;
                    buf2[end] = val;
                }

                end = (end+1)&(UART_BUF_SIZE-1);
                
                break;
            }
            case to_uart :> can_send: break;
//            default: break;
        }

        if(can_send && head != end)
        {
            to_uart <: (int)buf_cmd[head];
            if(buf_cmd[head] == 2)
            {
                to_uart <: (int)buf1[head];
                to_uart <: (int)buf2[head];
            }
            head = (head+1)&(UART_BUF_SIZE-1);
            can_send = 0;
        }
    }
}

void UART_byte_stream(chanend from_sense, chanend to_uart, int channel)
{
    int time_table[256];
    int n_table=0;
    int last_time=-1, last_power=-1;
    int can_send, val, i, pwr, time, found=0;
    unsigned char bytes[9];
    int b_len=0;

    int c_p_diff=0;
    int c_p_abs=0;
    int c_t_abs=0;
    int c_t_diff=0;
    int c_t_tab=0;

    while(1)
    {
        to_uart :> can_send;
        from_sense <: can_send;

        from_sense :> val;

        if(val == 1)
        {
            val = (channel & 0x7) | (0x8);
            to_uart <: (int)1;
            to_uart <: (unsigned char)val;
        }
        else if(val == 0)
        {
            printf("lastp %d\n", last_power);
            last_time = -1;
            last_power = -1;
            val = (channel & 0x7);
            to_uart <: (int)1;
            to_uart <: (unsigned char)val;
            printf("%d %d  %d %d %d\nn_table %d\n", c_p_abs, c_p_diff, c_t_abs, c_t_diff, c_t_tab, n_table);
            c_p_abs = c_p_diff = c_t_abs = c_t_diff = c_t_tab = 0;
            n_table = 0;
        }
        else if(val == 2)
        {
            bytes[0] = (channel & 0x7) | (0x10);
            b_len = 1;
            from_sense :> pwr;
            from_sense :> time;

            if(last_time == -1 || pwr-last_power > 128 || pwr-last_power < -127)
            {
                bytes[1] = (pwr >> 24) & 0xFF;
                bytes[2] = (pwr >> 16) & 0xFF;
                bytes[3] = (pwr >> 8) & 0xFF;
                bytes[4] = (pwr) & 0xFF;
                b_len += 4;
                c_p_abs += 1;
            }
            else
            {
                bytes[0] |= 0x80;
                bytes[1] = (signed char)(pwr-last_power);
                b_len += 1;
                c_p_diff += 1;
            }

            found = -1;
            for(i = 0; i < n_table; ++i)
                if(time_table[i] == time - last_time)
                    found = i;
            if(found != -1)
            {
                bytes[0] |= 0x20;
                bytes[b_len] = found;
                b_len += 1;
                c_t_tab += 1;
            }
            else if(last_time == -1 || time-last_time > 65535 || 1)
            {
                if(n_table < 256 && last_time != -1)
                {
                    time_table[n_table] = time - last_time;
                    n_table += 1;
                }
                bytes[b_len] = (time >> 24) & 0xFF;  b_len+=1;
                bytes[b_len] = (time >> 16) & 0xFF;  b_len+=1;
                bytes[b_len] = (time >> 8) & 0xFF;  b_len+=1;
                bytes[b_len] = time & 0xFF;  b_len+=1;
                c_t_abs += 1;
            }
            else
            {
                val = time - last_time;
                if(n_table < 256)
                {
                    time_table[n_table] = val;
                    n_table += 1;
                }
                bytes[0] |= 0x40;
                bytes[b_len] = (val >> 8) & 0xFF; b_len += 1;
                bytes[b_len] = (val) & 0xFF; b_len += 1;
                c_t_diff += 1;
            }

            last_time = time;
            last_power = pwr;

            to_uart <: b_len;
            for(i = 0; i < b_len; ++i)
            {
                to_uart <: bytes[i];
            }
        }
    }
}

void UART_comms(out port uartTX, out port uartRX, chanend sensors[CHANS])
{
    timer t;
    unsigned tv,i,j;
    unsigned char c;
    int n;

    uartTX <: 1;

    sensors[0] <: 1;

    while(1)
    {
        for(int i = 0; i < CHANS; ++i)
        select {
            case sensors[i] :> n :
                {
                    for(j = 0; j < n; ++j)
                    {
                        sensors[i] :> c;
                        txByte(uartTX, c);
                    }
                   sensors[0] <: 1;
                    break;
                }
            default: break;
        }
    }
}

#pragma unsafe arrays

int main()
{
    chan sends[CHANS], chanTX, chanRX;
    chan flashring[4], to_bstream, to_uart;

    par {
        on stdcore[0] : fadecolours(selg, selr);
        on stdcore[0] : flash(led0, flashring[0], flashring[1], 1);
        on stdcore[1] : flash(led1, flashring[1], flashring[2], 0);
        on stdcore[2] : flash(led2, flashring[2], flashring[3], 0);
        on stdcore[3] : flash(led3, flashring[3], flashring[0], 0);
        on stdcore[0] : {
            UART_comms(tx, rx, sends);
        }
        // on stdcore[0] : {

        //     while(1) {
        //         sends[1] <: 2;

        //         sends[1] <: 0x11;
        //         sends[1] <: 0x11;
        //         sends[1] <: 0x11;
        //         sends[1] <: 0x11;
        //         sends[1] <: 10;

        //         sends[1] <: 0xAA;
        //         sends[1] <: 0xAA;
        //         sends[1] <: 0xAA;
        //         sends[1] <: 0xAA;
        //         sends[1] <: 11;
        //     }

        // }
       // on stdcore[1]: test_ina(sdaA_X1A, sclA_X1A, triggerA_X1A, sends[1], IIC_ADDRESS_ADC_A, 400000, 50);

    on stdcore[1]: UART_buffer(to_uart, to_bstream);
    on stdcore[1]: UART_byte_stream(to_bstream, sends[0], 0);

    // Cortex m0 and m3
      on stdcore[3]: test_ina(A_X3B, triggerA_X3B, to_uart, IIC_ADDRESS_ADC_A, 40000, 5000, INA219_CFG_PGA_RANGE_40, -1);
      // on stdcore[3]: test_ina(A_X3B, triggerA_X3B, to_uart, IIC_ADDRESS_ADC_A, 40000, 5000, INA219_CFG_PGA_RANGE_40, 100000);
//      on stdcore[3]: test_ina(sdaA_X3B, sclA_X3B, triggerA_X3B, sends[0], IIC_ADDRESS_ADC_A, 40000, 50, INA219_CFG_PGA_RANGE_40, 100000);
//      on stdcore[3]: test_ina(sdaB_X3B, sclB_X3B, triggerB_X3B, sends[1], IIC_ADDRESS_ADC_B, 40000, 5000, INA219_CFG_PGA_RANGE_40, -1);
//      on stdcore[3]: test_ina(sdaB_X3B, sclB_X3B, triggerB_X3B, sends[1], IIC_ADDRESS_ADC_B, 40000, 5000, INA219_CFG_PGA_RANGE_80, 500000);

        // Cortex a8
        // mpu
//      on stdcore[3]: test_ina(sdaA_X3A, sclA_X3A, triggerA_X3A, sends[2], IIC_ADDRESS_ADC_A, 400000, 100, INA219_CFG_PGA_RANGE_40, -1);
//      on stdcore[3]: test_ina(sdaA_X3A, sclA_X3A, triggerA_X3A, sends[2], IIC_ADDRESS_ADC_A, 400000, 100, INA219_CFG_PGA_RANGE_40, 500000);
        // ddr
//      on stdcore[2]: test_ina(sdaA_X2A, sclA_X2A, triggerA_X2A, sends[3], IIC_ADDRESS_ADC_A, 400000, 1000, INA219_CFG_PGA_RANGE_160, -1);
      // on stdcore[2]: test_ina(sdaA_X2A, sclA_X2A, triggerA_X2A, sends[3], IIC_ADDRESS_ADC_A, 400000, 1000, INA219_CFG_PGA_RANGE_160, 500000);
        // vcore
//      on stdcore[2]: test_ina(sdaB_X2A, sclB_X2A, triggerB_X2A, sends[4], IIC_ADDRESS_ADC_B, 400000, 1000, INA219_CFG_PGA_RANGE_160, -1);
      // on stdcore[2]: test_ina(sdaB_X2A, sclB_X2A, triggerB_X2A, sends[4], IIC_ADDRESS_ADC_B, 400000, 1000, INA219_CFG_PGA_RANGE_160, 500000);

        // epiphany
 //     on stdcore[1]: test_ina(sdaA_X1A, sclA_X1A, triggerA_X1A, sends[5], IIC_ADDRESS_ADC_A, 400000, 50, INA219_CFG_PGA_RANGE_40, 500000);
   //   on stdcore[1]: test_ina(sdaB_X1A, sclB_X1A, triggerB_X1A, sends[6], IIC_ADDRESS_ADC_B, 800000, 50, INA219_CFG_PGA_RANGE_40, 500000);

      // xmos
//      on stdcore[0]: test_ina(sdaA_bottom, sclA_bottom, triggerA_bottom, sends[7], IIC_ADDRESS_ADC_B, 400000, 50, INA219_CFG_PGA_RANGE_40, -1);


        // on stdcore[2]: printf("hi1");
        // on stdcore[2]: printf("hi2");
    }
}
