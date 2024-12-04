from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import openai
import os
import json
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configuración inicial
load_dotenv()
app = Flask(__name__)
CORS(app)

# Configurar OpenAI
try:
    openai.api_key = os.getenv('OPENAI_API_KEY')
    logger.debug("OpenAI configurado correctamente")
except Exception as e:
    logger.error(f"Error configurando OpenAI: {e}")
    raise

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
            logger.debug(f"Procesando upload para área: {area}")
            
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

            brief_file = BRIEF_DIR / f'{area}.json'
            with open(brief_file, 'w', encoding='utf-8') as f:
                json.dump(brief_data, f, ensure_ascii=False, indent=2)

            logger.debug(f"Datos guardados exitosamente para {area}")
            return jsonify({"status": "success", "message": f"Datos guardados para {area}"})

        except Exception as e:
            logger.error(f"Error en upload: {str(e)}")
            return jsonify({"status": "error", "message": str(e)})

    return render_template('upload.html')

@app.route('/generar', methods=['POST'])
def generar():
    try:
        data = request.json
        area = data.get('area_solicitada')
        logger.debug(f"Generando ideas para área: {area}")

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

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """Eres un experto en creatividad RADICAL y DISRUPTIVA.
                    
                    TU OBJETIVO ES:
                    1. ANALIZAR el contexto específico del cliente/marca
                    2. IDENTIFICAR las ideas básicas/convencionales proporcionadas para EVITARLAS
                    3. Generar ideas COMPLETAMENTE OPUESTAS y REVOLUCIONARIAS
                    
                    REGLAS IMPORTANTES:
                    - NUNCA sugieras ideas similares a las proporcionadas
                    - ROMPE todos los paradigmas de la categoría
                    - EVITA cualquier aproximación convencional
                    - REVOLUCIONA la forma de pensar cada elemento
                    - GENERA IDEAS QUE NADIE HAYA IMPLEMENTADO ANTES
                    
                    PROCESO:
                    1. Primero analiza el brief y contexto
                    2. Identifica qué ideas son "básicas" o "esperadas" para EVITARLAS
                    3. Genera ideas que sean OPUESTAS o RADICALMENTE DIFERENTES
                    4. Asegúrate que cada idea sea IMPLEMENTABLE pero REVOLUCIONARIA
                    5. VERIFICA que ninguna idea se parezca a las proporcionadas"""},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.9
            )
            logger.debug("Respuesta de OpenAI recibida")

            respuesta = response.choices[0].message['content']
            return jsonify({area: respuesta})

        except Exception as e:
            logger.error(f"Error en la llamada a OpenAI: {str(e)}")
            return jsonify({'error': f'Error en la generación: {str(e)}'})

    except Exception as e:
        logger.error(f"Error general: {str(e)}")
        return jsonify({'error': str(e)})

def crear_prompt_btl(data):
    return f"""
    ANÁLISIS DEL CONTEXTO:
    Solicitud: {data.get('solicitud', 'No especificado')}
    
    IDEAS CONVENCIONALES A EVITAR:
    - Concepto actual: {data.get('concepto', 'No especificado')}
    - Locaciones actuales: {data.get('locaciones', 'No especificado')}
    - Activaciones actuales: {data.get('activaciones', 'No especificado')}
    - Puesta en escena actual: {data.get('puesta_escena', 'No especificado')}
    - Forma de invitar actual: {data.get('forma_invitar', 'No especificado')}

    GENERA IDEAS RADICALMENTE DIFERENTES PARA:

    1. CONCEPTOS CREATIVOS:
    EVITAR conceptos como: {data.get('concepto', '')}
    Proponer 3 conceptos REVOLUCIONARIOS:
    CONCEPTO 1:
    - Idea central (DEBE SER RADICAL):
    - Por qué rompe TODOS los paradigmas:
    - Elementos NUNCA ANTES VISTOS:
    - Impacto REVOLUCIONARIO esperado:
    [Repetir formato para conceptos 2 y 3]

    2. LOCACIONES ÚNICAS:
    EVITAR locaciones como: {data.get('locaciones', '')}
    Proponer 3 espacios IMPENSABLES:
    LOCACIÓN 1:
    - Espacio REVOLUCIONARIO:
    - Por qué NADIE lo ha hecho antes:
    - Elementos DISRUPTIVOS:
    - Impacto TRANSFORMADOR:
    [Repetir formato para locaciones 2 y 3]

    3. ACTIVACIONES:
    EVITAR activaciones como: {data.get('activaciones', '')}
    Proponer 3 activaciones NUNCA VISTAS:
    ACTIVACIÓN 1:
    - Mecánica REVOLUCIONARIA:
    - Elementos IMPENSABLES:
    - Factor RADICAL:
    - Impacto TRANSFORMADOR:
    [Repetir formato para activaciones 2 y 3]

    4. PUESTA EN ESCENA:
    EVITAR elementos como: {data.get('puesta_escena', '')}
    Proponer 3 montajes REVOLUCIONARIOS:
    MONTAJE 1:
    - Concepto RADICAL:
    - Elementos NUNCA VISTOS:
    - Factor DISRUPTIVO:
    - Impacto TRANSFORMADOR:
    [Repetir formato para montajes 2 y 3]

    5. FORMA DE INVITAR:
    EVITAR métodos como: {data.get('forma_invitar', '')}
    Proponer 3 métodos REVOLUCIONARIOS:
    MÉTODO 1:
    - Mecánica RADICAL:
    - Elementos DISRUPTIVOS:
    - Factor INNOVADOR:
    - Impacto TRANSFORMADOR:
    [Repetir formato para métodos 2 y 3]

    IMPORTANTE:
    - Cada idea debe ser RADICALMENTE DIFERENTE a lo proporcionado
    - EVITA cualquier similitud con las ideas convencionales mencionadas
    - Asegúrate que cada propuesta sea REVOLUCIONARIA pero IMPLEMENTABLE
    - ROMPE todos los paradigmas de la categoría
    """

def crear_prompt_trade(data):
    return f"""
    ANÁLISIS DEL CONTEXTO:
    Solicitud: {data.get('solicitud', 'No especificado')}
    
    IDEAS CONVENCIONALES A EVITAR:
    - Material POP actual: {data.get('material-pop', 'No especificado')}
    - Dinámicas actuales: {data.get('dinamicas', 'No especificado')}
    - Exhibición actual: {data.get('exhibicion', 'No especificado')}

    GENERA IDEAS RADICALMENTE DIFERENTES PARA:

    1. EXHIBICIÓN:
    EVITAR exhibiciones como: {data.get('exhibicion', '')}
    Proponer 3 formas REVOLUCIONARIAS de exhibir:
    EXHIBICIÓN 1:
    - Concepto RADICAL:
    - Elementos NUNCA VISTOS:
    - Factor DISRUPTIVO:
    - Impacto TRANSFORMADOR en ventas:
    [Repetir formato para exhibiciones 2 y 3]

    2. MATERIAL POP:
    EVITAR materiales como: {data.get('material-pop', '')}
    Proponer 3 materiales REVOLUCIONARIOS:
    MATERIAL 1:
    - Concepto RADICAL:
    - Elementos DISRUPTIVOS:
    - Innovación NUNCA VISTA:
    - Impacto TRANSFORMADOR:
    [Repetir formato para materiales 2 y 3]

    3. DINÁMICAS COMERCIALES:
    EVITAR dinámicas como: {data.get('dinamicas', '')}
    Proponer 3 mecánicas REVOLUCIONARIAS:
    DINÁMICA 1:
    - Mecánica RADICAL:
    - Elementos DISRUPTIVOS:
    - Factor INNOVADOR:
    - Impacto TRANSFORMADOR:
    [Repetir formato para dinámicas 2 y 3]

    IMPORTANTE:
    - Cada idea debe ser RADICALMENTE DIFERENTE a lo proporcionado
    - EVITA cualquier similitud con las ideas convencionales mencionadas
    - Asegúrate que cada propuesta sea REVOLUCIONARIA pero IMPLEMENTABLE
    - ROMPE todos los paradigmas del retail
    """

def crear_prompt_digital(data):
    return f"""
    ANÁLISIS DEL CONTEXTO:
    Solicitud: {data.get('solicitud', 'No especificado')}
    
    IDEAS CONVENCIONALES A EVITAR:
    - Contenido actual: {data.get('contenido', 'No especificado')}
    - Conceptos actuales: {data.get('conceptos', 'No especificado')}
    - Estrategia actual: {data.get('estrategia', 'No especificado')}

    GENERA IDEAS RADICALMENTE DIFERENTES PARA:

    1. ESTRATEGIA DIGITAL:
    EVITAR estrategias como: {data.get('estrategia', '')}
    Proponer 3 enfoques REVOLUCIONARIOS:
    ESTRATEGIA 1:
    - Concepto RADICAL:
    - Elementos NUNCA VISTOS:
    - Factor DISRUPTIVO:
    - Impacto TRANSFORMADOR:
    [Repetir formato para estrategias 2 y 3]

    2. CONTENIDO:
    EVITAR contenidos como: {data.get('contenido', '')}
    Proponer 3 formatos REVOLUCIONARIOS:
    CONTENIDO 1:
    - Formato RADICAL:
    - Elementos DISRUPTIVOS:
    - Factor INNOVADOR:
    - Impacto TRANSFORMADOR:
    [Repetir formato para contenidos 2 y 3]

    3. MECÁNICAS DE INTERACCIÓN:
    EVITAR mecánicas como: {data.get('mecanicas', '')}
    Proponer 3 interacciones REVOLUCIONARIAS:
    MECÁNICA 1:
    - Concepto RADICAL:
    - Elementos NUNCA VISTOS:
    - Factor DISRUPTIVO:
    - Impacto TRANSFORMADOR:
    [Repetir formato para mecánicas 2 y 3]

    IMPORTANTE:
    - Cada idea debe ser RADICALMENTE DIFERENTE a lo proporcionado
    - EVITA cualquier similitud con las ideas convencionales mencionadas
    - Asegúrate que cada propuesta sea REVOLUCIONARIA pero IMPLEMENTABLE
    - ROMPE todos los paradigmas digitales
    """

def crear_prompt_ideas(data):
    return f"""
    ANÁLISIS DEL CONTEXTO:
    Solicitud: {data.get('solicitud', 'No especificado')}
    
    IDEAS A EVITAR EXPLÍCITAMENTE:
    {data.get('no-queremos', 'No especificado')}

    GENERA 3 IDEAS COMPLETAMENTE REVOLUCIONARIAS:

    IDEA 1:
    - Concepto RADICAL:
    - Por qué ROMPE TODOS los paradigmas:
    - Elementos NUNCA ANTES VISTOS:
    - Implementación REVOLUCIONARIA:
    - Impacto TRANSFORMADOR:
    - Medición de RESULTADOS DISRUPTIVOS:
    
    [Repetir mismo formato detallado para ideas 2 y 3]

    IMPORTANTE:
    - Cada idea debe ser RADICALMENTE DIFERENTE a lo proporcionado
    - EVITA cualquier similitud con las ideas convencionales mencionadas
    - ROMPE completamente con lo establecido en la categoría
    - Asegúrate que cada propuesta sea REVOLUCIONARIA pero IMPLEMENTABLE
    """

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
