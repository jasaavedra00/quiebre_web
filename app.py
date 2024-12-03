from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import openai
import os
import json
import logging
from pathlib import Path
import pkg_resources

# Verificar versión de openai
openai_version = pkg_resources.get_distribution('openai').version
if openai_version != '0.28.0':
    raise ImportError(f"Se requiere openai==0.28.0, pero se encontró {openai_version}")

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

# ... [El resto de las funciones crear_prompt_* se mantienen igual] ...

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
