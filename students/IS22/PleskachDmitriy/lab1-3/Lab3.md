**Отчёт по лабораторной работе 3**

Цель: научиться использовать векторные базы данных и семантический поиск для обработки текстовых данных и потенциальной интеграции с LLM.

**1. Настройка окружения**

Работа началась с настройки среды: в проект внесли файл requirements.txt и конфигурацию для devcontainer (папка .devcontainer с файлами Dockerfile, devcontainer.json, docker-compose.yml). Это позволило запустить изолированную среду с необходимыми сервисами. Сборка была выполнена командой Dev Containers: Rebuild and Reopen in Container и прошла без ошибок

![](ScrShot\Aspose.Words.d4457806-770e-4b45-8398-f971b12b787a.001.png)
![](ScrShot\Aspose.Words.d4457806-770e-4b45-8398-f971b12b787a.002.png)

**2. Создание векторной базы данных**

Milvus заработал на порте 8000, следующим действием было инициализировать модуль милвуса.

Следующим шагом было добавление клиента для Milvus. В файле milvus\_client.py мы описываем класс MilvusClient, который будет управлять подключением к векторной БД и операциями с ней. Реализация включает в себя: настройку соединения с базой, метод создания коллекции (create\_collection()), метод для вставки данных (insert\_data()) и метод семантического поиска (search()).

from pymilvus import (

`    `connections,

`    `Collection,

`    `CollectionSchema,

`    `FieldSchema,

`    `DataType,

`    `utility

)

from typing import List, Optional

class MilvusClient:



`    `def \_\_init\_\_(

`        `self,

`        `host: str = "standalone",

`        `port: int = 19530,

`        `alias: str = "default"

`    `):

`        `self.host = host

`        `self.port = port

`        `self.alias = alias

`        `self.\_connect()

**3. Парсинг текстовых файлов**

Следующий этап работы был посвящён обработке данных. Были реализованы следующие модули:

text\_parser.py — содержит инструменты для чтения файлов, нормализации и сегментации текста на фрагменты (чанки), включая функцию автоматического парсинга с интегрированным чанкированием.

document\_processor.py — в этом модуле, следуя заданию, был создан класс DocumentProcessor. Изначально он предназначался для обработки отдельных файлов, но затем его функциональность была расширена: добавилась пакетная обработка всех файлов в указанной директории, их чанкирование, генерация эмбеддингов и последующая загрузка в Milvus.

embedder.py — отвечает за создание векторных представлений (эмбеддингов) текста с использованием модели. Для удобства интеграции была также добавлена вспомогательная функция create\_embedding\_function, позволяющая подключить этот функционал к классу DocumentProcessor.

Для демонстрации полного цикла работы системы был создан скрипт example\_usage.py. Он последовательно выполняет подключение к Milvus, создание коллекции, обработку файлов, генерацию эмбеддингов и семантический поиск.

Клиент Milvus (milvus\_client.py) был дополнен полезными методами, такими как получение метаинформации о коллекции, её удаление, извлечение всех фрагментов конкретного документа и возможность восстановления исходного текста. Также в проекте появилась директория files для хранения исходных текстовых документов.

![](Aspose.Words.d4457806-770e-4b45-8398-f971b12b787a.003.png)![](Aspose.Words.d4457806-770e-4b45-8398-f971b12b787a.004.png)

**Задание 1**

Путём раскомментирования параметра gpus: all была добавлена возможность использовать ресурсы видеокарты через CUDA для генерации эмбеддингов.

services:

`  `app:

`    `build:

`      `context: ..

`      `dockerfile: .devcontainer/Dockerfile

`    `container\_name: milvus-lab-app

`    `working\_dir: /workspaces

`    `volumes:

`      `- ../:/workspaces

`    `command: sleep infinity

`    `gpus: all        # чтобы эмбеддер видел видеокарту

`    `depends\_on:

`      `- standalone

`    `networks:

`      `- internal-network

Изображение иллюстрирует ход сборки контейнера. Ключевым моментом является настройка версий PyTorch с CUDA, что обеспечивает возможность выполнения вычислений на графическом процессоре.

![](Aspose.Words.d4457806-770e-4b45-8398-f971b12b787a.005.png)

![](Aspose.Words.d4457806-770e-4b45-8398-f971b12b787a.006.png)** 

**Задание 2**

Задание №2 предусматривало реализацию целостного программного интерфейса (API) для системы Milvus. Разработку начали с инсталляции фреймворка Django и генерации нового Django-проекта project. ![](Aspose.Words.d4457806-770e-4b45-8398-f971b12b787a.007.png)

![](Aspose.Words.d4457806-770e-4b45-8398-f971b12b787a.008.png)



Далее создаётся файл services.py, предназначенный для централизованной инициализации ключевых компонентов системы:

milvus\_client — экземпляр клиента базы данных Milvus, отвечающий за установку соединения и выполнение операций с коллекциями, включая вставку и векторный поиск.

embedder — компонент, преобразующий тексты и поисковые запросы в векторные представления (эмбеддинги).

embedding\_fn — вспомогательная функция-обёртка для интеграции embedder с процессором документов.

document\_processor — основной процессор, который координирует работу системы: парсинг текстовых файлов, генерацию эмбеддингов и последующую загрузку полученных чанков в Milvus.

from core.milvus\_client import MilvusClient

from core.embedder import Embedder, create\_embedding\_function

from core.document\_processor import DocumentProcessor

milvus\_client = MilvusClient(host="standalone", port=19530)

embedder = Embedder(device="cuda")

embedding\_fn = create\_embedding\_function(

`    `model\_name="intfloat/multilingual-e5-base",

`    `batch\_size=32

)

document\_processor = DocumentProcessor(

`    `milvus\_client=milvus\_client,

`    `chunk\_size=256,

`    `chunk\_overlap=64,

`    `embedding\_function=embedding\_fn

)


Для организации API-интерфейса в файле views.py разработаны обработчики запросов. Эти классы (CreateCollectionView, UploadDocumentsView, SemanticSearchView, DocumentChunksView, CollectionInfoView) принимают HTTP-запросы и обеспечивают выполнение соответствующих операций в системе.

В частности, CreateCollectionView отвечает за инициализацию коллекций в Milvus через POST-метод. Корректность передаваемых данных обеспечивается интеграцией с ранее созданным сериализатором CreateCollectionSerializer.

class CreateCollectionView(APIView):

`    `"""Создание коллекции в Milvus"""

`    `def post(self, request):

`        `serializer = CreateCollectionSerializer(data=request.data)

`        `serializer.is\_valid(raise\_exception=True)

`        `data = serializer.validated\_data

`        `if data.get("force\_delete"):

`            `milvus\_client.delete\_collection(data["name"])

`        `collection = milvus\_client.create\_collection(

`            `collection\_name=data["name"],

`            `dimension=data["dimension"],

`            `metric\_type=data["metric\_type"]

`        `)

`        `return Response(

`            `{"message": f"Коллекция '{collection.name}' создана"},

`            `status=status.HTTP\_201\_CREATED

`        `)

UploadDocumentsView (POST): Загружает документы/текст в коллекцию. Использует UploadDocumentsSerializer для валидации. DocumentProcessor выполняет чанкирование, генерацию эмбеддингов и вставку данных в Milvus.

SemanticSearchView (POST): Осуществляет семантический поиск. Запрос валидируется через SearchSerializer, преобразуется в вектор с помощью embedder и отправляется в Milvus для поиска.

DocumentChunksView (GET): Возвращает все чанки документа по указанному пути.

CollectionInfoView (GET): Предоставляет метаинформацию о коллекции (количество записей, существование и др.).

from django.urls import path

from .views import (

`    `CreateCollectionView,

`    `UploadDocumentsView,

`    `SemanticSearchView,

`    `CollectionInfoView,

`    `DocumentChunksView

)

urlpatterns = [

`    `path("collections/create/", CreateCollectionView.as\_view()),

`    `path("collections/<str:name>/info/", CollectionInfoView.as\_view()),

`    `path("documents/upload/", UploadDocumentsView.as\_view()),

`    `path("documents/<str:collection\_name>/chunks/<path:file\_path>/",

`         `DocumentChunksView.as\_view()),

`    `path("search/", SemanticSearchView.as\_view()),

]

Далее настраивается маршрутизация в файле urls.py. Каждый добавленный путь сопоставляет URL с конкретной функцией представления:

Для создания коллекции: collections/create/

Для просмотра информации о коллекции: collections/<str:name>/info/

Для загрузки документов: documents/upload/ 

Для семантического поиска: search/

![](Aspose.Words.d4457806-770e-4b45-8398-f971b12b787a.009.png)

Итогом лабораторной работы стало создание законченной системы для семантического поиска на базе Milvus. Работа велась поэтапно: от конфигурации Docker-окружения и реализации низкоуровневых операций с векторной БД (клиент, парсинг, векторизация) до разработки удобного REST API на Django. Созданное API (3 POST- и 2 GET-метода) покрывает все основные сценарии: администрирование коллекций, загрузку и подготовку текстовых данных, выполнение поисковых запросов. Полнота решения подтверждена демонстрационным скриптом example\_usage.py и успешным тестированием всех функций, включая работу с GPU.

Таким образом, в процессе работы были закреплены ключевые компетенции в области векторных баз данных, обработки естественного языка и создания веб-сервисов. Поставленные цели выполнены полностью.

