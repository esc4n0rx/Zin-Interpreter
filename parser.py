import json
from lexer import Lexer  # Importando o Lexer do arquivo lexer.py

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = None
        self.index = -1
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

    def advance(self):
        self.index += 1
        if self.index < len(self.tokens):
            self.current_token = self.tokens[self.index]
        else:
            self.current_token = None

    def expect(self, token_type, value=None):
        if self.current_token is None:
            raise SyntaxError("Token inesperado: fim do arquivo")
        if self.current_token[0] != token_type or (value and self.current_token[1] != value):
            raise SyntaxError(f"Token inesperado: {self.current_token}")
        self.advance()

    def parse(self):
        """
        Ponto de entrada do parser.
        """
        self.advance()
        self.parse_inicio()
        self.parse_implementacao()
        self.parse_execucao()
        return self.ast

    # ---------------------------------------------------------
    #  BLOCO: INICIO
    # ---------------------------------------------------------
    def parse_inicio(self):
        self.expect("KEYWORD", "INICIO")
        self.expect("KEYWORD", "PROGAMA")
        self.ast["programa"]["nome"] = self.current_token[1]
        self.expect("IDENTIFIER")
        self.expect("SYMBOL", ".")

        # Lê as variáveis (se houver) no início
        while self.current_token and self.current_token[1] == "variavel":
            self.parse_variavel()

    def parse_variavel(self):
        self.expect("KEYWORD", "variavel")
        nome = self.current_token[1]
        self.expect("IDENTIFIER")
        self.expect("KEYWORD", "tipo")
        tipo = self.current_token[1]
        self.expect("TYPE")
        self.ast["programa"]["variaveis"].append({"nome": nome, "tipo": tipo})

    # ---------------------------------------------------------
    #  BLOCO: IMPLEMENTACAO
    # ---------------------------------------------------------
    def parse_implementacao(self):
        self.expect("KEYWORD", "IMPLEMENTACAO")
        self.expect("KEYWORD", "PROGAMA")
        self.expect("IDENTIFIER", self.ast["programa"]["nome"])
        self.expect("SYMBOL", ".")

        # (1) Bloco PRINCIPAL
        self.expect("KEYWORD", "PRINCIPAL")
        self.expect("SYMBOL", ".")
        principal = []
        while self.current_token and self.current_token[1] != "FIM":
            principal.append(self.parse_statement())
        self.expect("KEYWORD", "FIM")
        self.expect("KEYWORD", "PRINCIPAL")
        self.expect("SYMBOL", ".")
        self.ast["programa"]["implementacao"]["principal"] = principal

        # (2) Execuções logo após o PRINCIPAL (antes de MODULO)
        # Aqui vamos capturar linhas do tipo `EXECUTAR MODULO X.`
        # ou qualquer outro statement que você queira permitir.
        execucoes_apos_principal = []
        while self.current_token and self.current_token[1] not in ("MODULO", "EXECUCAO"):
            # Enquanto não entrar em outro bloco (MODULO/EXECUCAO), 
            # a gente interpreta como "statement"
            execucoes_apos_principal.append(self.parse_statement())

        self.ast["programa"]["implementacao"]["execucoes_apos_principal"] = execucoes_apos_principal

        # (3) Processa blocos de MODULO
        while self.current_token and self.current_token[1] == "MODULO":
            self.parse_modulo()

    def parse_modulo(self):
        self.expect("KEYWORD", "MODULO")
        nome_modulo = self.current_token[1]
        self.expect("IDENTIFIER")
        self.expect("SYMBOL", ".")
        funcoes = []

        # Funções dentro do módulo
        while self.current_token and self.current_token[1] != "FIM":
            if self.current_token[1] == "funcao":
                funcoes.append(self.parse_funcao())
            else:
                raise SyntaxError(f"Comando inesperado no módulo: {self.current_token}")

        self.expect("KEYWORD", "FIM")
        self.expect("KEYWORD", "MODULO")
        self.expect("SYMBOL", ".")

        # Adiciona o módulo à AST
        self.ast["programa"]["implementacao"].setdefault("modulos", {})[nome_modulo] = funcoes

    def parse_funcao(self):
        self.expect("KEYWORD", "funcao")
        nome_funcao = self.current_token[1]
        self.expect("IDENTIFIER")
        self.expect("SYMBOL", "(")
        parametros = []
        while self.current_token and self.current_token[0] == "IDENTIFIER":
            parametros.append(self.current_token[1])
            self.expect("IDENTIFIER")
            if self.current_token[1] == ",":
                self.expect("SYMBOL", ",")
        self.expect("SYMBOL", ")")

        # Corpo da função
        corpo = []
        while self.current_token and self.current_token[1] != "retorne":
            corpo.append(self.parse_statement())

        # Retorno
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
        """
        Tenta reconhecer um 'statement' baseado no token atual.
        """
        # (A) Atribuição: <IDENTIFIER> = <expr>.
        if self.current_token[0] == "IDENTIFIER":
            nome = self.current_token[1]
            self.expect("IDENTIFIER")
            self.expect("ASSIGN")
            valor = self.parse_expression()
            self.expect("SYMBOL", ".")
            return {"atribuir": {"variavel": nome, "valor": valor}}

        # (B) escreva("...")
        elif self.current_token[1] == "escreva":
            self.expect("KEYWORD", "escreva")
            self.expect("SYMBOL", "(")
            texto = self.current_token[1]
            self.expect("STRING")
            self.expect("SYMBOL", ")")
            self.expect("SYMBOL", ".")
            return {"escreva": texto.strip('"')}

        # (C) pergunte("..."{var}).
        elif self.current_token[1] == "pergunte":
            self.expect("KEYWORD", "pergunte")
            self.expect("SYMBOL", "(")
            texto = self.current_token[1]
            self.expect("STRING")
            self.expect("SYMBOL", "{")
            variavel = self.current_token[1]
            self.expect("IDENTIFIER")
            self.expect("SYMBOL", "}")
            self.expect("SYMBOL", ")")
            self.expect("SYMBOL", ".")
            return {"pergunte": {"texto": texto.strip('"'), "variavel": variavel}}

        # (D) SE ... FIM SE.
        elif self.current_token[1] == "SE":
            return self.parse_se()

        # (E) ENQUANTO ... FIM ENQUANTO.
        elif self.current_token[1] == "ENQUANTO":
            return self.parse_enquanto()

        # (F) EXECUTAR (pode ser EXECUTAR MODULO X. ou EXECUTAR X.)
        elif self.current_token[1] == "EXECUTAR":
            self.expect("KEYWORD", "EXECUTAR")
            if self.current_token[1] == "MODULO":
                self.expect("KEYWORD", "MODULO")
                nome_modulo = self.current_token[1]
                self.expect("IDENTIFIER")
                self.expect("SYMBOL", ".")
                return {"executar_modulo": nome_modulo}
            else:
                # Exemplo: EXECUTAR <IDENTIFIER>.
                nome_qualquer = self.current_token[1]
                self.expect("IDENTIFIER")
                self.expect("SYMBOL", ".")
                return {"executar": nome_qualquer}

        raise SyntaxError(f"Comando desconhecido: {self.current_token}")

    def parse_se(self):
        self.expect("KEYWORD", "SE")
        condicao = self.parse_expression()
        self.expect("KEYWORD", "ENTAO")
        self.expect("SYMBOL", ".")
        bloco_se = []
        while self.current_token and self.current_token[1] not in ("SENAO", "FIM"):
            bloco_se.append(self.parse_statement())

        bloco_senao = None
        if self.current_token and self.current_token[1] == "SENAO":
            self.expect("KEYWORD", "SENAO")
            self.expect("SYMBOL", ".")
            bloco_senao = []
            while self.current_token and self.current_token[1] != "FIM":
                bloco_senao.append(self.parse_statement())

        self.expect("KEYWORD", "FIM")
        self.expect("KEYWORD", "SE")
        self.expect("SYMBOL", ".")
        return {
            "tipo": "SE",
            "condicao": condicao,
            "bloco_se": bloco_se,
            "bloco_senao": bloco_senao
        }

    def parse_enquanto(self):
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
    def parse_expression(self):
        """
        Exemplo simplificado de parse de expressão,
        aceita apenas "IDENTIFIER" ou "NUMBER" 
        [operador] "IDENTIFIER" ou "NUMBER".
        """
        left = self.current_token[1]
        if self.current_token[0] in ("NUMBER", "IDENTIFIER"):
            self.expect(self.current_token[0])
            if self.current_token and self.current_token[0] == "OPERATOR":
                operator = self.current_token[1]
                self.expect("OPERATOR")
                right = self.current_token[1]
                self.expect(self.current_token[0])
                return {"left": left, "operator": operator, "right": right}
            return left
        raise SyntaxError(f"Expressão inválida: {self.current_token}")

    # ---------------------------------------------------------
    #  BLOCO: EXECUCAO
    # ---------------------------------------------------------
    def parse_execucao(self):
        # EXECUCAO PROGAMA TESTE_MODULOS.
        self.expect("KEYWORD", "EXECUCAO")
        self.expect("KEYWORD", "PROGAMA")
        self.expect("IDENTIFIER", self.ast["programa"]["nome"])
        self.expect("SYMBOL", ".")

        while self.current_token and self.current_token[1] == "EXECUTAR":
            self.expect("KEYWORD", "EXECUTAR")

            if self.current_token[1] == "PRINCIPAL":
                self.expect("KEYWORD", "PRINCIPAL")
                self.expect("SYMBOL", ".")
                self.ast["programa"]["execucao"]["modulos"].append("PRINCIPAL")
            else:
                modulo = self.current_token[1]
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

    lexer = Lexer()
    tokens = lexer.tokenize(code)

    parser = Parser(tokens)
    ast = parser.parse()

    program_name = ast["programa"]["nome"] 
    file_name = f"{program_name}.json"
    with open(file_name, "w", encoding="utf-8") as json_file:
        json.dump(ast, json_file, indent=4, ensure_ascii=False)

    print(f"AST salva no arquivo: {file_name}")
