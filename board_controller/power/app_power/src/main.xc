#include <xs1.h>
#include <platform.h>
#include <stdio.h>
#include <print.h>
#include "iic.h"
#include "ina219.h"

// #include "uart_rx.h"
// #include "uart_rx_impl.h"
// #include "uart_tx.h"
// #include "uart_tx_impl.h"

#define IIC_ADDRESS_ADC_B  (0x41 << 1)
#define IIC_ADDRESS_ADC_A  (0x45 << 1)

#define BIT_RATE 115200
#define BIT_TIME XS1_TIMER_HZ / BIT_RATE
#define BITS_PER_BYTE 8
#define SET_PARITY 0
#define STOP_BIT 1

// UART
on stdcore[0] :   port rx = PORT_UART_RX;
on stdcore[0] :  port tx = PORT_UART_TX;
unsigned baud_rate = BIT_RATE;

// Flash
// on stdcore[0] : port led1 = PORT_CLOCKLED_0;
// on stdcore[0] : port led2 = PORT_CLOCKLED_1;
// on stdcore[0] : port led3 = PORT_CLOCKLED_2;

// B
on stdcore[2]: port sdaBA = XS1_PORT_1E;
on stdcore[2]: port sclBA = XS1_PORT_1F;
on stdcore[2]: port triggerBA = XS1_PORT_4C;

on stdcore[2]: port sdaBB = XS1_PORT_1G;
on stdcore[2]: port sclBB = XS1_PORT_1H;
on stdcore[2]: port triggerBB = XS1_PORT_4D;

// D
on stdcore[2]: port sdaDA = XS1_PORT_1M;
on stdcore[2]: port sclDA = XS1_PORT_1N;
on stdcore[2]: port triggerDA = XS1_PORT_8D;

// A
on stdcore[2]: port sdaAA = XS1_PORT_1A;
on stdcore[2]: port sclAA = XS1_PORT_1B;
on stdcore[2]: port triggerAA = XS1_PORT_4A;

on stdcore[2]: port sdaAB = XS1_PORT_1C;
on stdcore[2]: port sclAB = XS1_PORT_1D;
on stdcore[2]: port triggerAB = XS1_PORT_4B;

// C
on stdcore[2]: port sdaCA = XS1_PORT_1I;
on stdcore[2]: port sclCA = XS1_PORT_1J;
on stdcore[2]: port triggerCA = XS1_PORT_4E;

on stdcore[2]: port sdaCB = XS1_PORT_1K;
on stdcore[2]: port sclCB = XS1_PORT_1L;
on stdcore[2]: port triggerCB = XS1_PORT_4F;

void test_ina(port sda, port scl, port trigger, chanend send, unsigned int address, unsigned maxuA, unsigned resistor)
{
    timer t;
    INA219_t ina219;
    int pwr, bus, interval, current, shunt;
    int cfg, ret, trig, delay;



    // // printf("Configuring INA219\n");
    cfg = INA219_CFGB_BUSV_RANGE(INA219_CFG_BUSV_RANGE_16)
        | INA219_CFGB_PGA_RANGE(INA219_CFG_PGA_RANGE_40)
        | INA219_CFGB_BADC_RES_AVG(INA219_CFG_ADC_RES_12)
        | INA219_CFGB_SADC_RES_AVG(INA219_CFG_ADC_RES_12)
        | INA219_CFGB_OPMODE(INA219_CFG_OPMODE_SCBV_CT);
        //| INA219_CFGB_OPMODE(INA219_CFG_OPMODE_SV_CT);
    //  // printf("Initialised\n");
    ret = ina219_init(ina219, t, scl, sda, address);
    if(ret != XMOS_SUCCESS)
        printf("Init error");
    ret = ina219_config(ina219, t, scl, sda, cfg);
    if(ret != XMOS_SUCCESS)
        printf("Config error");
    // // printf("Configured\n");
    ret = ina219_auto_calibrate(ina219, t, scl, sda, maxuA, resistor, 1);
    if(ret != XMOS_SUCCESS)
        printf("calibrate error");
    //ina219_calibrate(ina219, t, scl, sda, 0x9174, 22, 440);

    // while(1);

    interval = 50000;
    t :> delay;

     while(1)
     {
    //     // n_vals = 0;
    //     // avg = 0;
    //     // while(!(trig&1))
    //     //     trigger :> trig;

    //     // t :> start;

    //     // while(trig&1)
    //     {
            t when timerafter(delay) :> void;
            delay += interval;
    //         // t :> now;
            bus = ina219_bus_mV(ina219,scl,sda);
             send <: bus;
            pwr = ina219_power_uW(ina219,t,scl,sda);
             send <: pwr;
             current = ina219_current_uA(ina219, t, scl,sda);
             send <: current;
             shunt = ina219_shunt_uV(ina219,scl, sda);
             send <: shunt;
    //         // power_array[n_vals] = pwr;
    //         // ++n_vals;
    //         // avg += pwr;
    //         //trigger :> trig;
    //         printf("Bus %dmV, Power %duW, Current %duA, Shunt %duV ** Trigger %d\n",bus, pwr, current, shunt, trig&1);

    //         // if(n_vals > 1024)
    //             // break;
    //     }

    //     // t :> stop;

    //     // for(i = 0; i < n_vals; ++i)
    //     //     printf("%d, ", power_array[i]);
    //     // printf("\nAvg power: %duW, measurements %d, %d cycles, energy: %dnJ\n\n", avg/n_vals, n_vals, stop-start, avg/n_vals * ((stop-start)/100) / 1000);

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
            printf("%d: %4duV %5duW %5duA %3duV\t", i, bus, pwr, cur, sht);
        }
        printf("\n");
    }
}

// void UART_comms(chanend uartTX, chanend uartRX)
// {
//     uart_rx_client_state rxState;
//     uart_rx_init(uartRX, rxState);

//     uart_rx_set_baud_rate(uartRX, rxState, baud_rate);
//     uart_tx_set_baud_rate(uartTX, baud_rate);

//     while(1)
//     {
//         uart_tx_send_byte(uartTX, 0x0A);
//         uart_tx_send_byte(uartTX, 0x04);
//     }
// }

// void flash(port led1, port led2, port led3)
// {
//     timer t;
//     unsigned int n;
//     int i = 0;

//     t :> n;

//     for(;;)
//     {
//         for(i = 0; i < 4 ; ++i)
//         {
//             t when timerafter(n) :> n;
//             n += 10000000;
//             led1 <: 1<<i;
//             led2 <: 0;
//             led3 <: 0;
//         }
//         for(i = 0; i < 4 ; ++i)
//         {
//             t when timerafter(n) :> n;
//             n += 10000000;
//             led1 <: 0;
//             led3 <: 0;
//             led2 <: 1<<i;
//         }
//         for(i = 0; i < 4 ; ++i)
//         {
//             t when timerafter(n) :> n;
//             n += 10000000;
//             led1 <: 0;
//             led2 <: 0;
//             led3 <: 1<<i;
//         }
//     }
// }

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

void UART_comms(port uartTX, port uartRX)
{

    while(1)
    {
        txByte(uartTX, 'A');
        txByte(uartTX, 'b');
    }
}

#pragma unsafe arrays

int main()
{
    chan sends[4], chanTX, chanRX;

    par {
        on stdcore[0]: printer(sends);
        // on stdcore[0]: flash(led1, led2, led3);
        // on stdcore[0] :
        // {
        //     unsigned char tx_buffer[64];
        //     unsigned char rx_buffer[64];
        //     tx <: 1;
        //     par {
        //         uart_rx(rx, rx_buffer, 64, baud_rate, BITS_PER_BYTE, SET_PARITY, STOP_BIT, chanRX);
        //         uart_tx(tx, tx_buffer, 64, baud_rate, BITS_PER_BYTE, SET_PARITY, STOP_BIT, chanTX);
        //     }
        // }
        on stdcore[0] : {
          UART_comms(tx, rx);
        }
       on stdcore[2]: test_ina(sdaAA, sclAA, triggerAA, sends[0], IIC_ADDRESS_ADC_A, 40000, 1000);
       on stdcore[2]: test_ina(sdaAB, sclAB, triggerAB, sends[1], IIC_ADDRESS_ADC_B, 40000, 1000);
       on stdcore[2]: test_ina(sdaCA, sclCA, triggerCA, sends[2], IIC_ADDRESS_ADC_A, 40000, 5000);
       on stdcore[2]: test_ina(sdaCB, sclCB, triggerCB, sends[3], IIC_ADDRESS_ADC_B, 40000, 5000);

        // on stdcore[2]: printf("hi1");
        // on stdcore[2]: printf("hi2");
    }
}
