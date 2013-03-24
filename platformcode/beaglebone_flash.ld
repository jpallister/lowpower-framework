
MEMORY
{
  ram (rwx) : ORIGIN = 0x80300000, LENGTH = 0x1000000
/*  dataram (rwx) : ORIGIN = 0x82000000, LENGTH=0x1000000
  stackram (rwx) : ORIGIN = 0x83000000, LENGTH=0x1000000*/
}

SECTIONS
{
    .text :
    {
        *(vectors*)
        *(.text*)      /* Program code */
        *(.rodata*)
        . = ALIGN(8);
        _end_text = .;
        _start_datai = .;
    } >ram

    . = 0x82000000;

    .data :
    {
        _start_data = .;
        __data_start = .;
        *(vtable)
        *(.data .data.*)      /* Data memory */
        *(.ARM)
        *(.comment)
        . = ALIGN(8);
        _end_data = .;
        __data_end = .;
    }

    .data_init : {_end_datai = .;}

    __exidx_start = .;
    .ARM.exidx   : { *(.ARM.exidx*) }
    __exidx_end = .;

    .bss :
    {
	__bss_start__ = ALIGN(0x8);
    __bss_start = .;
    _start_bss = .;
        *(.bss*)       /* Zero-filled run time allocate data memory */
    . = ALIGN(4);
    _end_bss = .;
	__bss_end__ = .;
    __bss_end = .;
    _end = .;
    __end = .;
    }

    . = ALIGN(256);

    _start_heap = .;
    PROVIDE( __cs3_heap_start = _start_heap);

    . = 0x84000000;
    __stack = .;

}

__end__ = .;
PROVIDE(end = .);
