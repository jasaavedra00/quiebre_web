from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
import os
import logging

# Configuración inicial
load_dotenv()
app = Flask(__name__)
CORS(app)

# Configurar OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generar', methods=['POST'])
def generar():
    try:
        data = request.json
        area = data.get('area_solicitada')
        logger.debug(f"Generando ideas para área: {area}")

        # Configurar el prompt según el área
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
                {"role": "system", "content": """Eres un experto creativo en marketing y publicidad, 
                especializado en generar ideas disruptivas y originales. Tus respuestas deben ser 
                detalladas, innovadoras y factibles de implementar."""},
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

def crear_prompt_btl(data):
    return f"""
    Por favor, genera 5 ideas creativas y disruptivas de BTL basadas en la siguiente información:
    
    SOLICITUD: {data.get('solicitud', '')}
    CONCEPTOS CLAVE: {data.get('conceptos', '')}
    LOCACIONES POSIBLES: {data.get('locaciones', '')}
    ANTES Y DESPUÉS: {data.get('antes-despues', '')}
    MOMENTO PEAK: {data.get('momento-peak', '')}
    ACTIVACIONES: {data.get('activaciones', '')}
    PUESTA EN ESCENA: {data.get('puesta-escena', '')}
    FORMA DE INVITAR: {data.get('forma-invitar', '')}
    
    Para cada idea, proporciona:
    1. Descripción detallada del concepto
    2. Cómo se ejecutaría
    3. Impacto esperado
    4. Elementos necesarios
    5. Momento clave de la activación
    
    Formato de respuesta:
    IDEA 1: [descripción completa]
    - Ejecución:
    - Impacto:
    - Elementos:
    - Momento clave:

    [Repetir formato para cada idea]
    """

def crear_prompt_trade(data):
    return f"""
    Por favor, genera 5 ideas creativas y disruptivas de TRADE basadas en la siguiente información:
    
    SOLICITUD: {data.get('solicitud', '')}
    MATERIAL POP: {data.get('material-pop', '')}
    IDEAS DE DINÁMICAS: {data.get('dinamicas', '')}
    MATERIALIDAD: {data.get('materialidad', '')}
    
    Para cada idea, proporciona:
    1. Descripción detallada de la activación
    2. Materiales y elementos necesarios
    3. Dinámica de implementación
    4. Impacto esperado en el punto de venta
    
    Formato de respuesta:
    IDEA 1: [descripción completa]
    - Materiales:
    - Dinámica:
    - Impacto:
    - Implementación:

    [Repetir formato para cada idea]
    """

def crear_prompt_digital(data):
    return f"""
    Por favor, genera 5 ideas creativas y disruptivas de DIGITAL basadas en la siguiente información:
    
    SOLICITUD: {data.get('solicitud', '')}
    IDEAS DE CONTENIDO: {data.get('contenido', '')}
    CONCEPTOS: {data.get('conceptos', '')}
    
    Para cada idea, proporciona:
    1. Descripción detallada del contenido
    2. Plataformas recomendadas
    3. Formato y estilo
    4. Engagement esperado
    5. Call to action
    
    Formato de respuesta:
    IDEA 1: [descripción completa]
    - Plataformas:
    - Formato:
    - Engagement:
    - Call to action:

    [Repetir formato para cada idea]
    """

def crear_prompt_ideas(data):
    return f"""
    Por favor, genera 5 ideas creativas y disruptivas basadas en la siguiente información:
    
    SOLICITUD: {data.get('solicitud', '')}
    IDEAS A EVITAR: {data.get('no-queremos', '')}
    
    Para cada idea, asegúrate de que:
    1. Sea completamente diferente a las ideas que NO queremos
    2. Sea innovadora y original
    3. Tenga potencial de impacto real
    4. Sea factible de implementar
    5. Genere una experiencia memorable
    
    Formato de respuesta:
    IDEA 1: [descripción completa]
    - Por qué es diferente:
    - Impacto esperado:
    - Implementación:
    - Experiencia:

    [Repetir formato para cada idea]
    """

if __name__ == '__main__':
    app.run(debug=True)
