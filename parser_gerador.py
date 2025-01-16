import json
from lexer_gerador import Lexer 

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
        if self.current_token.type != token_type or (value and self.current_token.value != value):
            raise SyntaxError(f"Token inesperado: {self.current_token}")
        self.advance()

    def parse(self):
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
        self.ast["programa"]["nome"] = self.current_token.value
        self.expect("IDENTIFIER")
        self.expect("SYMBOL", ".")


        while self.current_token and self.current_token.value == "importe":
            self.ast["programa"].setdefault("importes", []).append(self.parse_importe())

        while self.current_token and self.current_token.value == "variavel":
            self.parse_variavel()

    def parse_variavel(self):
        self.expect("KEYWORD", "variavel")
        nome = self.current_token.value
        self.expect("IDENTIFIER")
        self.expect("KEYWORD", "tipo")
        tipo = self.current_token.value
        self.expect("TYPE")

        if tipo == "lista":
            if self.current_token and self.current_token.value == "=":
                self.expect("ASSIGN")
                valores = self.parse_lista()
            else:
                valores = []
            self.ast["programa"]["variaveis"].append(
                {"nome": nome, "tipo": tipo, "valores": valores}
            )

        elif tipo == "grupo":
            if self.current_token and self.current_token.value == "=":
                self.expect("ASSIGN")
                valores = self.parse_grupo()
            else:
                valores = {"campos": [], "dados": []}
            self.ast["programa"]["variaveis"].append(
                {"nome": nome, "tipo": tipo, "valores": valores}
            )
        else:

            self.ast["programa"]["variaveis"].append({"nome": nome, "tipo": tipo})

    # ---------------------------------------------------------
    #  BLOCO: IMPLEMENTACAO
    # ---------------------------------------------------------
    def parse_implementacao(self):
        self.expect("KEYWORD", "IMPLEMENTACAO")
        self.expect("KEYWORD", "PROGAMA")
        self.expect("IDENTIFIER", self.ast["programa"]["nome"])
        self.expect("SYMBOL", ".")


        self.expect("KEYWORD", "PRINCIPAL")
        self.expect("SYMBOL", ".")
        principal = []
        while self.current_token and self.current_token.value != "FIM":
            principal.append(self.parse_statement())
        self.expect("KEYWORD", "FIM")
        self.expect("KEYWORD", "PRINCIPAL")
        self.expect("SYMBOL", ".")
        self.ast["programa"]["implementacao"]["principal"] = principal

        execucoes_apos_principal = []
        while self.current_token and self.current_token.value not in ("MODULO", "EXECUCAO"):
            execucoes_apos_principal.append(self.parse_statement())
        self.ast["programa"]["implementacao"]["execucoes_apos_principal"] = execucoes_apos_principal

        while self.current_token and self.current_token.value == "MODULO":
            self.parse_modulo()

    def parse_modulo(self):
        self.expect("KEYWORD", "MODULO")
        nome_modulo = self.current_token.value
        self.expect("IDENTIFIER")
        self.expect("SYMBOL", ".")
        funcoes = []

        while self.current_token and self.current_token.value != "FIM":
            if self.current_token.value == "funcao":
                funcoes.append(self.parse_funcao())
            else:
                raise SyntaxError(f"Comando inesperado no módulo: {self.current_token}")

        self.expect("KEYWORD", "FIM")
        self.expect("KEYWORD", "MODULO")
        self.expect("SYMBOL", ".")
        self.ast["programa"]["implementacao"].setdefault("modulos", {})[nome_modulo] = funcoes

    def parse_funcao(self):
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

        corpo = []
        while self.current_token and self.current_token.value != "retorne":
            corpo.append(self.parse_statement())

        self.expect("KEYWORD", "retorne")
        retorno = self.parse_expression()
        self.expect("SYMBOL", ".")

        return {
            "nome": nome_funcao,
            "parametros": parametros,
            "corpo": corpo,
            "retorno": retorno
        }

    def parse_lista(self):
        self.expect("SYMBOL", "[")
        valores = []
        while self.current_token and self.current_token.value != "]":
            if self.current_token.type in ("NUMBER", "STRING"):
                valores.append(self.current_token.value)
                self.expect(self.current_token.type)
                if self.current_token and self.current_token.value == ",":
                    self.expect("SYMBOL", ",")
            else:
                raise SyntaxError(f"Valor inválido na lista: {self.current_token}")
        self.expect("SYMBOL", "]")
        return valores

    def parse_grupo(self):
        self.expect("KEYWORD", "GRUPO")
        self.expect("SYMBOL", "(")

        self.expect("SYMBOL", "[")
        campos = []
        while self.current_token and self.current_token.value != "]":
            if self.current_token.type == "STRING":
                campos.append(self.current_token.value.strip('"'))
                self.expect("STRING")
                if self.current_token and self.current_token.value == ",":
                    self.expect("SYMBOL", ",")
            else:
                raise SyntaxError(f"Campo inválido no cabeçalho do grupo: {self.current_token}")
        self.expect("SYMBOL", "]")


        dados = []
        if self.current_token and self.current_token.value == ",":
            self.expect("SYMBOL", ",")
            while self.current_token and self.current_token.value != ")":
                self.expect("SYMBOL", "[")
                registro = []
                while self.current_token and self.current_token.value != "]":
                    if self.current_token.type in ("STRING", "NUMBER"):
                        val = (self.current_token.value.strip('"')
                               if self.current_token.type == "STRING"
                               else self.current_token.value)
                        registro.append(val)
                        self.expect(self.current_token.type)
                        if self.current_token and self.current_token.value == ",":
                            self.expect("SYMBOL", ",")
                    else:
                        raise SyntaxError(f"Valor inválido no registro do grupo: {self.current_token}")
                self.expect("SYMBOL", "]")

                dados.append(registro)

                if self.current_token and self.current_token.value == ",":
                    self.expect("SYMBOL", ",")

        self.expect("SYMBOL", ")")
        return {"campos": campos, "dados": dados}

    # ---------------------------------------------------------
    #  PARSE DE STATEMENTS
    # ---------------------------------------------------------
    def parse_statement(self):
        """
        Lê um statement de alto nível. Pode ser:
        - Atribuição: nome_variavel = alguma_expressao.
        - escreva("...")
        - pergunte("...", {var})
        - SE ... FIM SE.
        - ENQUANTO ... FIM ENQUANTO.
        - EXECUTAR ...
        - importe ...
        - etc.
        """

        if self.current_token and self.current_token.type == "IDENTIFIER":
            nome_ident = self.current_token.value
            self.expect("IDENTIFIER")

            if self.current_token and self.current_token.type == "ASSIGN":
                self.expect("ASSIGN")
                valor = self.parse_expression()
                self.expect("SYMBOL", ".")
                return {"atribuir": {"variavel": nome_ident, "valor": valor}}

            else:
                raise SyntaxError(
                    f"Era esperado '=' após '{nome_ident}', mas veio: {self.current_token}"
                )

        elif self.current_token and self.current_token.value == "escreva":
            self.expect("KEYWORD", "escreva")
            self.expect("SYMBOL", "(")
            texto = self.current_token.value
            self.expect("STRING")
            self.expect("SYMBOL", ")")
            self.expect("SYMBOL", ".")
            return {"escreva": texto.strip('"')}

        elif self.current_token and self.current_token.value == "importe":
            return self.parse_importe()

        elif self.current_token and self.current_token.value == "pergunte":
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

        elif self.current_token and self.current_token.value == "SE":
            return self.parse_se()

        elif self.current_token and self.current_token.value == "ENQUANTO":
            return self.parse_enquanto()
        

        elif self.current_token and self.current_token.value == "PARA":
            return self.parse_para()
        
        elif self.current_token and self.current_token.value == "REPITA":
            return self.parse_repita()

        elif self.current_token and self.current_token.value == "EXECUTAR":
            self.expect("KEYWORD", "EXECUTAR")
            if self.current_token.value == "MODULO":
                self.expect("KEYWORD", "MODULO")
                nome_modulo = self.current_token.value
                self.expect("IDENTIFIER")
                self.expect("SYMBOL", ".")
                return {"executar_modulo": nome_modulo}
            else:
                nome_qualquer = self.current_token.value
                self.expect("IDENTIFIER")
                self.expect("SYMBOL", ".")
                return {"executar": nome_qualquer}

        raise SyntaxError(f"Comando desconhecido ou inválido: {self.current_token}")

    # ---------------------------------------------------------
    #  EXPRESSÕES
    # ---------------------------------------------------------
    #
    #  agora  vamos permitir "zin_math.raiz_quadrada(49)"
    # dentro de expressões como:
    #   resultado = 10 / zin_math.raiz_quadrada(49).
    #
    #
    # parse_expression() -> parse_binop() (que lida com left op right)
    # parse_binop() -> parse_primary() e, se o token for OPERATOR, consome e continua
    # parse_primary() -> NUMBER, IDENTIFIER (pode virar modulo.funcao(...)), ...
    #
    def parse_expression(self):
        left_node = self.parse_binop()
        return left_node
    

    def parse_para(self):
        """
        Exemplo de sintaxe:
        PARA i = 0 ATE 10 PASSO 2 FACA.
            ... bloco ...
        FIM PARA.
        """

        self.expect("KEYWORD", "PARA")

        var_name = None
        if self.current_token.type == "IDENTIFIER":
            var_name = self.current_token.value
            self.advance()
        else:
            raise SyntaxError(f"Era esperado um identificador após 'PARA', mas veio: {self.current_token}")


        self.expect("ASSIGN")  # '='


        start_expr = self.parse_expression()


        self.expect("KEYWORD", "ATE")


        end_expr = self.parse_expression()


        step_expr = None
        if self.current_token and self.current_token.value == "PASSO":
            self.expect("KEYWORD", "PASSO")
            step_expr = self.parse_expression()


        self.expect("KEYWORD", "FACA")
        self.expect("SYMBOL", ".")


        bloco_para = []
        while self.current_token and not (
            self.current_token.value == "FIM" and self._peek_next_value() == "PARA"
        ):
            bloco_para.append(self.parse_statement())


        self.expect("KEYWORD", "FIM")
        self.expect("KEYWORD", "PARA")
        self.expect("SYMBOL", ".")

        return {
            "tipo": "PARA",
            "var": var_name,
            "start": start_expr,
            "end": end_expr,
            "step": step_expr,
            "bloco": bloco_para
        }

    def _peek_next_value(self):
        """
        Método auxiliar que tenta ver o 'próximo' token sem consumir o atual,
        para ajudar no parse do 'FIM PARA' (e não confundir 'FIM PROGAMA', etc.).
        """
        next_index = self.index + 1
        if next_index < len(self.tokens):
            return self.tokens[next_index].value
        return None


    def parse_binop(self):
        """
        Lê um "fator" (parse_primary),
        se o próximo token for OPERATOR, consome e lê outro fator.
        Repete até não ter mais operadores. 
        OBS: Isso não implementa precedência real, mas já aceita expressões
        sequenciais como "10 + x * y - func(3)".
        """
        node = self.parse_primary()  


        while self.current_token and self.current_token.type == "OPERATOR":
            op = self.current_token.value
            self.expect("OPERATOR")
            right = self.parse_primary()

            node = {
                "left": node,
                "operator": op,
                "right": right
            }

        return node
    

    def parse_repita(self):
        """
        Exemplo de sintaxe:
        REPITA.
            ... bloco ...
        ATE (condicao).
        
        ou se você quiser algo como
        REPITA.
            ...
        FIM REPITA ATE (condição).
        
        Ajuste conforme a sintaxe que desejar.
        """
        self.expect("KEYWORD", "REPITA")
        self.expect("SYMBOL", ".")

        bloco_repita = []
        
        while self.current_token and self.current_token.value != "ATE":
            bloco_repita.append(self.parse_statement())

        
        self.expect("KEYWORD", "ATE")


        if self.current_token and self.current_token.value == "(":
            self.expect("SYMBOL", "(")
            cond_expr = self.parse_expression()
            self.expect("SYMBOL", ")")
        else:
           
            cond_expr = self.parse_expression()


        return {
            "tipo": "REPITA",
            "bloco": bloco_repita,
            "condicao": cond_expr
        }


    def parse_primary(self):
        """
        Lê um fator primário: 
        - NUMBER
        - IDENTIFIER (pode ser "modulo.funcao(...)" ou var normal)
        - Parênteses para sub-expressão (caso queira suportar (1+2)*3)
        - Acesso a lista [índice]
        """
        if not self.current_token:
            raise SyntaxError("Fim inesperado na expressão.")

        token = self.current_token

        if token.type == "NUMBER":
            value = token.value
            self.expect("NUMBER")
            return value


        if token.type == "IDENTIFIER":
            ident1 = token.value
            self.expect("IDENTIFIER")


            if self.current_token and self.current_token.type == "SYMBOL" and self.current_token.value == ".":
                self.expect("SYMBOL", ".")
                ident2 = self.current_token.value
                self.expect("IDENTIFIER")


                if self.current_token and self.current_token.type == "SYMBOL" and self.current_token.value == "(":
                    args = self.parse_function_args()
                    return {
                        "chamada_modulo": {
                            "modulo": ident1,
                            "funcao": ident2,
                            "argumentos": args
                        }
                    }
                else:

                    return {
                        "acesso_modulo": {
                            "modulo": ident1,
                            "nome": ident2
                        }
                    }

            elif self.current_token and self.current_token.type == "SYMBOL" and self.current_token.value == "(":
                args = self.parse_function_args(func_name=ident1)
                return {
                    "func_call": {
                        "nome": ident1,
                        "args": args
                    }
                }

            elif self.current_token and self.current_token.type == "SYMBOL" and self.current_token.value == "[":
                self.expect("SYMBOL", "[")
                index_expr = self.parse_expression()
                self.expect("SYMBOL", "]")
                return {
                    "acesso_lista": {
                        "nome": ident1,
                        "indice": index_expr
                    }
                }
            else:

                return ident1
 
        if token.type == "SYMBOL" and token.value == "(":
            self.expect("SYMBOL", "(")
            expr = self.parse_expression()
            self.expect("SYMBOL", ")")
            return expr

        raise SyntaxError(f"Expressão inválida em parse_primary: {token}")

    def parse_function_args(self, func_name=None):
        """
        Consumimos '(' e lemos argumentos até ')'.
        """


        args = []
        self.expect("SYMBOL", "(")
        while self.current_token and self.current_token.value != ")":
            args.append(self.parse_expression())
            if self.current_token and self.current_token.value == ",":
                self.expect("SYMBOL", ",")
        self.expect("SYMBOL", ")")
        return args

    # ---------------------------------------------------------
    #  PARSE SE, ENQUANTO, etc.
    # ---------------------------------------------------------
    def parse_se(self):
        self.expect("KEYWORD", "SE")
        condicao = self.parse_expression()
        self.expect("KEYWORD", "ENTAO")
        self.expect("SYMBOL", ".")
        bloco_se = []
        while self.current_token and self.current_token.value not in ("SENAO", "FIM"):
            bloco_se.append(self.parse_statement())

        bloco_senao = None
        if self.current_token and self.current_token.value == "SENAO":
            self.expect("KEYWORD", "SENAO")
            self.expect("SYMBOL", ".")
            bloco_senao = []
            while self.current_token and self.current_token.value != "FIM":
                bloco_senao.append(self.parse_statement())

        self.expect("KEYWORD", "FIM")
        self.expect("KEYWORD", "SE")
        self.expect("SYMBOL", ".")

        return {
            "tipo": "SE",
            "condicao": condicao,
            "bloco_se": bloco_se,
            "bloco_senao": bloco_senao,
        }

    def parse_enquanto(self):
        self.expect("KEYWORD", "ENQUANTO")
        condicao = self.parse_expression()
        self.expect("KEYWORD", "FACA")
        self.expect("SYMBOL", ".")
        bloco_enquanto = []
        while self.current_token and self.current_token.value != "FIM":
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
    #  BLOCO: EXECUCAO
    # ---------------------------------------------------------
    def parse_execucao(self):
        self.expect("KEYWORD", "EXECUCAO")
        self.expect("KEYWORD", "PROGAMA")
        self.expect("IDENTIFIER", self.ast["programa"]["nome"])
        self.expect("SYMBOL", ".")
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

    # ---------------------------------------------------------
    #  IMPORTAÇÃO
    # ---------------------------------------------------------
    def parse_importe(self):
        self.expect("KEYWORD", "importe")
        nome_modulo = self.current_token.value
        self.expect("IDENTIFIER")
        self.expect("SYMBOL", ".")
        return {"importe": nome_modulo}


# ----------------------------------------------------------
#  Exemplo de uso do Lexer e Parser
# ----------------------------------------------------------
if __name__ == "__main__":
    code = """
    INICIO PROGAMA TESTE_MODULOS.
    variavel nome tipo texto
    variavel idade tipo inteiro
    variavel lista_numeros tipo lista = [10, 20, 30, 40, 50]
    variavel grupo_pessoas tipo grupo = GRUPO(
        ["NOME", "FUNCAO", "IDADE"],
        ["joao", "administrador", 15],
        ["vitor", "supervisor", 16],
        ["sandro", "operador", 19]
    )

    IMPLEMENTACAO PROGAMA TESTE_MODULOS.
    PRINCIPAL.

    pergunte("Qual o seu nome?" {nome}).
    pergunte("Qual a sua idade?" {idade}).

    escreva("Primeiro número da lista: {lista_numeros[0]}").
    escreva("Nome da segunda pessoa no grupo: {grupo_pessoas[1].NOME}").

    resultado_raiz = zin_math.raiz_quadrada(49).
    resultado = 10 / zin_math.raiz_quadrada(49).
    teste = valor1 + zin_math.raiz_quadrada(49).

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
    lexer.build()
    tokens = lexer.tokenize(code)

    parser = Parser(tokens)
    ast = parser.parse()

    print("AST gerada:")
    print(json.dumps(ast, indent=4, ensure_ascii=False))
