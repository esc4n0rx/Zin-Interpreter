

check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "$1 não está instalado."
        echo "Por favor, instale-o antes de continuar."
        exit 1
    fi
}


check_command "python3"


check_command "git"


INSTALL_DIR="/usr/local/bin/zin"


if [ ! -d "$INSTALL_DIR" ]; then
    echo "Criando diretório de instalação em $INSTALL_DIR..."
    sudo mkdir -p "$INSTALL_DIR"
    echo "Clonando o repositório do Zin Interpreter..."
    sudo git clone https://github.com/esc4n0rx/Zin-Interpreter "$INSTALL_DIR"
else
    echo "Zin já está instalado no diretório $INSTALL_DIR. Atualizando repositório..."
    sudo git -C "$INSTALL_DIR" pull
fi

ZIN_SCRIPT="/usr/local/bin/zin"
echo "Criando o script de execução em $ZIN_SCRIPT..."

sudo tee "$ZIN_SCRIPT" > /dev/null << 'EOF'
#!/bin/bash

ZIN_DIR="/usr/local/bin/zin"

case "$1" in
    -run)
        python3 "$ZIN_DIR/interpretador.py" "$2"
        ;;
    -version)
        echo "Zin Interpreter v0.0.1"
        ;;
    -create)
        if [ -z "$2" ]; then
            echo "Por favor, forneça o nome do arquivo."
            exit 1
        fi
        cat <<EOT > "$2"
INICIO PROGAMA $2.

IMPLEMENTACAO PROGAMA $2.
PRINCIPAL.
FIM PRINCIPAL.

EXECUCAO PROGAMA $2.
EXECUTAR PRINCIPAL.

FIM PROGAMA $2.
EOT
        echo "Arquivo $2 criado com sucesso."
        ;;
    *)
        echo "Comando não reconhecido."
        echo "Use:"
        echo "  zin -run [arquivo.zin]    Para executar um programa."
        echo "  zin -version             Para ver a versão atual."
        echo "  zin -create [arquivo.zin] Para criar um arquivo base."
        ;;
esac
EOF

sudo chmod +x "$ZIN_SCRIPT"

if ! echo "$PATH" | grep -q "/usr/local/bin"; then
    echo "Adicionando /usr/local/bin ao PATH..."
    echo "export PATH=\"/usr/local/bin:\$PATH\"" >> ~/.bashrc
    source ~/.bashrc
fi

echo "Instalação concluída! Abra um novo terminal para usar o Zin."
echo "Use o comando 'zin' para executar."
