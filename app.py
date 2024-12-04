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

        logger.debug(f"Prompt generado: {prompt}")

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """Eres un experto en creatividad disruptiva con amplia experiencia en marketing y publicidad.
                    Tu objetivo es generar ideas que sean:
                    1. DISRUPTIVAS Y REVOLUCIONARIAS
                    2. ESPECÍFICAMENTE ADAPTADAS al contexto y solicitud del cliente
                    3. RELEVANTES para el target y objetivos planteados
                    4. FACTIBLES de implementar dentro de las restricciones dadas
                    
                    IMPORTANTE:
                    - Analiza primero el contexto/solicitud
                    - Asegúrate que cada idea responda directamente a los objetivos
                    - Las ideas deben ser únicas pero relevantes para la marca/producto
                    - Considera restricciones y limitaciones mencionadas"""},
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
    CONTEXTO DE LA SOLICITUD:
    - Marca/Cliente: {data.get('marca', 'No especificado')}
    - Objetivo: {data.get('objetivo', 'No especificado')}
    - Target: {data.get('target', 'No especificado')}
    - Restricciones/Consideraciones: {data.get('restricciones', 'No especificado')}
    - Presupuesto: {data.get('presupuesto', 'No especificado')}
    
    Basado en este contexto específico, genera ideas DISRUPTIVAS para cada elemento:

    1. CONCEPTOS CREATIVOS:
    Contexto actual: {data.get('concepto', '')}
    Proponer 3 conceptos que revolucionen la categoría Y se alineen con el objetivo:
    CONCEPTO 1:
    - Idea central:
    - Alineación con objetivo:
    - Elementos disruptivos:
    - Relevancia para el target:
    [Repetir formato para conceptos 2 y 3]

    2. LOCACIONES ÚNICAS:
    Contexto actual: {data.get('locaciones', '')}
    Proponer 3 espacios que sorprendan al target específico:
    LOCACIÓN 1:
    - Espacio propuesto:
    - Por qué funciona para este target:
    - Elementos disruptivos:
    - Alineación con marca:
    [Repetir formato para locaciones 2 y 3]

    3. ACTIVACIONES:
    Contexto actual: {data.get('activaciones', '')}
    Proponer 3 activaciones que cumplan el objetivo:
    ACTIVACIÓN 1:
    - Mecánica:
    - Relevancia para objetivo:
    - Elemento disruptivo:
    - Conexión con target:
    [Repetir formato para activaciones 2 y 3]

    4. PUESTA EN ESCENA:
    Proponer 3 montajes alineados con la marca:
    MONTAJE 1:
    - Descripción:
    - Alineación con marca:
    - Elemento sorpresa:
    - Impacto esperado:
    [Repetir formato para montajes 2 y 3]

    5. TECNOLOGÍA Y EXPERIENCIA:
    Proponer 3 usos innovadores considerando el target:
    PROPUESTA 1:
    - Tecnología:
    - Relevancia para target:
    - Factor innovador:
    - Medición de resultados:
    [Repetir formato para propuestas 2 y 3]
    """

def crear_prompt_trade(data):
    return f"""
    CONTEXTO DE LA SOLICITUD:
    - Marca/Cliente: {data.get('marca', 'No especificado')}
    - Objetivo comercial: {data.get('objetivo', 'No especificado')}
    - Canal: {data.get('canal', 'No especificado')}
    - Restricciones: {data.get('restricciones', 'No especificado')}
    - KPIs esperados: {data.get('kpis', 'No especificado')}

    Basado en este contexto específico, genera ideas DISRUPTIVAS para:

    1. EXHIBICIÓN:
    Contexto actual: {data.get('exhibicion', '')}
    Proponer 3 formas revolucionarias que impulsen ventas:
    EXHIBICIÓN 1:
    - Concepto:
    - Alineación con objetivo comercial:
    - Elemento disruptivo:
    - ROI esperado:
    [Repetir formato para exhibiciones 2 y 3]

    2. MATERIAL POP:
    Contexto actual: {data.get('material-pop', '')}
    Proponer 3 materiales que revolucionen el punto de venta:
    MATERIAL 1:
    - Descripción:
    - Impacto en ventas:
    - Innovación:
    - Medición de efectividad:
    [Repetir formato para materiales 2 y 3]

    3. DINÁMICAS COMERCIALES:
    Contexto actual: {data.get('dinamicas', '')}
    Proponer 3 mecánicas que aumenten conversión:
    DINÁMICA 1:
    - Mecánica:
    - Alineación con KPIs:
    - Factor innovador:
    - Resultados esperados:
    [Repetir formato para dinámicas 2 y 3]
    """

def crear_prompt_digital(data):
    return f"""
    CONTEXTO DE LA SOLICITUD:
    - Marca/Cliente: {data.get('marca', 'No especificado')}
    - Objetivo digital: {data.get('objetivo', 'No especificado')}
    - Plataformas: {data.get('plataformas', 'No especificado')}
    - Target digital: {data.get('target', 'No especificado')}
    - KPIs digitales: {data.get('kpis', 'No especificado')}

    Basado en este contexto específico, genera ideas DISRUPTIVAS para:

    1. ESTRATEGIA DIGITAL:
    Contexto actual: {data.get('estrategia', '')}
    Proponer 3 enfoques revolucionarios:
    ESTRATEGIA 1:
    - Concepto:
    - Alineación con objetivo:
    - Innovación digital:
    - KPIs impactados:
    [Repetir formato para estrategias 2 y 3]

    2. CONTENIDO:
    Contexto actual: {data.get('contenido', '')}
    Proponer 3 formatos que revolucionen la categoría:
    CONTENIDO 1:
    - Formato:
    - Relevancia para target:
    - Factor viral:
    - Medición de impacto:
    [Repetir formato para contenidos 2 y 3]

    3. INTERACCIÓN:
    Proponer 3 mecánicas innovadoras:
    MECÁNICA 1:
    - Descripción:
    - Alineación con objetivo:
    - Elemento disruptivo:
    - Engagement esperado:
    [Repetir formato para mecánicas 2 y 3]
    """

def crear_prompt_ideas(data):
    return f"""
    CONTEXTO DE LA SOLICITUD:
    - Brief: {data.get('solicitud', '')}
    - Objetivo principal: {data.get('objetivo', 'No especificado')}
    - Target: {data.get('target', 'No especificado')}
    - Ideas a evitar: {data.get('no-queremos', '')}
    - Restricciones: {data.get('restricciones', 'No especificado')}
    
    Basado en este contexto específico, genera 3 ideas COMPLETAMENTE DISRUPTIVAS:

    IDEA 1:
    - Concepto Principal:
    - Alineación con objetivo:
    - Por qué es disruptiva:
    - Relevancia para target:
    - Elementos innovadores:
    - Implementación:
    - Medición de resultados:
    
    [Repetir mismo formato detallado para ideas 2 y 3]

    IMPORTANTE: 
    - Cada idea debe ser ÚNICA pero RELEVANTE para el brief
    - Asegúrate que cada idea responda al objetivo principal
    - Considera las restricciones mencionadas
    - Evita específicamente las ideas mencionadas como no deseadas
    """

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
