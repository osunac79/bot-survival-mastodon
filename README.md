# 🧟‍♂️ Bot de Supervivencia Zombi para Mastodon

Un bot autónomo en Python que simula la gestión diaria de un asentamiento de supervivientes durante un apocalipsis zombi. Funciona de forma interactiva en **Mastodon**, donde la comunidad toma decisiones mediante encuestas diarias que afectan a los recursos, la moral y la supervivencia de la aldea.

El sistema se ejecuta automáticamente cada día a través de **GitHub Actions**, registrando el avance del juego en un archivo de estado persistente (`estado.json`).

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
* **🗳️ Encuesta interactiva:** Cada día se lanzan 3 o 4 opciones de acción para que los seguidores decidan el destino del grupo en las siguientes 24 horas.
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
│       └── ejecucion.yml    # Configuración de GitHub Actions (cron + ejecucion manual)
├── bot.py                   # Lógica principal del juego y conexión con la API
├── estado_base.json         # Plantilla con los valores iniciales del Día 1
├── estado.json              # Registro del estado actual de la partida
├── requirements.txt         # Dependencias del proyecto (Mastodon.py)
├── .gitignore
├── LICENSE                  # Licencia de código abierto (MIT)
└── README.md
