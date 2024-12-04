from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
try:
    from openai import OpenAI
    print("OpenAI importado correctamente")
except ImportError as e:
    print(f"Error importando OpenAI: {e}")
    import subprocess
    print("Intentando instalar openai...")
    subprocess.check_call(["pip", "install", "openai==1.3.0"])
    from openai import OpenAI
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

# Configurar OpenAI con el nuevo cliente
try:
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    logger.debug("OpenAI client initialized successfully")
except Exception as e:
    logger.error(f"Error initializing OpenAI client: {e}")
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

        logger.debug(f"Prompt generado: {prompt}")

        try:
            # Generar respuesta con OpenAI (nueva sintaxis)
            response = client.chat.completions.create(
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
            logger.debug("Respuesta de OpenAI recibida")

            respuesta = response.choices[0].message.content
            return jsonify({area: respuesta})

        except Exception as e:
            logger.error(f"Error en la llamada a OpenAI: {str(e)}")
            return jsonify({'error': f'Error en la generación: {str(e)}'})

    except Exception as e:
        logger.error(f"Error general: {str(e)}")
        return jsonify({'error': str(e)})

def crear_prompt_btl(data):
    return f"""
    Por favor, genera ideas DISRUPTIVAS y DIFERENTES para CADA UNO de los siguientes aspectos:

    1. LOCACIONES:
    Contexto actual: {data.get('locaciones', '')}
    Proponer 3 locaciones disruptivas:
    LOCACIÓN 1:
    - Descripción:
    - Por qué es disruptiva:
    - Elementos innovadores:
    
    [Continuar con mismo formato para locaciones 2 y 3]

    2. ACTIVACIONES:
    Contexto actual: {data.get('activaciones', '')}
    Proponer 3 activaciones disruptivas:
    ACTIVACIÓN 1:
    - Descripción:
    - Elementos innovadores:
    - Interacción con el público:
    
    [Continuar con mismo formato para activaciones 2 y 3]
    """

def crear_prompt_trade(data):
    return f"""
    Por favor, genera ideas DISRUPTIVAS y DIFERENTES para CADA UNO de los siguientes aspectos:

    1. MATERIAL POP:
    Contexto actual: {data.get('material-pop', '')}
    Generar 3 propuestas disruptivas:
    PROPUESTA 1:
    - Descripción:
    - Por qué es disruptiva:
    - Elementos innovadores:
    
    [Continuar con mismo formato para propuestas 2 y 3]

    2. DINÁMICAS:
    Contexto actual: {data.get('dinamicas', '')}
    Proponer 3 dinámicas disruptivas:
    DINÁMICA 1:
    - Descripción:
    - Mecánica:
    - Factor diferenciador:
    
    [Continuar con mismo formato para dinámicas 2 y 3]

    3. MATERIALIDAD:
    Contexto actual: {data.get('materialidad', '')}
    Proponer 3 opciones innovadoras:
    OPCIÓN 1:
    - Material propuesto:
    - Ventajas únicas:
    - Aplicaciones posibles:
    
    [Continuar con mismo formato para opciones 2 y 3]
    """

def crear_prompt_digital(data):
    return f"""
    Por favor, genera ideas DISRUPTIVAS y DIFERENTES para CADA UNO de los siguientes aspectos:

    1. CONTENIDO:
    Contexto actual: {data.get('contenido', '')}
    Generar 3 propuestas de contenido:
    CONTENIDO 1:
    - Descripción:
    - Formato:
    - Factor viral:
    
    [Continuar con mismo formato para contenidos 2 y 3]

    2. CONCEPTOS:
    Contexto actual: {data.get('conceptos', '')}
    Proponer 3 conceptos disruptivos:
    CONCEPTO 1:
    - Descripción:
    - Elementos innovadores:
    - Viralización esperada:
    
    [Continuar con mismo formato para conceptos 2 y 3]
    """

def crear_prompt_ideas(data):
    return f"""
    SOLICITUD ACTUAL: {data.get('solicitud', '')}
    IDEAS A EVITAR: {data.get('no-queremos', '')}
    
    Por favor, genera 3 ideas COMPLETAMENTE DISRUPTIVAS:

    IDEA 1:
    - Concepto Principal:
    - Por qué es disruptiva:
    - Elementos innovadores:
    - Implementación:
    - Diferenciadores clave:
    
    [Continuar con mismo formato para ideas 2 y 3]
    """

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
