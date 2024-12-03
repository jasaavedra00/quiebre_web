from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
import os
import json
import logging
from pathlib import Path

# Configuración inicial
load_dotenv()
app = Flask(__name__)
CORS(app)

# Configurar OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Asegurar que existan los directorios necesarios
DATA_DIR = Path('data')
BRIEF_DIR = DATA_DIR / 'brief'
CASOS_DIR = DATA_DIR / 'casos'
GUIDELINES_DIR = DATA_DIR / 'guidelines'

for dir_path in [BRIEF_DIR, CASOS_DIR, GUIDELINES_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

def crear_prompt_btl(data):
    return f"""
    SOLICITUD PRINCIPAL: {data.get('solicitud', '')}
    
    Por favor, genera ideas DISRUPTIVAS y DIFERENTES para CADA UNO de los siguientes aspectos:

    1. CONCEPTOS CLAVE:
    Contexto actual: {data.get('conceptos', '')}
    Generar 3 conceptos disruptivos:
    CONCEPTO 1:
    - Descripción:
    - Por qué es disruptivo:
    - Elementos innovadores:
    
    CONCEPTO 2:
    [mismo formato]
    
    CONCEPTO 3:
    [mismo formato]

    2. LOCACIONES:
    Opciones actuales: {data.get('locaciones', '')}
    Proponer 3 locaciones disruptivas:
    LOCACIÓN 1:
    - Descripción del espacio:
    - Por qué es disruptiva:
    - Ventajas únicas:
    
    [Continuar con mismo formato para locaciones 2 y 3]

    3. ANTES Y DESPUÉS:
    Contexto actual: {data.get('antes-despues', '')}
    Proponer 3 ideas de transformación:
    TRANSFORMACIÓN 1:
    - Descripción del cambio:
    - Impacto visual:
    - Elementos sorpresa:
    
    [Continuar con mismo formato para transformaciones 2 y 3]

    4. MOMENTO PEAK:
    Contexto actual: {data.get('momento-peak', '')}
    Proponer 3 momentos peak:
    MOMENTO 1:
    - Descripción del momento:
    - Factor sorpresa:
    - Impacto esperado:
    
    [Continuar con mismo formato para momentos 2 y 3]

    5. ACTIVACIONES:
    Contexto actual: {data.get('activaciones', '')}
    Proponer 3 activaciones disruptivas:
    ACTIVACIÓN 1:
    - Descripción:
    - Elementos innovadores:
    - Interacción con el público:
    
    [Continuar con mismo formato para activaciones 2 y 3]

    6. PUESTA EN ESCENA:
    Contexto actual: {data.get('puesta-escena', '')}
    Proponer 3 puestas en escena:
    ESCENA 1:
    - Descripción visual:
    - Elementos destacados:
    - Factor wow:
    
    [Continuar con mismo formato para escenas 2 y 3]

    7. FORMA DE INVITAR:
    Contexto actual: {data.get('forma-invitar', '')}
    Proponer 3 formas disruptivas de invitar:
    INVITACIÓN 1:
    - Descripción del método:
    - Factor sorpresa:
    - Llamado a la acción:
    
    [Continuar con mismo formato para invitaciones 2 y 3]
    """

def crear_prompt_trade(data):
    return f"""
    SOLICITUD PRINCIPAL: {data.get('solicitud', '')}
    
    Por favor, genera ideas DISRUPTIVAS y DIFERENTES para CADA UNO de los siguientes aspectos:

    1. MATERIAL POP:
    Contexto actual: {data.get('material-pop', '')}
    Generar 3 propuestas disruptivas:
    PROPUESTA 1:
    - Descripción del material:
    - Innovación principal:
    - Impacto en punto de venta:
    
    [Continuar con mismo formato para propuestas 2 y 3]

    2. DINÁMICAS:
    Contexto actual: {data.get('dinamicas', '')}
    Proponer 3 dinámicas innovadoras:
    DINÁMICA 1:
    - Descripción:
    - Elementos disruptivos:
    - Interacción con el consumidor:
    
    [Continuar con mismo formato para dinámicas 2 y 3]

    3. MATERIALIDAD:
    Contexto actual: {data.get('materialidad', '')}
    Proponer 3 conceptos de materiales:
    MATERIAL 1:
    - Descripción:
    - Innovación:
    - Impacto visual:
    
    [Continuar con mismo formato para materiales 2 y 3]
    """

def crear_prompt_digital(data):
    return f"""
    SOLICITUD PRINCIPAL: {data.get('solicitud', '')}
    
    Por favor, genera ideas DISRUPTIVAS y DIFERENTES para CADA UNO de los siguientes aspectos:

    1. CONTENIDO:
    Contexto actual: {data.get('contenido', '')}
    Generar 3 propuestas de contenido:
    CONTENIDO 1:
    - Descripción:
    - Formato innovador:
    - Engagement esperado:
    
    [Continuar con mismo formato para contenidos 2 y 3]

    2. CONCEPTOS:
    Contexto actual: {data.get('conceptos', '')}
    Proponer 3 conceptos disruptivos:
    CONCEPTO 1:
    - Descripción:
    - Elementos innovadores:
    - Viralización esperada:
    
    [Continuar con mismo formato para conceptos 2 y 3]

    3. PLATAFORMAS:
    Proponer 3 estrategias de plataformas:
    ESTRATEGIA 1:
    - Plataformas principales:
    - Uso innovador:
    - Integración cross-platform:
    
    [Continuar con mismo formato para estrategias 2 y 3]
    """

def crear_prompt_ideas(data):
    return f"""
    SOLICITUD PRINCIPAL: {data.get('solicitud', '')}
    IDEAS A EVITAR: {data.get('no-queremos', '')}
    
    Por favor, genera 3 ideas COMPLETAMENTE DISRUPTIVAS para CADA UNO de los siguientes aspectos:

    1. CONCEPTO GENERAL:
    IDEA 1:
    - Descripción del concepto:
    - Por qué es disruptivo:
    - Elementos innovadores:
    
    [Continuar con mismo formato para ideas 2 y 3]

    2. IMPLEMENTACIÓN:
    PROPUESTA 1:
    - Descripción detallada:
    - Aspectos técnicos:
    - Factores diferenciadores:
    
    [Continuar con mismo formato para propuestas 2 y 3]

    3. IMPACTO ESPERADO:
    IMPACTO 1:
    - Descripción del impacto:
    - Métricas esperadas:
    - Factores de éxito:
    
    [Continuar con mismo formato para impactos 2 y 3]
    """

@app.route('/generar', methods=['POST'])
def generar():
    try:
        data = request.json
        area = data.get('area_solicitada')
        logger.debug(f"Generando ideas para área: {area}")

        # Crear prompt según el área
        if area == 'btl':
            prompt = crear_prompt_btl(data['btl'])
        elif area == 'trade':
            prompt = crear_prompt_trade(data['trade'])
        elif area == 'digital':
            prompt = crear_prompt_digital(data['digital'])
        elif area == 'ideas':
            prompt = crear_prompt_ideas(data['ideas'])
        else:
            return jsonify({'error': 'Área no válida'})

        # Generar respuesta con OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """Eres un experto en creatividad disruptiva.
                Para cada aspecto solicitado, debes generar ideas COMPLETAMENTE DIFERENTES 
                a las mencionadas en el contexto. Cada idea debe ser única, innovadora y 
                factible de implementar. NO repitas conceptos entre las diferentes propuestas."""},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.9
        )

        respuesta = response.choices[0].message.content
        return jsonify({area: respuesta})

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
