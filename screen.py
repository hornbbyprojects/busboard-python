from machine import Pin
import time

RS_PIN_NUMBER = 16
E_PIN_NUMBER = 17
PIN_D4_NUMBER = 18
PIN_D5_NUMBER = 19
PIN_D6_NUMBER = 20
PIN_D7_NUMBER = 21

pinRs = Pin(RS_PIN_NUMBER, Pin.OUT)
pinE = Pin(E_PIN_NUMBER, Pin.OUT)
pinD4 = Pin(PIN_D4_NUMBER, Pin.OUT)
pinD5 = Pin(PIN_D5_NUMBER, Pin.OUT)
pinD6 = Pin(PIN_D6_NUMBER, Pin.OUT)
pinD7 = Pin(PIN_D7_NUMBER, Pin.OUT)

MICROSECOND = 0.000001
MILLISECOND = 0.001
E_SETUP_TIME = 300 * MICROSECOND # added data + address hold times, unsure if fair
# E_SETUP_TIME = 5 * MILLISECOND # 300 * MICROSECOND # added data + address hold times, unsure if fair
E_HOLD_TIME = 100 * MICROSECOND # Execution time is at least 37 ms
# E_HOLD_TIME = 5 * MILLISECOND # 50 * MICROSECOND # Execution time is at least 37 ms
E_PULSE = MICROSECOND # Must be > 450 ns by datasheet, we pick 1 microsecond

def pulseE():
    time.sleep(E_SETUP_TIME) # I believe setup time is 60 + 195 = 255 microseconds
    pinE.value(1)
    time.sleep(E_PULSE)
    pinE.value(0)
    time.sleep(E_HOLD_TIME)


def write_nibble(value):
    pinD4.value((value >> 0) & 1)
    pinD5.value((value >> 1) & 1)
    pinD6.value((value >> 2) & 1)
    pinD7.value((value >> 3) & 1)
    pulseE()

def write_byte(value):
    write_nibble((value & 0b11110000) >> 4);
    write_nibble(value & 0b1111);
    
def write_command(value):
    pinRs.value(0)
    write_byte(value)

def write_char(value):
    pinRs.value(1)
    write_byte(ord(value))

def write_string(str):
    for char in str:
        write_char(char)
        time.sleep(0.05)

def init():
    time.sleep(400 * MILLISECOND)
    pinRs.value(0)
    write_nibble(0b11) # Set to 8 bit
    time.sleep(5 * MILLISECOND) # datasheet says at least 4.1 ms

    write_nibble(0b11) # Set to 8 bit (second try for some reason)
    time.sleep(5 * MILLISECOND) # datasheet says at least 100 ms
    write_nibble(0b10) # Set to 4 bit

    write_command(0b0010_1100) # Function set 1(DL)_1NF*
    write_command(0b1111) # Display - _1DCB
    write_command(0b110) # 1(I/D)S
    

    clear()
    home()


def home():
    write_command(0b10)
    time.sleep(3 * MILLISECOND)

def clear():
    write_command(0b1)
    time.sleep(3 * MILLISECOND)

def set_addr(addr):
    write_command(0b10000000 | addr)


def newline():
    set_addr(0x40)

