import re

TOKEN_SPECS = [
    ('DEFINE', r'DEFINE'),
    ('RETURN', r'RETURN'),
    ('SET', r'SET'),
    ('IF', r'IF'),
    ('ELSE', r'ELSE'),
    ('WHILE', r'WHILE'),
    ('PRINT', r'SHOW'),
    ('NUMBER', r'\d+(\.\d+)?'),
    ('STRING', r'"(?:\\.|[^"\\])*"'),
    ('ID', r'[A-Za-z_][A-Za-z0-9_]*'),
    ('ASSIGN', r'='),
    ('COMPARE', r'==|!=|<=|>=|<|>'),
    ('OP', r'[+\-*/%?]'),
    ('END', r';'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACE', r'\['),
    ('RBRACE', r'\]'),
    ('OPEN_CURLY', r'\{'),
    ('CLOSE_CURLY', r'\}'),
    ('COMMA', r','),
    ('SKIP', r'[ \t]+'),
    ('NEWLINE', r'\n'),
]


class MyInterpreter:
    def __init__(self):
        self.variables = {}
        self.tokens = []
        self.current = 0

    def tokenize(self, code):
        tokens = []
        pos = 0
        while pos < len(code):
            match = None
            for name, pattern in TOKEN_SPECS:
                regex = re.compile(pattern)
                match = regex.match(code, pos)
                if match:
                    if name != 'SKIP' and name != 'NEWLINE':
                        tokens.append((name, match.group()))
                    pos = match.end()
                    break
            if not match:
                raise SyntaxError(f"Illegal character at {pos}")
        tokens.append(('EOF', ''))
        return tokens

    def execute_command(self, code):
        self.tokens = self.tokenize(code)
        self.current = 0
        while self.current < len(self.tokens) and self.tokens[self.current][0] != 'EOF':
            self.parse_and_run()

    def parse_and_run(self):
        if self.current >= len(self.tokens): return
        token_type = self.tokens[self.current][0]

        if token_type == 'SET':
            self.current += 1
            var_name = self.tokens[self.current][1]
            self.current += 1
            if self.tokens[self.current][0] == 'ASSIGN':
                self.current += 1
                val = self.evaluate_expression()
                self.variables[var_name] = val
                if self.current < len(self.tokens) and self.tokens[self.current][0] == 'END':
                    self.current += 1

        elif token_type == 'PRINT':
            self.current += 1
            if self.tokens[self.current][0] == 'LPAREN':
                self.current += 1
                val = self.evaluate_expression()
                print(f"[Output]: {val}")
                if self.tokens[self.current][0] == 'RPAREN':
                    self.current += 1
                if self.current < len(self.tokens) and self.tokens[self.current][0] == 'END':
                    self.current += 1
        else:
            self.current += 1

    def get_atom_value(self):
        if self.current >= len(self.tokens): return None

        token_type, value = self.tokens[self.current]
        self.current += 1

        if token_type == 'NUMBER':
            return float(value) if '.' in value else int(value)
        elif token_type == 'STRING':
            return value.strip('"')
        elif token_type == 'ID':
            return self.variables.get(value, value)
        return None

    def evaluate_term(self):
        left_val = self.get_atom_value()

        while self.current < len(self.tokens) and self.tokens[self.current][1] in ('*', '/'):
            op = self.tokens[self.current][1]
            self.current += 1
            right_val = self.get_atom_value()

            if op == '*':
                left_val *= right_val
            elif op == '/':
                left_val /= right_val

        return left_val

    def evaluate_expression(self):
        left_val = self.evaluate_term()

        while self.current < len(self.tokens) and self.tokens[self.current][1] in ('+', '-'):
            op = self.tokens[self.current][1]
            self.current += 1
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
    print("Custom Language Interpreter v1.2")
    while True:
        try:
            user_input = input(">> ")
            if user_input.lower() == 'exit': break
            interp.execute_command(user_input)
        except Exception as e:
            print(f"Error: {e}")
