<h1 align="center">📦 Correos Track Bot</h1>

<p align="center">
  <img src="/api/placeholder/1200/300" alt="Correos Track Bot Banner">
</p>

<p align="center">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python Version">
  </a>
  <a href="https://github.com/yourusername/correos-track-bot/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square" alt="License">
  </a>
  <a href="https://core.telegram.org/bots/api">
    <img src="https://img.shields.io/badge/Telegram-Bot_API-2CA5E0?style=flat-square&logo=telegram&logoColor=white" alt="Telegram Bot API">
  </a>
  <a href="https://www.correos.es/es/es/herramientas/localizador/envios">
    <img src="https://img.shields.io/badge/Correos-API-yellow?style=flat-square" alt="Correos API">
  </a>
</p>

<p align="center">
  Bot de Telegram para el seguimiento automático de envíos de Correos España con notificaciones en tiempo real.
</p>

## ✨ Características

- 🔄 **Seguimiento automático**: Monitorización continua de tus envíos
- 📱 **Notificaciones instantáneas**: Recibe alertas cuando hay actualizaciones
- 🎯 **Comandos intuitivos**: Interfaz fácil de usar mediante comandos de Telegram
- 📊 **Historial detallado**: Consulta el historial completo de cada envío
- 🔔 **Gestión automática**: Sugerencia de eliminación cuando el envío está entregado
- 💾 **Persistencia de datos**: Los seguimientos se mantienen entre reinicios
- 🔐 **Configuración segura**: Credenciales separadas del código principal

## 🚀 Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/yourusername/correos-track-bot.git
cd correos-track-bot
```

2. Instala las dependencias:
```bash
pip install requests
```

3. Crea un archivo `config.py` con tus credenciales:
```python
TELEGRAM_BOT_TOKEN = "TU_BOT_TOKEN"
TELEGRAM_CHAT_ID = "TU_CHAT_ID"
CHECK_INTERVAL = 300
COMMAND_CHECK_INTERVAL = 1
CORREOS_API_URL = "https://api1.correos.es/digital-services/searchengines/api/v1/"
```

## 🔧 Configuración

### Crear un bot de Telegram:
1. Habla con [@BotFather](https://t.me/botfather) en Telegram
2. Usa el comando `/newbot` y sigue las instrucciones
3. Guarda el token que te proporciona

### Obtener el Chat ID:
1. Inicia un chat con tu bot
2. Envía cualquier mensaje
3. Visita: `https://api.telegram.org/bot<TU_TOKEN>/getUpdates`
4. Busca el número `chat_id` en la respuesta

## 💻 Uso

### Iniciar el bot:
```bash
python correos_tracker.py
```

### Comandos disponibles:
- `/add NUMERO` - Añade un envío al seguimiento
- `/status NUMERO` - Muestra el estado actual de un envío
- `/list` - Lista todos los envíos en seguimiento
- `/remove NUMERO` - Elimina un envío del seguimiento
- `/help` - Muestra la ayuda

## 📸 Capturas de pantalla

<p align="center">
  <img src="/api/placeholder/300/500" alt="Demo Bot" width="300">
  <img src="/api/placeholder/300/500" alt="Tracking Example" width="300">
</p>

## 🛠️ Tecnologías utilizadas

- [Python](https://www.python.org/) - Lenguaje de programación
- [Telegram Bot API](https://core.telegram.org/bots/api) - API para bots de Telegram
- [Correos API](https://api1.correos.es) - API de seguimiento de Correos
- [Requests](https://docs.python-requests.org/) - Cliente HTTP para Python

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor, abre primero un issue para discutir los cambios que te gustaría realizar.

1. Haz un Fork del proyecto
2. Crea tu rama de características (`git checkout -b feature/AmazingFeature`)
3. Haz commit de tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Haz Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## ⭐ Muestra tu apoyo

Si este proyecto te ha resultado útil, considera darle una estrella ⭐️

## 📧 Contacto

Project Link: [https://github.com/vgvr0/correos-tracking-bot](https://github.com/vgvr0/correos-tracking-bot)
