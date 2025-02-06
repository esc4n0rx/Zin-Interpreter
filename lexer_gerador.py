import ply.lex as lex
import logging

# Configurando o logging para exibir mensagens de debug e superiores
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

# Definindo a classe Lexer que será responsável por transformar o código fonte em tokens
class Lexer:
    # Lista de tokens que nossa linguagem Zin reconhece
        tokens = [
        'KEYWORD',    # Palavras reservadas da linguagem
        'TYPE',       # Tipos de dados (ex.: inteiro, texto, etc.)
        'OPERATOR',   # Operadores aritméticos e de comparação
        'ASSIGN',     # Operador de atribuição (=)
        'NUMBER',     # Números inteiros e decimais
        'STRING',     # Literais de string
        'IDENTIFIER', # Identificadores (nomes de variáveis, funções, etc.)
        'SYMBOL'    # Símbolos como parênteses, chaves, colchetes, etc.
    ]


    # Conjunto de palavras-chave que nosso interpretador reconhece
        keywords = {
            'INICIO', 'FIM', 'PROGAMA', 'IMPLEMENTACAO', 'EXECUCAO', 'PRINCIPAL',
            'MODULO', 'variavel', 'tipo', 'escreva', 'pergunte', 'EXECUTAR',
            'SE', 'SENAO', 'ENQUANTO', 'FACA', 'ENTAO', 'funcao', 'retorne',
            'GRUPO', 'importe','ARQUIVO_INICIO', 'ARQUIVO_ESCREVA','ARQUIVO_LEIA',    

            # Novas keywords para estruturas de controle
            'PARA',     # Para laço do tipo for
            'ATE',      # Exemplo: PARA i = 0 ATE 10
            'PASSO',    # Incremento do loop
            'REPITA'    # Exemplo: REPITA ... ATE ...
        }

        # Conjunto de tipos que a linguagem Zin reconhece
        types = {'inteiro', 'texto', 'decimal', 'booleano', 'lista', 'grupo'}

        # Expressões regulares para definir os tokens
        t_ASSIGN = r'='                    # Operador de atribuição
        t_OPERATOR = r'\+|\-|\*|/|>=|<=|==|!=|>|<'  # Operadores aritméticos e comparativos
        t_SYMBOL = r'[{}().,\[\]]'          # Símbolos diversos da linguagem
        t_STRING = r'\".*?\"|\'.*?\''        # Literais de string (suporta "texto" ou 'texto')
        t_ignore = ' \t'                    # Ignora espaços e tabulações

    # Regra para identificar números (inteiros e decimais)
        def t_NUMBER(self, t):
            r'\d+(\.\d+)?'
            # Se tiver ponto, é decimal; caso contrário, é inteiro
            t.value = float(t.value) if '.' in t.value else int(t.value)
            return t

        # Regra para ignorar comentários que começam com '#'
        def t_COMMENT(self, t):
            r'\#.*'
            # Simplesmente pulamos o comentário (não retornamos token nenhum)
            pass

        # Regra para identificar identificadores (nomes, variáveis, funções, etc.)
        def t_IDENTIFIER(self, t):
            r'[a-zA-Z_][a-zA-Z_0-9]*'
            # Se o valor do identificador estiver na lista de keywords, trocamos o tipo para KEYWORD
            if t.value in self.keywords:
                t.type = 'KEYWORD'
            # Se estiver na lista de tipos, definimos como TYPE
            elif t.value in self.types:
                t.type = 'TYPE'
            return t

        # Regra para tratar quebras de linha e atualizar o número da linha no lexer
        def t_newline(self, t):
            r'\n+'
            # Incrementamos o contador de linhas conforme a quantidade de quebras encontradas
            t.lexer.lineno += len(t.value)


            # Regra para identificar o comando ARQUIVO-INICIO
        def t_ARQUIVO_INICIO(self, t):
            r'ARQUIVO\-INICIO'
            # Loga o reconhecimento deste token (opcional)
            # logging.debug("Token ARQUIVO-INICIO reconhecido.")
            return t

        # Regra para identificar o comando ARQUIVO-ESCREVA
        def t_ARQUIVO_ESCREVA(self, t):
            r'ARQUIVO\-ESCREVA'
            return t

        # Regra para identificar o comando ARQUIVO-LEIA
        def t_ARQUIVO_LEIA(self, t):
            r'ARQUIVO\-LEIA'
            return t


        # Regra para lidar com erros léxicos (caracteres não reconhecidos)
        def t_error(self, t):
            # Montamos uma mensagem de erro com detalhes do token inválido
            error_message = f"Token inválido '{t.value[0]}' na linha {t.lineno}, posição {t.lexpos}."
            # Logamos o erro
            logging.error(error_message)
            # Levantamos uma exceção para sinalizar o erro
            raise SyntaxError(error_message)
            # Esta linha não será executada, mas serve para indicar que o token inválido seria pulado
            t.lexer.skip(1)

        # Método para construir o lexer utilizando o módulo ply.lex
        def build(self, **kwargs):
            # Aqui usamos a função lex.lex para construir o lexer a partir do nosso módulo
            self.lexer = lex.lex(module=self, **kwargs)
            # Logamos que o lexer foi construído com sucesso
            logging.info("Lexer built com sucesso.")

        # Método para tokenizar um código fonte (transformar o código em uma lista de tokens)
        def tokenize(self, data):
            try:
                # Alimenta o lexer com os dados (código fonte)
                self.lexer.input(data)
                # Coleta todos os tokens gerados e os armazena em uma lista
                tokens_list = list(iter(self.lexer.token, None))
                # Loga quantos tokens foram gerados
                logging.info(f"Tokenização concluída. Número de tokens: {len(tokens_list)}")
                return tokens_list
            except SyntaxError as e:
                # Caso ocorra um erro de sintaxe, logamos o erro e retornamos uma lista vazia
                logging.error(f"Erro durante a tokenização: {e}")
                return []

if __name__ == "__main__":
    # Código de teste corrigido
    code = """
    INICIO PROGAMA TESTE_ERRO.
    variavel test tipo texto
    ARQUIVO-INICIO("arquivo",.txt).
    ARQUIVO-ESCREVA("TESTE ESCREVENDO ALGO NO ARQUIVO,arquivo.txt").
    ARQUIVO-LEIA(arquivo.txt).
    """
    # Cria uma instância do Lexer
    lexer = Lexer()
    # Constrói o lexer (gera as estruturas internas necessárias)
    lexer.build()
    try:
        # Tenta tokenizar o código de teste
        tokens = lexer.tokenize(code)
        # Se desejar, itere e logue os tokens aqui (ex.: logging.debug(token))
        
    except SyntaxError as e:
        # Caso haja um erro de sintaxe, loga o erro
        logging.error(f"Erro capturado no teste: {e}")

