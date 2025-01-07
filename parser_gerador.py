import json
from lexer_gerador import Lexer  # Importando o Lexer com PLY. Só pra gente dizer que a gente sabe o que tá fazendo.

# O Parser, aquele que vai tentar dar sentido à sequência de tokens
# e criar nossa querida AST (ou bagunça controlada).
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = None
        self.index = -1
        # É aqui que a gente vai montar nosso dicionário bonitinho
        # fingindo que é super organizado.
        self.ast = {
            "programa": {
                "nome": None,
                "variaveis": [],
                "implementacao": {},
                "execucao": {
                    "modulos": []
                }
            }
        }

    # Função pra mover pro próximo token. Tipo pular de pedra em pedra no rio.
    def advance(self):
        self.index += 1
        if self.index < len(self.tokens):
            self.current_token = self.tokens[self.index]
        else:
            self.current_token = None

    # Esperamos que o próximo token seja o esperado. Se não for, chora e morre.
    def expect(self, token_type, value=None):
        if self.current_token is None:
            raise SyntaxError("Token inesperado: fim do arquivo")
        if self.current_token.type != token_type or (value and self.current_token.value != value):
            raise SyntaxError(f"Token inesperado: {self.current_token}")
        self.advance()

    # Ponto de entrada do parser. É aqui que o caos (tokens) vira ordem (AST).
    def parse(self):
        self.advance()
        self.parse_inicio()
        self.parse_implementacao()
        self.parse_execucao()
        return self.ast

    # ---------------------------------------------------------
    #  BLOCO: INICIO
    # ---------------------------------------------------------
    # Lê o "INICIO PROGAMA NOME_DO_PROGRAMA." e as variáveis iniciais.
    def parse_inicio(self):
        self.expect("KEYWORD", "INICIO")
        self.expect("KEYWORD", "PROGAMA")
        self.ast["programa"]["nome"] = self.current_token.value
        self.expect("IDENTIFIER")
        self.expect("SYMBOL", ".")

        # Cata as variáveis no começo do programa, se rolar
        while self.current_token and self.current_token.value == "variavel":
            self.parse_variavel()

    def parse_variavel(self):
        self.expect("KEYWORD", "variavel")
        nome = self.current_token.value
        self.expect("IDENTIFIER")
        self.expect("KEYWORD", "tipo")
        tipo = self.current_token.value
        self.expect("TYPE")
        # Coloca a variável na lista. Esperamos que sejam poucas, né?
        self.ast["programa"]["variaveis"].append({"nome": nome, "tipo": tipo})

    # ---------------------------------------------------------
    #  BLOCO: IMPLEMENTACAO
    # ---------------------------------------------------------
    # Lê o "IMPLEMENTACAO PROGAMA NOME_DO_PROGRAMA.", depois PRINCIPAL,
    # possivelmente execuções pós-principal, e MODULOS. Mamma mia.
    def parse_implementacao(self):
        self.expect("KEYWORD", "IMPLEMENTACAO")
        self.expect("KEYWORD", "PROGAMA")
        self.expect("IDENTIFIER", self.ast["programa"]["nome"])
        self.expect("SYMBOL", ".")

        # (1) Bloco PRINCIPAL
        self.expect("KEYWORD", "PRINCIPAL")
        self.expect("SYMBOL", ".")
        principal = []
        while self.current_token and self.current_token.value != "FIM":
            principal.append(self.parse_statement())
        self.expect("KEYWORD", "FIM")
        self.expect("KEYWORD", "PRINCIPAL")
        self.expect("SYMBOL", ".")
        self.ast["programa"]["implementacao"]["principal"] = principal

        # (2) Execuções logo após o PRINCIPAL (antes de MODULO, se existir)
        execucoes_apos_principal = []
        while self.current_token and self.current_token.value not in ("MODULO", "EXECUCAO"):
            execucoes_apos_principal.append(self.parse_statement())

        self.ast["programa"]["implementacao"]["execucoes_apos_principal"] = execucoes_apos_principal

        # (3) Processa blocos de MODULO
        while self.current_token and self.current_token.value == "MODULO":
            self.parse_modulo()

    def parse_modulo(self):
        self.expect("KEYWORD", "MODULO")
        nome_modulo = self.current_token.value
        self.expect("IDENTIFIER")
        self.expect("SYMBOL", ".")
        funcoes = []

        # Vem as funções. Se tiver outra coisa que não seja função, explode.
        while self.current_token and self.current_token.value != "FIM":
            if self.current_token.value == "funcao":
                funcoes.append(self.parse_funcao())
            else:
                raise SyntaxError(f"Comando inesperado no módulo: {self.current_token}")

        self.expect("KEYWORD", "FIM")
        self.expect("KEYWORD", "MODULO")
        self.expect("SYMBOL", ".")

        # Salva esse módulo de volta na AST. Colecionar módulos é nossa meta.
        self.ast["programa"]["implementacao"].setdefault("modulos", {})[nome_modulo] = funcoes

    def parse_funcao(self):
        # Opa, uma função! Bora ler nome, parâmetros, corpo e retorno.
        self.expect("KEYWORD", "funcao")
        nome_funcao = self.current_token.value
        self.expect("IDENTIFIER")
        self.expect("SYMBOL", "(")
        parametros = []
        while self.current_token and self.current_token.type == "IDENTIFIER":
            parametros.append(self.current_token.value)
            self.expect("IDENTIFIER")
            if self.current_token.value == ",":
                self.expect("SYMBOL", ",")
        self.expect("SYMBOL", ")")

        # Corpo: statements até achar o retorne
        corpo = []
        while self.current_token and self.current_token.value != "retorne":
            corpo.append(self.parse_statement())

        # Pega o retorno da função
        self.expect("KEYWORD", "retorne")
        retorno = self.parse_expression()
        self.expect("SYMBOL", ".")

        return {
            "nome": nome_funcao,
            "parametros": parametros,
            "corpo": corpo,
            "retorno": retorno
        }

    # ---------------------------------------------------------
    #  PARSE DE STATEMENTS
    # ---------------------------------------------------------
    def parse_statement(self):
        # Identifica o tipo de statement pelo token atual. Se não bater, pau.
        if self.current_token.type == "IDENTIFIER":
            # Atribuição: var = valor.
            nome = self.current_token.value
            self.expect("IDENTIFIER")
            self.expect("ASSIGN")
            valor = self.parse_expression()
            self.expect("SYMBOL", ".")
            return {"atribuir": {"variavel": nome, "valor": valor}}

        elif self.current_token.value == "escreva":
            # "escreva("alguma coisa")..."
            self.expect("KEYWORD", "escreva")
            self.expect("SYMBOL", "(")
            texto = self.current_token.value
            self.expect("STRING")
            self.expect("SYMBOL", ")")
            self.expect("SYMBOL", ".")
            return {"escreva": texto.strip('"')}

        elif self.current_token.value == "pergunte":
            # "pergunte("alguma coisa" {variavel})..."
            self.expect("KEYWORD", "pergunte")
            self.expect("SYMBOL", "(")
            texto = self.current_token.value
            self.expect("STRING")
            self.expect("SYMBOL", "{")
            variavel = self.current_token.value
            self.expect("IDENTIFIER")
            self.expect("SYMBOL", "}")
            self.expect("SYMBOL", ")")
            self.expect("SYMBOL", ".")
            return {"pergunte": {"texto": texto.strip('"'), "variavel": variavel}}

        elif self.current_token.value == "SE":
            return self.parse_se()

        elif self.current_token.value == "ENQUANTO":
            return self.parse_enquanto()

        elif self.current_token.value == "EXECUTAR":
            self.expect("KEYWORD", "EXECUTAR")
            if self.current_token.value == "MODULO":
                # "EXECUTAR MODULO NomeModulo."
                self.expect("KEYWORD", "MODULO")
                nome_modulo = self.current_token.value
                self.expect("IDENTIFIER")
                self.expect("SYMBOL", ".")
                return {"executar_modulo": nome_modulo}
            else:
                # "EXECUTAR qualquer_coisa."
                nome_qualquer = self.current_token.value
                self.expect("IDENTIFIER")
                self.expect("SYMBOL", ".")
                return {"executar": nome_qualquer}

        raise SyntaxError(f"Comando desconhecido: {self.current_token}")

    def parse_enquanto(self):
        # "ENQUANTO cond FAÇA. ... FIM ENQUANTO."
        self.expect("KEYWORD", "ENQUANTO")
        condicao = self.parse_expression()
        self.expect("KEYWORD", "FAÇA")
        self.expect("SYMBOL", ".")
        bloco_enquanto = []
        while self.current_token and self.current_token[1] != "FIM":
            bloco_enquanto.append(self.parse_statement())
        self.expect("KEYWORD", "FIM")
        self.expect("KEYWORD", "ENQUANTO")
        self.expect("SYMBOL", ".")
        return {
            "tipo": "ENQUANTO",
            "condicao": condicao,
            "bloco": bloco_enquanto
        }

    # ---------------------------------------------------------
    #  EXPRESSÕES
    # ---------------------------------------------------------
    # Lê algo que pode ser NUMBER ou IDENTIFIER, e pode ter operador no meio.
    def parse_expression(self):
        left = self.current_token.value
        if self.current_token.type in ("NUMBER", "IDENTIFIER"):
            self.expect(self.current_token.type)
            # Se tiver operador, bora montar {left, operator, right}
            if self.current_token and self.current_token.type == "OPERATOR":
                operator = self.current_token.value
                self.expect("OPERATOR")
                right = self.current_token.value
                self.expect(self.current_token.type)
                return {"left": left, "operator": operator, "right": right}
            return left
        raise SyntaxError(f"Expressão inválida: {self.current_token}")

    def parse_se(self):
        # "SE condicao ENTAO. ... SENAO. ... FIM SE."
        self.expect("KEYWORD", "SE")
        condicao = self.parse_expression()
        self.expect("KEYWORD", "ENTAO")
        self.expect("SYMBOL", ".")
        
        # Bloco do "SE"
        bloco_se = []
        while self.current_token and self.current_token.value not in ("SENAO", "FIM"):
            bloco_se.append(self.parse_statement())

        # Se tiver "SENAO"
        bloco_senao = None
        if self.current_token and self.current_token.value == "SENAO":
            self.expect("KEYWORD", "SENAO")
            self.expect("SYMBOL", ".")
            bloco_senao = []
            while self.current_token and self.current_token.value != "FIM":
                bloco_senao.append(self.parse_statement())

        # FIM SE, que é tipo a tampa da panela
        self.expect("KEYWORD", "FIM")
        self.expect("KEYWORD", "SE")
        self.expect("SYMBOL", ".")

        return {
            "tipo": "SE",
            "condicao": condicao,
            "bloco_se": bloco_se,
            "bloco_senao": bloco_senao,
        }

    # ---------------------------------------------------------
    #  BLOCO: EXECUCAO
    # ---------------------------------------------------------
    def parse_execucao(self):
        # "EXECUCAO PROGAMA NOME_DO_PROGRAMA."
        self.expect("KEYWORD", "EXECUCAO")
        self.expect("KEYWORD", "PROGAMA")
        self.expect("IDENTIFIER", self.ast["programa"]["nome"])
        self.expect("SYMBOL", ".")

        # Lê as EXECUTAR
        while self.current_token and self.current_token.value == "EXECUTAR":
            self.expect("KEYWORD", "EXECUTAR")
            if self.current_token.value == "PRINCIPAL":
                self.expect("KEYWORD", "PRINCIPAL")
                self.expect("SYMBOL", ".")
                self.ast["programa"]["execucao"]["modulos"].append("PRINCIPAL")
            else:
                modulo = self.current_token.value
                self.expect("IDENTIFIER")
                self.expect("SYMBOL", ".")
                self.ast["programa"]["execucao"]["modulos"].append(modulo)


# ----------------------------------------------------------
#         Teste do Lexer e Parser
# ----------------------------------------------------------
if __name__ == "__main__":
    code = """
    INICIO PROGAMA TESTE_MODULOS.
    variavel nome tipo texto
    variavel idade tipo inteiro

    IMPLEMENTACAO PROGAMA TESTE_MODULOS.
    PRINCIPAL.
    pergunte("Qual o seu nome?" {nome}).
    pergunte("Qual a sua idade?" {idade}).
    EXECUTAR MODULO SAUDACAO.
    EXECUTAR MODULO VERIFICA_IDADE.
    FIM PRINCIPAL.

    MODULO SAUDACAO.
    funcao cumprimenta(nome)
        escreva("Olá {nome}, seja bem-vindo!").
    retorne null.
    FIM MODULO.

    MODULO VERIFICA_IDADE.
    funcao verifica(idade)
        SE idade >= 18 ENTAO.
            escreva("Você é maior de idade.").
        SENAO.
            escreva("Você é menor de idade.").
        FIM SE.
    retorne null.
    FIM MODULO.

    EXECUCAO PROGAMA TESTE_MODULOS.
    EXECUTAR PRINCIPAL.

    FIM PROGAMA TESTE_MODULOS.
    """

    # Lê, tokeniza e parseia. Torcemos pra não explodir.
    lexer = Lexer()
    lexer.build()
    tokens = lexer.tokenize(code)

    parser = Parser(tokens)
    ast = parser.parse()

    # Salva a AST em arquivo JSON, porque a gente é chique.
    program_name = ast["programa"]["nome"]
    file_name = f"{program_name}.json"
    with open(file_name, "w", encoding="utf-8") as json_file:
        json.dump(ast, json_file, indent=4, ensure_ascii=False)

    print(f"AST salva no arquivo: {file_name}")
