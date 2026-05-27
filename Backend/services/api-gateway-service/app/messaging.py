"""Módulo de mensajería para publicar y consumir eventos en RabbitMQ."""

import json
import os
import threading
import time
from datetime import datetime, timezone
from typing import Callable, Iterable

import pika

# Configuracion del exchange y la conexion a RabbitMQ.
EXCHANGE_NAME = "novalink.events"
EXCHANGE_TYPE = "topic"
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")


def _utc_now_iso() -> str:
    """Obtiene timestamp UTC en formato ISO 8601."""
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _connect() -> pika.BlockingConnection:
    """Crea la conexion con RabbitMQ usando la URL configurada."""
    return pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))


def publish_event(
    event_type: str,
    data: dict,
    *,
    version: str = "v1",
    correlation_id: str | None = None,
) -> None:
    """Publica un evento en el exchange topic de RabbitMQ."""
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
    """Inicia un consumidor en segundo plano para la cola especificada."""

    def _run() -> None:
        while True:
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
                    try:
                        payload = json.loads(body)
                        handler(payload)
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                    except Exception as exc:
                        print(f"[gateway] handler error: {exc}")
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

                channel.basic_qos(prefetch_count=1)
                channel.basic_consume(queue=queue_name, on_message_callback=_on_message)
                channel.start_consuming()
            except Exception as exc:
                print(f"[gateway] consumer error: {exc}")
                time.sleep(5)

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
