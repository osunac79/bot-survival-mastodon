import os
import json
import random
from mastodon import Mastodon

# ==========================================
# CONFIGURACIÓN Y CLIENTE MASTODON
# ==========================================

MASTODON_TOKEN = os.environ.get("MASTODON_TOKEN")
MASTODON_BASE_URL = os.environ.get("MASTODON_BASE_URL", "https://mastodon.social")

def obtener_cliente_mastodon():
    if not MASTODON_TOKEN:
        raise ValueError("No se encontró la variable de entorno MASTODON_TOKEN")
    return Mastodon(
        access_token=MASTODON_TOKEN,
        api_base_url=MASTODON_BASE_URL
    )

# ==========================================
# BIBLIOTECA DE EVENTOS NOCTURNOS (40 VARIANTES)
# ==========================================

EVENTOS_FORTUNA = [
    {
        "texto": "🌃 Noche: A medianoche, las vigías detectaron sombras cerca del portón sur. Resultó ser una pequeña caravana de mercaderes errantes buscando refugio contra el frío. A cambio de pernoctar bajo nuestro perímetro, han compartido suministros médicos y enlatados antes de partir al amanecer.",
        "efectos": {"suministros": 15, "moral": 5}
    },
    {
        "texto": "🌃 Noche: La patrulla nocturna encontró un camión militar volcado en la hondonada del arroyo. Aunque la cabina estaba destrozada, la caja trasera permanecía sellada y llena de raciones de combate intactas. Un hallazgo providencial para el refugio.",
        "efectos": {"suministros": 20}
    },
    {
        "texto": "🌃 Noche: Durante la madrugada, una suave lluvia limpió el aire pesado del asentamiento. Los supervivientes improvisaron canalones para recoger agua limpia y la sensación de alivio colectivo ha devuelto la esperanza a la comunidad.",
        "efectos": {"moral": 15, "suministros": 5}
    },
    {
        "texto": "🌃 Noche: Un perro mestizo apareció rascando la puerta principal. Llevaba enganchada al collar una bolsa con medicinas esenciales y mapas marcados con zonas seguras. Tras alimentarlo, la criatura se ha quedado a hacer guardia con los vigías.",
        "efectos": {"suministros": 10, "moral": 10}
    },
    {
        "texto": "🌃 Noche: Los exploradores nocturnos lograron reactivar un pequeño generador diésel abandonado en la vieja estación de servicio. La luz cálida iluminó el patio central por primera vez en meses, infundiendo un renovado espíritu de camaradería.",
        "efectos": {"moral": 20}
    },
    {
        "texto": "🌃 Noche: Una familia de supervivientes exhaustos llegó pidiendo auxilio tras días huyendo de los infectados. Entre sus pertenencias traían semillas y herramientas de carpintería que reforzarán las defensas y la despensa de la aldea.",
        "efectos": {"poblacion": 3, "suministros": 10, "barricadas": 5}
    },
    {
        "texto": "🌃 Noche: Un viento favorable alejó hacia el este a un numeroso grupo de caminantes que se dirigía directamente hacia el perímetro. La noche transcurrió en una calma serena que permitió descansar profundamente a las patrullas exhaustas.",
        "efectos": {"moral": 10}
    },
    {
        "texto": "🌃 Noche: Mientras reforzaban el sótano del edificio central, los guardias descubrieron un antiguo almacén olvidado tras un tabique de yeso. Mantenía alimentos en conserva y mantas térmicas en perfecto estado de conservación.",
        "efectos": {"suministros": 15, "moral": 5}
    }
]

EVENTOS_NEUTROS = [
    {
        "texto": "🌃 Noche: Una densa niebla dominó el valle de medianoche a amanecer. Aunque la visibilidad descendió a cero y la tensión se palpaba en cada puesto de guardia, no se registraron aproximaciones ni incidentes cerca del muro.",
        "efectos": {}
    },
    {
        "texto": "🌃 Noche: El eco de disparos lejanos retumbó en la montaña durante horas. Las torres de vigilancia se mantuvieron en alerta máxima con las armas amartilladas, pero la amenaza no llegó a aproximarse al refugio.",
        "efectos": {}
    },
    {
        "texto": "🌃 Noche: Una manada de perros salvajes merodeó el perímetro exterior atraída por el olor a comida. Tras unas horas de ladridos y tensión contenida en la empalizada, los animales continuaron su marcha hacia la ciudad.",
        "efectos": {}
    },
    {
        "texto": "🌃 Noche: El crujido constante de las vigas viejas por el viento nocturno mantuvo en vela a varios residentes del sector norte. Afortunadamente, solo fue un susto causado por la tormenta distante.",
        "efectos": {}
    },
    {
        "texto": "🌃 Noche: Un dron desconocido sobrevoló el recinto a gran altura antes de perderse en el horizonte nocturno. Su origen sigue siendo un misterio, pero no se percibió ningún movimiento hostil en los alrededores.",
        "efectos": {}
    },
    {
        "texto": "🌃 Noche: La patrulla detectó las siluetas de un par de infectados solitarios atrapados entre los arbustos lejanos. Dado que no representaban un peligro inmediato, los vigías prefirieron guardar munición y no hacer ruido.",
        "efectos": {}
    },
    {
        "texto": "🌃 Noche: Noche rutinaria y tranquila en la colonia. Los turnos de guardia se cumplieron sin novedades y los cocineros pudieron preparar el desayuno a primera hora sin sobresaltos.",
        "efectos": {}
    },
    {
        "texto": "🌃 Noche: Un grupo de sombras cruzó el bosque a varios cientos de metros. Parecía una patrulla errante de saqueadores, pero afortunadamente no advirtieron la presencia de nuestra empalizada en la oscuridad.",
        "efectos": {}
    },
    {
        "texto": "🌃 Noche: El frío fue especialmente severo durante la madrugada. Se consumieron más troncos de los habituales en las hogueras de guardia, pero todos los residentes amanecieron a salvo y sin congelaciones.",
        "efectos": {}
    },
    {
        "texto": "🌃 Noche: Una señal estática cruzó brevemente la frecuencia de la radio de la torre de control. Aunque intentaron responder, nadie contestó al otro lado. El silencio volvió a dominar la noche.",
        "efectos": {}
    },
    {
        "texto": "🌃 Noche: Se avistaron bengalas de emergencia a varios kilómetros al sur. Tras un breve debate en la guardia central, se decidió mantener la posición defensiva y no arriesgar vidas en una incursión a ciegas.",
        "efectos": {}
    },
    {
        "texto": "🌃 Noche: El crujido de las ramas secas provocó la falsa alarma en la puerta este. Resultó ser solo un ciervo desorientado que huyó espantado en cuanto los focos lo enfocaron.",
        "efectos": {}
    }
]

EVENTOS_MODERADOS = [
    {
        "texto": "🌃 Noche: Fuertes rachas de viento azotaron la empalizada oeste durante toda la madrugada. Varias planchas de chapa y tablones cedieron ante la fuerza del aire, obligando al equipo de mantenimiento a improvisar arreglos de urgencia.",
        "efectos": {"barricadas": -10}
    },
    {
        "texto": "🌃 Noche: Un grupo reducido de infectados impactó contra el portón inferior. Aunque los guardias acabaron rápidamente con la amenaza a punta de lanza, la puerta sufrió desencajes que habrá que reparar.",
        "efectos": {"barricadas": -15}
    },
    {
        "texto": "🌃 Noche: La humedad extrema y las filtraciones de agua en la bodega principal echaron a perder varios sacos de grano y cajas de suministros secos que no estaban bien elevados del suelo.",
        "efectos": {"suministros": -10}
    },
    {
        "texto": "🌃 Noche: Se desató una acalorada discusión en el comedor comunitario a cuenta del reparto de las raciones. La tensión acumulada incendió los ánimos y dejó un ambiente enrarecido y pesimista entre la población.",
        "efectos": {"moral": -15}
    },
    {
        "texto": "🌃 Noche: Una plaga de roedores infestó la despensa auxiliar durante la noche. Antes de que los guardias lograran contenerla, echaron a perder una parte considerable de los víveres frescos.",
        "efectos": {"suministros": -15}
    },
    {
        "texto": "🌃 Noche: Una descarga eléctrica por una tormenta seca quemó el cableado del sistema de focos del perímetro. La oscuridad obligó a duplicar los turnos de guardia, agotando físicamente a los vigías.",
        "efectos": {"moral": -10, "barricadas": -5}
    },
    {
        "texto": "🌃 Noche: Un pequeño brote de fiebre estacional afectó a varios residentes. Aunque no es el virus, el consumo de medicamentos para bajar la fiebre ha mermado el botiquín del refugio.",
        "efectos": {"suministros": -10, "moral": -5}
    },
    {
        "texto": "🌃 Noche: Durante una patrulla exterior, dos guardias cayeron en una zanja oculta por la vegetación. Sufrieron torceduras leves y requirieron asistencia médica urgente antes de volver a su puesto.",
        "efectos": {"suministros": -5, "moral": -5}
    },
    {
        "texto": "🌃 Noche: Un disparo accidental de un centinela nervioso despertó a todo el campamento a mitad de la noche. El susto no provocó heridos, pero el cansancio y el pánico mermaron el estado de ánimo general.",
        "efectos": {"moral": -10}
    },
    {
        "texto": "🌃 Noche: La cerca exterior de espinos cedió tras el peso acumulado de varios cadáveres de la semana pasada. La zona ha quedado expuesta a futuras incursiones hasta que se pueda limpiar.",
        "efectos": {"barricadas": -10}
    },
    {
        "texto": "🌃 Noche: El congelador principal sufrió un fallo en el termostato a medianoche. Varias reservas de carne conservada se echaron a perder antes de que los cocineros se dieran cuenta al amanecer.",
        "efectos": {"suministros": -12}
    },
    {
        "texto": "🌃 Noche: Un pequeño incendio provocado por una estufa defectuosa destruyó una de las tiendas de campaña del patio. La rápida intervención de los vecinos evitó tragedias, pero se perdieron pertenencias clave.",
        "efectos": {"moral": -10, "suministros": -5}
    }
]

EVENTOS_GRAVES = [
    {
        "texto": "🌃 Noche: Una numerosa horda atraída por el ruido colisionó bruscamente contra el sector este de la empalizada. Tras horas de combate desesperado a oscuras, se logró repeler el ataque, pero la estructura ha quedado destrozada.",
        "efectos": {"barricadas": -25, "suministros": -10, "moral": -10}
    },
    {
        "texto": "🌃 Noche: Un grupo organizado de saqueadores fuertemente armados intentó asaltar la puerta principal. El intercambio de disparos se prolongó hasta el alba; aunque la aldea resistió, sufrimos bajas humanas e irreparable daños defensivos.",
        "efectos": {"poblacion": -2, "barricadas": -20, "suministros": -10}
    },
    {
        "texto": "🌃 Noche: Un incendio voraz se declaró en el almacén de provisiones secundario por un cortocircuito. A pesar del esfuerzo desesperado de todos los supervivientes haciendo cadena con cubos de agua, gran parte de los víveres quedaron reducidos a cenizas.",
        "efectos": {"suministros": -30, "moral": -15}
    },
    {
        "texto": "🌃 Noche: Un derrumbe en la zanja defensiva del flanco norte permitió que un grupo de infectados se colara silenciosamente en el refugio. La sangrienta escaramuza nocturna terminó con víctimas mortales y un profundo trauma colectivo.",
        "efectos": {"poblacion": -3, "moral": -20, "barricadas": -15}
    },
    {
        "texto": "🌃 Noche: Un brote severo de disentería debido a agua contaminada afectó gravemente al campamento durante la madrugada. El consumo masivo de suero y medicamentos agotó la reserva de medicinas de urgencia.",
        "efectos": {"suministros": -25, "poblacion": -1, "moral": -15}
    },
    {
        "texto": "🌃 Noche: Un grupo de residentes desesperados intentó huir de la colonia al amparo de la noche llevándose consigo varios sacos de raciones y herramientas clave. El robo y la traición han dejado un clima desolador.",
        "efectos": {"poblacion": -2, "suministros": -20, "moral": -20}
    },
    {
        "texto": "🌃 Noche: Un vehículo fuera de control conducido por infectados o desesperados se estrelló violentamente contra la puerta principal, abriendo una brecha masiva. Reparar el destrozo requerirá semanas de trabajo duro.",
        "efectos": {"barricadas": -35, "moral": -10}
    },
    {
        "texto": "🌃 Noche: La combinación de una tormenta feroz y el empuje constante de los muertos colapsó el muro de contención trasero. Los supervivientes tuvieron que combatir bajo un aguacero helado para evitar ser masacrados.",
        "efectos": {"barricadas": -30, "suministros": -10, "moral": -15}
    }
]

# ==========================================
# OPCIONES DE ENCUESTA RECURRENTES
# ==========================================

OPCIONES_ENCUESTA = [
    {
        "pregunta": "¿Qué prioridad le damos a las tareas de hoy?",
        "opciones": [
            {"texto": "🥖 Buscar suministros en el pueblo", "efectos": {"suministros": 15, "barricadas": -5}},
            {"texto": "🧱 Reforzar las barricadas del norte", "efectos": {"barricadas": 20, "suministros": -5}},
            {"texto": "🕯️ Organizar una hoguera comunitaria", "efectos": {"moral": 15, "suministros": -5}},
            {"texto": "📻 Rastrear frecuencias de radio", "efectos": {"moral": 5, "poblacion": 1}}
        ]
    },
    {
        "pregunta": "Se ha avistado un convoy abandonado a 2 km. ¿Cómo procedemos?",
        "opciones": [
            {"texto": "🚚 Enviar equipo pesado de extracción", "efectos": {"suministros": 25, "barricadas": -10}},
            {"texto": "👁️ Enviar solo a dos exploradores sigilosos", "efectos": {"suministros": 10, "moral": 5}},
            {"texto": "🚫 Ignorarlo por seguridad", "efectos": {"moral": -5}}
        ]
    },
    {
        "pregunta": "Un grupo de desconocidos pide refugio en la entrada. ¿Qué decisión tomamos?",
        "opciones": [
            {"texto": "👥 Acogerlos tras desarmarlos", "efectos": {"poblacion": 3, "suministros": -10, "moral": 5}},
            {"texto": "📦 Darles comida y pedirles que se vayan", "efectos": {"suministros": -5, "moral": 5}},
            {"texto": "🚪 Rechazarlos tajantemente", "efectos": {"moral": -10, "barricadas": 5}}
        ]
    }
]

# ==========================================
# GESTIÓN DE ARCHIVO DE ESTADO
# ==========================================

FICHERO_ESTADO = "estado.json"

def cargar_estado():
    if not os.path.exists(FICHERO_ESTADO):
        return {
            "dia": 1,
            "poblacion": 25,
            "suministros": 100,
            "barricadas": 100,
            "moral": 100,
            "historial_eventos": [],
            "ultima_encuesta_id": None,
            "opciones_ultima_encuesta": []
        }
    with open(FICHERO_ESTADO, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_estado(estado):
    with open(FICHERO_ESTADO, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=2)

# ==========================================
# LÓGICA PRINCIPAL DEL JUEGO
# ==========================================

def procesar_evento_nocturno(estado):
    dado = random.randint(1, 100)

    if dado <= 10:
        evento = random.choice(EVENTOS_FORTUNA)
    elif dado <= 50:
        evento = random.choice(EVENTOS_NEUTROS)
    elif dado <= 80:
        evento = random.choice(EVENTOS_MODERADOS)
    else:
        evento = random.choice(EVENTOS_GRAVES)

    efectos = evento.get("efectos", {})
    for clave, cambio in efectos.items():
        if clave in estado:
            estado[clave] += cambio
            if clave in ["suministros", "barricadas", "moral"]:
                estado[clave] = max(0, min(100, estado[clave]))
            elif clave == "poblacion":
                estado[clave] = max(0, estado[clave])

    return evento["texto"]

def resolver_encuesta_anterior(client, estado):
    if not estado.get("ultima_encuesta_id") or not estado.get("opciones_ultima_encuesta"):
        return ""

    try:
        status = client.status(estado["ultima_encuesta_id"])
        poll = status.get("poll")
        
        if not poll:
            return ""

        votos = [option["votes_count"] for option in poll["options"]]
        max_votos = max(votos)
        
        if max_votos == 0:
            ganadora_idx = random.randint(0, len(poll["options"]) - 1)
        else:
            ganadora_idx = votos.index(max_votos)

        opcion_elegida = estado["opciones_ultima_encuesta"][ganadora_idx]
        efectos = opcion_elegida.get("efectos", {})

        for clave, cambio in efectos.items():
            if clave in estado:
                estado[clave] += cambio
                if clave in ["suministros", "barricadas", "moral"]:
                    estado[clave] = max(0, min(100, estado[clave]))
                elif clave == "poblacion":
                    estado[clave] = max(0, estado[clave])

        return f"📊 **Resolución decisión anterior:** Ganó la opción '{opcion_elegida['texto']}' con {votos[ganadora_idx]} voto(s).\n\n"
    except Exception as e:
        print(f"Error al leer la encuesta anterior: {e}")
        return ""

def main():
    client = obtener_cliente_mastodon()
    estado = cargar_estado()

    # 1. Comprobar condición de Game Over previa
    if estado["poblacion"] <= 0 or estado["suministros"] <= 0 or estado["moral"] <= 0:
        texto_game_over = (
            f"💀 **GAME OVER - DÍA {estado['dia']}** 💀\n\n"
            "La aldea ha sucumbido al apocalipsis. Los suministros, la moral o la población se han agotado por completo. "
            "Los pocos supervivientes se han dispersado en la oscuridad.\n\n"
            "#ApocalipsisZombi #GameOver #MastodonBot"
        )
        client.status_post(texto_game_over)
        return

    # 2. Resolver la encuesta del día anterior
    texto_resolucion = resolver_encuesta_anterior(client, estado)

    # 3. Procesar el evento nocturno aleatorio
    texto_evento = procesar_evento_nocturno(estado)

    # 4. Seleccionar nueva encuesta para hoy
    encuesta_hoy = random.choice(OPCIONES_ENCUESTA)
    opciones_texto = [opc["texto"] for opc in encuesta_hoy["opciones"]]

    # 5. Incrementar el día
    estado["dia"] += 1

    # 6. Construir el informe diario en el post
    informe = (
        f"🧟‍♂️ **INFORME DE SUPERVIVENCIA - DÍA {estado['dia']}**\n\n"
        f"{texto_resolucion}"
        f"{texto_evento}\n\n"
        f"📋 **ESTADO DEL REFUGIO:**\n"
        f"👥 Población: {estado['poblacion']} personas\n"
        f"🥖 Suministros: {estado['suministros']}%\n"
        f"🧱 Barricadas: {estado['barricadas']}%\n"
        f"🕯️ Moral: {estado['moral']}%\n\n"
        f"❓ **DECISIÓN PARA HOY:** {encuesta_hoy['pregunta']}\n\n"
        f"#ApocalipsisZombi #Supervivencia #MastodonBot"
    )

    # 7. Publicar encuesta en Mastodon (duración 86400 segundos = 24 horas)
    poll = client.make_poll(options=opciones_texto, expires_in=86400)
    nuevo_post = client.status_post(status=informe, poll=poll)

    # 8. Actualizar IDs de seguimiento y guardar estado
    estado["ultima_encuesta_id"] = nuevo_post["id"]
    estado["opciones_ultima_encuesta"] = encuesta_hoy["opciones"]
    guardar_estado(estado)

if __name__ == "__main__":
    main()