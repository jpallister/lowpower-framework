#include <xs1.h>
#include <platform.h>
#include <stdio.h>
#include <print.h>
#include "iic.h"
#include "ina219.h"

//#define DEBUG_PRINT
//#define CONTINUOUS

#define IIC_ADDRESS_ADC_B  (0x41 << 1)
#define IIC_ADDRESS_ADC_A  (0x45 << 1)

#define BIT_RATE 1152000
#define BIT_TIME XS1_TIMER_HZ / BIT_RATE
#define BITS_PER_BYTE 8
#define SET_PARITY 0
#define STOP_BIT 1

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

// B
on stdcore[3]: port sdaA_X3B = XS1_PORT_1E;
on stdcore[3]: port sclA_X3B = XS1_PORT_1F;
on stdcore[3]: port triggerA_X3B = XS1_PORT_4C;

on stdcore[3]: port sdaB_X3B = XS1_PORT_1G;
on stdcore[3]: port sclB_X3B = XS1_PORT_1H;
on stdcore[3]: port triggerB_X3B = XS1_PORT_4D;

// on stdcore[2]: out port sdaBB = XS1_PORT_1G;
// on stdcore[2]: out port sclBB = XS1_PORT_1H;
// on stdcore[2]: port triggerBB = XS1_PORT_4D;


void test_ina(port sda, port scl, port trigger, chanend send, unsigned int address, unsigned maxuA, unsigned resistor)
{
    timer t;
    INA219_t ina219;
    int pwr, bus, interval, current, shunt;
    unsigned cfg, ret, trig, delay, now;
    short power_array[50];
    short current_array[50];
    short bus_array[50];
    short shunt_array[50];
    short timestamp_array[50];
    int n_vals, avg, start;

    cfg = INA219_CFGB_BUSV_RANGE(INA219_CFG_BUSV_RANGE_16)
        | INA219_CFGB_PGA_RANGE(INA219_CFG_PGA_RANGE_40)
        | INA219_CFGB_BADC_RES_AVG(INA219_CFG_ADC_RES_12)
        | INA219_CFGB_SADC_RES_AVG(INA219_CFG_ADC_RES_12)
        | INA219_CFGB_OPMODE(INA219_CFG_OPMODE_SCBV_CT);
        //| INA219_CFGB_OPMODE(INA219_CFG_OPMODE_SV_CT);
    ret = ina219_init(ina219, t, scl, sda, address);
    if(ret != XMOS_SUCCESS)
        printf("Init error");
    ret = ina219_config(ina219, t, scl, sda, cfg);
    if(ret != XMOS_SUCCESS)
        printf("Config error");
    ret = ina219_auto_calibrate(ina219, t, scl, sda, maxuA, resistor, 1);
    if(ret != XMOS_SUCCESS)
        printf("calibrate error");

    interval = 50000;
    t :> delay;
    delay += resistor * 10;
    t when timerafter(delay) :> void;

     while(1)
     {
        while(trig&1)
        {
            trigger :> trig;
            pwr = ina219_power_uW(ina219,t,scl,sda);
        }

        send <: 1;

        while(!(trig&1))
        {
            t :> now;
            bus = ina219_bus_mV(ina219,scl,sda);
            pwr = ina219_power_uW(ina219,t,scl,sda);
            current = ina219_current_uA(ina219, t, scl,sda);
            shunt = ina219_shunt_uV(ina219,scl, sda);
            send <: 2;
            send <: bus;
            send <: pwr;
            send <: current;
            send <: shunt;
            send <: now;
            trigger :> trig;
            // printf("Bus %dmV, Power %duW, Current %duA, Shunt %duV Trigger: %d\n",bus, pwr, current, shunt, trig&1);
        }
        send <:0;
        // printf("Trigger finished\n");
    }
    // return;

}

#define CHANS   4

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

    /* input initial time */
    t :> time;

    /* output start bit */
    TXD <: 0;
    time += BIT_TIME;
    t when timerafter (time) :> void;

    /* output data bits */
    for (int i=0; i <8; i++) {
        TXD <: >> byte;
        time += BIT_TIME;
        t when timerafter (time) :> void;
    }

    /* output stop bit */
    TXD <: 1;
    time += BIT_TIME;
    t when timerafter (time) :> void;
}

void UART_comms(out port uartTX, out port uartRX, chanend sensors[CHANS])
{
    timer t;
    unsigned n;

    uartTX <: 1;

    while(1)
    {
        select {
            case (int i = 0; i < CHANS; ++i)
                sensors[i] :> n :
                {
                    txByte(uartTX, 0xAB);
                    txByte(uartTX, 0xCD);

                    txByte(uartTX, n);
                    txByte(uartTX, i);

                    if(n == 2)
                        for(int k = 0;  k < 5; ++k)
                        {
                            int val;

                            sensors[i] :> val;
                            txByte(uartTX, (val >> 24) & 0xFF);
                            txByte(uartTX, (val >> 16) & 0xFF);
                            txByte(uartTX, (val >> 8) & 0xFF);
                            txByte(uartTX, val & 0xFF);
                        }
                    break;
                }
        }
    }
}

#pragma unsafe arrays

int main()
{
    chan sends[4], chanTX, chanRX;
    chan flashring[4];

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
       on stdcore[3]: test_ina(sdaA_X3B, sclA_X3B, triggerA_X3B, sends[0], IIC_ADDRESS_ADC_A, 40000, 5000);
       on stdcore[3]: test_ina(sdaB_X3B, sclB_X3B, triggerB_X3B, sends[1], IIC_ADDRESS_ADC_B, 40000, 5000);
       // on stdcore[2]: test_ina(sdaAB, sclAB, triggerAB, sends[1], IIC_ADDRESS_ADC_B, 40000, 1000);
       // on stdcore[2]: test_ina(sdaCA, sclCA, triggerCA, sends[2], IIC_ADDRESS_ADC_A, 40000, 5000);
       // on stdcore[2]: test_ina(sdaCB, sclCB, triggerCB, sends[3], IIC_ADDRESS_ADC_B, 40000, 5000);

        // on stdcore[2]: printf("hi1");
        // on stdcore[2]: printf("hi2");
    }
}
