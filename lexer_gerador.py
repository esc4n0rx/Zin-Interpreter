import ply.lex as lex

class Lexer:
    # A lista de tokens.
    tokens = [
        'KEYWORD', 
        'TYPE', 
        'OPERATOR', 
        'ASSIGN', 
        'NUMBER',
        'STRING', 
        'IDENTIFIER', 
        'SYMBOL'
    ]

    # Palavras-chave e tipos.
    keywords = {
        'INICIO', 'FIM', 'PROGAMA', 'IMPLEMENTACAO', 'EXECUCAO', 'PRINCIPAL',
        'MODULO', 'variavel', 'tipo', 'escreva', 'pergunte', 'EXECUTAR',
        'SE', 'SENAO', 'ENQUANTO', 'FACA', 'ENTAO', 'funcao', 'retorne',
        'GRUPO', 'importe',

        # -------------
        # Novas keywords
        # -------------
        'PARA',     # Para laço do tipo for
        'ATE',      # Ex: PARA i = 0 ATE 10
        'PASSO',    # Incremento do loop
        'REPITA'    # Ex: REPITA ... ATE ...
    }

    # Conjunto de tipos que a linguagem Zin reconhece
    types = {'inteiro', 'texto', 'decimal', 'booleano', 'lista', 'grupo'}

    # Expressões regulares
    t_ASSIGN = r'='
    t_OPERATOR = r'\+|\-|\*|/|>=|<=|==|!=|>|<'
    t_SYMBOL = r'[{}().,\[\]]'
    t_STRING = r'\".*?\"|\'.*?\''
    t_ignore = ' \t'

    # Número
    def t_NUMBER(self, t):
        r'\d+(\.\d+)?'
        t.value = float(t.value) if '.' in t.value else int(t.value)
        return t

    # Ignorar comentários
    def t_COMMENT(self, t):
        r'\#.*'
        pass

    # Identificadores
    def t_IDENTIFIER(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        if t.value in self.keywords:
            t.type = 'KEYWORD'
        elif t.value in self.types:
            t.type = 'TYPE'
        return t

    # Nova linha
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # Erro léxico
    def t_error(self, t):
        error_message = f"Token inválido '{t.value[0]}' na linha {t.lineno}, posição {t.lexpos}."
        raise SyntaxError(error_message)
        t.lexer.skip(1)

    # Constrói o lexer
    def build(self, **kwargs):
        import ply.lex as lex
        self.lexer = lex.lex(module=self, **kwargs)

    # Tokeniza um código
    def tokenize(self, data):
        try:
            self.lexer.input(data)
            return list(iter(self.lexer.token, None))
        except SyntaxError as e:
            print(f"Erro durante a tokenização: {e}")
            return []

if __name__ == "__main__":

    code = """
    INICIO PROGAMA TESTE_ERRO.
    importe zin_math.
    variavel resultado_raiz tipo decimal
    resultado_raiz = zin_math.raiz_quadrada(49))
    FIM PROGAMA TESTE_ERRO.
    """

    lexer = Lexer()
    lexer.build()
    try:
        tokens = lexer.tokenize(code)
        for token in tokens:
            print(token)
    except SyntaxError as e:
        print(f"Erro capturado no teste: {e}")
