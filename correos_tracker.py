import requests
import json
from datetime import datetime
import time
import logging
from typing import Dict, List, Optional, Set
import sys
import pickle
from pathlib import Path
from config import *

class CorreosTracker:
    def __init__(self):
        self.base_url = CORREOS_API_URL
        self.telegram_bot_token = TELEGRAM_BOT_TOKEN
        self.telegram_chat_id = TELEGRAM_CHAT_ID
        self.tracked_shipments = {}
        self.tracking_numbers = set()
        self.data_file = Path("tracking_data.pkl")
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Cargar datos guardados
        self.load_data()

    def load_data(self) -> None:
        """Carga los datos guardados de seguimientos previos"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'rb') as f:
                    data = pickle.load(f)
                    self.tracked_shipments = data.get('shipments', {})
                    self.tracking_numbers = data.get('numbers', set())
                self.logger.info(f"Datos cargados: {len(self.tracking_numbers)} envíos en seguimiento")
            except Exception as e:
                self.logger.error(f"Error al cargar datos: {e}")

    def save_data(self) -> None:
        """Guarda los datos de seguimiento"""
        try:
            with open(self.data_file, 'wb') as f:
                data = {
                    'shipments': self.tracked_shipments,
                    'numbers': self.tracking_numbers
                }
                pickle.dump(data, f)
        except Exception as e:
            self.logger.error(f"Error al guardar datos: {e}")

    def get_shipment_status(self, tracking_number: str) -> Optional[Dict]:
        """Obtiene el estado actual del envío desde la API de Correos"""
        params = {
            'text': tracking_number,
            'language': 'ES',
            'searchType': 'envio'
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Error al obtener estado del envío {tracking_number}: {e}")
            return None

    def send_telegram_message(self, message: str, reply_markup: Optional[Dict] = None) -> bool:
        """Envía un mensaje a través de Telegram con teclado opcional"""
        telegram_url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
        data = {
            "chat_id": self.telegram_chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
        
        try:
            response = requests.post(telegram_url, json=data)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            self.logger.error(f"Error al enviar mensaje a Telegram: {e}")
            return False

    def create_remove_keyboard(self, tracking_number: str) -> Dict:
        """Crea un teclado inline con la opción de eliminar"""
        return {
            "inline_keyboard": [[{
                "text": "🗑️ Eliminar seguimiento",
                "callback_data": f"remove_{tracking_number}"
            }]]
        }

    def handle_callback_query(self, callback_query: Dict) -> None:
        """Maneja las respuestas de los botones inline"""
        query_id = callback_query.get('id')
        data = callback_query.get('data', '')
        
        if data.startswith('remove_'):
            tracking_number = data.replace('remove_', '')
            response_text = self.remove_tracking(tracking_number)
            
            # Responder a la callback query
            self.answer_callback_query(query_id, "Envío eliminado del seguimiento")
            
            # Editar el mensaje original
            message_id = callback_query['message']['message_id']
            self.edit_message_text(
                message_id,
                f"✅ El envío <code>{tracking_number}</code> ha sido eliminado del seguimiento."
            )

    def answer_callback_query(self, callback_query_id: str, text: str) -> None:
        """Responde a una callback query"""
        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/answerCallbackQuery"
        data = {
            "callback_query_id": callback_query_id,
            "text": text
        }
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
        except requests.RequestException as e:
            self.logger.error(f"Error al responder callback query: {e}")

    def edit_message_text(self, message_id: int, text: str) -> None:
        """Edita un mensaje existente"""
        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/editMessageText"
        data = {
            "chat_id": self.telegram_chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": "HTML"
        }
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
        except requests.RequestException as e:
            self.logger.error(f"Error al editar mensaje: {e}")

    def is_delivered(self, event: Dict) -> bool:
        """Comprueba si un evento indica que el envío está entregado"""
        delivered_phrases = [
            "ENTREGADO",
            "ENTREGA EFECTUADA",
            "ENTREGADO AL DESTINATARIO"
        ]
        return (
            event['phase'] in ['3', '4'] or
            any(phrase in event['summaryText'].upper() for phrase in delivered_phrases) or
            any(phrase in event['extendedText'].upper() for phrase in delivered_phrases)
        )

    def format_status_message(self, tracking_number: str, events: List[Dict]) -> str:
        """Formatea el mensaje de estado completo para Telegram"""
        if not events:
            return f"📦 No hay información disponible para el envío: <code>{tracking_number}</code>"
        
        latest_event = events[-1]
        is_delivered = self.is_delivered(latest_event)
        
        message = [
            f"📦 Estado del envío: <code>{tracking_number}</code>\n",
            f"{'📬' if is_delivered else '📍'} Estado actual: {latest_event['summaryText']}",
            f"📅 Última actualización: {latest_event['eventDate']} {latest_event['eventTime']}",
            f"ℹ️ Detalle: {latest_event['extendedText']}",
            f"🏷️ Fase: {latest_event['desPhase']}\n",
            "📋 Historial de eventos:"
        ]
        
        # Añadir historial de eventos en orden cronológico inverso
        for event in reversed(events):
            message.append(
                f"- {event['eventDate']} {event['eventTime']}: {event['summaryText']}"
            )
        
        return "\n".join(message)

    def format_update_message(self, tracking_number: str, event: Dict) -> str:
        """Formatea el mensaje de actualización para Telegram"""
        is_delivered = self.is_delivered(event)
        emoji = "📬" if is_delivered else "📦"
        
        return (
            f"{emoji} Actualización de envío: <code>{tracking_number}</code>\n"
            f"📅 Fecha: {event['eventDate']} {event['eventTime']}\n"
            f"📍 Estado: {event['summaryText']}\n"
            f"ℹ️ Detalle: {event['extendedText']}\n"
            f"🏷️ Fase: {event['desPhase']}"
        )

    def add_tracking(self, tracking_number: str) -> str:
        """Añade un nuevo número de seguimiento y devuelve su estado actual"""
        if tracking_number in self.tracking_numbers:
            return f"El envío <code>{tracking_number}</code> ya está en seguimiento."
        
        current_data = self.get_shipment_status(tracking_number)
        
        if not current_data or 'shipment' not in current_data or not current_data['shipment']:
            return f"❌ No se pudo obtener información para el envío <code>{tracking_number}</code>"

        shipment_info = current_data['shipment'][0]
        events = shipment_info.get('events', [])
        
        if not events:
            return f"❌ No hay eventos disponibles para el envío <code>{tracking_number}</code>"

        # Añadir a seguimiento
        self.tracking_numbers.add(tracking_number)
        self.tracked_shipments[tracking_number] = events[-1]
        self.save_data()
        
        # Devolver estado actual
        return (
            f"✅ Envío añadido al seguimiento:\n\n"
            f"{self.format_status_message(tracking_number, events)}"
        )

    def remove_tracking(self, tracking_number: str) -> str:
        """Elimina un número de seguimiento"""
        if tracking_number in self.tracking_numbers:
            self.tracking_numbers.remove(tracking_number)
            self.tracked_shipments.pop(tracking_number, None)
            self.save_data()
            return f"✅ El envío <code>{tracking_number}</code> ha sido eliminado del seguimiento."
        return f"❌ El envío <code>{tracking_number}</code> no estaba en seguimiento."

    def list_tracking(self) -> str:
        """Lista todos los envíos en seguimiento"""
        if not self.tracking_numbers:
            return "No hay envíos en seguimiento."
        
        message = ["📋 Envíos en seguimiento:"]
        for number in sorted(self.tracking_numbers):
            message.append(f"- <code>{number}</code>")
        return "\n".join(message)

    def check_updates(self) -> None:
        """Verifica actualizaciones para todos los envíos en seguimiento"""
        for tracking_number in list(self.tracking_numbers):
            current_data = self.get_shipment_status(tracking_number)
            
            if not current_data or 'shipment' not in current_data or not current_data['shipment']:
                continue

            shipment_info = current_data['shipment'][0]
            events = shipment_info.get('events', [])
            
            if not events:
                continue

            latest_event = events[-1]
            stored_event = self.tracked_shipments.get(tracking_number)

            # Si es nuevo o hay actualización
            if not stored_event or (stored_event['eventDate'] != latest_event['eventDate'] or 
                                  stored_event['eventTime'] != latest_event['eventTime']):
                
                # Actualizar último evento conocido
                self.tracked_shipments[tracking_number] = latest_event
                self.save_data()
                
                # Enviar notificación de actualización
                message = self.format_update_message(tracking_number, latest_event)
                self.send_telegram_message(message)

                # Si el envío está entregado, mostrar botón para eliminarlo
                if self.is_delivered(latest_event):
                    remove_message = (
                        f"📬 ¡El envío <code>{tracking_number}</code> ha sido entregado!\n\n"
                        f"¿Quieres dejar de seguir este envío?"
                    )
                    keyboard = self.create_remove_keyboard(tracking_number)
                    self.send_telegram_message(remove_message, keyboard)

    def process_command(self, command: str, args: str) -> Optional[str]:
        """Procesa comandos de Telegram"""
        if command == "/help":
            return (
                "Comandos disponibles:\n"
                "/add NUMERO - Añade un envío al seguimiento\n"
                "/remove NUMERO - Elimina un envío del seguimiento\n"
                "/status NUMERO - Muestra el estado actual de un envío\n"
                "/list - Lista todos los envíos en seguimiento\n"
                "/help - Muestra esta ayuda"
            )
        elif command == "/add" and args:
            return self.add_tracking(args.strip())
        elif command == "/remove" and args:
            return self.remove_tracking(args.strip())
        elif command == "/status" and args:
            return self.get_current_status(args.strip())
        elif command == "/list":
            return self.list_tracking()
        return None

    def get_current_status(self, tracking_number: str) -> str:
        """Obtiene el estado actual de un envío"""
        current_data = self.get_shipment_status(tracking_number)
        
        if not current_data or 'shipment' not in current_data or not current_data['shipment']:
            return f"❌ No se pudo obtener información para el envío <code>{tracking_number}</code>"

        shipment_info = current_data['shipment'][0]
        events = shipment_info.get('events', [])
        
        return self.format_status_message(tracking_number, events)

    def get_updates(self) -> List[Dict]:
        """Obtiene actualizaciones de Telegram"""
        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/getUpdates"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json().get('result', [])
        except requests.RequestException as e:
            self.logger.error(f"Error al obtener actualizaciones de Telegram: {e}")
            return []

def main():
    if TELEGRAM_BOT_TOKEN == "TU_BOT_TOKEN" or TELEGRAM_CHAT_ID == "TU_CHAT_ID":
        print("Error: Debes configurar TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID en el archivo config.py")
        sys.exit(1)
        
    # Inicializar tracker
    tracker = CorreosTracker()
    
    print(f"Bot iniciado. Intervalo de verificación: {CHECK_INTERVAL} segundos")
    print("Presiona Ctrl+C para detener")
    
    last_update_id = 0
    last_check_time = 0
    
    try:
        while True:
            current_time = time.time()
            
            # Procesar actualizaciones de Telegram (comandos y callbacks)
            updates = tracker.get_updates()
            for update in updates:
                if update['update_id'] > last_update_id:
                    last_update_id = update['update_id']
                    
                    # Manejar callback queries (botones)
                    if 'callback_query' in update:
                        tracker.handle_callback_query(update['callback_query'])
                    
                    # Manejar comandos
                    elif 'message' in update and 'text' in update['message']:
                        text = update['message']['text']
                        if text.startswith('/'):
                            command_parts = text.split(maxsplit=1)
                            command = command_parts[0].lower()
                            args = command_parts[1] if len(command_parts) > 1 else ""
                            
                            response = tracker.process_command(command, args)
                            if response:
                                tracker.send_telegram_message(response)
            
            # Verificar actualizaciones de envíos cada CHECK_INTERVAL segundos
            if current_time - last_check_time >= CHECK_INTERVAL:
                tracker.check_updates()
                last_check_time = current_time
            
            # Pequeña pausa para no saturar la CPU
            time.sleep(COMMAND_CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nDetención solicitada. Guardando datos...")
        tracker.save_data()
        print("Finalizado.")
        sys.exit(0)

if __name__ == "__main__":
    main()