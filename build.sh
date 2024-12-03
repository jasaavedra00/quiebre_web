#!/usr/bin/env bash
pip install --upgrade pip
pip uninstall openai -y
pip install openai==0.28
pip install -r requirements.txt
