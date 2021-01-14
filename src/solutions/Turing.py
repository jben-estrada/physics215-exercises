"""
`Turing` class, an implementation of a universal Turing machine. It can be initialized with at least one symbol. The tape can be arbitrarily extended.

This variant of the Turing machine has the following instructions:
    - Tape cell shift instructions
        > shiftl - Move to the left of the current tape cell.
        > shiftr - Move to the right of the current tape cell.
        > noshift - Stay in the current cell.
    - Write instructions
        > write SYMBOL - Write the symbol `SYMBOL` onto the current cell.
        > erase - Erase the symbol on the current cell. Alias to the write `BLANK_SYM` where `BLANK_SYM` is the blank symbol.
    - Change state instruction
        > goto STATE - Jump to the specified state `STATE`.
"""

from collections import defaultdict
from TMParser import TMParser


class Turing:
    """
    An implementation of the Turing machine.
    """

    def __init__(self, instruction):
        self.parser = TMParser(instruction)

        self.symbols, self.blank_symbol, self.init_state, self.trans_tbl = \
            self.parser.parse()
        self.curr_state = self.init_state

        self.tape_pos = 0
        self.tape = None
        self.init_tape = None
        self.init_state = None
        self.halt = False

    def load_tape(self, tape=None):
        if tape is None:
            base_dict = {0: self.blank_symbol}
        else:
            base_dict = dict((i, elem) for i, elem in enumerate(tape))
        
        self.init_tape = defaultdict(lambda: self.blank_symbol, base_dict)
        self.tape = self.init_tape.copy()

    def __move_tape(self, increment):
        self.tape_pos += increment

        # If the key `self.tape_pos` does not exist, the blank symbol
        # is mapped to the missing key.
        self.tape[self.tape_pos] = self.tape[self.tape_pos]
    
    def __exec(self):
        curr_symbol = self.tape[self.tape_pos]
        if curr_symbol not in self.symbols:
            raise ValueError(f"Unknown symbol '{curr_symbol}'")

        instrc_set = self.trans_tbl[self.curr_state][curr_symbol]

        # The TM halts if no instruction is received.
        if len(instrc_set) > 0:
            for instrc in instrc_set:
                self.__exec_one_instrc(instrc)
        else:
            self.halt = True
    
    def __exec_one_instrc(self, instrc):
        op_name = instrc[0]
        if   op_name == self.parser.OP_SHFTL:
            self.__move_tape(-1)
        elif op_name == self.parser.OP_SHFTR:
            self.__move_tape(+1)
        elif op_name == self.parser.OP_NSHFT:
            pass  # Do nothing
        elif op_name == self.parser.OP_ERASE:
            self.tape[self.tape_pos] = self.blank_symbol
        elif op_name == self.parser.OP_WRITE:
            symbol = instrc[1]
            self.tape[self.tape_pos] = symbol
        elif op_name == self.parser.OP_GOTO:
            state = instrc[1]
            self.curr_state = state
        else:
            raise ValueError(f"Unknown operation: {instrc[0]}")
    
    def reset(self):
        self.tape = self.init_tape
        self.tape_pos = 0
        self.curr_state = self.init_state
    
    def print_tape(self, lbound, ubound, delim=" | "):
        print(end=delim)
        for idx in range(lbound, ubound):
            print(f"{self.tape[idx]}",  end=delim)
        print()   # Print a new line.

    def __iter__(self):
        return self
    
    def __next__(self):
        if self.tape is None:
            raise AttributeError("No initial tape content.")

        self.__exec()
        if self.halt:
            raise StopIteration
        
        return self.tape_pos, self.curr_state
