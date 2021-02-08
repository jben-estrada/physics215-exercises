"""
Parser for the class `Turing`, an implementation of a universal Turing Machine.

Author: John Benedick Estrada
"""


class TMParser:
    """
    A parser for my Turing programming machine language. This outputs transition tables.
    """

    # Reserved and invalid strings
    EOF = "\0"
    OP_SHFTL = "shiftl"
    OP_SHFTR = "shiftr"
    OP_NSHFT = "noshift"
    OP_ERASE = "erase"
    OP_WRITE = "write"
    OP_GOTO = "goto"
    NUL_OP_LST = {OP_SHFTL, OP_SHFTR, OP_NSHFT, OP_ERASE}
    NON_VALID_ID_NAME = {";", ":", *{chr(i) for i in range(ord(" ") + 1)}}

    def __init__(self, input_str):
        self.input_str = input_str if input_str[-1] == "\0" else input_str+"\0"
        self.pos = 0
        self.trans_tbl = {}
        self.symbols = set()
        self.blank_symbol = None
        self.init_state = None
        self.trans_tbl = {}

        self.curr_token_str = None   # A temporary storage for token strings.
    
    def error(self, msg=""):
        # Get error information.
        lbound, rbound = self.find_line_bounds()
        line_num = "[{}]: ".format(self.current_line_num())
        curr_line = self.input_str[lbound: rbound]
        line_ptr = " "*(self.pos - lbound + len(line_num)) + "^"
        err_msg = "\n{}{}\n{}\n\n{}".format(line_num, curr_line, line_ptr, msg)

        raise SyntaxError(err_msg)

    def current_line_num(self):
        newline_count = 0
        for i, c in enumerate(self.input_str):
            if i == self.pos:
                break
            if c == "\n":
                newline_count += 1
        return newline_count
    
    def find_line_bounds(self):
        lbound, rbound = self.pos, self.pos
        input_len = len(self.input_str)

        # Find the lower index bound of the current line.
        while True:
            if lbound < 0:
                lbound = 0
                break
            if self.input_str[lbound] == "\n":
                lbound += 1
                break
            lbound -= 1

        # Find the upper index bound of the current line.
        while True:
            if rbound == input_len - 1:
                break
            if self.input_str[rbound] == "\n":
                break
            rbound += 1
        return lbound, rbound

    def parse(self):
        self.scan_program()  # Combination of lexer and parser.
        return self.symbols, self.blank_symbol, self.init_state, self.trans_tbl
    
    def scan_program(self):
        # Scan 'program'
        self.scan_symbol_cnstrc()
        while self.input_str[self.pos] != self.EOF:
            self.scan_state_cnstrc()
    
    def repeat_scan(self, repeating_func):
        while True:
            initial_pos = self.pos
            try:
                repeating_func()
            except SyntaxError:
                # Roll back to the first position.
                self.pos = initial_pos
                break

    def scan_str_literal(self, string):
        for c in string:
            if self.input_str[self.pos] != c:
                self.error("Expected: '{}'".format(string))
            self.pos += 1

    def scan_symbol_cnstrc(self):
        self.repeat_scan(self.scan_end_line)
        self.scan_str_literal("symbol:")
        self.scan_end_line()
        self.scan_blank_symbol_decl()
        self.repeat_scan(self.scan_symbol_decl)
        self.repeat_scan(self.scan_end_line)

    def scan_blank_symbol_decl(self):
        self.repeat_scan(self.scan_whitespace)
        # Get blank symbol name.
        blank_sym_name = self.get_symbol_name()
        self.scan_whitespace()
        self.repeat_scan(self.scan_whitespace)
        self.scan_str_literal("(blank)")
        self.scan_end_line()

        # Get the latest token string (the symbol name) and assign it as the
        # blank symbol.
        # Put the symbol name in the symbol set.
        if blank_sym_name in self.symbols:
            self.error("The symbol '{}' is declared more than once".format(blank_sym_name))
        self.symbols.add(blank_sym_name)
        self.blank_symbol = blank_sym_name

    def scan_symbol_decl(self):
        self.repeat_scan(self.scan_whitespace)
        # Scan for the symbol name.
        symbol_name = self.get_symbol_name()
        self.scan_end_line()

        # Put the symbol name in the symbol set.
        if symbol_name in self.symbols:
            self.error("The symbol '{}' is declared more than once".format(symbol_name))
        self.symbols.add(symbol_name)
    
    def get_symbol_name(self):
        return self.get_id_name()

    def scan_state_cnstrc(self):  # HERE
        self.scan_state_header()
        self.repeat_scan(self.scan_instrc)
        self.repeat_scan(self.scan_end_line)

        self.curr_token_str = None

    def scan_state_header(self):
        state_name = self.get_state_name()
        self.scan_str_literal(":")
        self.scan_end_line()

        # Register a state.
        if state_name in self.trans_tbl:
            self.error("The state '{}' is declared more than once".format(state_name))
        self.trans_tbl[state_name] = dict((s, []) for s in self.symbols)

        if self.init_state is None:
            self.init_state = state_name
        
        self.curr_token_str = [state_name]
    
    def get_state_name(self):
        return self.get_id_name()

    def scan_instrc(self):
        self.repeat_scan(self.scan_whitespace)
        symbol_name = self.get_symbol_name()
        # Register the symbol name.
        self.curr_token_str.append(symbol_name)

        # Scan right arrow.
        self.scan_whitespace()
        self.repeat_scan(self.scan_whitespace)
        self.scan_str_literal("->")
        self.scan_whitespace()
        self.repeat_scan(self.scan_whitespace)

        self.scan_op_stat()
        self.repeat_scan(self.scan_del_op_stat)

        # Make way for the read symbols of other instructions in the current
        # state declaration.
        self.curr_token_str.pop()

        self.scan_end_line()
    
    def scan_del_op_stat(self):
        # Scan the delimiter.
        self.scan_str_literal(";")
        self.repeat_scan(self.scan_whitespace)
        self.scan_op_stat()

    def scan_op_stat(self):
        # Scan for operation names.
        for op_name in [*self.NUL_OP_LST, self.OP_WRITE, self.OP_GOTO]:
            initial_pos = self.pos
            try:
                self.scan_str_literal(op_name)
                break
            except SyntaxError:
                # Revert back to the initial position to test other names.
                self.pos = initial_pos
        else:
            self.error("Invalid operator name")
        
        # Specify which type of operators was scanned.
        if op_name in self.NUL_OP_LST:
            op = (op_name,)
        elif op_name == self.OP_WRITE:
            self.scan_whitespace()
            self.repeat_scan(self.scan_whitespace)
            symbol_name = self.get_symbol_name()
            if symbol_name not in self.symbols:
                self.error("Unknown symbol {}".format(symbol_name))

            op = (op_name, symbol_name)
        elif op_name == self.OP_GOTO:
            self.scan_whitespace()
            self.repeat_scan(self.scan_whitespace)
            state_name = self.get_state_name()
            if state_name in self.symbols:
                self.error("The symbol '{}' cannot be a state".format(state_name))

            op = (op_name, state_name)
        else:
            raise AttributeError("Internal error. Unknown operator name")

        curr_state, curr_symbol = self.curr_token_str
        if curr_symbol not in self.trans_tbl[curr_state]:
            self.error("'{}' is not a defined symbol".format(curr_symbol))

        self.trans_tbl[curr_state][curr_symbol].append(op)

    def scan_whitespace(self):
        c = self.input_str[self.pos]
        if c == "\n" or not c.isspace():
            self.error("Must be a white space.")
        self.pos += 1

    def get_id_name(self):
        scanned_char = []
        while True:
            c = self.input_str[self.pos]
            if c in self.NON_VALID_ID_NAME:
                break
            scanned_char.append(c)
            self.pos += 1

        if len(scanned_char) == 0:
            self.error("Name must be a non-white space character")
        return "".join(scanned_char)

    def scan_end_line(self):
        # Scan for extra spaces.
        self.repeat_scan(self.scan_whitespace)

        # Scan for possible comment.
        if self.input_str[self.pos] == "#":
            while True:
                if self.input_str[self.pos] == "\n":
                    self.pos += 1
                    break
                if self.input_str[self.pos] == self.EOF:
                    break
                self.pos += 1                
        else:
            # Scan for the end line character "\n":
            if self.input_str[self.pos] != "\n":
                self.error("Invalid end of line")
            self.pos += 1
