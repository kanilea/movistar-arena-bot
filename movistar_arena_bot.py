#!/usr/bin/env python3
"""
Movistar Arena Bot - Monitoreo de disponibilidad de entradas
Autor: Bot automático para seguimiento de tickets
Función: Monitorea disponibilidad en sectores A, B, C, D de Movistar Arena Argentina
"""

import time
import json
import logging
import requests
import smtplib
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Cargar configuración desde variables de entorno o archivo
def load_config():
    config = {
        "target_url": os.getenv("TARGET_URL", "https://www.movistararena.com.ar/Ticketera/592cc91b-9b77-4de2-bb9c-93e960efe3f2"),
        "target_sectors": ["CAMPO A", "CAMPO B", "CAMPO C", "CAMPO D"],
        "check_interval": int(os.getenv("CHECK_INTERVAL", "300")),
        "telegram": {
            "bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
            "chat_id": os.getenv("TELEGRAM_CHAT_ID", "")
        },
        "email": {
            "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            "smtp_port": int(os.getenv("SMTP_PORT", "587")),
            "sender_email": os.getenv("SENDER_EMAIL", ""),
            "sender_password": os.getenv("SENDER_PASSWORD", ""),
            "recipient_email": os.getenv("RECIPIENT_EMAIL", "")
        }
    }
    
    # Si hay archivo config.json, cargarlo
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r") as f:
                file_config = json.load(f)
                config.update(file_config)
        except:
            pass
    
    return config

CONFIG = load_config()

class MovistarArenaBot:
    def __init__(self):
        self.setup_logging()
        self.setup_driver()
        self.availability_log = set()  # Para evitar notificaciones duplicadas
        
    def setup_logging(self):
        """Configurar logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler()  # En cloud environment, solo stdout
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_driver(self):
        """Configurar Chrome WebDriver con opciones para cloud environment"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        options.add_argument('--disable-javascript')
        options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 10)  # Reducido para cloud
            self.logger.info("WebDriver inicializado correctamente")
        except Exception as e:
            self.logger.error(f"Error inicializando WebDriver: {e}")
            # Si Chrome no funciona, usar requests como fallback
            self.driver = None
            
    def check_ticket_availability_with_requests(self):
        """Fallback con requests si Chrome falla"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            }
            response = requests.get(CONFIG["target_url"], headers=headers, timeout=10)
            page_text = response.text.upper()
            
            available_sectors = []
            for sector in CONFIG["target_sectors"]:
                if sector in page_text:
                    # Buscar palabras clave de disponibilidad
                    context_start = max(0, page_text.find(sector) - 100)
                    context_end = min(len(page_text), page_text.find(sector) + 200)
                    context = page_text[context_start:context_end]
                    
                    if any(keyword in context for keyword in ['DISPONIBLE', 'AVAILABLE', 'COMPRAR']):
                        available_sectors.append({
                            'name': sector,
                            'status': 'DISPONIBLE',
                            'timestamp': datetime.now()
                        })
                        self.logger.info(f"¡Sector disponible encontrado con requests! {sector}")
            
            return available_sectors
            
        except Exception as e:
            self.logger.error(f"Error con requests: {e}")
            return []
    
    def check_ticket_availability(self):
        """Verificar disponibilidad de tickets en los sectores objetivo"""
        if not self.driver:
            return self.check_ticket_availability_with_requests()
            
        try:
            self.driver.get(CONFIG["target_url"])
            self.logger.info(f"Cargando página: {CONFIG['target_url']}")
            
            # Esperar короткое время
            time.sleep(3)
            
            # Buscar por texto en página
            page_text = self.driver.page_source.upper()
            available_sectors = []
            
            for sector in CONFIG["target_sectors"]:
                if sector in page_text:
                    # Buscar palabras clave de disponibilidad
                    context_start = max(0, page_text.find(sector) - 100)
                    context_end = min(len(page_text), page_text.find(sector) + 200)
                    context = page_text[context_start:context_end]
                    
                    if any(keyword in context for keyword in ['DISPONIBLE', 'AVAILABLE', 'COMPRAR']):
                        available_sectors.append({
                            'name': sector,
                            'status': 'DISPONIBLE',
                            'timestamp': datetime.now()
                        })
                        self.logger.info(f"¡Sector disponible encontrado! {sector}")
            
            return available_sectors
            
        except Exception as e:
            self.logger.error(f"Error verificando disponibilidad: {e}")
            # Fallback a requests
            return self.check_ticket_availability_with_requests()
    
    def send_telegram_notification(self, message):
        """Enviar notificación via Telegram"""
        if not CONFIG["telegram"]["bot_token"] or not CONFIG["telegram"]["chat_id"]:
            self.logger.warning("Telegram no configurado")
            return False
            
        try:
            url = f"https://api.telegram.org/bot{CONFIG['telegram']['bot_token']}/sendMessage"
            data = {
                'chat_id': CONFIG['telegram']['chat_id'],
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                self.logger.info("Notificación Telegram enviada exitosamente")
                return True
            else:
                self.logger.error(f"Error enviando Telegram: {response.text}")
                return False
        except Exception as e:
            self.logger.error(f"Excepción enviando Telegram: {e}")
            return False
    
    def send_email_notification(self, subject, message):
        """Enviar notificación via Email"""
        if not CONFIG["email"]["sender_email"] or not CONFIG["email"]["sender_password"]:
            self.logger.warning("Email no configurado")
            return False
            
        try:
            msg = MIMEMultipart()
            msg['From'] = CONFIG['email']['sender_email']
            msg['To'] = CONFIG['email']['recipient_email']
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'html'))
            
            server = smtplib.SMTP(CONFIG['email']['smtp_server'], CONFIG['email']['smtp_port'])
            server.starttls()
            server.login(CONFIG['email']['sender_email'], CONFIG['email']['sender_password'])
            
            text = msg.as_string()
            server.sendmail(CONFIG['email']['sender_email'], CONFIG['email']['recipient_email'], text)
            server.quit()
            
            self.logger.info("Email enviado exitosamente")
            return True
        except Exception as e:
            self.logger.error(f"Error enviando email: {e}")
            return False
    
    def create_notification_message(self, available_sectors):
        """Crear mensaje de notificación formateado"""
        message = "🎟️ <b>¡ENTRADAS DISPONIBLES EN MOVISTAR ARENA!</b> 🎟️\n\n"
        message += f"📅 Evento: Sebastián Yatra\n"
        message += f"🔗 Link: {CONFIG['target_url']}\n\n"
        message += "📍 <b>Sectores disponibles:</b>\n"
        
        for sector in available_sectors:
            message += f"• <b>{sector['name']}</b> - {sector['status']}\n"
        
        message += f"\n⏰ Detectado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        message += "🚨 ¡Actúa rápido antes de que se agoten!"
        
        return message
    
    def process_availability(self, available_sectors):
        """Procesar disponibilidad y enviar notificaciones"""
        if not available_sectors:
            self.logger.info("No hay sectores disponibles en este momento")
            return
        
        # Verificar si ya notificamos estos sectores
        current_check = set()
        for sector in available_sectors:
            current_check.add(sector['name'])
        
        # Enviar notificación solo si hay nuevos sectores disponibles
        if not current_check.issubset(self.availability_log):
            self.availability_log.update(current_check)
            
            # Crear mensajes
            telegram_message = self.create_notification_message(available_sectors)
            email_subject = "🎟️ ¡ENTRADAS DISPONIBLES - Movistar Arena!"
            email_message = f"""
            <html>
            <body>
                <h2>🎟️ ¡ENTRADAS DISPONIBLES EN MOVISTAR ARENA!</h2>
                <p><strong>Evento:</strong> Sebastián Yatra</p>
                <p><strong>Sectores disponibles:</strong></p>
                <ul>
            """
            
            for sector in available_sectors:
                email_message += f"<li><strong>{sector['name']}</strong> - {sector['status']}</li>"
            
            email_message += f"""
                </ul>
                <p><strong>Link:</strong> <a href="{CONFIG['target_url']}">Comprar entradas aquí</a></p>
                <p><strong>Detectado:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                <p><em>¡Actúa rápido antes de que se agoten!</em></p>
            </body>
            </html>
            """
            
            # Enviar notificaciones
            self.send_telegram_notification(telegram_message)
            self.send_email_notification(email_subject, email_message)
        else:
            self.logger.info("Sectores ya notificados previamente")
    
    def run(self):
        """Bucle principal del bot"""
        self.logger.info("🚀 Iniciando Movistar Arena Bot...")
        self.logger.info(f"📍 Monitoreando sectores: {CONFIG['target_sectors']}")
        self.logger.info(f"⏱️ Intervalo de chequeo: {CONFIG['check_interval']} segundos")
        
        try:
            while True:
                try:
                    self.logger.info(f"🔍 Verificando disponibilidad... ({datetime.now()})")
                    
                    available_sectors = self.check_ticket_availability()
                    self.process_availability(available_sectors)
                    
                    self.logger.info(f"💤 Esperando {CONFIG['check_interval']} segundos para próxima verificación")
                    time.sleep(CONFIG['check_interval'])
                    
                except KeyboardInterrupt:
                    self.logger.info("🛑 Bot detenido por usuario")
                    break
                except Exception as e:
                    self.logger.error(f"Error en bucle principal: {e}")
                    time.sleep(60)  # Esperar 1 minuto antes de reintentar
                    
        finally:
            if self.driver:
                self.driver.quit()
            self.logger.info("🔚 Bot finalizado")

if __name__ == "__main__":
    bot = MovistarArenaBot()
    bot.run()