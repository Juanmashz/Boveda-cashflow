from flask import Flask, request, jsonify, render_template
import boto3
from decimal import Decimal
import json
import os # <--- NUEVO: Para leer variables de entorno
from flask_wtf.csrf import CSRFProtect # <--- NUEVO: Para protección CSRF

app = Flask(__name__)
app.config['SECRET_KEY'] = 'una-clave-super-secreta-y-segura'
csrf = CSRFProtect(app)
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# --- RUTAS DE LA INTERFAZ WEB ---
# Nueva ruta principal: Pantalla de inicio de sesión
@app.route('/')
def login():
    return render_template('login.html')

# Mover el gestor de DynamoDB a una ruta protegida
@app.route('/basedatos')
def basedatos():
    return render_template('index.html')

# La bóveda de S3 se mantiene igual
@app.route('/boveda')
def boveda():
    return render_template('boveda.html')

# --- GET: Leer datos dinámicamente por tabla ---
@app.route('/api/<tabla>', methods=['GET'])
def obtener_datos(tabla):
    try:
        table_resource = dynamodb.Table(tabla)
        response = table_resource.scan()
        return jsonify({"items": response.get('Items', [])}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- POST: Crear o Actualizar dinámicamente ---
@app.route('/api/<tabla>', methods=['POST'])
def guardar_dato(tabla):
    data = json.loads(request.data, parse_float=Decimal)
    try:
        table_resource = dynamodb.Table(tabla)
        table_resource.put_item(Item=data)
        return jsonify({"mensaje": "Registro guardado exitosamente"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- DELETE: Eliminar dinámicamente ---
@app.route('/api/<tabla>/<pk_name>/<pk_value>', methods=['DELETE'])
def eliminar_dato(tabla, pk_name, pk_value):
    try:
        table_resource = dynamodb.Table(tabla)
        table_resource.delete_item(Key={pk_name: str(pk_value)})
        return jsonify({"mensaje": "Registro eliminado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # <--- NUEVO: Leer host desde variable de entorno para evitar el Blocker
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    app.run(host=host, port=80)
