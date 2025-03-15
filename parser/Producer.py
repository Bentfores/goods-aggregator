from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField

class KafkaAvroProducer:
    def __init__(self, kafka_broker: str, schema_registry_url: str, topic: str, schema_path: str):
        self.topic = topic

        # Инициализация клиента Schema Registry
        self.schema_registry_client = SchemaRegistryClient({"url": schema_registry_url})

        # Загружаем Avro-схему из файла
        with open(schema_path, "r") as f:
            self.schema_str = f.read()

        # Создаём сериализаторы
        self.avro_serializer = AvroSerializer(self.schema_registry_client, self.schema_str)
        self.key_serializer = StringSerializer("utf_8")

        # Конфигурация Kafka-продюсера
        self.producer = Producer({"bootstrap.servers": kafka_broker})

    def delivery_report(self, err, msg):
        """Функция обратного вызова для проверки отправки сообщений"""
        if err is not None:
            print(f"Ошибка при отправке сообщения: {err}")
        else:
            print(f"Сообщение отправлено в {msg.topic()} [{msg.partition()}] с offset {msg.offset()}")

    def send(self, data):
        """Метод для отправки массива данных в Kafka"""
        self.producer.produce(
            topic=self.topic,
            key="product-batch",
            value=self.avro_serializer({"products": data}, SerializationContext(self.topic, MessageField.VALUE)),
            callback=self.delivery_report
        )
        self.producer.flush()  # Ожидание завершения всех отправок
