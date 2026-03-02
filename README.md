# 🎟️ Movistar Arena Bot

Bot automático para monitorear disponibilidad de entradas en Movistar Arena Argentina

## 🚀 Funcionalidades

- ✅ Monitoreo constante de disponibilidad en sectores A, B, C, D
- 📱 Notificaciones instantáneas via Telegram
- 📧 Notificaciones via Email
- 🐳 Contenerización Docker para despliegue en la nube
- 🔄 Configuración flexible de intervalos de chequeo
- 📊 Logging completo de actividades

## 📋 Prerrequisitos

- Python 3.11+
- Chrome Browser
- Docker (opcional, para despliegue en nube)
- Cuenta de Telegram Bot
- Cuenta de Email (Gmail recomendado)

## ⚙️ Configuración

### 1. Telegram Bot
1. Habla con [@BotFather](https://t.me/BotFather) en Telegram
2. Crea un nuevo bot: `/newbot`
3. Obtén tu **BOT_TOKEN**
4. Obtén tu **CHAT_ID** (habla con @userinfobot)

### 2. Email
1. Activa App Passwords en tu cuenta Gmail
2. Genera una App Password para el bot
3. Configura tus credenciales en `config.json`

### 3. Configurar el Bot
Edita `config.json` con tus datos:
```json
{
    "telegram": {
        "bot_token": "TU_BOT_TOKEN_AQUI",
        "chat_id": "TU_CHAT_ID_AQUI"
    },
    "email": {
        "sender_email": "tu_email@gmail.com",
        "sender_password": "TU_APP_PASSWORD",
        "recipient_email": "destinatario@gmail.com"
    }
}
```

## 🏃‍♂️ Ejecución Local

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecutar el bot
```bash
python movistar_arena_bot.py
```

### 3. Monitoreo
El bot comenzará a verificar cada 5 minutos la disponibilidad
y te notificará cuando encuentre entradas en los sectores A, B, C, D.

## ☁️ Despliegue en la Nube

### Opción 1: Docker Compose (Recomendado)
```bash
# Configurar tus credenciales en config.json
docker-compose up -d
```

### Opción 2: Docker
```bash
docker build -t movistar-bot .
docker run -d --name movistar-arena-bot \
  -v $(pwd)/config.json:/app/config.json \
  -v $(pwd)/logs:/app/logs \
  movistar-bot
```

### Opción 3: Servicios Cloud
- **AWS ECS**: Sube la imagen Docker a ECR y ejecuta en ECS
- **Google Cloud Run**: Despliega como contenedor serverless
- **Azure Container Instances**: Ejecuta como contenedor aislado
- **DigitalOcean App Platform**: Despliegue directo desde GitHub
- **Railway**: Despliegue automático con GitHub integration

## 📱 Ejemplo de Notificación

### Telegram:
```
🎟️ ¡ENTRADAS DISPONIBLES EN MOVISTAR ARENA! 🎟️

📅 Evento: Sebastián Yatra
🔗 Link: [URL del evento]

📍 Sectores disponibles:
• CAMPO A - DISPONIBLE - $15000
• CAMPO B - DISPONIBLE - $12000

⏰ Detectado: 02/03/2026 14:30:25
🚨 ¡Actúa rápido antes de que se agoten!
```

### Email:
Mensaje HTML formateado con hipervínculos directos a compra.

## 🔧 Personalización

### Cambiar Sectores
Edita `target_sectors` en config.json:
```json
"target_sectors": ["CAMPO A", "CAMPO B", "CAMPO C", "CAMPO D", "PALCO VIP"]
```

### Cambiar Intervalo
Modifica `check_interval` (en segundos):
```json
"check_interval": 180  // 3 minutos
```

### CambiarEvento
Actualiza `target_url` en config.json con el nuevo link del evento.

## 🐛 Troubleshooting

### Problemas Comunes:
1. **ChromeDriver errors**: Asegúrate que Chrome esté actualizado
2. **Telegram no responde**: Verifica BOT_TOKEN y CHAT_ID
3. **Email no envía**: Revisa App Password y credenciales SMTP
4. **Timeout errors**: Aumenta el timeout en config.json

### Logs:
```bash
# Ver logs en tiempo real
tail -f movistar_bot.log

# Logs en Docker
docker logs movistar_arena_bot
```

## 🔒 Seguridad

- Las credenciales se cargan desde config.json (no se suben a Git)
- Soporta variables de entorno para producción
- Ejecución en headless mode sin interfaz gráfica
- Rate limiting integrado para no sobrecargar el servidor

## 📞 Soporte

Si tienes problemas o preguntas:
1. Revisa el log `movistar_bot.log`
2. Verifica tu configuración en `config.json`
3. Asegúrate que el evento esté activo en Movistar Arena

## 📄 Licencia

MIT License - Uso bajo tu responsabilidad.
Respeta los términos de servicio de Movistar Arena.

---

**⚠️ Importante**: Este bot es para fines de monitoreo únicamente.
No assume responsabilidad por pérdidas de entradas o problemas con el servicio.