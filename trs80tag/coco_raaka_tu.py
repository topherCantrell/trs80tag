# https://pypi.org/project/MC6809/

from MC6809.components.cpu6809 import CPU
from MC6809.components.memory import Memory
from MC6809.core.configs import BaseConfig

import random
import os
import logging

class CoCoRaakaTu:
    
    GAME_NAME = 'coco_raaka_tu'
    
    NUM_COLUMNS = 32
    
    @staticmethod
    def print_banner():
        print('Raaka-Tu - 1982 for the TRS-80 Color Computer')
        print('See the disassembly: http://computerarcheology.com/CoCo/RaakaTu/')
        print('Everything you need to know: http://www.figmentfly.com/raakatu/raakatu.html')
    
    def __init__(self,cols=NUM_COLUMNS):
        
        logging.getLogger('MC6809').disabled = True
        
        fn = os.path.join(os.path.dirname(__file__),'coco_raaka_tu.bin')
        with open(fn,'rb') as f:
            self.binary = f.read()    
        self.binary = list(b'\x00' * 0x600 + self.binary)
        
        CFG_DICT = {
            "verbosity": None,
            "trace": None,
        }
        class Config(BaseConfig):
            RAM_START = 0x0000
            RAM_END = 0x7FFF
            ROM_START = 0x8000
            ROM_END = 0xFFFF
        cfg = Config(CFG_DICT)
         
        # Memory management -- defer everything to our read/write functions
        #  
        memory = Memory(cfg)
        memory.add_read_byte_callback(self.read_memory,0,0xFFFF)
        memory.add_write_byte_callback(self.write_memory,0,0xFFFF)
        
        # Start of program is 0x600
        #
        self.cpu = CPU(memory, cfg)
        self.still_running = False
        
        self.buffer = ''
        self.cols = cols
        
    def print_char(self,c):        
        if c == '\r' or c == '\n':
            self.print_flush()
        else:
            self.buffer = self.buffer + c
    
    
    def print_flush(self): 
        while True:
    
            self.buffer = self.buffer.strip()
    
            if len(self.buffer) <= self.cols:
                print(self.buffer)
                self.buffer = ''
                return
    
            if self.buffer[self.cols] == ' ':
                print(self.buffer[0:self.cols])
                self.buffer = self.buffer[self.cols:]
            else:
                i = self.buffer[0:self.cols].rfind(' ')
                if i < 0:
                    i = self.cols
                print(self.buffer[:i])
                self.buffer = self.buffer[i:]
    
    def show_error_message(self):
        '''Instead of flashing in place
        '''
        
        s = ''
        for y in range(32):
            c = self.binary[0x5E0+y]        
            if c<32 or c>127 or c==96:
                c = 32
            s = s + chr(c)        
        print(s.strip())
        
    def simulate_coco_input(self):
        '''Get input from the user and poke it into COCO screen memory    
        '''        
        
        for y in range(32):
            self.binary[0x5E0+y]=96
        
        user_input = input('> ')
        user_input = user_input.strip().upper()
        p = 0x5E0  # Start of the bottom row
        for c in user_input:
            c = ord(c)
            if c == 32:        
                self.binary[p] = 96
                p += 1
            elif c>=65 and c<=90:
                self.binary[p] = c
                p += 1
            if p>=0x5FF:
                break

        #for p in range(0x5E0,0x5E0+32):
        #    print(self.binary[p])
            
    def simulate_coco_print(self,s):
        '''Print a character
        '''
        
        #print('##',s)
        
        self.print_char(s)     
    
    def read_memory(self,_cycles,frm,addr):
                
        # This is the "print character routine. We point it to C000 then handle the
        # print by intercepting the routine at C000.
        #
        if addr==0xA002:
            return 0xC0
        if addr==0xA003:
            return 0x00    
        if addr==0xC000:
            self.simulate_coco_print(chr(self.cpu.accu_a.value))        
            return 0x39
        
        # The wait-for-key calls this routine to roll the random number. Since we
        # are eating that spin-wait, we'll provide random numbers here.
        #
        if addr==0x12A8:
            self.binary[0x1338] = random.randint(0,255)
            self.cpu.accu_a.set(random.randint(0,255))
            return 0x39
        
        # This bypasses the built in 32-column management. We'll handle word-breaks in
        # the print routine, which allows for any size console.
        # 
        if addr==0x89:        
            return 0
        
        # This is where the error message is flashed. Instead, we'll just print the error.
        #        
        if addr==0x9A5:
            self.show_error_message()        
        if addr==0x9BB:        
            return 0x21  # BRN to avoid a loop of flashes
            
        # This is where the game gets a line of input from the user.
        #
        if addr==0xACC or addr==0xA63:
            self.simulate_coco_input()
            return 0x39
        
        # This is the infinite loop when the player does a QUIT.
        # We'll abort the running program
        #
        if addr==0x10B5:                   
            self.still_running = False
            return 0x20
            
        # This is in RAM.
        #    
        if addr<=0x3F17:        
            # print('.. '+hex(addr)+' @'+hex(frm)+' <'+hex(self.binary[addr]))
            return self.binary[addr]
        
        raise Exception('## UNHANDLED READ from=' + hex(frm) + ' destination=' + hex(addr))    
    
    def write_memory(self,_cycles,frm,addr,value):
         
        # This is RAM.     
        #      
        if addr<=0x3F17:
            self.binary[addr] = value
            return
            
        raise Exception('## UNHANDLED WRITE from'+hex(frm)+' destination='+hex(addr)+' value='+hex(value))
    
    def run_forever(self):
    
        self.cpu.program_counter.set(0x600)
        self.still_running = True        
        while self.still_running:
            self.cpu.run()   

