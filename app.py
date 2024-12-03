from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import openai
import os
import json
import logging
from pathlib import Path

# Configuración inicial
load_dotenv()
app = Flask(__name__)
CORS(app)

# Configurar OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

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

@app.route('/upload', methods=['GET', 'POST'])
def upload_knowledge():
    if request.method == 'POST':
        try:
            area = request.form.get('area')
            
            # Crear estructura de datos
            brief_data = {
                "descripcion_general": request.form.get('descripcion', '').strip(),
                "objetivos_comunes": [obj.strip() for obj in request.form.get('objetivos', '').split('\n') if obj.strip()],
                "elementos_clave": {
                    "experiencia": request.form.get('experiencia', '').strip(),
                    "interaccion": request.form.get('interaccion', '').strip(),
                    "viralidad": request.form.get('viralidad', '').strip()
                },
                "mejores_practicas": [prac.strip() for prac in request.form.get('practicas', '').split('\n') if prac.strip()],
                "casos_exitosos": []
            }

            # Procesar casos de éxito
            casos_texto = request.form.get('casos', '')
            casos_list = [caso.strip() for caso in casos_texto.split('\n\n') if caso.strip()]
            
            for caso in casos_list:
                caso_dict = {
                    "cliente": "Cliente",
                    "proyecto": caso,
                    "descripcion": "Extraído de presentación",
                    "resultados": "Ver presentación original para detalles"
                }
                brief_data["casos_exitosos"].append(caso_dict)

            # Guardar en archivos JSON
            brief_file = BRIEF_DIR / f'{area}.json'
            with open(brief_file, 'w', encoding='utf-8') as f:
                json.dump(brief_data, f, ensure_ascii=False, indent=2)

            return jsonify({"status": "success", "message": f"Datos guardados para {area}"})

        except Exception as e:
            logger.error(f"Error en upload: {str(e)}")
            return jsonify({"status": "error", "message": str(e)})

    return render_template('upload.html')

def crear_prompt_ideas(data, ideas_previas=None):
    prompt = f"""
    SOLICITUD ACTUAL: {data.get('solicitud', '')}
    IDEAS A EVITAR ABSOLUTAMENTE: {data.get('no-queremos', '')}
    
    REGLAS ESTRICTAS PARA GENERACIÓN DE IDEAS:
    1. Cada idea DEBE ser radicalmente diferente a las ideas listadas para evitar
    2. Cada idea DEBE ser única y no relacionada con las otras ideas propuestas
    3. Cada idea DEBE explicar por qué es disruptiva
    4. Cada idea DEBE incluir elementos innovadores específicos
    5. NO repetir conceptos ni aproximaciones similares
    
    ESTRUCTURA DE RESPUESTA PARA CADA IDEA:
    
    IDEA [número]:
    - Concepto Principal: [descripción breve y clara]
    - Por qué es disruptiva: [explicación detallada]
    - Elementos innovadores: [lista específica]
    - Implementación: [detalles prácticos]
    - Diferenciadores clave: [qué la hace única]
    """
    
    if ideas_previas:
        prompt += f"""
        IDEAS PREVIAS (EVITAR SIMILITUDES):
        {json.dumps(ideas_previas, indent=2)}
        
        IMPORTANTE:
        - Las nuevas ideas deben ser COMPLETAMENTE DIFERENTES a las anteriores
        - NO repetir conceptos ni enfoques similares
        - Cada nueva idea debe tener un ángulo radicalmente distinto
        """
    
    return prompt

@app.route('/generar', methods=['POST'])
def generar():
    try:
        data = request.json
        area = data.get('area_solicitada')
        logger.debug(f"Generando ideas para área: {area}")
        
        # Obtener ideas previas si existen
        ideas_previas = data.get('ideas_previas', [])
        
        # Crear prompt según el área
        if area == 'ideas':
            prompt = crear_prompt_ideas(data['ideas'], ideas_previas)
        else:
            # Mantener la lógica existente para otras áreas
            if area == 'btl':
                prompt = crear_prompt_btl(data['btl'])
            elif area == 'trade':
                prompt = crear_prompt_trade(data['trade'])
            elif area == 'digital':
                prompt = crear_prompt_digital(data['digital'])
            else:
                return jsonify({'error': 'Área no válida'})

        # Generar respuesta con OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """Eres un experto en creatividad disruptiva.
                Tu objetivo es generar ideas radicalmente diferentes y revolucionarias.
                NUNCA repitas conceptos ni uses aproximaciones similares.
                Cada idea debe ser completamente única y alejada de lo convencional."""},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.9
        )

        respuesta = response.choices[0].message['content']
        return jsonify({area: respuesta})

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({'error': str(e)})

def crear_prompt_btl(data):
    return f"""
    Por favor, genera 5 ideas creativas y disruptivas de BTL basadas en:
    
    SOLICITUD: {data.get('solicitud', '')}
    CONCEPTOS CLAVE: {data.get('conceptos', '')}
    LOCACIONES POSIBLES: {data.get('locaciones', '')}
    ANTES Y DESPUÉS: {data.get('antes-despues', '')}
    MOMENTO PEAK: {data.get('momento-peak', '')}
    ACTIVACIONES: {data.get('activaciones', '')}
    PUESTA EN ESCENA: {data.get('puesta-escena', '')}
    FORMA DE INVITAR: {data.get('forma-invitar', '')}
    
    ESTRUCTURA DE RESPUESTA PARA CADA IDEA:
    
    IDEA [número]:
    - Concepto Principal: [descripción breve]
    - Por qué es disruptiva: [explicación]
    - Elementos innovadores: [lista]
    - Implementación: [detalles]
    - Diferenciadores clave: [qué la hace única]
    """

def crear_prompt_trade(data):
    return f"""
    Por favor, genera 5 ideas creativas y disruptivas de TRADE basadas en:
    
    SOLICITUD: {data.get('solicitud', '')}
    MATERIAL POP: {data.get('material-pop', '')}
    IDEAS DE DINÁMICAS: {data.get('dinamicas', '')}
    MATERIALIDAD: {data.get('materialidad', '')}
    
    ESTRUCTURA DE RESPUESTA PARA CADA IDEA:
    
    IDEA [número]:
    - Concepto Principal: [descripción breve]
    - Por qué es disruptiva: [explicación]
    - Elementos innovadores: [lista]
    - Implementación: [detalles]
    - Diferenciadores clave: [qué la hace única]
    """

def crear_prompt_digital(data):
    return f"""
    Por favor, genera 5 ideas creativas y disruptivas de DIGITAL basadas en:
    
    SOLICITUD: {data.get('solicitud', '')}
    IDEAS DE CONTENIDO: {data.get('contenido', '')}
    CONCEPTOS: {data.get('conceptos', '')}
    
    ESTRUCTURA DE RESPUESTA PARA CADA IDEA:
    
    IDEA [número]:
    - Concepto Principal: [descripción breve]
    - Por qué es disruptiva: [explicación]
    - Elementos innovadores: [lista]
    - Implementación: [detalles]
    - Diferenciadores clave: [qué la hace única]
    """

if __name__ == '__main__':
    app.run(debug=True)
