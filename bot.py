import os
import json
import copy
import random
from mastodon import Mastodon

# ==========================================
# CONFIGURACIÓN Y CLIENTE MASTODON
# ==========================================

MASTODON_TOKEN = os.environ.get("MASTODON_TOKEN")
# "or" en lugar del valor por defecto de get(): así también funciona si el secret existe pero está vacío
MASTODON_BASE_URL = os.environ.get("MASTODON_BASE_URL") or "https://mastodon.social"
# Límite de caracteres por toot de tu instancia (500 en la mayoría). Se puede cambiar con la variable MASTODON_MAX_CHARS
LIMITE_CARACTERES = int(os.environ.get("MASTODON_MAX_CHARS") or 500)
# 23 h en lugar de 24 h: así la encuesta siempre está cerrada cuando el cron del día siguiente la lee,
# aunque GitHub retrase la ejecución unos minutos
DURACION_ENCUESTA = 23 * 3600

# --- Mecánicas de comunidad (seguidores) ---
SEGUIDORES_POR_BLOQUE = 10     # cada 10 seguidores nuevos...
POBLACION_POR_BLOQUE = 3       # ...llegan 3 supervivientes al refugio
SEGUIDORES_POR_HITO = 25       # cada 25 seguidores nuevos se alcanza un hito
MAX_SALUDOS_POR_DIA = 8        # máximo de @menciones de bienvenida por día (el resto se resume en una línea)
MAX_IDS_RECORDADOS = 300       # seguidores ya saludados que se recuerdan en estado.json


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
    },

    # --- Racionamiento y gestión de recursos ---
    {
        "pregunta": "Las reservas de comida duran cuatro días. ¿Cómo comemos hoy?",
        "opciones": [
            {"texto": "🍽️ Una comida caliente al día", "efectos": {"suministros": 10, "moral": 15}},
            {"texto": "🍞 Raciones frías y abundantes", "efectos": {"suministros": 20, "moral": -10}},
            {"texto": "🥫 Guardarlo todo para el día de la crisis", "efectos": {"suministros": 5, "moral": -15}}
        ]
    },
    {
        "pregunta": "Ha aparecido un alijo de material médico escondido. ¿Qué hacemos?",
        "opciones": [
            {"texto": "💊 Repartirlo entre los heridos", "efectos": {"suministros": 10, "poblacion": -1, "moral": 5}},
            {"texto": "🧠 Guardarlo bajo llave para emergencias", "efectos": {"suministros": 20, "moral": -5}},
            {"texto": "🤝 Devolverlo al lugar donde lo encontramos", "efectos": {"suministros": 10, "moral": 15}}
        ]
    },
    {
        "pregunta": "El pozo del patio da agua turbia. ¿Cómo seguimos bebiendo?",
        "opciones": [
            {"texto": "💧 Cavar un pozo nuevo en el monte", "efectos": {"suministros": 15, "barricadas": -5}},
            {"texto": "🧪 Hervir y filtrar el agua vieja", "efectos": {"suministros": 10, "moral": -10}},
            {"texto": "🚱 Racionar el agua al máximo", "efectos": {"suministros": 5, "moral": -15}}
        ]
    },
    {
        "pregunta": "El almacén está amontonado y no se encuentra nada. ¿Qué hacemos?",
        "opciones": [
            {"texto": "📦 Vaciarlo todo y hacer inventario", "efectos": {"suministros": 15, "moral": -10}},
            {"texto": "🏷️ Dejarlo como está, no hay tiempo", "efectos": {"suministros": 5, "moral": 5}},
            {"texto": "🛒 Ir a reponer las reservas al Pueblo", "efectos": {"suministros": 25, "barricadas": -10, "moral": -5}}
        ]
    },
    {
        "pregunta": "Un vecino guarda comida bajo su catre. ¿Qué hacemos?",
        "opciones": [
            {"texto": "⚖️ Repartirla según las necesidades", "efectos": {"suministros": 15, "poblacion": -1, "moral": -5}},
            {"texto": "🔍 Quitársela sin darle explicaciones", "efectos": {"suministros": 20, "moral": -20}},
            {"texto": "😶 Dejarlo como está y no decir nada", "efectos": {"suministros": 10, "moral": 10}}
        ]
    },
    {
        "pregunta": "El gasoil del generador se acaba. ¿Qué apagamos?",
        "opciones": [
            {"texto": "💡 Apagar los focos del perímetro", "efectos": {"barricadas": -15, "suministros": 15}},
            {"texto": "📻 Dejar la radio y apagar lo demás", "efectos": {"moral": 10, "suministros": 5, "barricadas": -5}},
            {"texto": "🔇 Apagar todo hasta nuevo aviso", "efectos": {"suministros": 20, "moral": -15}}
        ]
    },

    # --- Dilemas sociales y de comunidad ---
    {
        "pregunta": "Un grupo interno quiere echar a los recién llegados. ¿Qué dices?",
        "opciones": [
            {"texto": "🗳️ Votamos todos y respetamos el fallo", "efectos": {"moral": 15, "poblacion": -2}},
            {"texto": "🗣️ Que la asamblea lo discuta primero", "efectos": {"moral": 10, "suministros": -5}},
            {"texto": "✊ Defender los muros a cualquier precio", "efectos": {"barricadas": 20, "moral": -20, "poblacion": -2}}
        ]
    },
    {
        "pregunta": "El centinela lleva tres noches sin dormir. ¿Qué hacemos?",
        "opciones": [
            {"texto": "😴 Relevarlo con quien sea", "efectos": {"moral": 15, "barricadas": -5}},
            {"texto": "☕ Que aguante un par de noches más", "efectos": {"barricadas": 5, "moral": -15}},
            {"texto": "🛌 Montar guardias dobles de día", "efectos": {"suministros": -10, "moral": 10, "barricadas": 5}}
        ]
    },
    {
        "pregunta": "Hay fiebre alta en el módulo de los niños. ¿Qué hacemos?",
        "opciones": [
            {"texto": "🚧 Aislar por completo el módulo", "efectos": {"poblacion": -1, "moral": 10, "suministros": -5}},
            {"texto": "💉 Tratarles aquí con los pocos que quedan", "efectos": {"suministros": 10, "poblacion": -2, "moral": -15}},
            {"texto": "🤫 No decir nada y esperar a ver qué pasa", "efectos": {"poblacion": -3, "moral": -10}}
        ]
    },
    {
        "pregunta": "Alguien propone repartir las armas a partes iguales. ¿Qué haces?",
        "opciones": [
            {"texto": "✅ Repartir las armas a partes iguales", "efectos": {"moral": 20, "barricadas": -15}},
            {"texto": "🛡️ Mantener el arsenal en la guardia", "efectos": {"barricadas": 15, "moral": -10}},
            {"texto": "📣 Someter la propuesta a asamblea", "efectos": {"moral": 5, "suministros": -5}}
        ]
    },
    {
        "pregunta": "Media aldea se quiere ir hacia la ciudad. ¿Qué decide el refugio?",
        "opciones": [
            {"texto": "🗳️ Dejarlos marchar en libertad", "efectos": {"moral": 15, "suministros": -15}},
            {"texto": "🚫 Prohibir la salida a todo el mundo", "efectos": {"poblacion": -2, "moral": -15, "barricadas": 5}},
            {"texto": "🩹 Hacer una expedición con ellos", "efectos": {"poblacion": -4, "moral": -20, "suministros": 10}}
        ]
    },

    # --- Exploración y expediciones ---
    {
        "pregunta": "Una baliza se enciende al sur, en mitad de la noche. ¿Qué hacemos?",
        "opciones": [
            {"texto": "🚗 Ir con el vehículo y bien armados", "efectos": {"suministros": 30, "barricadas": -15}},
            {"texto": "🚶 Ir a pie y sin hacer ruido", "efectos": {"suministros": 10, "poblacion": -1, "moral": 5}},
            {"texto": "📡 Apuntar las coordenadas y seguir con lo nuestro", "efectos": {"moral": 5, "barricadas": 5}}
        ]
    },
    {
        "pregunta": "Una patrulla ha encontrado una granja con el silo lleno. ¿Cómo lo explotamos?",
        "opciones": [
            {"texto": "🐂 Llevarnos los animales", "efectos": {"suministros": 15, "poblacion": 2, "moral": 5}},
            {"texto": "🌾 Vaciar el silo hasta el fondo", "efectos": {"suministros": 30, "barricadas": -10, "moral": -5}},
            {"texto": "🔑 Quedarnos con la llave y volver luego", "efectos": {"suministros": 5, "moral": 10}}
        ]
    },
    {
        "pregunta": "Hay un mapa de una ruta de suministros en un coche abandonado. ¿Qué hacemos?",
        "opciones": [
            {"texto": "🗺️ Seguirla en convoy protegido", "efectos": {"suministros": 25, "barricadas": -10}},
            {"texto": "🧭 Mandar a un par de exploradores", "efectos": {"suministros": 15, "poblacion": -1}},
            {"texto": "🤥 Desconfiar de una ruta tan fácil", "efectos": {"suministros": 5, "moral": -5}}
        ]
    },
    {
        "pregunta": "Una horda bloquea el puente del río. ¿Pasamos o damos media vuelta?",
        "opciones": [
            {"texto": "🛡️ Cruzar con las barricadas montadas", "efectos": {"suministros": 20, "barricadas": -10}},
            {"texto": "🏃 Cruzar a paso ligero y rápido", "efectos": {"suministros": 30, "poblacion": -3}},
            {"texto": "🔙 Dar media vuelta y buscar otro puente", "efectos": {"suministros": 5, "moral": -10, "barricadas": 5}}
        ]
    },
    {
        "pregunta": "La patrulla vuelve con un rehén infectado. ¿Qué hacemos con él?",
        "opciones": [
            {"texto": "💊 Tratarlo y aislarlo en la enfermería", "efectos": {"suministros": -15, "poblacion": -1, "moral": 10}},
            {"texto": "🔫 Rematarlo para evitar el riesgo", "efectos": {"moral": -15, "barricadas": 10}},
            {"texto": "🚪 Echarlo del refugio y cerrar la puerta", "efectos": {"poblacion": -2, "moral": -5}}
        ]
    },

    # --- Decisiones oscuras y épicas ---
    {
        "pregunta": "Un drone militar lleva días sobrevolando el refugio. ¿Qué hacemos?",
        "opciones": [
            {"texto": "📡 Responder a sus señales", "efectos": {"poblacion": 5, "suministros": 20, "moral": -5}},
            {"texto": "🕵️ Apagar todo y hacerse el muerto", "efectos": {"moral": -5, "barricadas": 5}},
            {"texto": "💣 Dispararle antes de que avise a nadie", "efectos": {"poblacion": -3, "barricadas": -15, "moral": 10}}
        ]
    },
    {
        "pregunta": "Una empresa militar ofrece comprar al asentamiento entero. ¿Aceptamos?",
        "opciones": [
            {"texto": "💼 Firmar: contando, la aldea sobrevive", "efectos": {"suministros": 35, "moral": -20, "poblacion": -2}},
            {"texto": "⚖️ Negociar mejores condiciones", "efectos": {"suministros": 20, "moral": -10, "poblacion": -1}},
            {"texto": "🏳️ Esconderse y no dar señales de vida", "efectos": {"moral": 15, "barricadas": -10}}
        ]
    },
    {
        "pregunta": "Un grupo armado exige el mapa de los refugios cercanos. ¿Negociamos?",
        "opciones": [
            {"texto": "🗺️ Entregar el mapa a cambio de víveres", "efectos": {"suministros": 25, "poblacion": -1, "moral": -15}},
            {"texto": "🎭 Entregar un mapa falso y rezar", "efectos": {"suministros": -10, "moral": 5, "barricadas": -5}},
            {"texto": "🔥 Atacar antes de que se repongan", "efectos": {"barricadas": 15, "suministros": -10, "moral": 10}}
        ]
    },
    {
        "pregunta": "Han encontrado un laboratorio abandonado en la ciudad. ¿Qué hacemos?",
        "opciones": [
            {"texto": "🔬 Buscar una cura entre los hallazgos", "efectos": {"poblacion": 3, "suministros": -10, "moral": 10}},
            {"texto": "🔥 Prenderle fuego y no mirar atrás", "efectos": {"barricadas": 10, "suministros": 5, "moral": -10}},
            {"texto": "🎒 Llevarnos el material y cerrar la puerta", "efectos": {"suministros": 20, "barricadas": -5, "moral": -5}}
        ]
    }
]

# ==========================================
# HITOS DE LA COMUNIDAD (cada 25 seguidores nuevos)
# ==========================================
# Clave = número de hito (1 = 25 seguidores nuevos, 2 = 50, 3 = 75...).
# Cada hito aplica sus efectos al refugio y, si trae "encuesta", la añade a las decisiones posibles.
# Pasado el último hito, cada 25 seguidores más se usa HITO_GENERICO.

HITOS = {
    1: {
        "titulo": "🩺 Llega un MÉDICO al refugio",
        "texto": "Con su ayuda los heridos se recuperan antes y la gente respira más tranquila.",
        "efectos": {"moral": 10, "poblacion": 1},
        "encuesta": {
            "pregunta": "El médico necesita material para atender a los heridos. ¿Qué hacemos?",
            "opciones": [
                {"texto": "🏥 Montar una enfermería", "efectos": {"moral": 15, "suministros": -10}},
                {"texto": "💊 Buscar medicinas en la farmacia", "efectos": {"suministros": 15, "poblacion": -1}},
                {"texto": "🩹 Improvisar con lo que hay", "efectos": {"moral": -5, "suministros": 5}}
            ]
        }
    },
    2: {
        "titulo": "⚡ El refugio consigue un GENERADOR",
        "texto": "Por fin hay luz por las noches y la radio funciona sin parar.",
        "efectos": {"moral": 10, "barricadas": 5},
        "encuesta": {
            "pregunta": "El generador gasta mucho combustible. ¿Cómo lo usamos?",
            "opciones": [
                {"texto": "💡 Luz toda la noche", "efectos": {"moral": 15, "suministros": -10}},
                {"texto": "📻 Solo para la radio", "efectos": {"moral": 5, "poblacion": 1}},
                {"texto": "🔌 Apagarlo para ahorrar", "efectos": {"suministros": 10, "moral": -10}}
            ]
        }
    },
    3: {
        "titulo": "🔭 Se levanta una TORRE DE VIGILANCIA",
        "texto": "Los vigías ven venir las hordas desde lejos y las barricadas aguantan mejor.",
        "efectos": {"barricadas": 20},
        "encuesta": {
            "pregunta": "¿Cómo organizamos las guardias en la torre?",
            "opciones": [
                {"texto": "🌙 Doble turno de noche", "efectos": {"barricadas": 10, "moral": -10}},
                {"texto": "🔄 Turnos rotativos para todos", "efectos": {"moral": 10, "barricadas": 5}},
                {"texto": "🎯 Solo los mejores tiradores", "efectos": {"barricadas": 15, "moral": -5}}
            ]
        }
    },
    4: {
        "titulo": "📡 Llega un CONVOY DE AYUDA (¡hito épico!)",
        "texto": "Una señal de radio guía hasta el refugio a un convoy cargado de víveres y supervivientes.",
        "efectos": {"poblacion": 5, "suministros": 25, "moral": 15},
        "encuesta": {
            "pregunta": "El jefe del convoy propone una alianza con otros refugios. ¿Qué respondemos?",
            "opciones": [
                {"texto": "🤝 Aceptar la alianza", "efectos": {"poblacion": 3, "suministros": 15, "moral": 10}},
                {"texto": "📦 Solo intercambiar víveres", "efectos": {"suministros": 20, "moral": 5}},
                {"texto": "🔒 Mantenernos aislados", "efectos": {"barricadas": 10, "moral": -5}}
            ]
        }
    },
    5: {
        "titulo": "🌱 Nace un HUERTO en el patio",
        "texto": "Las primeras verduras ya crecen y el grupo tiene algo que cuidar entre todos.",
        "efectos": {"suministros": 15, "moral": 5},
        "encuesta": {
            "pregunta": "El huerto necesita agua y vigilancia. ¿Qué prioridad le damos?",
            "opciones": [
                {"texto": "💧 Recoger agua de lluvia", "efectos": {"suministros": 15}},
                {"texto": "🌿 Que todos ayuden a cuidarlo", "efectos": {"suministros": 20, "barricadas": -5}},
                {"texto": "🚧 Cercarlo contra saqueadores", "efectos": {"barricadas": 10, "suministros": 5}}
            ]
        }
    },
    6: {
        "titulo": "🔧 Se abre un TALLER de refuerzos",
        "texto": "Con herramientas y chatarra, el refugio fabrica defensas mucho más sólidas.",
        "efectos": {"barricadas": 20, "moral": 5},
        "encuesta": {
            "pregunta": "¿Qué fabricamos primero en el taller?",
            "opciones": [
                {"texto": "🪤 Trampas para las hordas", "efectos": {"barricadas": 15, "suministros": -5}},
                {"texto": "🚪 Puertas blindadas", "efectos": {"barricadas": 25, "suministros": -10}},
                {"texto": "🛠️ Herramientas para todos", "efectos": {"moral": 10, "suministros": -5}}
            ]
        }
    },
    7: {
        "titulo": "🐕 Un PERRO GUARDIÁN se une al grupo",
        "texto": "Avisa de los intrusos antes que nadie y es la mascota más querida del refugio.",
        "efectos": {"moral": 10, "barricadas": 5},
        "encuesta": {
            "pregunta": "El perro huele algo raro en el bosque. ¿Le seguimos?",
            "opciones": [
                {"texto": "🌲 Seguirlo con una patrulla", "efectos": {"suministros": 20, "barricadas": -5}},
                {"texto": "🐾 Dejar que vaya solo", "efectos": {"suministros": 10, "moral": 5}},
                {"texto": "🛑 Mantenerlo en el refugio", "efectos": {"moral": 5}}
            ]
        }
    },
    8: {
        "titulo": "🏆 El refugio se convierte en LEYENDA",
        "texto": "Otros supervivientes hablan de este lugar por radio y todos quieren venir.",
        "efectos": {"poblacion": 5, "suministros": 20, "barricadas": 20, "moral": 20},
        "encuesta": {
            "pregunta": "Llegan decenas de refugiados. ¿Ampliamos el refugio?",
            "opciones": [
                {"texto": "🏗️ Ampliar con un segundo muro", "efectos": {"poblacion": 5, "barricadas": 10, "suministros": -15}},
                {"texto": "📋 Admitir solo por turnos", "efectos": {"poblacion": 2, "moral": 5}},
                {"texto": "🚷 Cerrar las puertas", "efectos": {"barricadas": 10, "moral": -10}}
            ]
        }
    }
}

HITO_GENERICO = {
    "titulo": "📦 La comunidad llega con un CARGAMENTO",
    "texto": "El refugio sigue creciendo y los recién llegados traen provisiones para todos.",
    "efectos": {"suministros": 15, "moral": 10, "poblacion": 2}
}

# ==========================================
# BIENVENIDAS A NUEVOS SEGUIDORES (20 VARIANTES)
# ==========================================
# {u} se sustituye por la @mención del nuevo seguidor (así le llega la notificación).

SALUDOS = [
    "🧟 {u} ha cruzado el cementerio sin que le mordieran y llega al refugio. ¡Bienvenido, superviviente!",
    "🔦 {u} aparece en la puerta con una linterna y cara de cansancio. ¡Pasa, que hay sopa caliente!",
    "🥫 {u} trae latas de conserva. Desde hoy es oficialmente nuestro héroe. ¡Bienvenido!",
    "🚪 Alguien llama a la puerta... ¡es {u}! Abrimos las barricadas un momento para dejarle entrar.",
    "🩹 {u} llega cojeando pero vivo. Nos viene bien otro par de manos. ¡Bienvenido al refugio!",
    "🔥 {u} se sienta junto a la hoguera del refugio. Un superviviente más en el grupo. ¡Bienvenido!",
    "🎒 {u} entra con la mochila a medio vaciar y una sonrisa. ¡Un nuevo vecino en pleno apocalipsis!",
    "🛡️ {u} se ofrece para hacer guardia esta noche. ¡Menudo valiente! Bienvenido al grupo.",
    "📻 La radio crepita y avisa: {u} ya está en la puerta. ¡Bienvenido, te esperábamos!",
    "🧱 {u} ayuda a reforzar las barricadas nada más llegar. ¡Así da gusto! Bienvenido.",
    "🌙 Entre las sombras aparece {u}. No es un zombi, ¡es un nuevo superviviente! Bienvenido.",
    "🍞 {u} ha encontrado pan en una tienda abandonada y lo comparte con todos. ¡Gracias y bienvenido!",
    "🧭 {u} se perdió por el bosque pero ha encontrado el refugio. ¡Ya estás a salvo!",
    "🕯️ {u} enciende una vela por los que no llegaron y se une a nosotros. Bienvenido al refugio.",
    "🏃 {u} llega corriendo con una horda detrás. ¡Cerrad la puerta! ...Bienvenido, superviviente.",
    "🔧 {u} sabe arreglar generadores y radios. ¡Menuda suerte que se una a nosotros! Bienvenido.",
    "🐕 {u} llega acompañado de un perro rastreador. ¡Los dos son bienvenidos en el refugio!",
    "☕ {u} trae café. En pleno apocalipsis. Esa persona se queda. ¡Bienvenido!",
    "🧪 {u} dice que sabe de medicina. Esperemos que no sea de las de internet 😅 ¡Bienvenido!",
    "🏚️ {u} lleva semanas sobreviviendo en solitario y por fin encuentra gente. Aquí tienes un hogar."
]

# ==========================================
# GESTIÓN DE ARCHIVO DE ESTADO
# ==========================================

FICHERO_ESTADO = "estado.json"

ESTADO_INICIAL = {
    "dia": 0,  # el primer informe que se publique será el DÍA 1
    "poblacion": 12,
    "suministros": 80,
    "barricadas": 100,
    "moral": 75,
    "terminado": False,
    "ultima_encuesta_id": None,
    "opciones_ultima_encuesta": [],
    # --- comunidad (seguidores) ---
    "seguidores_base": None,          # seguidores al estrenar esta versión; solo cuentan los nuevos
    "seguidores_progreso": 0,         # máximo de seguidores nuevos alcanzado
    "bloques_pagados": 0,             # bloques de 10 seguidores ya convertidos en población
    "hitos_reclamados": 0,            # hitos de 25 seguidores ya aplicados
    "encuestas_desbloqueadas": [],    # hitos cuya encuesta ya forma parte del juego
    "seguidores_saludados": []        # ids de seguidores que ya han recibido bienvenida
}


def cargar_estado():
    estado = copy.deepcopy(ESTADO_INICIAL)
    if os.path.exists(FICHERO_ESTADO):
        with open(FICHERO_ESTADO, "r", encoding="utf-8") as f:
            estado.update(json.load(f))  # compatible con estado.json de versiones anteriores
    return estado


def guardar_estado(estado):
    with open(FICHERO_ESTADO, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=2)

# ==========================================
# LÓGICA PRINCIPAL DEL JUEGO
# ==========================================

CLAVES_PORCENTUALES = ("suministros", "barricadas", "moral")

ETIQUETAS_EFECTOS = {
    "poblacion": "👥 población",
    "suministros": "🥖 suministros",
    "barricadas": "🧱 barricadas",
    "moral": "🕯️ moral"
}


class EncuestaAbierta(Exception):
    """La encuesta anterior todavía no ha terminado: hoy no se publica nada."""


def aplicar_efectos(estado, efectos):
    for clave, cambio in efectos.items():
        if clave not in ETIQUETAS_EFECTOS:
            continue
        estado[clave] += cambio
        if clave in CLAVES_PORCENTUALES:
            estado[clave] = max(0, min(100, estado[clave]))
        else:
            estado[clave] = max(0, estado[clave])


def hay_game_over(estado):
    return estado["poblacion"] <= 0 or estado["suministros"] <= 0 or estado["moral"] <= 0


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

    aplicar_efectos(estado, evento.get("efectos", {}))
    return evento["texto"]


def resolver_encuesta_anterior(client, estado):
    """Aplica los efectos de la opción ganadora. Si algo falla, lanza la excepción
    (el workflow queda en rojo y no se publica nada) para no perder los votos de la comunidad."""
    if not estado.get("ultima_encuesta_id") or not estado.get("opciones_ultima_encuesta"):
        return ""

    status = client.status(estado["ultima_encuesta_id"])
    poll = status.get("poll")
    if not poll:
        raise RuntimeError("El post anterior no tiene encuesta; no se puede resolver la decisión.")
    if not poll.get("expired", True):
        raise EncuestaAbierta("La encuesta anterior sigue abierta; hoy no se publica nada.")

    votos = [option["votes_count"] or 0 for option in poll["options"]]
    if len(votos) != len(estado["opciones_ultima_encuesta"]):
        raise RuntimeError("Las opciones guardadas no coinciden con las de la encuesta publicada.")

    max_votos = max(votos)
    # Si hay empate (incluido 0 votos en todas), se elige al azar entre las empatadas
    empatadas = [i for i, v in enumerate(votos) if v == max_votos]
    ganadora_idx = random.choice(empatadas)

    opcion_elegida = estado["opciones_ultima_encuesta"][ganadora_idx]
    aplicar_efectos(estado, opcion_elegida.get("efectos", {}))

    return (
        f"📊 Resolución de la decisión anterior: ganó '{opcion_elegida['texto']}' "
        f"con {votos[ganadora_idx]} voto(s).\n\n"
    )

# ==========================================
# COMUNIDAD: SEGUIDORES, HITOS Y BIENVENIDAS
# ==========================================


def resumen_efectos(efectos):
    partes = [f"{v:+d} {ETIQUETAS_EFECTOS[k]}" for k, v in efectos.items() if k in ETIQUETAS_EFECTOS and v]
    return "Efecto: " + ", ".join(partes)


def texto_hito(k, hito):
    nuevos = k * SEGUIDORES_POR_HITO
    texto = (
        f"🎉 ¡HITO DE LA COMUNIDAD! Ya son {nuevos} los seguidores nuevos que se unen a la lucha.\n\n"
        f"{hito['titulo']}\n{hito['texto']}\n\n"
        f"{resumen_efectos(hito['efectos'])}"
    )
    if hito.get("encuesta"):
        texto += "\n\n🗳️ ¡Nueva decisión desbloqueada para las próximas encuestas!"
    return texto


def obtener_datos_comunidad(client):
    """Devuelve (total de seguidores, [(id, acct), ...]) con los 80 seguidores más recientes primero."""
    cuenta = client.account_verify_credentials()
    seguidores = client.account_followers(cuenta["id"], limit=80)
    return cuenta["followers_count"], [(str(s["id"]), s["acct"]) for s in seguidores]


def procesar_comunidad(client, estado):
    """Aplica los efectos de los seguidores nuevos sobre el estado.
    Devuelve (anuncios, accts_nuevos, encuesta_desbloqueada)."""
    anuncios = []
    encuesta_nueva = None

    try:
        total, lista = obtener_datos_comunidad(client)
    except Exception as e:
        # Los seguidores no son críticos: el juego sigue y lo que falte se cuenta al día siguiente
        print(f"⚠️ No se pudo leer la comunidad (seguidores): {e}")
        return anuncios, [], encuesta_nueva

    ids_lista = [i for i, _ in lista]

    # Primera ejecución con esta versión: solo cuentan los seguidores que lleguen a partir de ahora
    if estado["seguidores_base"] is None:
        estado["seguidores_base"] = total
        estado["seguidores_saludados"] = ids_lista[:MAX_IDS_RECORDADOS]
        print(f"Comunidad inicializada: {total} seguidores de partida.")
        return anuncios, [], encuesta_nueva

    # Bienvenidas: seguidores que aún no estaban registrados
    conocidos = [str(i) for i in estado["seguidores_saludados"]]
    nuevos = [(i, acct) for i, acct in lista if i not in set(conocidos)]
    estado["seguidores_saludados"] = ([i for i, _ in nuevos] + conocidos)[:MAX_IDS_RECORDADOS]
    accts_nuevos = [acct for _, acct in nuevos]

    # Progreso: marca máxima de seguidores nuevos (si alguien deja de seguir no se pierde lo logrado)
    estado["seguidores_progreso"] = max(estado["seguidores_progreso"], total - estado["seguidores_base"])
    progreso = estado["seguidores_progreso"]

    # 1) Seguidores = supervivientes: cada 10 seguidores nuevos llegan 3 personas
    bloques = progreso // SEGUIDORES_POR_BLOQUE
    if bloques > estado["bloques_pagados"]:
        extra = (bloques - estado["bloques_pagados"]) * POBLACION_POR_BLOQUE
        estado["poblacion"] += extra
        estado["bloques_pagados"] = bloques
        anuncios.append(
            f"🎒 ¡La comunidad crece! Llegan {extra} supervivientes más al refugio "
            f"(+{POBLACION_POR_BLOQUE} de población por cada {SEGUIDORES_POR_BLOQUE} seguidores nuevos)."
        )

    # 2) Hitos cada 25 seguidores nuevos
    hitos_alcanzados = progreso // SEGUIDORES_POR_HITO
    for k in range(estado["hitos_reclamados"] + 1, hitos_alcanzados + 1):
        hito = HITOS.get(k, HITO_GENERICO)
        aplicar_efectos(estado, hito["efectos"])
        anuncios.append(texto_hito(k, hito))
        if hito.get("encuesta"):
            estado["encuestas_desbloqueadas"].append(k)
            encuesta_nueva = hito["encuesta"]
    estado["hitos_reclamados"] = max(estado["hitos_reclamados"], hitos_alcanzados)

    return anuncios, accts_nuevos, encuesta_nueva


def encuestas_disponibles(estado):
    """Encuestas base + las desbloqueadas por hitos (estas pesan el doble para que se vean)."""
    pool = list(OPCIONES_ENCUESTA)
    for k in estado["encuestas_desbloqueadas"]:
        hito = HITOS.get(k)
        if hito and hito.get("encuesta"):
            pool += [hito["encuesta"]] * 2
    return pool


def empaquetar(bloques):
    """Junta bloques de texto en toots sin pasar del límite de caracteres."""
    toots, actual = [], ""
    for bloque in bloques:
        candidato = f"{actual}\n\n{bloque}" if actual else bloque
        if len(candidato) <= LIMITE_CARACTERES:
            actual = candidato
        else:
            if actual:
                toots.append(actual)
            actual = bloque
    if actual:
        toots.append(actual)
    return toots


def bloques_saludos(accts):
    """Bienvenidas con @mención (así le llega la notificación al seguidor). Máximo MAX_SALUDOS_POR_DIA."""
    if not accts:
        return []
    cabecera = "👋 ¡NUEVOS SUPERVIVIENTES EN EL REFUGIO!"
    elegidos = accts[:MAX_SALUDOS_POR_DIA]
    plantillas = random.sample(SALUDOS, len(elegidos))  # sin repetir variante el mismo día
    lineas = [plantilla.format(u="@" + acct) for acct, plantilla in zip(elegidos, plantillas)]
    # La cabecera va pegada a la primera bienvenida para que nunca quede sola al final de un toot
    bloques = [f"{cabecera}\n\n{lineas[0]}"] + lineas[1:]
    resto = len(accts) - len(elegidos)
    if resto > 0:
        bloques.append(f"🧟 …y {resto} supervivientes más que también se han unido. ¡Gracias a todos!")
    return bloques


def construir_toots_comunidad(anuncios, accts):
    """Anuncios (población, hitos) + bienvenidas, repartidos en los toots que hagan falta."""
    return empaquetar(anuncios + bloques_saludos(accts))


def comprobar_longitud(*textos):
    for i, texto in enumerate(textos, start=1):
        if len(texto) > LIMITE_CARACTERES:
            raise ValueError(
                f"El toot {i} tiene {len(texto)} caracteres y el límite es {LIMITE_CARACTERES}. "
                "No se ha publicado nada."
            )


def main():
    estado = cargar_estado()

    # 0. Partida ya terminada: no publicar nada más
    if estado["terminado"]:
        print("La partida ha terminado. Para empezar otra, restaura estado.json.")
        return

    client = obtener_cliente_mastodon()

    # 1. Resolver la encuesta del día anterior
    try:
        texto_resolucion = resolver_encuesta_anterior(client, estado)
    except EncuestaAbierta as e:
        print(e)
        return

    # 2. Comunidad: seguidores nuevos, hitos y bienvenidas (antes del evento nocturno)
    anuncios, accts_nuevos, encuesta_desbloqueada = procesar_comunidad(client, estado)

    # 3. Evento nocturno aleatorio
    texto_evento = procesar_evento_nocturno(estado)

    # 4. Nuevo día y comprobación de Game Over (con los efectos ya aplicados)
    estado["dia"] += 1
    game_over = hay_game_over(estado)

    # 5. Construir los toots (sin Markdown: Mastodon no lo interpreta)
    toot_1 = (
        f"🧟‍♂️ INFORME DE SUPERVIVENCIA - DÍA {estado['dia']}\n\n"
        f"{texto_resolucion}"
        f"{texto_evento}"
    )
    bloque_estado = (
        f"📋 ESTADO DEL REFUGIO:\n"
        f"👥 Población: {estado['poblacion']} personas\n"
        f"🥖 Suministros: {estado['suministros']}%\n"
        f"🧱 Barricadas: {estado['barricadas']}%\n"
        f"🕯️ Moral: {estado['moral']}%\n\n"
    )

    if game_over:
        toot_2 = (
            f"{bloque_estado}"
            f"💀 GAME OVER - DÍA {estado['dia']} 💀\n\n"
            "La aldea ha sucumbido al apocalipsis. Los suministros, la moral o la población "
            "se han agotado por completo. Los pocos supervivientes se han dispersado en la oscuridad.\n\n"
            "#ApocalipsisZombi #GameOver #MastodonBot"
        )
        comprobar_longitud(toot_1, toot_2)

        primer_post = client.status_post(status=toot_1, language="es")
        client.status_post(status=toot_2, in_reply_to_id=primer_post["id"], language="es")

        estado["terminado"] = True
        estado["ultima_encuesta_id"] = None
        estado["opciones_ultima_encuesta"] = []
        guardar_estado(estado)
        return

    # 6. Nueva encuesta para hoy (si se acaba de desbloquear una por un hito, es la de hoy)
    encuesta_hoy = encuesta_desbloqueada or random.choice(encuestas_disponibles(estado))
    opciones_texto = [opc["texto"] for opc in encuesta_hoy["opciones"]]

    toots_comunidad = construir_toots_comunidad(anuncios, accts_nuevos)

    toot_encuesta = (
        f"{bloque_estado}"
        f"❓ DECISIÓN PARA HOY: {encuesta_hoy['pregunta']}\n\n"
        f"#ApocalipsisZombi #Supervivencia #MastodonBot"
    )
    # Se comprueba todo antes de publicar para no dejar el hilo a medias por longitud
    comprobar_longitud(toot_1, *toots_comunidad, toot_encuesta)

    # 7. Publicar el hilo: informe -> novedades de la comunidad (si hay) -> estado + encuesta
    anterior = client.status_post(status=toot_1, language="es")["id"]
    for texto in toots_comunidad:
        anterior = client.status_post(status=texto, in_reply_to_id=anterior, language="es")["id"]

    poll = client.make_poll(options=opciones_texto, expires_in=DURACION_ENCUESTA)
    post_encuesta = client.status_post(
        status=toot_encuesta,
        in_reply_to_id=anterior,
        poll=poll,
        language="es"
    )

    # 8. Guardar estado (el id de seguimiento es el del toot que lleva la encuesta)
    estado["ultima_encuesta_id"] = post_encuesta["id"]
    estado["opciones_ultima_encuesta"] = encuesta_hoy["opciones"]
    guardar_estado(estado)


if __name__ == "__main__":
    main()
