#!/usr/bin/env bash

# Limpiar cache de pip
pip cache purge

# Remover todas las dependencias existentes
pip freeze | xargs pip uninstall -y

# Instalar openai específicamente primero
pip install openai==0.28.0

# Verificar la instalación de openai
OPENAI_VERSION=$(pip freeze | grep openai)
echo "OpenAI version installed: $OPENAI_VERSION"

# Si la versión no es 0.28.0, salir con error
if [[ "$OPENAI_VERSION" != "openai==0.28.0" ]]; then
    echo "Error: Wrong OpenAI version installed"
    exit 1
fi

# Instalar el resto de dependencias
pip install -r requirements-base.txt

# Verificar todas las instalaciones
pip freeze
