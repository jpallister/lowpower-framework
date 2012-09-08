
MEMORY
{
  ram (rx) : ORIGIN = 0x80300000, LENGTH = 0x10000
}

__stack = ORIGIN(ram) + LENGTH(ram);

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
    } >ram

    .data_init : {_end_datai = .;} > ram

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
    } >ram
   
    . = ALIGN(256);

    _start_heap = .;
    PROVIDE( __cs3_heap_start = _start_heap);
}

__end__ = .;
PROVIDE(end = .);
