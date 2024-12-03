#!/usr/bin/env bash
# Primero desinstalamos cualquier versión existente
pip uninstall openai -y

# Luego instalamos la versión específica que necesitamos
pip install openai==0.28.0

# Finalmente instalamos el resto de dependencias
pip install -r requirements.txt

# Verificamos la versión instalada
pip freeze | grep openai
