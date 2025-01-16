import sys
import json
from lexer_gerador import Lexer
from parser_gerador import Parser


class Linter:
    def __init__(self, file_path):
        self.file_path = file_path
        self.tokens = []
        self.ast = None
        self.errors = []

    def lint(self):
        """
        Executa todas as etapas de validação no código Zin.
        """
        try:
            code = self._read_file()
        except FileNotFoundError:
            self.errors.append(f"Erro: Arquivo '{self.file_path}' não encontrado.")
            return
        except Exception as e:
            self.errors.append(f"Erro ao abrir o arquivo: {e}")
            return

        self._lexical_analysis(code)


        if not self.errors:
            self._syntactic_analysis()


        if not self.errors:
            self._semantic_analysis()

    def _read_file(self):
        """
        Lê o arquivo e retorna o conteúdo.
        """
        with open(self.file_path, "r", encoding="utf-8") as file:
            return file.read()

    def _lexical_analysis(self, code):
        """
        Realiza a análise léxica usando o Lexer.
        """
        lexer = Lexer()
        lexer.build()
        try:
            self.tokens = lexer.tokenize(code)
            print("Análise léxica: OK")
        except SyntaxError as e:
            self.errors.append(f"Erro Léxico: {e}")

    def _syntactic_analysis(self):
        """
        Realiza a análise sintática usando o Parser.
        """
        parser = Parser(self.tokens)
        try:
            self.ast = parser.parse()
            print("Análise sintática: OK")
        except SyntaxError as e:
            self.errors.append(f"Erro Sintático: {e}")

    def _semantic_analysis(self):
        """
        Realiza verificações semânticas no AST.
        """
        declared_variables = set()
        variable_types = {}

        def check_declarations(node):
            if isinstance(node, dict):
                if "atribuir" in node:
                    var_name = node["atribuir"]["variavel"]
                    value = node["atribuir"]["valor"]

                    if var_name not in declared_variables:
                        self.errors.append(f"Erro Semântico: Variável '{var_name}' usada antes de ser declarada.")

                    if isinstance(value, dict) and "chamada_modulo" in value:
                       
                        pass
                    elif isinstance(value, int):
                        variable_types[var_name] = "inteiro"
                    elif isinstance(value, str):
                        variable_types[var_name] = "texto"

                if "variaveis" in node:
                    for var in node["variaveis"]:
                        declared_variables.add(var["nome"])
                        variable_types[var["nome"]] = var["tipo"]

            elif isinstance(node, list):
                for subnode in node:
                    check_declarations(subnode)

        check_declarations(self.ast["programa"])

        def check_types(node):
            if isinstance(node, dict):
                if "atribuir" in node:
                    var_name = node["atribuir"]["variavel"]
                    value = node["atribuir"]["valor"]

                    if var_name in variable_types:
                        expected_type = variable_types[var_name]
                        if isinstance(value, int) and expected_type != "inteiro":
                            self.errors.append(
                                f"Erro Semântico: Tipo incompatível para '{var_name}'. Esperado: {expected_type}, encontrado: inteiro."
                            )
                        elif isinstance(value, str) and expected_type != "texto":
                            self.errors.append(
                                f"Erro Semântico: Tipo incompatível para '{var_name}'. Esperado: {expected_type}, encontrado: texto."
                            )

            elif isinstance(node, list):
                for subnode in node:
                    check_types(subnode)

        check_types(self.ast["programa"])

    def report(self):
        """
        Exibe os resultados da análise.
        """
        if self.errors:
            print("Erros encontrados:")
            for error in self.errors:
                print(f"- {error}")
        else:
            print("Nenhum erro encontrado. O código está válido.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python linter.py <arquivo.zin>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not file_path.endswith(".zin"):
        print("Erro: O arquivo deve ter a extensão .zin.")
        sys.exit(1)

    linter = Linter(file_path)
    linter.lint()
    linter.report()
