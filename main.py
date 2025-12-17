import re

TOKEN_SPECS = [
    # Keywords (use word boundaries so DEFINE doesn't match part of a longer identifier)
    ('DEFINE', r'\bDEFINE\b'),
    ('RETURN', r'\bRETURN\b'),
    ('SET', r'\bSET\b'),
    ('IF', r'\bIF\b'),
    ('ELSE', r'\bELSE\b'),
    ('WHILE', r'\bWHILE\b'),
    ('PRINT', r'\bSHOW\b'),

  
    ('NUMBER', r'\d+(\.\d+)?'),
    ('STRING', r'"(?:\\.|[^"\\])*"'),

    # Operators 
    ('COMPARE', r'==|!=|<=|>=|<|>'),  # must come BEFORE ASSIGN
    ('ASSIGN', r'='),

    ('OP', r'[+\-*/%?]'),
    ('END', r';'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACE', r'\['),
    ('RBRACE', r'\]'),
    ('OPEN_CURLY', r'\{'),
    ('CLOSE_CURLY', r'\}'),
    ('COMMA', r','),

    # Identifiers 
    ('ID', r'[A-Za-z_][A-Za-z0-9_]*'),

    # Whitespace
    ('SKIP', r'[ \t]+'),
    ('NEWLINE', r'\n'),
]


class MyInterpreter:
    def __init__(self):
        self.variables = {}
        self.tokens = []
        self.current = 0

        
        self.compiled_specs = [(name, re.compile(pattern)) for name, pattern in TOKEN_SPECS]

    def tokenize(self, code: str):
        tokens = []
        pos = 0

        while pos < len(code):
            match = None

            for name, regex in self.compiled_specs:
                match = regex.match(code, pos)
                if match:
                    if name not in ('SKIP', 'NEWLINE'):
                        tokens.append((name, match.group()))
                    pos = match.end()
                    break

            if not match:
                # Show the problematic character for easier debugging
                bad = code[pos:pos + 20].replace('\n', '\\n')
                raise SyntaxError(f"Illegal character at index {pos}: '{bad}'")

        tokens.append(('EOF', ''))
        return tokens

    def execute_command(self, code: str):
        self.tokens = self.tokenize(code)
        self.current = 0

        while self.current < len(self.tokens) and self.tokens[self.current][0] != 'EOF':
            self.parse_and_run()

    
    def peek(self):
        if self.current >= len(self.tokens):
            return ('EOF', '')
        return self.tokens[self.current]

    def consume(self, expected_type=None):
        tok = self.peek()
        if expected_type and tok[0] != expected_type:
            raise SyntaxError(f"Expected {expected_type}, got {tok[0]} ({tok[1]!r})")
        self.current += 1
        return tok

    
    def parse_and_run(self):
        if self.current >= len(self.tokens):
            return

        token_type, _ = self.peek()

        if token_type == 'SET':
            self.consume('SET')
            var_tok = self.consume('ID')
            self.consume('ASSIGN')
            val = self.evaluate_expression()
            self.variables[var_tok[1]] = val
            if self.peek()[0] == 'END':
                self.consume('END')
            return

        if token_type == 'PRINT':
            self.consume('PRINT')
            self.consume('LPAREN')
            val = self.evaluate_expression()
            self.consume('RPAREN')
            print(f"[Output]: {val}")
            if self.peek()[0] == 'END':
                self.consume('END')
            return

        
        self.current += 1

    
    def get_atom_value(self):
        tok_type, value = self.peek()

        if tok_type == 'NUMBER':
            self.consume('NUMBER')
            return float(value) if '.' in value else int(value)

        if tok_type == 'STRING':
            self.consume('STRING')
            # unescape \" \\ \n etc.
            inner = value[1:-1]
            return bytes(inner, "utf-8").decode("unicode_escape")

        if tok_type == 'ID':
            self.consume('ID')
            if value not in self.variables:
                raise NameError(f"Undefined variable: {value}")
            return self.variables[value]

        if tok_type == 'LPAREN':
            self.consume('LPAREN')
            val = self.evaluate_expression()
            self.consume('RPAREN')
            return val

        raise SyntaxError(f"Expected atom, got {tok_type} ({value!r})")

    def evaluate_term(self):
        left_val = self.get_atom_value()

        while self.peek()[0] == 'OP' and self.peek()[1] in ('*', '/'):
            op = self.consume('OP')[1]
            right_val = self.get_atom_value()

            if op == '*':
                left_val *= right_val
            elif op == '/':
                left_val /= right_val

        return left_val

    def evaluate_expression(self):
        left_val = self.evaluate_term()

        while self.peek()[0] == 'OP' and self.peek()[1] in ('+', '-'):
            op = self.consume('OP')[1]
            right_val = self.evaluate_term()

            if op == '+':
                if isinstance(left_val, str) or isinstance(right_val, str):
                    left_val = str(left_val) + str(right_val)
                else:
                    left_val += right_val
            elif op == '-':
                left_val -= right_val

        return left_val


if __name__ == "__main__":
    interp = MyInterpreter()
    print("Custom Language Interpreter v1.3 (fixed)")
    print("Type 'exit' to quit.")
    while True:
        try:
            user_input = input(">> ")
            if user_input.strip().lower() == 'exit':
                break
            interp.execute_command(user_input)
        except Exception as e:
            print(f"Error: {e}")
