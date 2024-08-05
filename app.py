from flask import Flask, render_template, request, session, redirect, url_for
import random
import time

app = Flask(__name__)
app.secret_key = 'clave_secreta_para_sesiones'

class Heroe:
    def __init__(self, nombre):
        self.nombre = nombre
        self.vida_base = 100
        self.fuerza_base = 10
        self.defensa_base = 5
        self.nivel_vida = 1
        self.nivel_fuerza = 1
        self.nivel_defensa = 1
        self.nivel_descanso = 1
        self.vida = self.vida_base
        self.fuerza = self.fuerza_base
        self.defensa = self.defensa_base
        self.descansos_restantes = 3
        self.tiempo_ultimo_descanso = time.time()
        self.magia = {
            "fuego": 0,
            "agua": 0,
            "tierra": 0,
            "aire": 0
        }
        self.experiencia = 0
        self.nivel = 1
        self.oro = 0
        self.piedras_evolucion = 0
        self.buff_dano = 1.0
        self.buff_resistencia = 1.0

    def mostrar_estado(self):
        return {
            'vida': self.vida,
            'fuerza': self.fuerza,
            'defensa': self.defensa,
            'descansos_restantes': self.descansos_restantes,
            'magia': self.magia,
            'experiencia': self.experiencia,
            'nivel': self.nivel,
            'oro': self.oro,
            'piedras_evolucion': self.piedras_evolucion,
            'buff_dano': self.buff_dano,
            'buff_resistencia': self.buff_resistencia,
            'nombre': self.nombre
        }

    def atacar(self, enemigo):
        daño = (self.fuerza * self.buff_dano) - (enemigo.defensa * enemigo.buff_resistencia)
        if daño < 0:
            daño = 0
        enemigo.vida -= daño
        resultado = f"{self.nombre} ataca a {enemigo.nombre} causando {daño:.2f} puntos de daño."
        if enemigo.vida <= 0:
            resultado += f" {enemigo.nombre} ha sido derrotado."
            self.ganar_experiencia(enemigo.experiencia)
            self.ganar_recompensas(enemigo)
        else:
            resultado += f" {enemigo.nombre} tiene {enemigo.vida} puntos de vida restantes."
        return resultado

    def ganar_experiencia(self, puntos):
        self.experiencia += puntos
        if self.experiencia >= 100:
            self.nivel += 1
            self.experiencia -= 100
            self.fuerza_base += 5
            self.defensa_base += 5
            self.actualizar_estadisticas()

    def ganar_recompensas(self, enemigo):
        oro_ganado = random.randint(10, 50) + enemigo.oro_base * self.nivel
        self.oro += oro_ganado
        resultado = f"¡{self.nombre} ha ganado {oro_ganado} monedas de oro!"
        probabilidad_piedra = 0.05 + 0.01 * (enemigo.fuerza / 10)
        if random.random() < probabilidad_piedra:
            self.piedras_evolucion += 1
            resultado += " ¡Y también ha encontrado una piedra de evolución!"
        return resultado

    def actualizar_estadisticas(self):
        self.vida = self.vida_base * (1 + 0.05 * (self.nivel_vida - 1))
        self.fuerza = self.fuerza_base * (1 + 0.05 * (self.nivel_fuerza - 1))
        self.defensa = self.defensa_base * (1 + 0.05 * (self.nivel_defensa - 1))

class Enemigo:
    def __init__(self, nombre, vida, fuerza, defensa, experiencia, oro_base, buff_resistencia=1.0):
        self.nombre = nombre
        self.vida = vida
        self.fuerza = fuerza
        self.defensa = defensa
        self.experiencia = experiencia
        self.oro_base = oro_base
        self.buff_resistencia = buff_resistencia

    def atacar(self, heroe):
        daño = (self.fuerza * self.buff_resistencia) - heroe.defensa
        if daño < 0:
            daño = 0
        heroe.vida -= daño
        return f"{self.nombre} ataca a {heroe.nombre} causando {daño:.2f} puntos de daño."

def crear_enemigo(nivel_heroe):
    enemigos = [
        Enemigo("Goblin", 50, 8, 3, 20, 10),
        Enemigo("Troll", 80, 12, 6, 35, 20),
        Enemigo("Dragón", 150, 20, 10, 100, 50),
        Enemigo("Golem", 150, 15, 350, 80, 40),
        Enemigo("Bruja", 80, 45, 60, 130, 60),
        Enemigo("Destructor", 80, 45, 60, 130, 70),
        Enemigo("Acorazado", 300, 20, 550, 200, 100),
        Enemigo("Mago", 50, 180, 20, 250, 80),
    ]
    
    base_probabilidades = [0.30, 0.20, 0.12, 0.13, 0.10, 0.08, 0.07, 0.05]
    incrementos = [-(nivel_heroe * 0.02)] * len(enemigos)
    
    probabilidades = [max(0, base + inc) for base, inc in zip(base_probabilidades, incrementos)]
    total_probabilidad = sum(probabilidades)
    probabilidades = [p / total_probabilidad for p in probabilidades]

    return random.choices(enemigos, weights=probabilidades, k=1)[0]

@app.route('/')
def index():
    if 'heroe' not in session:
        return redirect(url_for('crear_heroe'))
    heroe = session['heroe']
    return render_template('index.html', heroe=heroe)

@app.route('/crear_heroe', methods=['GET', 'POST'])
def crear_heroe():
    if request.method == 'POST':
        nombre_heroe = request.form['nombre']
        heroe = Heroe(nombre_heroe)
        session['heroe'] = heroe.mostrar_estado()
        return redirect(url_for('index'))
    return render_template('crear_heroe.html')

@app.route('/explorar')
def explorar():
    heroe = Heroe(**session['heroe'])
    evento = random.choice(["enemigo", "tesoro", "nada", "piedra"])
    resultado = ""

    if evento == "enemigo":
        enemigo = crear_enemigo(heroe.nivel)
        resultado = f"Un {enemigo.nombre} ha aparecido!"
        session['enemigo'] = enemigo.__dict__
        return render_template('combate.html', heroe=heroe.mostrar_estado(), enemigo=enemigo.__dict__, resultado=resultado)
    elif evento == "tesoro":
        elemento = random.choice(["fuego", "agua", "tierra", "aire"])
        heroe.magia[elemento] += 1
        resultado = f"¡Has encontrado un tesoro con magia de {elemento}!"
    elif evento == "piedra":
        heroe.piedras_evolucion += 1
        resultado = "¡Has encontrado una piedra de evolución!"
    else:
        resultado = "No has encontrado nada en esta exploración."

    session['heroe'] = heroe.mostrar_estado()
    return render_template('explorar.html', heroe=heroe.mostrar_estado(), resultado=resultado)

@app.route('/combate', methods=['POST'])
def combate():
    heroe = Heroe(**session['heroe'])
    enemigo = Enemigo(**session['enemigo'])
    accion = request.form.get('accion')
    resultado = ""

    if accion == "atacar":
        resultado = heroe.atacar(enemigo)
        if enemigo.vida > 0:
            resultado += "\n" + enemigo.atacar(heroe)
    elif accion == "defenderse":
        resultado = f"{heroe.nombre} se defiende."
    elif accion == "escapar":
        if random.random() < 0.5:
            resultado = f"{heroe.nombre} ha escapado exitosamente."
            session.pop('enemigo')
            return redirect(url_for('explorar'))
        else:
            resultado = f"{heroe.nombre} intentó escapar, pero {enemigo.nombre} lo atrapó."

    session['heroe'] = heroe.mostrar_estado()
    session['enemigo'] = enemigo.__dict__
    return render_template('combate.html', heroe=heroe.mostrar_estado(), enemigo=enemigo.__dict__, resultado=resultado)

if __name__ == "__main__":
    app.run(debug=True)
