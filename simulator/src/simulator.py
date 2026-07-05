import sys, pathlib
import multiprocessing
import time
import random
from scipy.constants import golden_ratio as gr
from prettytable import PrettyTable
"""!
   @brief Вспомогательная функция exam_proc.
   @detail Функция, которая случайным образом выбирает три разных вопроса из
        банка вопросов.
   @param questions_array - полный список всех вопросов.
   @return список из трех случайных вопросов под разными номерами из банка вопросов.
"""
def question_list_former(questions_array):
    selected = random.sample(questions_array, 3)
    return selected

"""!
   @brief Определение класса QUESTION.
   @detail В качестве параметров класса выступает списки вопросов q_list, каждый из
        которых представляет собой список слов и список длин слов каждого вопроса
        q_size. Оба списка формируются после инициализации экземпляров класса.
"""

class QUESTION:
    def __init__(self, name, q_id):
        self.name = name
        self.id = q_id

"""!
   @brief Определение класса STUDENT.
   @detail В качестве атрибутов класса выступают имя студента(name), его пол(sex) и номер
    в общей очереди(id).  
"""
class STUDENT:
    def __init__(self, name, sex, st_id):
        self.name = name
        self.sex = sex
        self.id = st_id

"""!
   @brief Определение класса EXAMINER.
   @detail В качестве параметров класса выступают name - имя преподавателя, id - номер
        в списке, sex - пол преподавателя, student - имя экзаменуемого студента,
        st_num - число студентов, которые сдавали экзамен данному преподавателю, а
        lose_st_num - число студентов, заваливших экзамен данному преподавателю.
        Метод change_student("Имя_студента") используется для сохранения имени студента,
        сдающего экзамен в данный момент.
        Метод fix_st_res(result) в случае, когда результат сдачи result = "Провалил"
        параметр lose_st_num увеличивается на единицу, в случае result = "Сдал" указанный
        параметр остается неизменным.
        Метод is_pause(flag) утстанавличается значение параметра student равное "-", если
        flag = True.
"""
class EXAMINER:
    def __init__(self, name, sex, ex_id):
        self.name = name
        self.id = ex_id
        self.sex = sex
        self.student = '-'
        self.st_num = 0
        self.lose_st_num = 0
    def change_student(self, name):
        self.student = name
        self.st_num += 1
    def fix_st_res(self, _result):
        if _result == 'Провалил':
            self.lose_st_num += 1
    def is_pause(self, flag):
        if flag:
            self.student = '-'

"""!
   @brief Вспомогательная функция _get_answer, examiner_answer_massive.
   @detail Функция, которая возвращает веса распределения верояности на основе 
        разбиения по золотому сечению. Количество разбиений определяется числом
        элементов в вопросе за вычетом единицы. 
   @param sex - имеет два значения 'М' и 'Ж'.
   @return случайный ответ.
"""
def _weights_array_form(question1):
    weights1 = []
    my_sum = 0
    for _ in range(len(question1) - 1):
        prob = (1 - my_sum) / gr
        weights1.append(prob)
        my_sum += prob
    weights1.append(1 - my_sum)
    return weights1

"""!
   @brief Вспомогательная функция exam_result.
   @detail Функция, которая случайным образом на основе распределения вероятностей
        и пола выбирает один элемент из вопроса в качестве ответа (каждый вопрос 
        подается списком элементов). Если пол женский, то распределение вероятностей
        инвертируется за счет перестановки всех элементов вопроса в обратном порядке.
   @param questions_array - полный список всех вопросов.
   @param sex - имеет два значения 'М' и 'Ж'.
   @return случайный ответ.
"""
def _get_answer(question1, sex):
    copy_q1 = question1.copy()
    if sex == "Ж":
        copy_q1.reverse()
    weights1 = _weights_array_form(copy_q1)
    result = random.choices(copy_q1, weights = weights1, k = 1)[0]
    return result

"""!
   @brief Вспомогательная функция examiner_answer_massive.
   @detail Функция, которая определяет случайным образом будет ли добавляться
        один элемент в массив ответов или нет. Вероятность добавления каждого
        последующего вопроса равна 1/3.
   @param questions_array - полный список всех вопросов.
   @return список из трех случайных вопросов под разными номерами из банка вопросов.
"""
def need_to_continue():
    c_flag = 0
    if random.random() < 1/3:
        c_flag = 1
    return c_flag

"""!
   @brief Вспомогательная функция exam_result.
   @detail Функция, которая формирует случайным образом массив ответов
        преподавателя: с вероятностью 1/3 в массив  может добавиться каждый
        следующий элемент до тех пор пока не добавятся все элементы, либо пока
        не прекратиться добавление. Выбор элемента такой же как для случая
        студента.
   @param questions_array - полный список всех вопросов.
   @return список из трех случайных вопросов под разными номерами из банка вопросов.
"""
def examiner_answer_massive(question1, sex) -> list:
    copy_q1 = question1.copy()
    if sex == "Ж":
        copy_q1.reverse()

    results = []
    if copy_q1:
        index_get = random.choices(list(range(len(copy_q1))),
                                   weights=_weights_array_form(copy_q1), k=1)[0]
        results.append(copy_q1.pop(index_get))

    while copy_q1 and need_to_continue():
        index_get = random.choices(list(range(len(copy_q1))),
                                   weights=_weights_array_form(copy_q1), k=1)[0]
        results.append(copy_q1.pop(index_get))

    return results

"""!
    @brief Вспомогательная функция exam_result.
    @detail Функция, которая определяет настроение экзаменатора случайным образом 
    на основе заданного массива вероятностей.
    @return 0 если настроение плохое, 1 - если нейтральное и 2 - если хорошее.
"""
def get_ex_behavior() -> int:
    _weights = [0.125, 0.625, 0.25]
    _exam_behavior = [0, 1, 2]
    result = random.choices(_exam_behavior, weights = _weights, k = 1)[0]
    return result

"""!
    @brief Вспомогательная функция exam_proc.
    @detail Функция для вычисления результатов экзамена на основе данных о поле 
        студента, поле преподавателя и банке вопросов. Предполагается, что студент 
        получает три разных вопроса(этот момент не указан в тз).
    @param student - объект класса STUDENT;
    @param exam - объект класса EXAMINER;
    @param question - список всех вопросов.
    @return 'Сдал' , если студент ответил больше чем на один вопрос, в противном 
        случае - 'Провалил'.
"""
def exam_result(student, exam, question: list, q_query) -> str:
    result = 'Провалил'
    ex_behavior = get_ex_behavior()
    questions_num = 3
    questions = question_list_former(question)
    intermediate = 0

    for _i in range(min(len(questions), questions_num)):
        stud_answer = _get_answer(questions[_i].name, student.sex)
        exam_answer = examiner_answer_massive(questions[_i].name, exam.sex)
        if stud_answer in exam_answer:
            intermediate += 1
            q_query.put(("Q_INFO", questions[_i].id, questions[_i].name, 1))

    match ex_behavior:
        case 2:
            result = 'Сдал'
        case 1:
            if intermediate > 1:
                result = 'Сдал'

    return result

"""!
    @brief Функция сдачи экзамена.
    @detail Функция, которая моделирует процесс сдачи экзамена: создает список из
        трех случайных разных вопросов из банка и запускает функцию получения 
        результатов экзамена для студента.
    @param exam_ex - список преподавателей, где каждый его элемент принадлежит классу
        EXAMINER;
    @param st_query -  очередь студентов, где каждый её элемент принадлежит классу
        STUDENT;
    @param question - список объектов QUESTION (банк вопросов).
    @param report_query - очередь для отправки логов и статистике по сдаче студентами.
    @param report_ex_query - очередь для отправки статистике экзаменаторов
"""
def exam_proc(start_time, stud_num: int, exam_ex, st_query, question, report_query, report_ex_query,
              res_ex_func):
    def print_logs(r_query, st_num: int, init_time: float):
        _time = 0.0
        if time.perf_counter() - init_time > 0.1:
            _time = round(time.perf_counter() - init_time, 2)
        q_size = min(st_query.qsize(), st_num)
        r_query.put(("LOG_0", f"Осталось в очереди: {q_size} из {st_num}"))
        r_query.put(("LOG", f"Время с момента начала экзамена: {_time}"))
    end_time, waiting_flag, break_time, exam_p = 0, 0, 30, 100.0
    while True:
        student = st_query.get()
        print_logs(report_query, stud_num, start_time)
        if student is None:
            break

        exam_ex.change_student(student.name)
        result = res_ex_func(student, exam_ex, question, report_query)
        exam_time = len(exam_ex.name)
        exam_duration = random.uniform(exam_time-1, exam_time+1)
        time.sleep(exam_duration)
        end_time = round(time.perf_counter() - start_time, 2)

        report_query.put((student.name, result, student.id, exam_duration))
        print_logs(report_query, stud_num, start_time)

        exam_ex.fix_st_res(result)
        if exam_ex.st_num > 0:
            exam_p = round(exam_ex.lose_st_num/exam_ex.st_num*100, 2)

        report_ex_query.put((exam_ex.id, exam_ex.name, exam_ex.student, exam_ex.st_num,
                             exam_ex.lose_st_num, end_time, exam_p))

        if waiting_flag == 0 and  end_time >= break_time:
            report_query.put(("-", "-"))
            exam_ex.is_pause(True)
            rest_time = random.uniform(12, 18)
            time.sleep(rest_time)

            report_ex_query.put((exam_ex.id, exam_ex.name, exam_ex.student, exam_ex.st_num,
                                 exam_ex.lose_st_num, end_time, exam_p))
            print_logs(report_query, stud_num, start_time)
            waiting_flag = 1

    report_ex_query.put((exam_ex.id, exam_ex.name, "-", exam_ex.st_num, exam_ex.lose_st_num,
                         end_time, exam_p))
    print_logs(report_query, stud_num, start_time)
    report_query.put(("STOP_SIGNAL",))

"""!
    @brief Функция сортировки столбца.
    @detail Функция, которая позволяет отсортировать массив имен студентов, с сохранением исходного
        порядка сдачи, но с отображением тех, кто сдал, после студентов в очереди; провалившиеся
        студенты отображаются в самом конце.
    @param exam_ex - словарь, а котором ключем является позиция студента в очереди на сдачу, а 
        значениями являются кортежи имени и статуса сдачи, модифицируется в процессе работы;
    @param st_query - список студентов в очереди на сдачу.
"""
def sort_function_for_students(current: dict, original: list):
    status_pr = {"Очередь": 0, "Сдал": 1, "Провалил": 2}
    max_num = len(status_pr)
    ind_list_dict = {num: ind for ind, num in enumerate(original)}
    def add_sort_func(num):
        _name, status, _ = current[num]
        priority = status_pr.get(status, max_num)
        index = ind_list_dict.get(num, max_num)
        return priority, index
    return sorted(current.keys(), key = add_sort_func)

"""!
    @brief Функция заполнения массива полных названий файлов.
    @detail Функция, которая позволяет отсортировать массив имен студентов, с сохранением исходного
        порядка сдачи, но с отображением тех, кто сдал, после студентов в очереди; провалившиеся
        студенты отображаются в самом конце.
    @param name_files_list список полных имен файлов "examiners.txt", "questions.txt" и
        "students.txt".
"""
def get_path_math(name_files_list):
    try:
        #абсолютный путь к запущенному файлу .resolve() превращает относительный в абсолютный
        _path_ = pathlib.Path(__file__).resolve().parent
    except NameError:
        _path_ = pathlib.Path.cwd()
    path_ = []
    for my_file in name_files_list:
        p = _path_.joinpath(my_file).resolve()
        if not p.exists():
            print(f"Attention: There is no files in {p}")
        path_.append(str(p))
    return path_

"""!
    @brief вспомогательная функция основного блока.
    @detail Функция создает и заполняет очередь студентов, а также списки экзаминаторов,
        студентов и вопросов.
    @param file_path_mass массив абсолютных путей к файлам "examiners.txt",
        "questions.txt" и "students.txt".
"""
def fill_queues(file_path_mass, students_queue_from_main):
    _examiner_list, _student_list, _q_list, st_count, ex_count, q_count = [], [], [], 0, 0, 0

    for _i in range(3):
        with open(file_path_mass[_i], "r", encoding="utf-8") as file:
            for line in file:
                elements = line.strip().split()
                if not elements:
                    continue
                if _i == 0:
                    example_exam = EXAMINER(elements[0], elements[1], ex_count)
                    _examiner_list.append(example_exam)
                    ex_count += 1
                elif _i == 1:
                    q = QUESTION(elements, q_count)
                    _q_list.append(q)
                    q_count += 1
                elif _i == 2:
                    example_student = STUDENT(elements[0], elements[1], st_count)
                    students_queue_from_main.put(example_student)
                    _student_list.append(example_student)
                    st_count += 1
    _exam_num = len(_examiner_list)
    for _ in range(_exam_num):
        students_queue_from_main.put(None)
    return _q_list, _examiner_list, _student_list, _exam_num

"""!
    @brief Вспомогательная функция для print_final_statistic.
    @detail Выводит сначала указанный текст, после которого через запятую 
        идет перечисление элементов указанного массива.
    @param text - строка, которая будет выводиться перед данными массива;
    @param data_mass - массив, элементы которого будут выводиться без переноса
        строки.
"""
def print_text_with_list(text: str, data_mass: list):
    f_data = ""
    if data_mass:
        f_data = ", ".join(map(str, data_mass))

    print(f"{text}{f_data}")

"""!
    @brief Вспомогательная функция для print_final_statistic.
    @detail Формирует список студентов из значений словаря, для которых достигается минимальное значение
        по указанному элементу массива значений.
    @param my_dict - словарь, в котором ключом является номер студента в общей очереди, а значением список
        из имени студента, статуса сдачи экзамена и длительности сдачи;
    @param col_number - номер элементэ в списке значений словаря;
    @param err - значение ошибки, в пределах которой два числа будут одинаковы;
    @param flag - по умолчанию равен нулю, в противном случае поиск ведется только 
        среди провалившихся студентов;
    @return Список имен студентов, которые сдали экзамен быстрее других студентов.
    
"""
def get_name_mass(my_dict: dict, col_number: int, err: float, flag: int = 0) -> list:
    state_dict = {1: "Сдал", 2: "Провалил"}
    if flag == 0:
        filter_data = list(my_dict.values())
    elif flag in state_dict:
        filter_data = [value for value in my_dict.values() if value[1] == state_dict[flag]]
    else:
        return []

    if not filter_data:
        return []

    try:
        min_value = min(val[col_number] for val in filter_data)
        return [val[0] for val in filter_data if abs(val[col_number] - min_value) < err]
    except (IndexError, TypeError):
        return []

"""!
    @brief Вспомогательная функция print_final_statistic.
    @detail Формирует массив вопросов, на которых наиболее часто правильно отчевают студенты;
        если таких вопросов несколько, то все они добавляются в возвращаемый массив.
    @param my_dict - словарь, который в качестве ключа использует номер вопроса в списке, а 
        значениями являются
    @return массив строк, каждая из которых включает в себя все слова из массива значений словар
"""
def get_questions_massive(my_dict: dict):
    if not my_dict:
        return []

    max_value = max(val[1] for val in my_dict.values())

    return [" ".join(map(str, val[0])) for val in my_dict.values() if val[1] == max_value]

"""!
    @brief Вспомогательная функция для exam_visualization_table.
    @detail Выводит общую статистику под таблицами.
    @param ex_current - словарь данных в формате номер преподавателя: (имя
        экзаменатора, имя сдающего студента, количество сдающих студентов, число проваливших,
        время завершения экзамена для конкретного студента, процент провалившихся студентов у
        конкретного преподавателя);
    @param st_current - - словарь данных в формате номер преподавателя: (список из имени 
        студента, статуса сдачи, экзамена, длительности сдач.
    @param q_dict - словарь, в котором ключем является номер в списке вопросов, а значением массив,
        в котором первое значение это массив слов вопроса, а второе - число успешных ответов
        студентлв на указанный вопрос.
"""
def print_final_statistic(ex_current: dict, st_current: dict, q_dict: dict):
    name = get_name_mass(ex_current, 5, 0.01, 0)
    stud_name = get_name_mass(st_current, 2, 0.01, 1)
    lost_student = get_name_mass(st_current, 2, 0.01, 2)
    best_questions = get_questions_massive(q_dict)
    max_time = max((value[4] for value in ex_current.values()), default = 0)
    sum_fail_st = sum(1 for value in st_current.values() if value[1] == "Провалил")
    sum_len = len(st_current)

    if sum_len > 0:
        ex_res = "" if 1 - sum_fail_st/sum_len > 0.85 else "не "
    else:
        ex_res = "не "

    print(f"Время с момента начала экзамена и до момента его завершения: {max_time}")
    print_text_with_list("Имена лучших студентов: ", stud_name)
    print_text_with_list("Имена лучших экзаменаторов: ", name)
    print_text_with_list("Имена студентов, которых после экзамена отчислят: ", lost_student)
    print_text_with_list("Лучшие вопросы: ", best_questions)
    print(f"Вывод: экзамен {ex_res}удался")

"""!
    @brief Функция очистки.
    @detail Удаляет все данные с окна теминала  и выводит актуальное состояние таблиц.
    @param t_st - первая таблица в формате PrettyTables;
    @param t_ex - вторая таблица в формате PrettyTables.
"""
def refresh_screen(t_st: PrettyTable, t_ex: PrettyTable, logs0=None, logs=None):
    my_text = t_st.get_string() + "\n\n" + t_ex.get_string() + "\n\n"
    if logs0:
        my_text += f"{logs0[-1]}\n"
    if logs:
        my_text += f"{logs[-1]}\n"
    output = "\033[H" + my_text.replace("\n", "\033[K\n") + "\033[K\033[J"

    sys.stdout.write(output)
    sys.stdout.flush()
"""!
    @brief Функция обновления таблиц в окне терминала.
    @detail Очищает строки таблицы и заполняет их новыми данными.
    @param t_st - первая таблица в формате PrettyTable;
    @param t_ex - вторая таблица в формате PrettyTable;
    @param _c_data - словарь с текущими результаты студентов в формате st_id: (имя, статус,
        длительность сдачи);
    @param _o_order - массив id студентов, выстроенных в оригинальном порядке.
"""
def refresh_tables(t_st, t_ex, _c_data, _o_order, _ex_current):
    t_st.clear_rows()
    sorted_name = sort_function_for_students(_c_data, _o_order)
    for n in sorted_name:
        name, status, _ = _c_data[n]
        t_st.add_row([name, status])

    t_ex.clear_rows()
    final_table =  "Текущий студент" not in t_ex.field_names
    for statist in _ex_current.values():
        rows = list(statist)
        if final_table:
            rows.pop(1)
        t_ex.add_row(rows[:len(t_ex.field_names)])

"""!
    @brief Функция обновления таблиц в окне терминала.
    @detail Обеспечивает отображение актуальной информации в таблицах.
    @param ex_proc - список запущенных процессов;
    @param r_queue - - очередь (multiprocessing.Queue) сообщений. Поддерживает форматы:
        - ["STOP_SIGNAL"] - остановка;
        - ["LOG_0" / "LOG", текст] - логирование;
        - ["Q_INFO", id, вопрос, счетчик] - статистика вопросов;
        - [имя, статус, номер_в_списке, длительность] - данные студента;
    @param c_data - словарь данных в формате номер студента: (имя, статус сдачи, длительность сдачи);
    @param o_order - список студентов в изначальном порядке;
    @param t_st - первая таблица в формате PrettyTables;
    @param r_ex_queue - очередь сообщений в формате: номер экзаменатора в таблице, имя
        экзаменатора, имя сдающего студента, количество сдающих студентов, число проваливших,
        время завершения экзамена для конкретного студента, процент провалившихся студентов у
        конкретного преподавателя; 
    @param t_ex - вторая таблица в формате PrettyTables;
    @param ex_current - словарь данных в формате номер преподавателя: (имя
        экзаменатора, имя сдающего студента, количество сдающих студентов, число проваливших,
        время завершения экзамена для конкретного студента, процент провалившихся студентов у
        конкретного преподавателя);
    @param q_dict - словарь, в котором ключом является номер в списке вопросов, а значением является
        массив, в котором первый элемент содержит вопрос в виде массива слов, а второй элемент - 
        это число раз, когда студенты правильно отвечали на вопрос экзаменатора.
"""
def exam_visualization_table(ex_proc, r_queue, c_data, o_order, t_st, r_ex_queue, t_ex,
                             ex_current, q_dict):
    my_logs0 = []
    my_logs = []

    def redraw():
        refresh_tables(t_st, t_ex, c_data, o_order, ex_current)
        refresh_screen(t_st, t_ex, my_logs0, my_logs)

    def work_with_data_from_queue(r_q, r_ex_q, dict_q, dict_st, dict_ex, logs1, logs2):
        was_upgraded = False
        if not r_q.empty():
            data = r_q.get()

            if data[0] not in ("STOP_SIGNAL", "-"):

                was_upgraded = True
                if data[0] == "LOG_0":
                    logs1.append(data[1])
                elif data[0] == "LOG":
                    logs2.append(data[1])
                elif data[0] == "Q_INFO":
                    check_key = data[1]
                    if check_key not in dict_q:
                        dict_q[check_key] = [data[2], data[3]]
                    else:
                        dict_q[check_key][1] += 1

                elif len(data) == 4 and data[0] is not None:
                    dict_st[data[2]] = (data[0], data[1], data[3])

        if not r_ex_q.empty():
            ex_data = r_ex_q.get()
            was_upgraded = True
            dict_ex[ex_data[0]] = ex_data[1:]
        return was_upgraded

    sys.stdout.write("\033[H\033[J")
    redraw()
    while any(p.is_alive() for p in ex_proc) or not r_queue.empty() or not r_ex_queue.empty():
        changed = work_with_data_from_queue(r_queue, r_ex_queue, q_dict, c_data, ex_current, my_logs0, my_logs)

        if changed:
            redraw()
        else:
            time.sleep(0.1)

    while not r_queue.empty() or not r_ex_queue.empty():
        work_with_data_from_queue(r_queue, r_ex_queue, q_dict, c_data, ex_current, my_logs0, my_logs)

    if "Текущий студент" in t_ex.field_names:
        t_ex.del_column("Текущий студент")
    my_logs0.clear()
    my_logs.clear()
    sys.stdout.write("\033[H\033[J")
    redraw()
    print_final_statistic(ex_current, c_data, q_dict)

"""!
    @brief Основная функция
    @detail Функция считывает исходные данные из файлов, формирует списки вопросов,
        очередь студентов, и запускает процесс сдачи экзамента, после чего выводит статистику в виде таблиц.
"""
if __name__ == '__main__':
    try:
        file_names = ["examiners.txt", "questions.txt", "students.txt"]
        path = get_path_math(file_names)
        stud_qe = multiprocessing.Queue()
        q_list, exam_list, student_list, exam_num = fill_queues(path, stud_qe)
        questions_dict = {}
    except FileNotFoundError:
        sys.exit(f"Error: There is no input files.")
    except UnicodeDecodeError:
        sys.exit(f"Error: Some files have wrong encoding")
    except IndexError:
        sys.exit(f"Error: wrong format of files.")
    else:
        if not student_list:
            sys.exit(f"Error: Nobody to exam.")
        elif not exam_list:
            sys.exit(f"Error: There are no examiners.")
        elif len(q_list) < 2 or any(not q for q in q_list):
            sys.exit(f"Error: Too small amount of questions in the bank or empty questions.")
        else:
            r_qe = multiprocessing.Queue()
            r_ex_qe = multiprocessing.Queue()

            cur_data = {st.id: (st.name, "Очередь", 0) for st in student_list}
            ex_cur_data = {ex.id: (ex.name, "-", 0, 0, 0, 100) for ex in exam_list}
            or_odr = [st.id for st in student_list]

            table_sts = PrettyTable(["Студент", "Статус"])
            table_sts.align["Студент"] = "l"

            table_exs = PrettyTable(["Экзаменатор", "Текущий студент", "Всего студентов",
                                      "Завалил","Время работы"])
            table_exs.align["Экзаменатор"], table_exs.align["Текущий студент"] = "l", "l"

            t_0 = time.perf_counter()
            stud_nbs = len(student_list)
            r_qe.put(("LOG_0", f"Осталось в очереди: {stud_nbs} из {stud_nbs}"))
            r_qe.put(("LOG", f"Время с момента начала экзамена: {0}"))
            exam_procs = []
            for i in range(exam_num):
                proc = multiprocessing.Process(target=exam_proc,
                                               args=(t_0, stud_nbs, exam_list[i], stud_qe,
                                                     q_list, r_qe, r_ex_qe, exam_result))
                proc.start()
                exam_procs.append(proc)

            exam_visualization_table(exam_procs, r_qe, cur_data, or_odr, table_sts, r_ex_qe,
                                     table_exs, ex_cur_data, questions_dict)

            for proc in exam_procs:
                proc.join()
