import ply.lex as lex

class Lexer:
    # A lista de tokens, porque sem esses caras a gente não faz nada.
    tokens = [
        'KEYWORD', 'TYPE', 'OPERATOR', 'ASSIGN', 'NUMBER',
        'STRING', 'IDENTIFIER', 'SYMBOL'
    ]

    # Palavras-chave e tipos.
    keywords = {
        'INICIO', 'FIM', 'PROGAMA', 'IMPLEMENTACAO', 'EXECUCAO', 'PRINCIPAL', 
        'MODULO', 'variavel', 'tipo', 'escreva', 'pergunte', 'EXECUTAR', 
        'SE', 'SENAO', 'ENQUANTO', 'FAÇA', 'ENTAO', 'funcao', 'retorne', 
        'GRUPO', 'importe'  # Aqui adicionamos "importe"
    }

    # Tipos que fingimos que sabemos lidar.
    types = {'inteiro', 'texto', 'decimal', 'booleano', 'lista', 'grupo'}

    # Regras de expressões regulares.
    t_ASSIGN = r'='
    t_OPERATOR = r'\+|\-|\*|/|>=|<=|==|!=|>|<'
    t_SYMBOL = r'[{}().,\[\]]'
    t_STRING = r'\".*?\"|\'.*?\''
    t_ignore = ' \t'

    # Achamos um número? Então convertemos se tiver ponto ou não.
    def t_NUMBER(self, t):
        r'\d+(\.\d+)?'
        t.value = float(t.value) if '.' in t.value else int(t.value)
        return t

    # Ignorar comentários iniciados por #
    def t_COMMENT(self, t):
        r'\#.*'
        pass

    # Identificadores.
    def t_IDENTIFIER(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        if t.value in self.keywords:
            t.type = 'KEYWORD'
        elif t.value in self.types:
            t.type = 'TYPE'
        return t

    # Contar linhas.
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # Lidar com tokens inválidos.
    def t_error(self, t):
        raise SyntaxError(f"Token inválido: {t.value[0]}")
        t.lexer.skip(1)

    # Método build para criar o lexer.
    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    # Método tokenize para processar o código.
    def tokenize(self, data):
        self.lexer.input(data)
        return list(iter(self.lexer.token, None))


# Teste do Lexer com PLY para ver se funciona.
if __name__ == "__main__":
    # Teste com IMPORTAÇÃO
    code = """
    INICIO PROGAMA TESTE_IMPORT.
    importe zin_math.
    importe zin_file.

    variavel resultado_raiz tipo decimal
    variavel conteudo_arquivo tipo texto

    IMPLEMENTACAO PROGAMA TESTE_IMPORT.
    PRINCIPAL.
        resultado_raiz = zin_math.raiz_quadrada(49).
        escreva("A raiz quadrada de 49 é: {resultado_raiz}").

        zin_file.escrever_arquivo("teste.txt", "Este é um teste com Zin.").
        conteudo_arquivo = zin_file.ler_arquivo("teste.txt").
        escreva("Conteúdo do arquivo: {conteudo_arquivo}").

    FIM PRINCIPAL.

    EXECUCAO PROGAMA TESTE_IMPORT.
    EXECUTAR PRINCIPAL.

    FIM PROGAMA TESTE_IMPORT.

    """

    lexer = Lexer()
    lexer.build()
    tokens = lexer.tokenize(code)

    for token in tokens:
        print(token)
