from flask import Flask, jsonify, request
import random
from proximo_feriado import NextHoliday

app = Flask(__name__)
peliculas = [
    {'id': 1, 'titulo': 'Indiana Jones', 'genero': 'Acción'},
    {'id': 2, 'titulo': 'Star Wars', 'genero': 'Acción'},
    {'id': 3, 'titulo': 'Interstellar', 'genero': 'Ciencia ficción'},
    {'id': 4, 'titulo': 'Jurassic Park', 'genero': 'Aventura'},
    {'id': 5, 'titulo': 'The Avengers', 'genero': 'Acción'},
    {'id': 6, 'titulo': 'Back to the Future', 'genero': 'Ciencia ficción'},
    {'id': 7, 'titulo': 'The Lord of the Rings', 'genero': 'Fantasía'},
    {'id': 8, 'titulo': 'The Dark Knight', 'genero': 'Acción'},
    {'id': 9, 'titulo': 'Inception', 'genero': 'Ciencia ficción'},
    {'id': 10, 'titulo': 'The Shawshank Redemption', 'genero': 'Drama'},
    {'id': 11, 'titulo': 'Pulp Fiction', 'genero': 'Crimen'},
    {'id': 12, 'titulo': 'Fight Club', 'genero': 'Drama'}
]


def obtener_peliculas():
    return jsonify(peliculas)


def obtener_pelicula(id):
    pelicula_encontrada = next((p for p in peliculas if p['id'] == id), None)
    if not pelicula_encontrada:
        return jsonify({'error': 'Película no encontrada'}), 404
    return jsonify(pelicula_encontrada)


def agregar_pelicula():
    nueva_pelicula = {
        'id': obtener_nuevo_id(),
        'titulo': request.json['titulo'],
        'genero': request.json['genero']
    }
    peliculas.append(nueva_pelicula)
    print(peliculas)
    return jsonify(nueva_pelicula), 201


def actualizar_pelicula(id):
    pelicula = next((p for p in peliculas if p['id'] == id), None)
    if not pelicula:
        return jsonify({'error': 'Película no encontrada'}), 404
    pelicula['titulo'] = request.json.get('titulo', pelicula['titulo'])
    pelicula['genero'] = request.json.get('genero', pelicula['genero'])
    return jsonify(pelicula)


def eliminar_pelicula(id):
    global peliculas
    peliculas = [p for p in peliculas if p['id'] != id]
    return jsonify({'mensaje': 'Película eliminada correctamente'}), 200


def obtener_nuevo_id():
    if len(peliculas) > 0:
        ultimo_id = peliculas[-1]['id']
        return ultimo_id + 1
    else:
        return 1


app.add_url_rule('/peliculas', 'obtener_peliculas', obtener_peliculas, methods=['GET'])
app.add_url_rule('/peliculas/<int:id>', 'obtener_pelicula', obtener_pelicula, methods=['GET'])
app.add_url_rule('/peliculas', 'agregar_pelicula', agregar_pelicula, methods=['POST'])
app.add_url_rule('/peliculas/<int:id>', 'actualizar_pelicula', actualizar_pelicula, methods=['PUT'])
app.add_url_rule('/peliculas/<int:id>', 'eliminar_pelicula', eliminar_pelicula, methods=['DELETE'])


@app.route('/peliculas/genero/<string:genero>', methods=['GET'])
def filtrar_por_genero(genero):
    resultado = [p for p in peliculas if p['genero'].lower() == genero.lower()]
    return jsonify(resultado)

@app.route('/peliculas/buscar', methods=['GET'])
def buscar_por_titulo():
    query = request.args.get('titulo', '').lower()
    resultado = [p for p in peliculas if query in p['titulo'].lower()]
    return jsonify(resultado)


@app.route('/peliculas/sugerir', methods=['GET'])
def sugerir_aleatoria():
    return jsonify(random.choice(peliculas)) if peliculas else jsonify({'error': 'No hay películas'}), 404

@app.route('/peliculas/sugerir/<string:genero>', methods=['GET'])
def sugerir_por_genero(genero):
    opciones = [p for p in peliculas if p['genero'].lower() == genero.lower()]
    return jsonify(random.choice(opciones)) if opciones else jsonify({'error': 'Género no encontrado'}), 404

@app.route('/recomendar/<string:genero>', methods=['GET'])
def recomendar_feriado(genero):
    try:
        tipo_feriado = request.args.get('tipo', None)  # Obtener tipo desde query params
        next_holiday = NextHoliday()
        next_holiday.fetch_holidays(tipo=tipo_feriado)  # Pasar el tipo
        
        if not next_holiday.holiday:
            return jsonify({'error': 'No se encontraron feriados'}), 404
        
        opciones = [p for p in peliculas if p['genero'].lower() == genero.lower()]
        if not opciones:
            return jsonify({'error': 'No hay películas de este género'}), 404
        
        pelicula = random.choice(opciones)
        return jsonify({
            'feriado': next_holiday.holiday['motivo'],
            'fecha': f"{next_holiday.holiday['dia']}/{next_holiday.holiday['mes']}",
            'tipo': next_holiday.holiday['tipo'],  # Incluir tipo en respuesta
            'pelicula': pelicula
        }), 200
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500
    
if __name__ == '__main__':
    app.run()
