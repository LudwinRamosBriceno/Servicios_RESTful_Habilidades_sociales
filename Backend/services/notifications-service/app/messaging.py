import json
import os
import threading
import time
from datetime import datetime, timezone
from typing import Callable, Iterable

import pika

# Nombre del intercambio de eventos utilizado para publicar y consumir mensajes.
EXCHANGE_NAME = "novalink.events" 

# Tipo de intercambio utilizado en RabbitMQ, en este caso se utiliza "topic" para permitir el enrutamiento basado en patrones de clave de enrutamiento.
EXCHANGE_TYPE = "topic"

# URL de conexión a RabbitMQ, se obtiene de la variable de entorno RABBITMQ_URL o se utiliza un valor predeterminado si no está configurada.
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")


def _utc_now_iso() -> str:
    """
    Obtiene la fecha y hora actual en formato ISO 8601 con zona horaria UTC, sin microsegundos,
    y con el sufijo 'Z' para indicar UTC.
    """
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _connect() -> pika.BlockingConnection:
    """
    Establece una conexión con RabbitMQ utilizando la URL de conexión configurada.
    """
    return pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))


def publish_event(event_type: str, data: dict, *, version: str = "v1", correlation_id: str | None = None) -> None:
    """
    Publica un evento en RabbitMQ con el tipo de evento, los datos asociados, la versión del evento y un ID de correlación opcional.
    El evento se publica en el intercambio definido por EXCHANGE_NAME utilizando el tipo de evento como clave de enrutamiento.
    """
    event = {
        "event_type": event_type,
        "version": version,
        "timestamp": _utc_now_iso(),
        "data": data,
    }
    connection = _connect()
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type=EXCHANGE_TYPE, durable=True)
    props = pika.BasicProperties(
        content_type="application/json",
        delivery_mode=2,
        correlation_id=correlation_id,
    )
    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=event_type,
        body=json.dumps(event).encode("utf-8"),
        properties=props,
    )
    connection.close()


def start_consumer(queue_name: str, routing_keys: Iterable[str], handler: Callable[[dict], None]) -> None:
    """
    Inicia un consumidor de mensajes de RabbitMQ.
    """
    def _run() -> None:
        """
        Función interna que se ejecuta en un hilo separado para consumir mensajes de RabbitMQ.
        Se conecta a RabbitMQ, declara el intercambio y la cola, y se suscribe a los mensajes que coincidan con las claves de enrutamiento especificadas.
        Cuando se recibe un mensaje, se llama al controlador proporcionado para procesar el mensaje.
        """
        while True:
            # Intenta establecer la conexión y consumir mensajes.
            try:
                connection = _connect()
                channel = connection.channel()
                channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type=EXCHANGE_TYPE, durable=True)
                channel.queue_declare(queue=queue_name, durable=True)
                for key in routing_keys:
                    channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name, routing_key=key)

                def _on_message(ch, method, _properties, body) -> None:
                    """
                    Maneja un mensaje recibido, procesándolo con el handler proporcionado y confirmando o rechazando el mensaje según corresponda.
                    """
                    try:
                        payload = json.loads(body)
                        handler(payload)
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                    except Exception as exc:
                        print(f"[messaging] handler error: {exc}")
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

                # Configura el consumidor para procesar un mensaje a la vez y comienza a consumir mensajes de la cola.
                channel.basic_qos(prefetch_count=1)
                channel.basic_consume(queue=queue_name, on_message_callback=_on_message)
                channel.start_consuming()

            # Si ocurre cualquier error durante la conexión o el consumo de mensajes, se captura la excepción, se imprime un mensaje de error
            # y se espera 5 segundos antes de intentar reconectar.    
            except Exception as exc:
                print(f"[messaging] consumer error: {exc}")
                time.sleep(5)

    # Inicia el consumidor en un hilo separado para que pueda ejecutarse en segundo plano sin bloquear el hilo principal de la aplicación.
    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
