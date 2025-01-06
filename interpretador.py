import json
import os
from lexer import Lexer
from parser import Parser
import sys


class Interpretador:
    def __init__(self, arquivo_zin):
        self.arquivo_zin = arquivo_zin
        self.contexto = {}  # Armazena as variáveis e seus valores
        self.modulos = {}   # Armazena os módulos e suas funções
        self.pilha_contexto = []

    def processar_arquivo(self):
        # Verifica se o arquivo existe
        if not os.path.exists(self.arquivo_zin):
            raise FileNotFoundError(f"Arquivo {self.arquivo_zin} não encontrado.")

        # Verifica se o arquivo de saída JSON já existe
        nome_programa = os.path.splitext(os.path.basename(self.arquivo_zin))[0]
        arquivo_json = f"{nome_programa}.json"

        if not os.path.exists(arquivo_json):
            print("Gerando AST...")
            with open(self.arquivo_zin, "r", encoding="utf-8") as arquivo:
                codigo = arquivo.read()

            # Gera o JSON usando o Lexer e o Parser
            lexer = Lexer()
            tokens = lexer.tokenize(codigo)

            parser = Parser(tokens)
            ast = parser.parse()

            # Salva a AST no arquivo JSON
            with open(arquivo_json, "w", encoding="utf-8") as arquivo_json_out:
                json.dump(ast, arquivo_json_out, indent=4, ensure_ascii=False)
            print(f"AST salva no arquivo: {arquivo_json}")

        # Carrega o arquivo JSON para interpretar
        with open(arquivo_json, "r", encoding="utf-8") as arquivo_json_in:
            self.ast = json.load(arquivo_json_in)

    def executar(self):
        # Interpreta a AST carregada
        if "programa" not in self.ast:
            raise ValueError("AST inválida: estrutura do programa não encontrada.")

        programa = self.ast["programa"]
        print(f"Executando programa: {programa['nome']}")

        # Declara variáveis
        for variavel in programa["variaveis"]:
            self.contexto[variavel["nome"]] = None

        # Carrega módulos
        self.modulos = programa["implementacao"].get("modulos", {})

        # Executa os módulos especificados na execução
        if "execucao" in programa:
            for modulo in programa["execucao"]["modulos"]:
                if modulo.lower() == "principal":
                    self.executar_principal(programa["implementacao"]["principal"])
                elif modulo in self.modulos:
                    self.executar_modulo(modulo)

    def executar_principal(self, comandos):
        for comando in comandos:
            if "atribuir" in comando:
                self.interpretar_atribuicao(comando)
            elif "escreva" in comando:
                self.interpretar_escreva(comando)
            elif "pergunte" in comando:
                self.interpretar_pergunte(comando)
            elif comando.get("tipo") == "SE":
                self.interpretar_se(comando)
            elif comando.get("tipo") == "ENQUANTO":
                self.interpretar_enquanto(comando)
            elif "executar_modulo" in comando:
                self.executar_modulo(comando["executar_modulo"])

    def interpretar_atribuicao(self, comando):
        variavel = comando["atribuir"]["variavel"]
        valor = comando["atribuir"]["valor"]
        if isinstance(valor, dict) and "left" in valor:
            left = self.contexto.get(valor["left"], valor["left"])
            right = self.contexto.get(valor["right"], valor["right"])
            operator = valor["operator"]
            if operator == "+":
                self.contexto[variavel] = int(left) + int(right)
            elif operator == "-":
                self.contexto[variavel] = int(left) - int(right)
            elif operator == "*":
                self.contexto[variavel] = int(left) * int(right)
            elif operator == "/":
                self.contexto[variavel] = int(left) // int(right)
        else:
            self.contexto[variavel] = valor

    def interpretar_escreva(self, comando):
        texto = comando["escreva"]
        for variavel, valor in self.contexto.items():
            texto = texto.replace(f"{{{variavel}}}", str(valor) if valor is not None else "null")
        print(texto)

    def interpretar_pergunte(self, comando):
        texto = comando["pergunte"]["texto"]
        variavel = comando["pergunte"]["variavel"]
        resposta = input(f"{texto} ")
        if variavel in self.contexto:
            if isinstance(self.contexto[variavel], int):
                self.contexto[variavel] = int(resposta)
            else:
                self.contexto[variavel] = resposta

    def interpretar_se(self, comando):
        condicao = comando["condicao"]
        bloco_se = comando["bloco_se"]
        bloco_senao = comando.get("bloco_senao", [])

        resultado = self.avaliar_condicao(condicao)

        if resultado:
            self.executar_principal(bloco_se)
        elif bloco_senao:
            self.executar_principal(bloco_senao)

    def interpretar_enquanto(self, comando):
        condicao = comando["condicao"]
        bloco = comando["bloco"]

        while self.avaliar_condicao(condicao):
            self.executar_principal(bloco)

    def avaliar_condicao(self, condicao):
        left = self.contexto.get(condicao["left"], condicao["left"])
        right = self.contexto.get(condicao["right"], condicao["right"])

        if isinstance(left, str) and left.isdigit():
            left = int(left)
        if isinstance(right, str) and right.isdigit():
            right = int(right)

        operator = condicao["operator"]

        if operator == "==":
            return left == right
        elif operator == "!=":
            return left != right
        elif operator == ">":
            return left > right
        elif operator == "<":
            return left < right
        elif operator == ">=":
            return left >= right
        elif operator == "<=":
            return left <= right
        raise ValueError(f"Operador inválido: {operator}")

    def executar_modulo(self, nome_modulo):
        if nome_modulo not in self.modulos:
            raise ValueError(f"Módulo {nome_modulo} não encontrado.")

        funcoes = self.modulos[nome_modulo]
        for funcao in funcoes:
            self.executar_funcao(funcao)

    def executar_funcao(self, funcao):
        nome_funcao = funcao["nome"]
        parametros = funcao["parametros"]
        corpo = funcao["corpo"]
        retorno = funcao["retorno"]

        contexto_local = dict(self.contexto)

        self.pilha_contexto.append(self.contexto)

        self.contexto = contexto_local

        for param in parametros:
            if param not in self.contexto:
                self.contexto[param] = None

        print(f"Executando função: {nome_funcao} com contexto: {self.contexto}")

        self.executar_principal(corpo)

        resultado = self.avaliar_expressao(retorno)

        self.contexto = self.pilha_contexto.pop()

        return resultado


    def avaliar_expressao(self, expressao):
        if isinstance(expressao, dict):
            left = self.contexto.get(expressao["left"], expressao["left"])
            right = self.contexto.get(expressao["right"], expressao["right"])
            operator = expressao["operator"]
            if operator == "+":
                return int(left) + int(right)
            elif operator == "-":
                return int(left) - int(right)
            elif operator == "*":
                return int(left) * int(right)
            elif operator == "/":
                return int(left) // int(right)
        elif isinstance(expressao, str):
            return self.contexto.get(expressao, expressao)
        elif isinstance(expressao, int):
            return expressao
        raise ValueError(f"Expressão inválida: {expressao}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python interpretador.py <arquivo_zin>")
        sys.exit(1)

    arquivo_zin = sys.argv[1]
    interpretador = Interpretador(arquivo_zin)
    interpretador.processar_arquivo()
    interpretador.executar()
