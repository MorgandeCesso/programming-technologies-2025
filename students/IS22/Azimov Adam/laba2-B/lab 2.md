# Отчёт по Лабораторной работе №2

**Тема:** Обучение сверточной нейронной сети на CIFAR-100, сравнение стратегий уменьшения размерности (stride / max pooling / avg pooling), выбор лучшей модели и экспорт в ONNX.

## 1. Цель работы

1. Обучить CNN на выбранных классах CIFAR-100 с использованием GPU.
2. Провести 3 обучения с разными вариантами “пуллинга”:

- уменьшение размерности через **stride** (свёртка с шагом),
- **MaxPooling**,
- **AvgPooling**.

3. Сравнить качество, время обучения и переобучение.
4. Выбрать лучшую конфигурацию, сохранить модель и экспортировать в ONNX.
5. Проверить корректность ONNX-модели через `onnxruntime`.

## 2. Подготовка окружения и данных

### 2.1. Настройка окружения

Подключены основные библиотеки PyTorch, NumPy, инструменты визуализации и пакеты для ONNX:

```python
!pip install onnx onnxscript
!pip install torchsummary onnx onnxruntime
```

### 2.2. Использование GPU

Для ускорения обучения проверена доступность GPU (`!nvidia-smi`) и выбран `device`:

```python
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
```

Все вычисления выполняются на GPU через `.to(device)`.

### 2.3. Загрузка CIFAR-100 и выбор классов

Данные CIFAR-100 скачиваются и распаковываются:

```python
!wget -q https://www.cs.toronto.edu/~kriz/cifar-100-python.tar.gz
!tar -xzf cifar-100-python.tar.gz
```

Выбранные классы по варианту:

Согласно варианту, были выбраны 3 класса из набора данных CIFAR-100:
Класс № [Номер группы + 11] = [Название класса]
Класс № [Номер варианта + 37] = [Название класса]
Класс № [Произвольный третий класс] = [Название класса]

```
GROUP = 22
VARIANT = 1
CLASSES = [GROUP + 11, VARIANT + 37]
```

Пример изображения из выборки CIFAR100:

![alt text](images/image_6.png)

## 4. Архитектура CNN и варианты уменьшения размерности

### 4.1. Нормализация

В модель добавлен слой `Normalize`:

- перевод значений пикселей из `0..255` в `0..1`
- нормализация по mean/std CIFAR-100
- преобразование NHWC → NCHW (как требует `Conv2d`)

```python
x = input / 255.0
x = (x - self.mean) / self.std
return x.permute(0, 3, 1, 2)
```

### 4.2. CNN-модель

Модель `Cifar100_CNN` состоит из следующих последовательно соединённых слоёв:

```python
class Cifar100_CNN(nn.Module):
    def __init__(self, hidden_size=32, classes=100):
        super(Cifar100_CNN, self).__init__()
        self.seq = nn.Sequential(
            Normalize([0.5074,0.4867,0.4411],[0.2011,0.1987,0.2025]),
            nn.Conv2d(3, hidden_size, 5, stride=4, padding=2),
            nn.ReLU(),
            nn.Conv2d(hidden_size, hidden_size*2, 3, stride=1, padding=1),
            nn.ReLU(),
            nn.AvgPool2d(4),
            nn.Flatten(),
            nn.Linear(hidden_size*8, classes),
        )
    def forward(self, input):
        return self.seq(input)
```

Модель Cifar100_CNN представляет собой компактную сверточную нейронную сеть, специально разработанную для классификации изображений из датасета CIFAR-100.Архитектура состоит из последовательно соединённых слоёв.

Первый сверточный слой использует ядро 5×5 со stride=4 для значительного уменьшения размерности, а второй слой с ядром 3×3 и stride=1 служит для извлечения более детальных признаков. Модель демонстрирует эффективное сочетание методов уменьшения размерности через stride и пуллинг, что позволяет обрабатывать изображения 32×32 пикселя с минимальным количеством параметров.

### 4.1 Выбор функции потерь и оптимизатора градиентного спуска

```python
criterion = nn.CrossEntropyLoss()
# используется SGD c momentum
optimizer = optim.SGD(model.parameters(), lr=5e-3, momentum=0.9)
```

Для обучения модели была выбрана функция потерь CrossEntropyLoss.
В качестве оптимизатора использовался Stochastic Gradient Descent (SGD) с моментом 0.9 и скоростью обучения 5e-3, что позволяет плавно обновлять веса модели.

### 4.1 Обучение модели по эпохам

```python
EPOCHS = 500
REDRAW_EVERY = 20
steps_per_epoch = len(dataloader['train'])
steps_per_epoch_val = len(dataloader['test'])
# NEW
pbar = tqdm(total=EPOCHS*steps_per_epoch)
losses = []
losses_val = []
passed = 0
for epoch in range(EPOCHS):  # проход по набору данных несколько раз
    #running_loss = 0.0
    tmp = []
    model.train()
    for i, batch in enumerate(dataloader['train'], 0):
        # получение одного минибатча; batch это двуэлементный список из [inputs, labels]
        inputs, labels = batch
        # на GPU
        inputs, labels = inputs.to(device), labels.to(device)

        # очищение прошлых градиентов с прошлой итерации
        optimizer.zero_grad()

        # прямой + обратный проходы + оптимизация
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        #loss = F.cross_entropy(outputs, labels)
        loss.backward()
        optimizer.step()

        # для подсчёта статистик
        #running_loss += loss.item()
        accuracy = (labels.detach().argmax(dim=-1)==outputs.detach().argmax(dim=-1)).\
                    to(torch.float32).mean().cpu()*100
        tmp.append((loss.item(), accuracy.item()))
        pbar.update(1)
    #print(f'[{epoch + 1}, {i + 1:5d}] loss: {running_loss / steps_per_epoch:.3f}')
    losses.append((np.mean(tmp, axis=0),
                   np.percentile(tmp, 25, axis=0),
                   np.percentile(tmp, 75, axis=0)))
    #running_loss = 0.0
    tmp = []
    model.eval()
    with torch.no_grad(): # отключение автоматического дифференцирования
        for i, data in enumerate(dataloader['test'], 0):
            inputs, labels = data
            # на GPU
            inputs, labels = inputs.to(device), labels.to(device)

            outputs = model(inputs)
            loss = criterion(outputs, labels)
            #running_loss += loss.item()
            accuracy = (labels.argmax(dim=-1)==outputs.argmax(dim=-1)).\
                        to(torch.float32).mean().cpu()*100
            tmp.append((loss.item(), accuracy.item()))
    #print(f'[{epoch + 1}, {i + 1:5d}] val loss: {running_loss / steps_per_epoch_val:.3f}')
    losses_val.append((np.mean(tmp, axis=0),
                       np.percentile(tmp, 25, axis=0),
                       np.percentile(tmp, 75, axis=0)))
    if (epoch+1) % REDRAW_EVERY != 0:
        continue
    clear_output(wait=False)
    passed += pbar.format_dict['elapsed']
    pbar = tqdm(total=EPOCHS*steps_per_epoch, miniters=5)
    pbar.update((epoch+1)*steps_per_epoch)
    x_vals = np.arange(epoch+1)
    _, ax = plt.subplots(1, 2, figsize=(15, 5))
    stats = np.array(losses)
    stats_val = np.array(losses_val)
    ax[1].set_ylim(stats_val[:, 0, 1].min()-5, 100)
    ax[1].grid(axis='y')
    for i, title in enumerate(['CCE', 'Accuracy']):
        ax[i].plot(x_vals, stats[:, 0, i], label='train')
        ax[i].fill_between(x_vals, stats[:, 1, i],
                           stats[:, 2, i], alpha=0.4)
        ax[i].plot(x_vals, stats_val[:, 0, i], label='val')
        ax[i].fill_between(x_vals,
                           stats_val[:, 1, i],
                           stats_val[:, 2, i], alpha=0.4)
        ax[i].legend()
        ax[i].set_title(title)
    plt.show()
print('Обучение закончено за %s секунд' % passed)
```

### 4.1 Результат обучения

![alt text](images/image_1.png)
![alt text](images/image_2.png)

На тренировочных данных модель достигла идеальных результатов (accuracy 1.000), что указывает на возможное переобучение.
На тестовых данных точность снизилась до 0.885, что демонстрирует хорошую, но не идеальную обобщающую способность.

## 5. Что сравнивается: stride / max / avg

### 5.1 Пуллинг с помощью шага свёртки stride

- Это увеличение шага в свёрточном слое: фильтр перепрыгивает через пиксели, пропуская информацию между ними для быстрого уменьшения размерности.

```python
class Cifar100_CNN_Stride(nn.Module):
    def __init__(self, hidden_size=32, classes=len(CLASSES)):
        super().__init__()  # Важно!
        self.seq = nn.Sequential(
            Normalize([0.5074,0.4867,0.4411],[0.2011,0.1987,0.2025]),
            nn.Conv2d(3, hidden_size, 5, stride=4, padding=2),  # 32→8
            nn.ReLU(),
            nn.Conv2d(hidden_size, hidden_size*2, 3, stride=1, padding=1),  # 8→8
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(hidden_size*2 * 8 * 8, classes),
        )

    def forward(self, x):
        return self.seq(x)
```

Ниже представлен график кривые обучения свёрточной нейронной сети при использовании шага свёртки в качестве метода уменьшения размерности через stride

![alt text](images/image_stride_1.png)

По графикам функции потерь и точности видно, что модель очень быстро сходится на обучающей выборке: значение функции потерь стремится к нулю, а точность достигает 100%. При этом на валидационной выборке наблюдается рост значения функции потерь после начального снижения и стабилизация точности на уровне около 88%. Это свидетельствует о выраженном переобучении модели, обусловленном уменьшением размерности изображения за счёт увеличенного шага свёртки, что приводит к потере части пространственной информации.

Время обучения:

- Обучение закончено за 27.61451745033264 секунд

Результат обучения
![alt text](images/image_stride_2.png)

Из таблицы классификационных метрик видно, что на обучающей выборке модель демонстрирует идеальные показатели точности, полноты и F1-меры для всех классов. Однако на тестовой выборке общая точность снижается до 88%, при этом качество классификации заметно различается между классами. Наиболее слабые результаты наблюдаются для одного из классов, что подтверждает низкую обобщающую способность модели при использовании уменьшения размерности через шаг свёртки.

### 5.1 Макс-пуллинг (Max Pooling)

- Это отдельный слой, который берёт квадрат пикселей и оставляет только самый яркий/важный, выбрасывая всё остальное.

```python
class Cifar100_CNN_MaxPool(nn.Module):
    def __init__(self, hidden_size=32, classes=len(CLASSES)):
        super().__init__()
        self.seq = nn.Sequential(
            Normalize([0.5074,0.4867,0.4411],[0.2011,0.1987,0.2025]),
            nn.Conv2d(3, hidden_size, 5, padding=2),
            nn.ReLU(),
            nn.MaxPool2d(2),  # MaxPool
            nn.Conv2d(hidden_size, hidden_size*2, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),  # MaxPool
            nn.Flatten(),
            nn.Linear(hidden_size*2*8*8, classes),
        )
    def forward(self, input):
      return self.seq(input)
```

- Ниже представлен график кривые обучения свёрточной нейронной сети при использовании MaxPooling

![alt text](images/image_maxpool_1.png)

Графики показывают устойчивое снижение функции потерь и рост точности на обучающей выборке до 100%. На валидационной выборке значение функции потерь остаётся значительно ниже по сравнению с вариантом со stride, а точность стабилизируется на уровне 92–94%. Разрыв между обучающей и тестовой кривыми выражен слабее, что указывает на более эффективное обобщение и меньшую степень переобучения при использовании MaxPooling.

Время обучения:

- Обучение закончено за 43.329933881759644 секунд

Результат обучения
![alt text](images/image_maxpool_2.png)

Таблица классификационных метрик подтверждает высокое качество модели с MaxPooling: на тестовой выборке достигается точность 93%, а значения precision, recall и F1-меры являются высокими и более равномерными для всех классов по сравнению с первым вариантом. Это указывает на способность MaxPooling сохранять наиболее значимые признаки изображения и повышать устойчивость модели к вариациям входных данных.

### 5.1 Усредняющий пуллинг (Average Pooling)

- Это отдельный слой, который берёт квадрат пикселей и вычисляет их среднее значение, сохраняя общую картину.

```python
class Cifar100_CNN_AvgPool(nn.Module):
    def __init__(self, hidden_size=32, classes=100):
        super().__init__()
        self.seq = nn.Sequential(
            Normalize([0.5074,0.4867,0.4411],[0.2011,0.1987,0.2025]),
            nn.Conv2d(3, hidden_size, kernel_size=5, stride=1, padding=2),
            nn.ReLU(),
            nn.Conv2d(hidden_size, hidden_size*2, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.AvgPool2d(kernel_size=4),
            nn.Flatten(),
            nn.Linear(hidden_size*2 * 8 * 8, classes),
        )

    def forward(self, x):
        return self.seq(x)
```

- Ниже представлен график кривые обучения свёрточной нейронной сети при использовании AveragePooling

![alt text](images/image_avgpool_1.png)

На графиках обучения видно, что модель с AveragePooling также успешно обучается и достигает высокой точности на обучающей выборке. Однако значение функции потерь на валидационной выборке выше и демонстрирует более заметные колебания по сравнению с вариантом с MaxPooling. Это свидетельствует о том, что усредняющий пуллинг приводит к сглаживанию признаков, что снижает способность модели выделять наиболее информативные детали изображения.
Время обучения:

- Обучение закончено за 67.91825485229492 секунд

Результат обучения
![alt text](images/image_avgpool_2.png)

Из таблицы метрик следует, что модель с AveragePooling демонстрирует точность 88 .50% на тестовой выборке, что сопоставимо с вариантом MaxPooling. Тем не менее, значения F1-меры по отдельным классам несколько ниже и менее устойчивы, что указывает на более слабое выделение ключевых признаков при использовании усредняющего пуллинга по сравнению с максимальным.

## Вывод

В ходе лабораторной работы была разработана и обучена свёрточная нейронная сеть для классификации изображений датасета CIFAR-100 по трём выбранным классам с использованием графического ускорителя. Были исследованы три способа уменьшения пространственной размерности карт признаков: с помощью шага свёртки, MaxPooling и AveragePooling. Экспериментальные результаты показали, что уменьшение размерности через шаг свёртки обеспечивает более быстрое обучение, однако приводит к выраженному переобучению и снижению обобщающей способности модели. Использование усредняющего пуллинга позволяет получить более стабильное обучение, но уступает по точности классификации. Наилучшие результаты по качеству и устойчивости модели были достигнуты при использовании MaxPooling, что обусловлено сохранением наиболее значимых признаков изображения и снижением влияния шума.
