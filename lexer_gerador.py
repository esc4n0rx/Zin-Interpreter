import ply.lex as lex

class Lexer:
    # A lista de tokens, porque sem esses caras a gente não faz nada.
    tokens = [
        'KEYWORD', 'TYPE', 'OPERATOR', 'ASSIGN', 'NUMBER',
        'STRING', 'IDENTIFIER', 'SYMBOL'
    ]

    # Palavras-chave e tipos. Aqui começa a bagunça que a gente acha que tá organizado.
    keywords = {
        'INICIO', 'FIM', 'PROGAMA', 'IMPLEMENTACAO', 'EXECUCAO', 'PRINCIPAL', 
        'MODULO', 'variavel', 'tipo', 'escreva', 'pergunte', 'EXECUTAR', 
        'SE', 'SENAO', 'ENQUANTO', 'FAÇA', 'ENTAO', 'funcao', 'retorne', 
        'GRUPO'
    }

    # Tipos que fingimos que sabemos lidar.
    types = {'inteiro', 'texto', 'decimal', 'booleano', 'lista','grupo'}

    # Regras de expressões regulares, porque aqui é onde a gente tenta domar o caos.
    t_ASSIGN = r'='
    t_OPERATOR = r'\+|\-|\*|/|>=|<=|==|!=|>|<'
    t_SYMBOL = r'[{}().,\[\]]'
    t_STRING = r'\".*?\"|\'.*?\''
    t_ignore = ' \t'  # Porque espaço e tab são lixo que a gente não quer enxergar.

    # Achamos um número? Então convertemos se tiver ponto ou não, e é isso.
    def t_NUMBER(self, t):
        r'\d+(\.\d+)?'
        t.value = float(t.value) if '.' in t.value else int(t.value)
        return t


    def t_COMMENT(self, t):
        r'\#.*'
        pass
    
    # Identificadores, que podem acabar virando KEYWORD ou TYPE se nos der na telha.
    def t_IDENTIFIER(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        if t.value in self.keywords:
            t.type = 'KEYWORD'
        elif t.value in self.types:
            t.type = 'TYPE'
        return t

    # Pra contar linhas, porque às vezes a gente precisa mostrar que sabe em que linha tá o erro.
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # Se der ruim e encontrar um token que a gente não tem ideia do que é,
    # lançamos um SyntaxError. Porque drama é a alma do negócio.
    def t_error(self, t):
        raise SyntaxError(f"Token inválido: {t.value[0]}")
        t.lexer.skip(1)

    # Método build pra criar o lexer. Nome super criativo, óbvio.
    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    # Método tokenize pra rodar e cuspir os tokens num list. 
    # E a gente reza pra vir algo decente.
    def tokenize(self, data):
        self.lexer.input(data)
        return list(iter(self.lexer.token, None))


# Teste do Lexer com PLY pra ver se quebra ou não.
if __name__ == "__main__":
    # Não me venha dizer que esse código não é lindo. Ele funciona, e é isso que importa.
    # Teste com LISTA e GRUPO
    code = """
    variavel lista_numeros tipo lista = [1, 2, 3, 4, 5].
    variavel grupo_pessoas tipo grupo = GRUPO(
        ["NOME", "FUNCAO", "IDADE"],
        ["joao", "administrador", 15],
        ["vitor", "supervisor", 16],
        ["sandro", "operador", 19]
    ).
    escreva("Nome da primeira pessoa: {grupo_pessoas[0].NOME}").
    """

    lexer = Lexer()
    lexer.build()
    tokens = lexer.tokenize(code)

    for token in tokens:
        print(token)
