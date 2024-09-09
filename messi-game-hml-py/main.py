import threading
import eel
import webview
from flask import Flask, request, jsonify
from flask_cors import CORS

# Iniciar Flask
app = Flask(__name__)
CORS(app)

# Simular datos en memoria
invites = [
    {"guid": "Francis Stone", "email": "Francis@gmail.com", "password": "123", "role": "user"},
    {"guid": "Valery towers", "email": "Valery@gmail.com", "password": "777", "role": "admin"},
    {"guid": "Jonatan de la glock", "email": "Jonatan@gmail.com", "password": "888", "role": "admin"},
]

# Endpoint para obtener todas las invitaciones
# (sin validación de permisos) (http://localhost:5000/api/invites)
@app.route('/api/invites', methods=['GET'])
def get_all_invites():
    print("Se solicitó el listado de invitaciones")
    return jsonify(invites), 200


# Endpoint para obtener todas las invitaciones
# (protegido solo para admins) (http://localhost:5000/api/invites)
'''
@app.route('/api/invites', methods=['GET'])
def get_all_invites_for_admin():
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != 'Bearer admin_token':
        return jsonify({"message": "Unauthorized"}), 403
    
    return jsonify(invites), 200
'''

'''Example Attack Scenarios
Scenario #1
During the registration process for an application that 
allows only invited users to join, the mobile application 
triggers an API call to GET /api/invites/{invite_guid}. The response contains 
a JSON with details about the invite, including the user's role and the user's email.

An attacker duplicates the request and manipulates the HTTP method 
and endpoint to POST /api/invites/new. This endpoint should only be 
accessed by administrators using the admin console. The endpoint does 
not implement function level authorization checks.
'''
# Endpoint vulnerable para crear una nueva invitación 
# (sin validación de permisos) (http://localhost:5000/api/invites/new)
'''
{
    "email": "ramen@gmail.com",
    "password": "ramen123",
    "role": "admin"
}
'''
@app.route('/api/invites/new', methods=['POST'])
def create_invite():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    
    if any(i['email'] == email for i in invites):
        return jsonify({"message": "Email already exists"}), 409
    
    new_invite = {
        "guid": "invite" + str(len(invites) + 1),
        "email": email,
        "password": password,
        "role": role
    }
    
    invites.append(new_invite)
    return jsonify(new_invite), 201


# Añadir validación de permisos en la creación de invitaciones (http://localhost:5000/api/invites/new)
'''
{
    "email": "ramen@gmail.com",
    "password": "ramen123",
    "role": "admin"
}
'''

'''
@app.route('/api/invites/new', methods=['POST'])
def create_invite():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')

    # Verificar si el usuario que hace la solicitud es administrador
    user_role = request.headers.get('Role')

    if user_role != 'admin':
        return jsonify({"message": "Unauthorized access. Only admins can create invites."}), 403
    
    # Validar si ya existe un usuario con ese email
    if any(i['email'] == email for i in invites):
        return jsonify({"message": "Email already exists"}), 409
    
    # Crear el nuevo usuario
    new_invite = {
        "guid": "invite" + str(len(invites) + 1),
        "email": email,
        "password": password,
        "role": role
    }
    
    invites.append(new_invite)
    return jsonify(new_invite), 201
'''


# Endpoint para iniciar sesión
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Buscar al usuario en la lista de invitaciones
    user = next((i for i in invites if i['email'] == email and i['password'] == password), None)
    
    if user:
        if user['role'] == 'admin':
            return jsonify({"message": "Login successful", "role": "admin"}), 200
        else:
            return jsonify({"message": "You don't have admin access"}), 403
    else:
        return jsonify({"message": "Invalid credentials"}), 401

# Correr el servidor Flask en un hilo separado
def start_flask():
    app.run(host='localhost', port=5000)

# Iniciar Eel y Pywebview
def start_eel():
    eel.init('templates')

    @eel.expose
    def App():
        print('corriendo aplicacion')

    App()

    window = webview.create_window('Demo de Seguridad', 'templates/index.html', width=1200, height=730, resizable=False)
    webview.start()

flask_thread = threading.Thread(target=start_flask)
flask_thread.start()

start_eel()
