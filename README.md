# cfast-inkex
## Расширение редактора вектороной графики Inkscape по вводу цифровой модели здания для программы CFAST

### Системные требования
1) Inkscape >= 1.0.0
2) CFAST >= 7.6
3) Python >= 3.5

### Установка
1) Скачайте файлы плагина из репозитория ([zip-архив](https://github.com/bvchirkov/cfast-inkex/archive/refs/heads/master.zip))
2) Раскапуйте архив и поместите файлы в дирректорию, указанную в `Правка > Параметры > Система: Пользовательские расширения`
3) Перезапустите Inkscape

----

## Использование
Ввод осуществляется по этажам. Каждый этаж является группой слоев.

![](https://raw.githubusercontent.com/bvchirkov/imgs/main/cfast_inkex_layers_tree.png)

### Именование слоев
Имя слоя этажа: `Level*`, где `*` -- номер этажа.

Внутри слоя этажа может находится сколько угодно слоев, но информация извлекается только со слоев с именами `rooms*` (помещения) и `doors*` (двери).

### Область ввода
Все элементы здания должны располагаться выше оси X и правее оси Y, которые установлены на нулевой отметке.

![](https://raw.githubusercontent.com/bvchirkov/imgs/main/cfast_inkex_area.png)

Установить такие оси возможно с помощью направляющих линий.

![](https://raw.githubusercontent.com/bvchirkov/imgs/main/cfast_inkex_guides2.gif)

### Ввод здания
Порядок ввода помещений и дверей не регламентируется. 
Важно соблюдать принадлежность объектов слоям: двери должны быть на слое с дверям, помещения на слое с помещениями.

Ввод осуществляется только инструментом `Прямоугольник`. 

Тип, толщина и цвет линий не влияют и могут быть выбраны произвольными.

Дверь создается на границе помещений. Для связки двух помещений дверь должна двумя углами находится в одном помещении, а двумя в другом. 
Для свзяки помещения и "улицы": два угла в помещении, два за его пределами.

__Приведет к ошибке__:
1) пересечение помещений
2) персечение дверей
3) пересечение дверью более двух помещений

### Привязка масштаба
Для привязки масштаба выделите помещение, для которого знате реальный размер. Вызовите инструмент привязки `Расширения > CFAST > Привязка геометрии...`
и укажите соответсвующие значения в метрах.

Данную операцию необходимо выполнить для каждого этажа. Новая приявзка на одном этаже переопределяет предыдущую.

### Смещение этажей

Для получения этажей друг над другом, необходимо выполнит операцию `Привязка уровней`. 

Выберите слой `rooms` этажа, который является *ориентиром*. Создайте окружность с центром в точке, к которой будет осуществляться привязка. 
Повторите это действие для следующего этажа, который следут сместить.

Порядок выделения: 1) нижний слой (ориентир), 2) верхний слой (смещаемый).

1) Ориентиром всегда является нижний слой.
2) Выделять можно только следующие друг за другом.

Вызовите инструмент `Расширения > CFAST > Привязка уровней...`, выберите действие (*привязать/отвязать*) и нажмите кнопку подтвеждения операции **Применить**.

### Экспорт в формате CFAST
`Файл > Сохранить как... > CFATS geometry (*in)` и выберите папку для сохранения.

Перед сохранением необходимо убедиться, что выполнена установка масштаба на каждом этаже.
