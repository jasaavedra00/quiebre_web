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
    Genera ideas COMPLETAMENTE DISRUPTIVAS y REVOLUCIONARIAS para cada uno de estos elementos BTL.
    IMPORTANTE: Cada idea debe ser RADICALMENTE DIFERENTE a lo convencional.

    1. CONCEPTOS CREATIVOS:
    Contexto actual: {data.get('concepto', '')}
    Proponer 3 conceptos totalmente disruptivos:
    CONCEPTO 1:
    - Idea central:
    - Por qué rompe paradigmas:
    - Elementos innovadores:
    [Repetir formato para conceptos 2 y 3]

    2. LOCACIONES ÚNICAS:
    Contexto actual: {data.get('locaciones', '')}
    Proponer 3 espacios no convencionales:
    LOCACIÓN 1:
    - Espacio propuesto:
    - Por qué es disruptivo:
    - Ventajas diferenciales:
    [Repetir formato para locaciones 2 y 3]

    3. ANTES Y DESPUÉS:
    Proponer 3 formas innovadoras de transformación:
    TRANSFORMACIÓN 1:
    - Descripción del cambio:
    - Impacto visual:
    - Factor sorpresa:
    [Repetir formato para transformaciones 2 y 3]

    4. MOMENTO PEAK:
    Proponer 3 momentos cumbre únicos:
    MOMENTO 1:
    - Descripción del momento:
    - Factor wow:
    - Elementos memorables:
    [Repetir formato para momentos 2 y 3]

    5. ACTIVACIONES:
    Contexto actual: {data.get('activaciones', '')}
    Proponer 3 activaciones revolucionarias:
    ACTIVACIÓN 1:
    - Mecánica:
    - Interacción innovadora:
    - Elemento viral:
    [Repetir formato para activaciones 2 y 3]

    6. PUESTA EN ESCENA:
    Proponer 3 montajes disruptivos:
    MONTAJE 1:
    - Descripción escénica:
    - Elementos únicos:
    - Impacto sensorial:
    [Repetir formato para montajes 2 y 3]

    7. PANTALLAS Y TECNOLOGÍA:
    Proponer 3 usos no convencionales:
    PROPUESTA 1:
    - Tecnología propuesta:
    - Aplicación innovadora:
    - Diferenciador clave:
    [Repetir formato para propuestas 2 y 3]

    8. FORMA DE INVITAR:
    Proponer 3 métodos disruptivos de convocatoria:
    MÉTODO 1:
    - Descripción:
    - Factor sorpresa:
    - Elemento memorable:
    [Repetir formato para métodos 2 y 3]
    """

def crear_prompt_trade(data):
    return f"""
    Genera ideas COMPLETAMENTE DISRUPTIVAS para cada elemento de Trade Marketing.
    IMPORTANTE: Cada propuesta debe ROMPER con lo tradicional del retail.

    1. EXHIBICIÓN:
    Contexto actual: {data.get('exhibicion', '')}
    Proponer 3 formas revolucionarias de exhibir:
    EXHIBICIÓN 1:
    - Concepto disruptivo:
    - Elementos innovadores:
    - Impacto en el shopper:
    [Repetir formato para exhibiciones 2 y 3]

    2. MATERIAL POP:
    Contexto actual: {data.get('material-pop', '')}
    Proponer 3 materiales no convencionales:
    MATERIAL 1:
    - Descripción:
    - Innovación propuesta:
    - Ventaja diferencial:
    [Repetir formato para materiales 2 y 3]

    3. DINÁMICAS DE COMPRA:
    Contexto actual: {data.get('dinamicas', '')}
    Proponer 3 mecánicas revolucionarias:
    DINÁMICA 1:
    - Mecánica propuesta:
    - Factor innovador:
    - Impacto en ventas:
    [Repetir formato para dinámicas 2 y 3]

    4. EXPERIENCIA EN PUNTO DE VENTA:
    Proponer 3 experiencias únicas:
    EXPERIENCIA 1:
    - Descripción:
    - Elementos sensoriales:
    - Factor memorable:
    [Repetir formato para experiencias 2 y 3]
    """

def crear_prompt_digital(data):
    return f"""
    Genera ideas COMPLETAMENTE DISRUPTIVAS para cada elemento Digital.
    IMPORTANTE: Cada propuesta debe REVOLUCIONAR la forma de interacción digital.

    1. CONCEPTO DIGITAL:
    Contexto actual: {data.get('concepto', '')}
    Proponer 3 conceptos revolucionarios:
    CONCEPTO 1:
    - Idea central:
    - Innovación digital:
    - Factor viral:
    [Repetir formato para conceptos 2 y 3]

    2. CONTENIDO:
    Contexto actual: {data.get('contenido', '')}
    Proponer 3 formatos disruptivos:
    CONTENIDO 1:
    - Formato propuesto:
    - Elemento innovador:
    - Potencial de engagement:
    [Repetir formato para contenidos 2 y 3]

    3. MECÁNICA DE INTERACCIÓN:
    Proponer 3 formas únicas de interacción:
    MECÁNICA 1:
    - Descripción:
    - Innovación tecnológica:
    - Factor diferencial:
    [Repetir formato para mecánicas 2 y 3]

    4. VIRALIZACIÓN:
    Proponer 3 estrategias no convencionales:
    ESTRATEGIA 1:
    - Método propuesto:
    - Factor viral:
    - Medición de impacto:
    [Repetir formato para estrategias 2 y 3]
    """

def crear_prompt_ideas(data):
    return f"""
    SOLICITUD ACTUAL: {data.get('solicitud', '')}
    IDEAS A EVITAR: {data.get('no-queremos', '')}
    
    Genera 3 ideas COMPLETAMENTE DISRUPTIVAS que rompan todos los paradigmas del mercado:

    IDEA 1:
    - Concepto Principal:
    - Por qué revoluciona el mercado:
    - Elementos nunca antes vistos:
    - Implementación innovadora:
    - Impacto esperado:
    - Medición de resultados:
    
    [Repetir mismo formato detallado para ideas 2 y 3]

    IMPORTANTE: Cada idea debe ser RADICALMENTE DIFERENTE a las otras y a cualquier cosa existente en el mercado.
    """

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
