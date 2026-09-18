from __future__ import annotations

import enum
"""
    git update-index --assume-unchanged .idea/workspace.xml
    
    git status
    git add src/
"""

class ObjectToSave:
    """
        Основной класс, от которого будут наследоваться все сущности, которые
        нужно сохранить. Конвертируем структуры в словари, совместимые с json.
    """
    def _enums_to_int(self, val):
        """
            Рекурсивно превращает Enums и объекты в базовые типы (int, str, dict).
        """
        # если тут стоит функция, то не будем ее сохранять
        if callable(val):
            return None

        # если в поле только одно значение
        if isinstance(val, enum.Enum):
            return val.value

        # если в поле массив значений, мало ли.
        if isinstance(val, list):
            return [self._enums_to_int(item) for item in val]

        # если в полне словарь значений, тоже есть такое
        if isinstance(val, dict):
            return {self._enums_to_int(k): self._enums_to_int(v) for k, v in val.items()}

        # если мы нашли объект, у которого уже есть свой собственный метод
        if hasattr(val, "to_dict"):
            return val.to_dict()

        # если тут обычное число
        return val

    def to_dict(self):
        """
            собираем все поля объекта в один словарь со сложной структурой
        """
        result = dict()

        # Собираем ВСЕ слоты из всей иерархии классов
        all_slots = set() #чтобы не добавлять повторные слоты
        # не только по этому классу, но и по родительским
        for cls in self.__class__.__mro__:
            slot_name = getattr(cls, '__slots__', [])
            if isinstance(slot_name, str):
                slot_name = [slot_name]  # оборачиваем строку в список, чтобы не разделялся на буквы
            all_slots.update(slot_name)

        #  теперь проходимся по всем слотам
        for slot_name in all_slots:
            # Проверяем, что атрибут реально существует у объекта
            if hasattr(self, slot_name):
                value = getattr(self, slot_name)
                # просто добавляем значение по ключу в словарь
                result[slot_name] = self._enums_to_int(value)

        return result

    def from_dict(self, data_dict):
        """
            Заполняем данные по объектам, если экземпляр класса не создан, то создаем.
            Допустимые конфигурации - массив или словарь экземпляров, плюс значение
            или значение типа  enum.
        """

        # проверка на возможное отсутствие данных словаря, что-то пошло не так
        if not data_dict:
            return self

        # если нет типа убъекта, то вернем пустой словарь, иначе вернем класс, чтобы
        # использовать для генерации объекта
        types_info = getattr(self, '_TYPES', dict())

        for slot_name, value in data_dict.items():
            # если случилась накладка, мы просто бежим дальше. Не информативно, зато функционально
            #if not hasattr(self, slot_name):
            #    continue

            # получаем поле, или структуру, в которую будем сохранять
            attr_val = getattr(self, slot_name)
            #здесь теперь есть тип объектов, которые входят в класс
            obj_class = types_info.get(slot_name)


            # здесь у нас массив элеменов со сложной структурой скачиваем то
            # что можно
            if isinstance(attr_val, list) and isinstance(value, list) and obj_class:
                attr_val.clear()
                for item_data in value:
                    # создаем объект класса
                    new_object = obj_class().from_dict(item_data)
                    attr_val.append(new_object)

            # здесь проверяем, что объект, который мы проверяем, словарь
            # attr_name - куда пишем данные, value - то, что мы выгрузили
            elif isinstance(attr_val, dict) and isinstance(value, dict) and obj_class:
                attr_val.clear()
                for k_str, list_val in value.items():
                    try:
                        k = int(k_str)
                    except ValueError:
                        k = k_str # если это строка, а не число, есть и такие.
                    new_list = []
                    for opt in list_val:
                        _obj = obj_class()
                        _obj.from_dict(opt)
                        new_list.append(_obj)
                    attr_val[k] = new_list

            # если сложный объект, у которого есть свой собственный метод загрузки
            # его нужно обязательно применить, чтобы скачать нужные параметры
            elif hasattr(attr_val, "from_dict"):
                # если указанный объект имеет метод from_dict, то мы его и используем для загрузки
                # это в случаях, если объект имеет вложенную с руктуру
                attr_val.from_dict(value)

            # здесь просто нечто из  перечисляемого типа
            elif isinstance(attr_val, enum.Enum) and attr_val is not None:
                setattr(self, slot_name, type(attr_val)(value))

            # а это тот случай, когда ручками прописываем загрузку, должно быть просто число
            elif attr_val is None and obj_class:
                new_obj = obj_class().from_dict(value)
                setattr(self, slot_name, new_obj)
            else:
                #print(f"Setting {slot_name} to {value}")
                setattr(self, slot_name, value)

        return self
