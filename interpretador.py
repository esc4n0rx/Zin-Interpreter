import json
import os
import sys
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lexer_gerador import Lexer
from parser_gerador import Parser

class Interpretador:
    def __init__(self, arquivo_zin):
        self.arquivo_zin = arquivo_zin
        self.contexto = {}
        self.modulos = {}
        self.pilha_contexto = []

    def processar_arquivo(self):
        """Gera (se necessário) a AST em JSON e carrega para self.ast."""
        if not os.path.exists(self.arquivo_zin):
            raise FileNotFoundError(f"Arquivo {self.arquivo_zin} não encontrado.")

        nome_programa = os.path.splitext(os.path.basename(self.arquivo_zin))[0]
        arquivo_json = f"{nome_programa}.json"

        if not os.path.exists(arquivo_json):
            print("Gerando AST...")
            with open(self.arquivo_zin, "r", encoding="utf-8") as arquivo:
                codigo = arquivo.read()

            lexer = Lexer()
            lexer.build()
            tokens = lexer.tokenize(codigo)

            parser = Parser(tokens)
            ast = parser.parse()

            with open(arquivo_json, "w", encoding="utf-8") as arquivo_json_out:
                json.dump(ast, arquivo_json_out, indent=4, ensure_ascii=False)
            print(f"AST salva no arquivo: {arquivo_json}")

        with open(arquivo_json, "r", encoding="utf-8") as arquivo_json_in:
            self.ast = json.load(arquivo_json_in)

    def executar(self):
        """Ponto de entrada da execução do programa."""
        if "programa" not in self.ast:
            raise ValueError("AST inválida: não tem chave 'programa'.")

        programa = self.ast["programa"]
        print(f"Executando programa: {programa['nome']}")


        for var_info in programa["variaveis"]:
            var_nome = var_info["nome"]
            var_tipo = var_info["tipo"]

            if var_tipo == "lista":
                lista_python = []
                for item in var_info.get("valores", []):
                    if isinstance(item, str) and item.isdigit():
                        lista_python.append(int(item))
                    else:
                        lista_python.append(item)
                self.contexto[var_nome] = lista_python


            elif var_tipo == "grupo":
                self.contexto[var_nome] = var_info.get("valores", {})

            else:
                self.contexto[var_nome] = None

        implementacao = programa.get("implementacao", {})
        self.modulos = implementacao.get("modulos", {})

        if "importes" in programa:
            for imp_item in programa["importes"]:
            
                self.interpretar_importe(imp_item)


        if "execucao" in programa:
            for modulo in programa["execucao"]["modulos"]:
                if modulo.lower() == "principal":
                  
                    principal = implementacao["principal"]
                    self.executar_principal(principal)
                elif modulo in self.modulos:
                   
                    self.executar_modulo(modulo)
                

    def executar_principal(self, comandos):
        """Executa os comandos de um bloco (por exemplo, principal)."""
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
            elif comando.get("tipo") == "PARA":
                self.interpretar_para(comando)
            elif comando.get("tipo") == "REPITA":
                self.interpretar_repita(comando)
            elif "executar_modulo" in comando:
                self.executar_modulo(comando["executar_modulo"])
            elif "acesso_lista" in comando:
                valor = self.avaliar_expressao(comando)
                print(valor)
            elif "acesso_grupo" in comando:
                valor = self.avaliar_expressao(comando)
                print(valor)
            elif "importe" in comando:
                self.interpretar_importe(comando)

    # -------------------------------------------------
    # PARA e REPITA
    # -------------------------------------------------
    def interpretar_para(self, comando):
        var_name = comando["var"]
        start_ast = comando["start"]
        end_ast = comando["end"]
        step_ast = comando["step"]
        bloco = comando["bloco"]

        start_val = self.avaliar_expressao(start_ast)
        end_val = self.avaliar_expressao(end_ast)
        step_val = self.avaliar_expressao(step_ast) if step_ast else 1

        self.contexto[var_name] = start_val

        if step_val > 0:
            while self.contexto[var_name] <= end_val:
                self.executar_principal(bloco)
                self.contexto[var_name] += step_val
        else:
            while self.contexto[var_name] >= end_val:
                self.executar_principal(bloco)
                self.contexto[var_name] += step_val

    def interpretar_repita(self, comando):
        bloco = comando["bloco"]
        condicao_ast = comando["condicao"]

        while True:
            self.executar_principal(bloco)
            valor_condicao = self.avaliar_condicao(condicao_ast)
            if valor_condicao:
                break

    # -------------------------------------------------
    # Atribuição
    # -------------------------------------------------
    def interpretar_atribuicao(self, comando):
        var_nome = comando["atribuir"]["variavel"]
        expr_ast = comando["atribuir"]["valor"]
        valor_calculado = self.avaliar_expressao(expr_ast)
        self.contexto[var_nome] = valor_calculado

    # -------------------------------------------------
    # Escreva 
    # -------------------------------------------------
    def interpretar_escreva(self, comando):
        texto = comando["escreva"]

        for variavel, valor in self.contexto.items():
            if valor is None:
                valor = "null"
            texto = texto.replace(f"{{{variavel}}}", str(valor))


        padrao = r"\{([^{}]+)\}"
        matches = re.findall(padrao, texto)

        for m in matches:
            if "." in m or "[" in m:
                valor_dinamico = self.avaliar_placeholder_dinamico(m)
                placeholder_str = f"{{{m}}}"
                texto = texto.replace(placeholder_str, str(valor_dinamico))
            else:

                placeholder_str = f"{{{m}}}"
                texto = texto.replace(placeholder_str, str(self.contexto.get(m, "null")))

        print(texto)

    # -------------------------------------------------
    # Ajuste para tratar índice como variável ou número
    # -------------------------------------------------
    def avaliar_placeholder_dinamico(self, expressao_str):
        """
        Exemplo de expressao_str:
          - "numeros[contador]"
          - "numeros[0]"
          - "produtos[1].NOME"
        """
        if "." in expressao_str:

            parte_lista, campo = expressao_str.split(".", 1)
            nome_lista, indice_str = self.extrair_lista(parte_lista)

            indice_ast = self._build_ast_for_index(indice_str)

            ast_grupo = {
                "acesso_grupo": {
                    "nome": nome_lista,
                    "indice": indice_ast,    
                    "campo": campo
                }
            }
            return self.avaliar_expressao(ast_grupo)
        else:
            nome_lista, indice_str = self.extrair_lista(expressao_str)
            indice_ast = self._build_ast_for_index(indice_str)

            ast_lista = {
                "acesso_lista": {
                    "nome": nome_lista,
                    "indice": indice_ast
                }
            }
            return self.avaliar_expressao(ast_lista)

    def _build_ast_for_index(self, indice_str):
        """Se 'indice_str' for dígito, converte para int. Senão, deixa como string (variável)."""
        if indice_str.isdigit():
            return int(indice_str)
        else:
            return indice_str

    def extrair_lista(self, texto):
        """
        Exemplo:
          "numeros[contador]" -> ("numeros", "contador")
          "produtos[1]" -> ("produtos", "1")
        """
        if "[" not in texto or "]" not in texto:
            return (texto, "0")

        nome, resto = texto.split("[", 1)
        indice_str = resto.split("]", 1)[0]
        return (nome, indice_str)

    # -------------------------------------------------
    # Pergunte
    # -------------------------------------------------
    def interpretar_pergunte(self, comando):
        texto = comando["pergunte"]["texto"]
        variavel = comando["pergunte"]["variavel"]
        resposta = input(f"{texto} ")

        if variavel in self.contexto:
            if isinstance(self.contexto[variavel], int):
                try:
                    self.contexto[variavel] = int(resposta)
                except ValueError:
                    self.contexto[variavel] = resposta
            else:
                self.contexto[variavel] = resposta

    # -------------------------------------------------
    # SE
    # -------------------------------------------------
    def interpretar_se(self, comando):
        condicao = comando["condicao"]
        bloco_se = comando["bloco_se"]
        bloco_senao = comando.get("bloco_senao", [])

        resultado = self.avaliar_condicao(condicao)
        if resultado:
            self.executar_principal(bloco_se)
        else:
            self.executar_principal(bloco_senao)

    def avaliar_condicao(self, condicao_ast):
        val = self.avaliar_expressao(condicao_ast)
        return bool(val)

    # -------------------------------------------------
    # ENQUANTO
    # -------------------------------------------------
    def interpretar_enquanto(self, comando):
        condicao = comando["condicao"]
        bloco = comando["bloco"]
        while True:
            teste = self.avaliar_condicao(condicao)
            if not teste:
                break
            self.executar_principal(bloco)

    # -------------------------------------------------
    # IMPORTAR MÓDULOS
    # -------------------------------------------------
    def interpretar_importe(self, comando):
        nome_modulo = comando["importe"]
        try:
            modulo = __import__(f"libs.{nome_modulo}", fromlist=["*"])
            self.contexto[nome_modulo] = modulo
            print(f"Módulo '{nome_modulo}' importado com sucesso.")
        except ImportError:
            raise ImportError(f"Erro ao importar o módulo '{nome_modulo}'. Verifique se existe em 'libs'.")

    # -------------------------------------------------
    # Execução de módulos
    # -------------------------------------------------
    def executar_modulo(self, nome_modulo):
        if nome_modulo not in self.modulos:
            raise ValueError(f"Módulo '{nome_modulo}' não encontrado na AST.")
        funcoes = self.modulos[nome_modulo]
        for func in funcoes:
            self.executar_funcao(func)

    def executar_funcao(self, funcao):
        nome_funcao = funcao["nome"]
        parametros = funcao["parametros"]
        corpo = funcao["corpo"]
        retorno_ast = funcao["retorno"]

        contexto_local = dict(self.contexto)
        self.pilha_contexto.append(self.contexto)
        self.contexto = contexto_local


        for p in parametros:
            if p not in self.contexto:
                self.contexto[p] = None

        print(f"Executando função: {nome_funcao}")
        self.executar_principal(corpo)

        resultado = self.avaliar_expressao(retorno_ast)

        self.contexto = self.pilha_contexto.pop()
        return resultado

    # -------------------------------------------------
    # Avaliação de Expressões (coração do interpretador)
    # -------------------------------------------------
    def avaliar_expressao(self, expr):
        """Avalia recursivamente um nó da AST de 'expr' e retorna valor real (int, float, str etc.)."""

        if isinstance(expr, (int, float)):
            return expr


        if isinstance(expr, str):

            return self.contexto.get(expr, expr)


        if isinstance(expr, dict):

            if "chamada_modulo" in expr:
                return self.executar_chamada_modulo(expr["chamada_modulo"])


            if "acesso_lista" in expr:
                return self.avaliar_acesso_lista(expr["acesso_lista"])


            if "acesso_grupo" in expr:
                return self.avaliar_acesso_grupo(expr["acesso_grupo"])

            if "left" in expr and "operator" in expr and "right" in expr:
                left_val = self.avaliar_expressao(expr["left"])
                right_val = self.avaliar_expressao(expr["right"])
                op = expr["operator"]

                if isinstance(left_val, str) and left_val.isdigit():
                    left_val = int(left_val)
                if isinstance(right_val, str) and right_val.isdigit():
                    right_val = int(right_val)

                if op == "+":  return left_val + right_val
                if op == "-":  return left_val - right_val
                if op == "*":  return left_val * right_val
                if op == "/":  return left_val // right_val
                if op == "==": return left_val == right_val
                if op == "!=": return left_val != right_val
                if op == ">":  return left_val > right_val
                if op == "<":  return left_val < right_val
                if op == ">=": return left_val >= right_val
                if op == "<=": return left_val <= right_val

                raise ValueError(f"Operador não suportado: {op}")

        raise ValueError(f"Expressão inválida: {expr}")

    def executar_chamada_modulo(self, info):
        nome_modulo = info["modulo"]
        nome_funcao = info["funcao"]
        args_ast = info["argumentos"]

        args_val = [self.avaliar_expressao(a) for a in args_ast]

        if nome_modulo not in self.contexto:
            raise ValueError(f"Módulo '{nome_modulo}' não foi importado ou não está no contexto.")

        modulo_obj = self.contexto[nome_modulo]
        if not hasattr(modulo_obj, nome_funcao):
            raise ValueError(f"Função '{nome_funcao}' não encontrada no módulo '{nome_modulo}'.")

        func = getattr(modulo_obj, nome_funcao)
        resultado = func(*args_val)
        return resultado

    def avaliar_acesso_lista(self, acesso):
        """
        acesso = {
          "nome": "numeros",
          "indice": <pode ser int ou string (var) ou dict (expressão)>
        }
        """
        nome_lista = acesso["nome"]
        indice_ast = acesso["indice"]

        if isinstance(indice_ast, dict):
            indice_val = self.avaliar_expressao(indice_ast)

        elif isinstance(indice_ast, str) and indice_ast.isdigit():
            indice_val = int(indice_ast)
       
        elif isinstance(indice_ast, str):
            indice_val = self.avaliar_expressao(indice_ast)
        else:

            indice_val = indice_ast

        if not isinstance(indice_val, int):
            raise ValueError(f"Índice '{indice_val}' não é inteiro para a lista '{nome_lista}'.")

        if nome_lista not in self.contexto or not isinstance(self.contexto[nome_lista], list):
            raise ValueError(f"'{nome_lista}' não é uma lista válida.")

        lista = self.contexto[nome_lista]
        if indice_val < 0 or indice_val >= len(lista):
            raise IndexError(f"Índice '{indice_val}' fora do intervalo para a lista '{nome_lista}'.")

        return lista[indice_val]

    def avaliar_acesso_grupo(self, acesso):
        """
        acesso = {
          "nome": "produtos",
          "indice": <int ou var/expr>,
          "campo": "NOME"
        }
        """
        nome_grupo = acesso["nome"]
        indice_ast = acesso["indice"]
        campo = acesso["campo"]

        if isinstance(indice_ast, dict):
            indice_val = self.avaliar_expressao(indice_ast)
        elif isinstance(indice_ast, str) and indice_ast.isdigit():
            indice_val = int(indice_ast)
        elif isinstance(indice_ast, str):
            indice_val = self.avaliar_expressao(indice_ast)
        else:
            indice_val = indice_ast

        if not isinstance(indice_val, int):
            raise ValueError(f"Índice '{indice_val}' não é inteiro para o grupo '{nome_grupo}'.")

        if nome_grupo not in self.contexto or not isinstance(self.contexto[nome_grupo], dict):
            raise ValueError(f"'{nome_grupo}' não é um grupo válido.")

        grupo = self.contexto[nome_grupo]
        campos = grupo.get("campos", [])
        dados = grupo.get("dados", [])

        if indice_val < 0 or indice_val >= len(dados):
            raise IndexError(f"Índice '{indice_val}' fora do intervalo para o grupo '{nome_grupo}'.")

        if campo not in campos:
            raise ValueError(f"Campo '{campo}' não encontrado no grupo '{nome_grupo}'.")

        campo_index = campos.index(campo)
        return dados[indice_val][campo_index]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python interpretador.py <arquivo_zin>")
        sys.exit(1)

    arquivo_zin = sys.argv[1]
    interpretador = Interpretador(arquivo_zin)
    interpretador.processar_arquivo()
    interpretador.executar()
