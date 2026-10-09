# 🧟‍♂️ Bot de Supervivencia Zombi para Mastodon

Un bot autónomo en Python que simula la gestión diaria de un asentamiento de supervivientes durante un apocalipsis zombi. Funciona de forma interactiva en **Mastodon**, donde la comunidad toma decisiones mediante encuestas diarias que afectan a los recursos, la moral y la supervivencia de la aldea.

El sistema se ejecuta automáticamente cada día a través de **GitHub Actions**, registrando el avance del juego en un archivo de estado persistente (`estado.json`).

Cada día se publica un **hilo**: informe de la noche, novedades de la comunidad (si las hay) y, al final, el estado del refugio con la encuesta (que dura 23 h).

---

## 📊 Mecánicas del Juego

El bot publica un informe diario con el estado actual de la aldea y plantea una nueva encrucijada a la comunidad.

* **📋 Resolución de la jornada anterior:** Analiza los votos acumulados en la encuesta previa y aplica los efectos de la opción ganadora sobre los recursos.
* **🌃 Evento nocturno aleatorio:** Durante la noche ocurre un suceso al azar clasificado en 4 niveles de gravedad (Fortuna, Neutro, Moderado o Grave) que puede beneficiar o perjudicar al asentamiento.
* **📦 Gestión de recursos:**
  * 🥖 **Suministros:** Alimentos y medicinas necesarios para mantener con vida a la población.
  * 🧱 **Barricadas:** La defensa principal del perímetro contra las hordas.
  * 🕯️ **Moral:** El estado de ánimo de los supervivientes. Si cae a cero, la desesperación destruye el grupo.
  * 👥 **Población:** El número de personas en el refugio.
* **🗳️ Encuesta interactiva:** Cada día se lanzan 3 o 4 opciones de acción para que los seguidores decidan el destino del grupo durante las siguientes 23 horas.
* **💀 Condición de Game Over:** Si los recursos esenciales o la población se agotan, la partida finaliza trágicamente y el bot notifica la caída definitiva de la aldea.

---

## 🛠️ Requisitos e Instalación

### Requisitos previos
* Una cuenta de bot creada en cualquier instancia de **Mastodon**.
* Un token de acceso de la API de Mastodon (*AccessToken*).
* Una cuenta de **GitHub** para alojar el repositorio y programar las ejecuciones.

### Estructura del Proyecto

```text
├── .github/
│   └── workflows/
│       └── ejecucion.yml    # Configuración de GitHub Actions (cron + ejecución manual)
├── bot.py                   # Lógica principal del juego y conexión con la API
├── estado.json              # Registro del estado actual de la partida
├── requirements.txt         # Dependencias del proyecto (Mastodon.py)
├── .gitignore
├── LICENSE                  # Licencia de código abierto (MIT)
└── README.md
```

---

## 👥 Mecánicas de comunidad (seguidores)

Seguir al bot tiene efecto directo en la partida. Solo cuentan los seguidores **nuevos** desde que se estrena esta versión.

* **🎒 Seguidores = supervivientes:** por cada 10 seguidores nuevos llegan 3 personas al refugio (+3 de población).
* **🏆 Hitos cada 25 seguidores nuevos:** cada hito mejora el refugio y, casi siempre, desbloquea una decisión nueva para las encuestas.

| Seguidores nuevos | Hito | Efecto |
|---|---|---|
| 25 | 🩺 Médico | +10 moral, +1 población |
| 50 | ⚡ Generador | +10 moral, +5 barricadas |
| 75 | 🔭 Torre de vigilancia | +20 barricadas |
| 100 | 📡 Convoy de ayuda (hito épico) | +5 población, +25 suministros, +15 moral |
| 125 | 🌱 Huerto | +15 suministros, +5 moral |
| 150 | 🔧 Taller de refuerzos | +20 barricadas, +5 moral |
| 175 | 🐕 Perro guardián | +10 moral, +5 barricadas |
| 200 | 🏆 Leyenda del refugio | +5 población, +20 suministros, +20 barricadas, +20 moral |
| 225, 250... | 📦 Cargamento de la comunidad | +15 suministros, +10 moral, +2 población |

* **👋 Bienvenida con @:** cada seguidor nuevo recibe una mención en un toot de bienvenida (20 variantes de texto), con lo que le llega una notificación. Máximo 8 menciones al día; si hay más, el resto se resume en una línea.
* Los efectos de la comunidad se aplican antes del evento nocturno, así que pueden salvar al refugio de un mal día.
* Si la API de seguidores falla un día, el juego sigue con normalidad y los seguidores pendientes se cuentan al día siguiente.

> El token de Mastodon necesita los permisos `read` y `write:statuses` (con `read` basta para consultar los seguidores).

### Empezar una partida nueva

Cuando la partida termina (Game Over) el bot deja de publicar. Para empezar otra, sustituye el contenido de `estado.json` por el del repositorio original (día 0, población 12, suministros 80, barricadas 100, moral 75, `terminado` en `false` y los campos de comunidad a cero).
