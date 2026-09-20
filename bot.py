import json
import os
import random
from mastodon import Mastodon

# ==============================================================================
# 1. CONFIGURACIÓN Y VALORES INICIALES
# ==============================================================================

ACCESS_TOKEN = 'yxV2giz8Ug6Y2r1iHIR4_mBubHBrxusXKSsNRKiKpLw'
API_BASE_URL = 'https://mastodon.social'  # Cambia por la URL de tu instancia
ARCHIVO_ESTADO = 'estado.json'

ESTADO_INICIAL = {
    "dia": 1,
    "poblacion": 12,
    "bebes": 0,
    "suministros": 80,
    "barricadas": 100,
    "moral": 75,
    "dias_bebes": []
}

# Tabla de eventos aleatorios nocturnos (Suman 100% de probabilidad)
EVENTOS_NOCTURNOS = [
    {
        "probabilidad": 40,
        "texto": "🌙 La noche transcurrió en absoluta calma. Todos pudieron descansar.",
        "efectos": {}
    },
    {
        "probabilidad": 10,
        "texto": "🧟 Un par de zombies rondaron las vallas antes de ser eliminados.",
        "efectos": {"barricadas": -10, "moral": -5}
    },
    {
        "probabilidad": 10,
        "texto": "🐀 Una plaga de ratas arruinó parte de las provisiones en el almacén.",
        "efectos": {"suministros": -15}
    },
    {
        "probabilidad": 10,
        "texto": "🔥 Hubo una fuerte discusión entre los aldeanos por las raciones.",
        "efectos": {"moral": -10}
    },
    {
        "probabilidad": 10,
        "texto": "🩸 **¡ATAQUE DE CANÍBALES!** Intentaron asaltar el sector norte.",
        "efectos": {"barricadas": -20, "moral": -10}
    },
    {
        "probabilidad": 10,
        "texto": "🧟‍♂️ **HORDA NOCTURNA:** Un grupo amplio de infectados embistió el muro.",
        "efectos": {"barricadas": -25, "suministros": -10}
    },
    {
        "probabilidad": 5,
        "texto": "🍼 **¡NUEVA VIDA!** Nace un bebé sano en la enfermería.",
        "efectos": {"bebes": 1, "moral": 15}
    },
    {
        "probabilidad": 5,
        "texto": "📦 Los vigías encontraron una caja de suministros junto al perímetro.",
        "efectos": {"suministros": 20}
    }
]

# ==============================================================================
# 2. GESTIÓN DEL ARCHIVO DE ESTADO (JSON)
# ==============================================================================

def cargar_estado():
    if os.path.exists(ARCHIVO_ESTADO):
        with open(ARCHIVO_ESTADO, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Si no existe, guardar y retornar el estado inicial
        guardar_estado(ESTADO_INICIAL)
        return dict(ESTADO_INICIAL)

def guardar_estado(estado):
    with open(ARCHIVO_ESTADO, 'w', encoding='utf-8') as f:
        json.dump(estado, f, indent=4, ensure_ascii=False)

# ==============================================================================
# 3. LECTURA DE LA ENCUESTA ANTERIOR
# ==============================================================================

def obtener_opcion_ganadora(mastodon):
    try:
        cuenta_bot = mastodon.account_verify_credentials()
        publicaciones = mastodon.account_statuses(cuenta_bot['id'], limit=5)
        
        toot_con_encuesta = None
        for status in publicaciones:
            if status.get('poll') is not None:
                toot_con_encuesta = status
                break
                
        if not toot_con_encuesta:
            print("⚠️ No se encontró encuesta previa. Se selecciona la opción 0 por defecto.")
            return 0

        encuesta = toot_con_encuesta['poll']
        opciones = encuesta['options']
        votos = [opcion['votes_count'] for opcion in opciones]
        total_votos = sum(votos)
        
        if total_votos == 0:
            opcion_elegida = random.randint(0, len(opciones) - 1)
            print(f"⚠️ La encuesta no recibió votos. Selección aleatoria: opción {opcion_elegida}.")
            return opcion_elegida

        votos_maximos = max(votos)
        return votos.index(votos_maximos)

    except Exception as e:
        print(f"❌ Error al consultar la API de Mastodon: {e}")
        return 0

# ==============================================================================
# 4. LÓGICA DEL JUEGO Y PROCESAMIENTO DIARIO
# ==============================================================================

def obtener_evento_aleatorio():
    pesos = [e["probabilidad"] for e in EVENTOS_NOCTURNOS]
    return random.choices(EVENTOS_NOCTURNOS, weights=pesos, k=1)[0]

def procesar_dia(estado, opcion_ganadora):
    # 1. Aplicar consecuencias de la encuesta ganadora
    resumen_decision = ""
    if opcion_ganadora == 0:
        estado['suministros'] += 25
        estado['moral'] += 5
        resumen_decision = "📦 La expedición regresó con suministros (+25% Suministros, +5% Moral)."
    elif opcion_ganadora == 1:
        estado['barricadas'] += 20
        resumen_decision = "🔨 La comunidad trabajó duro en el perímetro (+20% Barricadas)."
    elif opcion_ganadora == 2:
        estado['moral'] += 15
        resumen_decision = "🎯 Las patrullas aumentaron la seguridad y tranquilidad (+15% Moral)."

    # 2. Aplicar evento nocturno aleatorio
    evento = obtener_evento_aleatorio()
    texto_evento = evento["texto"]
    
    for clave, valor in evento["efectos"].items():
        if clave == "bebes" and valor > 0:
            estado['bebes'] += valor
            estado['dias_bebes'].extend([0] * valor)
        else:
            estado[clave] += valor

    # 3. Avance de calendario y consumo
    estado['dia'] += 1
    consumo = estado['poblacion'] + int(estado['bebes'] * 1.5)
    estado['suministros'] -= consumo

    # Crecimiento de los bebés (pasan a adultos tras 15 días)
    nuevos_dias_bebes = []
    bebes_crecidos = 0
    for dias in estado['dias_bebes']:
        dias_actualizados = dias + 1
        if dias_actualizados >= 15:
            bebes_crecidos += 1
        else:
            nuevos_dias_bebes.append(dias_actualizados)
            
    if bebes_crecidos > 0:
        estado['bebes'] -= bebes_crecidos
        estado['poblacion'] += bebes_crecidos
        
    estado['dias_bebes'] = nuevos_dias_bebes

    # 4. Límites de variables
    estado['suministros'] = max(0, min(100, estado['suministros']))
    estado['barricadas'] = max(0, min(100, estado['barricadas']))
    estado['moral'] = max(0, min(100, estado['moral']))
    estado['poblacion'] = max(0, estado['poblacion'])
    estado['bebes'] = max(0, estado['bebes'])

    return estado, resumen_decision, texto_evento

def comprobar_game_over(estado):
    if estado['poblacion'] <= 0:
        return True, "💀 **SIN SOBREVIVIENTES:** El último defensor ha caído. La aldea ha quedado en completo silencio."
    elif estado['barricadas'] <= 0:
        return True, "💥 **BARRICADAS DESTRUIDAS:** El perímetro se derrumbó. Una horda combinada invadió el refugio."
    elif estado['suministros'] <= 0 and estado['moral'] <= 10:
        return True, "🥀 **COLAPSO Y HAMBRUNA:** Sin comida ni agua, la desesperación provocó un motín final."
    return False, ""

# ==============================================================================
# 5. PUBLICACIÓN DE MENSAJES EN MASTODON
# ==============================================================================

def publicar_informe_diario(mastodon, estado, resumen_decision, texto_evento):
    mensaje = (
        f"🏚️ **ALDEA ATRINCHERADA** — Día {estado['dia']}\n\n"
        f"📋 **Ayer:** {resumen_decision}\n"
        f"🌃 **Noche:** {texto_evento}\n\n"
        f"👥 Población: {estado['poblacion']} supervivientes\n"
        f"🍼 Bebés: {estado['bebes']}\n"
        f"🍞 Suministros: {estado['suministros']}% {'⚠️' if estado['suministros'] < 30 else ''}\n"
        f"🛡️ Barricadas: {estado['barricadas']}% {'⚠️' if estado['barricadas'] < 30 else ''}\n"
        f"🔥 Moral: {estado['moral']}%\n\n"
        f"❓ **¿En qué debe centrarse la comunidad hoy?**"
    )
    
    opciones = [
        "📦 Saquear el supermercado",
        "🔨 Reforzar las barricadas",
        "🎯 Patrullar el perímetro"
    ]
    
    poll = mastodon.make_poll(options=opciones, expires_in=86400)
    mastodon.status_post(status=mensaje, poll=poll)
    print(f"✅ ¡Día {estado['dia']} publicado con éxito!")

def publicar_game_over(mastodon, estado, motivo):
    dias_sobrevividos = estado['dia']
    mensaje_derrota = (
        f"☠️ **FIN DE LA PARTIDA — GAME OVER** ☠️\n\n"
        f"{motivo}\n\n"
        f"📊 **Récord del refugio:**\n"
        f"🗓️ Días sobrevividos: {dias_sobrevividos}\n"
        f"👥 Población final: {estado['poblacion']}\n\n"
        f"🔄 La aldea se ha perdido para siempre. En la próxima ejecución comenzará la historia de un nuevo grupo."
    )
    mastodon.status_post(status=mensaje_derrota)
    print(f"💀 Game Over publicado. La aldea resistió {dias_sobrevividos} días.")
    guardar_estado(ESTADO_INICIAL)

# ==============================================================================
# 6. PUNTO DE ENTRADA PRINCIPAL
# ==============================================================================

def ejecutar_bot():
    mastodon = Mastodon(
        access_token=ACCESS_TOKEN,
        api_base_url=API_BASE_URL
    )
    
    # 1. Cargar estado actual de la aldea
    estado = cargar_estado()
    
    # 2. Consultar encuesta ganadora previa
    opcion_ganadora = obtener_opcion_ganadora(mastodon)
    
    # 3. Procesar día actual
    estado, resumen_decision, texto_evento = procesar_dia(estado, opcion_ganadora)
    
    # 4. Verificar derrota o publicar el nuevo día
    derrota, motivo = comprobar_game_over(estado)
    if derrota:
        publicar_game_over(mastodon, estado, motivo)
    else:
        guardar_estado(estado)
        publicar_informe_diario(mastodon, estado, resumen_decision, texto_evento)

if __name__ == "__main__":
    ejecutar_bot()
