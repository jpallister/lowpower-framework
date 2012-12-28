#include <xs1.h>
#include <platform.h>
#include <stdio.h>
#include <print.h>
#include "i2c.h"
#include "ina219.h"

//////////////////////////////////////////////////////////////////////////
// Config defines

#define ADC_RANGE   INA219_CFG_ADC_RES_9

//#define ENABLE_CORTEX_M0
// #define ENABLE_CORTEX_M3

#define ENABLE_CORTEX_A8

#define ENABLE_EPIPHANY
// #define ENABLE_XMOS


//#define DEBUG_PRINT
//#define CONTINUOUS

#define USE_MARKER_BYTE

#define MAX_SAMPLERATE      10000

#define I2C_FAST_TICKS      250
#define I2C_HISPEED_TICKS   32

#define UART_BUF_SIZE   2048
#define UART_TABLE_SIZE 256

//////////////////////////////////////////////////////////////////////////

#define INDEX_M0    0
#define INDEX_M3    1
#define INDEX_A8_0  2
#define INDEX_A8_1  3
#define INDEX_A8_2  4

#define IIC_ADDRESS_ADC_B  (0x41)
#define IIC_ADDRESS_ADC_A  (0x45)

#define BIT_RATE (115200*4)
#define BIT_TIME XS1_TIMER_HZ / BIT_RATE
#define BITS_PER_BYTE 8
#define SET_PARITY 0
#define STOP_BIT 1

#define MIN_DELAY   (XS1_TIMER_HZ/MAX_SAMPLERATE)
#ifdef CONTINUOUS
    #define INTERVAL    1000000
    #undef MAX_SAMPLERATE
    #define MAX_SAMPLERATE INTERVAL
#else
    #define INTERVAL    -1
#endif

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
on stdcore[3]: port triggerA_X3B = XS1_PORT_4C;
on stdcore[3]: struct r_i2c A_X3B = {XS1_PORT_1F, XS1_PORT_1E, I2C_FAST_TICKS, I2C_HISPEED_TICKS};


on stdcore[3]: port triggerB_X3B = XS1_PORT_4D;
on stdcore[3]: struct r_i2c B_X3B = {XS1_PORT_1H, XS1_PORT_1G, I2C_FAST_TICKS, I2C_HISPEED_TICKS};

// 3A
on stdcore[3]: port triggerA_X3A = XS1_PORT_4A;
on stdcore[3]: struct r_i2c A_X3A = {XS1_PORT_1B, XS1_PORT_1A, I2C_FAST_TICKS, I2C_HISPEED_TICKS};

//on stdcore[3]: port sdaB_X3A = XS1_PORT_1C;
//on stdcore[3]: port sclB_X3A = XS1_PORT_1D;
on stdcore[3]: port triggerB_X3A = XS1_PORT_4B;
on stdcore[3]: struct r_i2c B_X3A = {XS1_PORT_1D, XS1_PORT_1C, I2C_FAST_TICKS, I2C_HISPEED_TICKS};
// on stdcore[3]: struct r_i2c B_X3A = {XS1_PORT_1D, XS1_PORT_1C, 1000};

// 1A
on stdcore[1]: port triggerA_X1A = XS1_PORT_4A;
on stdcore[1]: struct r_i2c A_X1A = {XS1_PORT_1B, XS1_PORT_1A, I2C_FAST_TICKS, I2C_HISPEED_TICKS};

on stdcore[1]: port triggerB_X1A = XS1_PORT_4B;
on stdcore[1]: struct r_i2c B_X1A = {XS1_PORT_1D, XS1_PORT_1C, I2C_FAST_TICKS, I2C_HISPEED_TICKS};

// 2A
on stdcore[2]: port triggerA_X2A = XS1_PORT_4A;
on stdcore[2]: struct r_i2c A_X2A = {XS1_PORT_1B, XS1_PORT_1A, I2C_FAST_TICKS, I2C_HISPEED_TICKS};

on stdcore[2]: port triggerB_X2A = XS1_PORT_4B;
on stdcore[2]: struct r_i2c B_X2A = {XS1_PORT_1D, XS1_PORT_1C, I2C_FAST_TICKS, I2C_HISPEED_TICKS};

// Bottom row
// on stdcore[0]: port sdaA_bottom = XS1_PORT_1A;
// on stdcore[0]: port sclA_bottom = XS1_PORT_1B;
// on stdcore[0]: port triggerA_bottom = XS1_PORT_1C;


// if interval == -1, wait for trigger
void test_ina(struct r_i2c &ports, port trigger, chanend send, unsigned int address, unsigned maxuA, unsigned resistor, int pga_range, int interval)
{
    timer t;
    INA219_t ina219;
    int pwr, bus, current, shunt;
    unsigned cfg, ret, trig, delay, now;
    int n_vals, avg, start;
    int cnt, last;
    unsigned long energy;
    unsigned long tottime, pwr_avg=0;

    unsigned  p_cnt=0;

    cfg = INA219_CFGB_BUSV_RANGE(INA219_CFG_BUSV_RANGE_16)
        | INA219_CFGB_PGA_RANGE(pga_range)
        | INA219_CFGB_BADC_RES_AVG(ADC_RANGE)
        | INA219_CFGB_SADC_RES_AVG(ADC_RANGE)
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

    printf("Power LSB:%d\n", ina219.pow_lsb);


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
            send <: ina219.pow_lsb;
        }


        cnt = 0;
        t :> now;
        energy = 0;
        tottime = 0;
        while(!(trig&1))
        {
            last = now;
            t when timerafter(now + MIN_DELAY) :> now;
            pwr = ina219_power_uW(ina219,t,ports);
            t :> start;

            #ifdef CONTINUOUS
                bus = ina219_bus_mV(ina219,ports);
                current = ina219_current_uA(ina219, t, ports);
                shunt = ina219_shunt_uV(ina219,ports);
            #endif
            send <: 2;
            send <: pwr/ina219.pow_lsb;
            send <: now;
            trigger :> trig;

            if(interval != -1)
            {
                t when timerafter(now + interval) :> now;
                trig = 0;
            }

        #ifdef DEBUG_PRINT
          printf("%dmV %duW %duA %duV   %duW\n", bus, pwr, current, shunt, pwr_avg);
        #endif
            cnt += 1;

            energy += pwr*(now-last)>>10;
            tottime += (now-last);
        }

        if(interval == -1)
            send <:0;

        #ifdef DEBUG_PRINT
            printf("unTriggered: %d measurements\nEnergy %d\nTime %d\n", cnt, energy/1000*1024, tottime);
        #endif

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

#ifdef CONTINUOUS
void UART_buffer(chanend from_sense, chanend to_uart)
{
    int val, op, p, t;

    while(1)
    {
        to_uart :> val;
        from_sense :> op;
        if(op == 2)
        {
            from_sense :> p;
            from_sense :> t;
        }
        if(op == 1)
        {
            from_sense :> p;
        }
        to_uart <: op;
        if(op == 2)
        {
            to_uart <: p;
            to_uart <: t;
        }
        if(op == 1)
            to_uart <: p;
    }
}
#else
void UART_buffer(chanend from_sense, chanend to_uart)
{
    int buf1[UART_BUF_SIZE];
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
                if(val == 1)
                {
                    from_sense :> val;
                    buf1[end] = val;
                }

                end = (end+1)&(UART_BUF_SIZE-1);

                break;
            }
            case to_uart :> can_send: break;
        //    default: break;
        }

        if(can_send && head != end)
        {
            to_uart <: (int)buf_cmd[head];
            if(buf_cmd[head] == 2)
            {
                to_uart <: (int)buf1[head];
                to_uart <: (int)buf2[head];
            }
            if(buf_cmd[head] == 1)
            {
                to_uart <: (int)buf1[head];
            }
            head = (head+1)&(UART_BUF_SIZE-1);
            can_send = 0;
        }
    }
}
#endif

void UART_byte_stream(chanend from_sense, chanend to_uart, int channel)
{
    int time_table[UART_TABLE_SIZE];
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

    int do_continuous=0;

    #ifdef CONTINUOUS
        do_continuous = 1;
    #endif

    while(1)
    {
        to_uart :> can_send;
        from_sense <: can_send;

        from_sense :> val;

        if(val == 1)
        {
            from_sense :> pwr;

            val = (channel & 0x7) | (0x8);
            to_uart <: (int)3;
            to_uart <: (unsigned char)val;
            to_uart <: (unsigned char)((pwr>>8)&0xFF); // Send pow_lsb onwards
            to_uart <: (unsigned char)(pwr&0xFF);      // Send pow_lsb onwards
        }
        else if(val == 0)
        {
            last_time = -1;
            last_power = -1;
            val = (channel & 0x7);
            to_uart <: (int)1;
            to_uart <: (unsigned char)val;
            c_p_abs = c_p_diff = c_t_abs = c_t_diff = c_t_tab = 0;
            n_table = 0;
        }
        else if(val == 2)
        {
            bytes[0] = (channel & 0x7) | (0x10);
            b_len = 1;
            from_sense :> pwr;
//            pwr = pwr / 280;
            from_sense :> time;
            val = pwr - last_power;

            if(last_time == -1 || val > 32767 || val < -32767 || do_continuous)
            {
                bytes[1] = (pwr >> 24) & 0xFF;
                bytes[2] = (pwr >> 16) & 0xFF;
                bytes[3] = (pwr >> 8) & 0xFF;
                bytes[4] = (pwr) & 0xFF;
                b_len += 4;
                c_p_abs += 1;
            }
            else if(val > 128 || val < -127)
            {
                bytes[0] |= 0x40;
                bytes[b_len] = (val >> 8) & 0xFF; b_len += 1;
                bytes[b_len] = (val) & 0xFF; b_len += 1;
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
            if(found != -1 && !do_continuous && 0)
            {
                bytes[0] |= 0x20;
                bytes[b_len] = found;
                b_len += 1;
                c_t_tab += 1;
            }
            else //if(last_time == -1 || time-last_time > 65535 || 1)
            {
                if(n_table < UART_TABLE_SIZE && last_time != -1)
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
            // else
            // {
            //     val = time - last_time;
            //     if(n_table < 256)
            //     {
            //         time_table[n_table] = val;
            //         n_table += 1;
            //     }
            //     bytes[0] |= 0x40;
            //     bytes[b_len] = (val >> 8) & 0xFF; b_len += 1;
            //     bytes[b_len] = (val) & 0xFF; b_len += 1;
            //     c_t_diff += 1;
            // }

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
    unsigned tv,i,j;
    unsigned char c;
    int n;

    uartTX <: 1;

    #ifdef ENABLE_CORTEX_M0
        sensors[INDEX_M0] <: 1;
    #endif

    #ifdef ENABLE_CORTEX_M3
        sensors[INDEX_M3] <: 1;
    #endif

    #ifdef ENABLE_CORTEX_A8
        sensors[INDEX_A8_0] <: 1;
        sensors[INDEX_A8_1] <: 1;
        sensors[INDEX_A8_2] <: 1;
    #endif

    while(1)
    {
        for(int i = 0; i < CHANS; ++i)
        select {
            case sensors[i] :> n :
                {
                    #ifdef USE_MARKER_BYTE
                        txByte(uartTX, 0xA5);
                    #endif
                    for(j = 0; j < n; ++j)
                    {
                        sensors[i] :> c;
                        txByte(uartTX, c);
                    }
                   sensors[i] <: 1;
                   break;
                }
            default: break;
        }
    }
}

#pragma unsafe arrays

int main()
{
    chan sends[CHANS];
    chan flashring[4], to_bstream, to_uart;
    chan m0_to_buf, m0_to_compress;
    chan m3_to_buf, m3_to_compress;
    chan a8_to_buf[3], a8_to_compress[3];

    par
    {
        // Useless flashing
        on stdcore[0] : fadecolours(selg, selr);
        on stdcore[0] : flash(led0, flashring[0], flashring[1], 1);
        on stdcore[1] : flash(led1, flashring[1], flashring[2], 0);
        on stdcore[2] : flash(led2, flashring[2], flashring[3], 0);
        on stdcore[3] : flash(led3, flashring[3], flashring[0], 0);

        // UART communications
        on stdcore[0] : UART_comms(tx, rx, sends);

    #ifdef ENABLE_CORTEX_M0
        on stdcore[3]: test_ina(A_X3B, triggerA_X3B, m0_to_buf, IIC_ADDRESS_ADC_A, 40000, 5000, INA219_CFG_PGA_RANGE_40, INTERVAL);
        on stdcore[1]: UART_buffer(m0_to_buf, m0_to_compress);
        on stdcore[1]: UART_byte_stream(m0_to_compress, sends[0], 0);
    #endif

    #ifdef ENABLE_CORTEX_M3
        on stdcore[3]: test_ina(B_X3B, triggerB_X3B, m3_to_buf, IIC_ADDRESS_ADC_B, 40000, 5000, INA219_CFG_PGA_RANGE_40, INTERVAL);
        on stdcore[1]: UART_buffer(m3_to_buf, m3_to_compress);
        on stdcore[1]: UART_byte_stream(m3_to_compress, sends[1], 1);
    #endif

    #ifdef ENABLE_CORTEX_A8
        // mpu
        on stdcore[3]: test_ina(A_X3A, triggerA_X3A, a8_to_buf[0], IIC_ADDRESS_ADC_A, 400000, 100, INA219_CFG_PGA_RANGE_40, INTERVAL);
        // ddr
        on stdcore[2]: test_ina(A_X2A, triggerA_X2A, a8_to_buf[1], IIC_ADDRESS_ADC_A, 400000, 1000, INA219_CFG_PGA_RANGE_160, INTERVAL);
        // vcore
        on stdcore[2]: test_ina(B_X2A, triggerB_X2A, a8_to_buf[2], IIC_ADDRESS_ADC_B, 400000, 1000, INA219_CFG_PGA_RANGE_160, INTERVAL);

        on stdcore[1]: UART_buffer(a8_to_buf[0], a8_to_compress[0]);
        on stdcore[1]: UART_byte_stream(a8_to_compress[0], sends[2], 2);
        on stdcore[2]: UART_buffer(a8_to_buf[1], a8_to_compress[1]);
        on stdcore[2]: UART_byte_stream(a8_to_compress[1], sends[3], 3);
        on stdcore[0]: UART_buffer(a8_to_buf[2], a8_to_compress[2]);
        on stdcore[0]: UART_byte_stream(a8_to_compress[2], sends[4], 4);
    #endif

    // epiphany
    // on stdcore[1]: test_ina(sdaA_X1A, sclA_X1A, triggerA_X1A, sends[5], IIC_ADDRESS_ADC_A, 400000, 50, INA219_CFG_PGA_RANGE_40, 500000);
    // on stdcore[1]: test_ina(sdaB_X1A, sclB_X1A, triggerB_X1A, sends[6], IIC_ADDRESS_ADC_B, 800000, 50, INA219_CFG_PGA_RANGE_40, 500000);

    // xmos
    // on stdcore[0]: test_ina(sdaA_bottom, sclA_bottom, triggerA_bottom, sends[7], IIC_ADDRESS_ADC_B, 400000, 50, INA219_CFG_PGA_RANGE_40, -1);

    }
}
