import re

class Lexer:
    def __init__(self):
        # Especificações de tokens
        self.token_specification = [
            # Palavras-chave que parecem importantes (porque sem elas o código não roda)
            ('KEYWORD', r'\b(INICIO|FIM|PROGAMA|IMPLEMENTACAO|EXECUCAO|PRINCIPAL|MODULO|variavel|tipo|escreva|pergunte|EXECUTAR|SE|SENAO|ENQUANTO|FAÇA|ENTAO|funcao|retorne)\b'),
            
            # Tipos, porque a gente precisa saber que tipo de variável tá lidando
            ('TYPE', r'\b(inteiro|texto|decimal|booleano|lista)\b'),
            
            # Operadores: porque o povo adora somar e dividir coisas
            ('OPERATOR', r'\+|\-|\*|/|>=|<=|==|!=|>|<'),  
            
            # Atribuição: todo mundo precisa de um "="
            ('ASSIGN', r'='),  
            
            # Números: porque ninguém quer que 42 seja um texto (ou quer?)
            ('NUMBER', r'\b\d+(\.\d+)?\b'),  
            
            # Strings, o famoso "texto entre aspas" (até hoje confundo as aspas simples e duplas às vezes)
            ('STRING', r'\".*?\"|\'.*?\''),  
            
            # Identificadores: os nomes criativos das variáveis, como "x" e "contador"
            ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z_0-9]*'),  
            
            # Símbolos, porque parênteses e pontos são vida
            ('SYMBOL', r'[{}().,]'),  
            
            # Comentários: onde a gente escreve coisas que ninguém vai ler
            ('COMMENT', r'//.*|#.*'),  
            
            # Novas linhas: não tem utilidade aqui, mas o código precisa de ordem
            ('NEWLINE', r'\n'),  
            
            # Espaços e tabulações: ninguém vê, mas sem eles vira caos
            ('SKIP', r'[ \t]+'),  
            
            # Mismatches: qualquer coisa que não faz sentido vai cair aqui
            ('MISMATCH', r'.'),  
        ]

        # Compilei as regexes porque performance é importante (mesmo que ninguém perceba)
        self.token_regex = re.compile('|'.join(f'(?P<{name}>{regex})' for name, regex in self.token_specification))

    def tokenize(self, code):
        tokens = []
        for match in self.token_regex.finditer(code):
            kind = match.lastgroup
            value = match.group(kind)

            # Ignorar as coisas inúteis
            if kind == 'NEWLINE' or kind == 'SKIP':  
                continue
            elif kind == 'COMMENT':  # Ignorar comentários (como se fossem invisíveis)
                continue
            elif kind == 'MISMATCH':  # Aqui a gente reclama se encontrar algo bizarro
                raise SyntaxError(f"Token inválido: {value}")
            
            # Token legítimo, então adiciona à lista (parabéns, você passou no teste!)
            tokens.append((kind, value))
        
        return tokens

# Teste do Lexer (aquele momento de descobrir se funciona ou se vai gerar caos)
if __name__ == "__main__":
    code = """
    MODULO SAUDACAO.
        funcao cumprimenta(nome)
            escreva("Olá {nome}, seja bem-vindo!").
        retorne null.
    FIM MODULO.

    IMPLEMENTACAO PROGAMA.
    PRINCIPAL.
        EXECUTAR MODULO SAUDACAO.cumprimenta("João").
    FIM PRINCIPAL.
    """

    lexer = Lexer()
    tokens = lexer.tokenize(code)

    # Mostra os tokens no console (ou os erros, porque a vida não é perfeita)
    for token in tokens:
        print(token)
