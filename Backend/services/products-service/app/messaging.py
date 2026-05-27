"""Módulo de mensajería para publicar y consumir eventos en RabbitMQ."""

import json
import os
import threading
import time
from datetime import datetime, timezone
from typing import Callable, Iterable

import pika

EXCHANGE_NAME = "novalink.events"
EXCHANGE_TYPE = "topic"
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")


def _utc_now_iso() -> str:
    """Obtiene la hora actual en formato ISO 8601."""
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _connect() -> pika.BlockingConnection:
    """Crea una conexión a RabbitMQ con la URL configurada."""
    return pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))


def publish_event(
    event_type: str,
    data: dict,
    *,
    version: str = "v1",
    correlation_id: str | None = None,
) -> None:
    """Publica un evento en el exchange de RabbitMQ."""
    event = {
        "event_type": event_type,
        "version": version,
        "timestamp": _utc_now_iso(),
        "data": data,
    }
    connection = _connect()
    channel = connection.channel()
    channel.exchange_declare(
        exchange=EXCHANGE_NAME, exchange_type=EXCHANGE_TYPE, durable=True
    )
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


def start_consumer(
    queue_name: str, routing_keys: Iterable[str], handler: Callable[[dict], None]
) -> None:
    """Inicia un consumidor de RabbitMQ en un hilo separado."""

    def _run() -> None:
        """Ejecuta el consumidor de RabbitMQ."""
        while True:
            # Intenta conectarse a RabbitMQ y consumir mensajes.
            try:
                connection = _connect()
                channel = connection.channel()
                channel.exchange_declare(
                    exchange=EXCHANGE_NAME, exchange_type=EXCHANGE_TYPE, durable=True
                )
                channel.queue_declare(queue=queue_name, durable=True)
                for key in routing_keys:
                    channel.queue_bind(
                        exchange=EXCHANGE_NAME, queue=queue_name, routing_key=key
                    )

                def _on_message(ch, method, _properties, body) -> None:
                    """Procesa el mensaje y confirma o rechaza segun corresponda."""
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

            # Si ocurre un error en la conexión o el consumo de mensajes,
            # imprime el error y espera 5 segundos antes de intentar reconectar.
            except Exception as exc:
                print(f"[messaging] consumer error: {exc}")
                time.sleep(5)

    # Inicia el consumidor en un hilo separado para que no bloquee la ejecución principal del servicio.
    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
