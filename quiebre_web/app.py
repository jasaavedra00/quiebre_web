from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
from flask_cors import CORS
import logging
from openai import OpenAI

# Configuración inicial
app = Flask(__name__)
CORS(app)
load_dotenv()

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Inicializar OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generar', methods=['POST'])
def generar_quiebre():
    try:
        datos = request.get_json()
        area_solicitada = datos.get('area_solicitada')
        logger.debug(f"Generando ideas para área: {area_solicitada}")
        
        # Configuración de áreas
        areas_config = {
            'btl': {
                'titulo': 'BTL (Below The Line)',
                'role': "Eres un experto en marketing BTL altamente creativo y disruptivo.",
                'campos': {
                    'conceptos': 'CONCEPTOS DISRUPTIVOS',
                    'locaciones': 'LOCACIONES INNOVADORAS',
                    'antesDespues': 'ANTES Y DESPUÉS IMPACTANTE',
                    'momentoPeak': 'MOMENTO PEAK MEMORABLE',
                    'activaciones': 'ACTIVACIONES ÚNICAS',
                    'puestaEscena': 'PUESTA EN ESCENA INNOVADORA',
                    'formaInvitar': 'FORMA DE INVITAR ORIGINAL'
                }
            }
        }

        if area_solicitada in areas_config:
            config = areas_config[area_solicitada]
            area_datos = datos[area_solicitada]
            solicitud = area_datos.get('solicitud', '')

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": config['role']},
                    {"role": "user", "content": f"Solicitud: {solicitud}"}
                ],
                temperature=0.9,
                max_tokens=2000
            )

            return jsonify({area_solicitada: response.choices[0].message.content})

        return jsonify({"error": "Área no válida"}), 400

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
