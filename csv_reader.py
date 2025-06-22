import argparse
import csv

from tabulate import tabulate

"""
Словарь с функциями агрегирования, поддерживающими min, max и avg.
"""
AGGREGATIONS = {
    'min': min,
    'max': max,
    'avg': lambda vals: sum(vals) / len(vals) if vals else None,
}


def parse_condition(cond):
    """
    Разбирает строковое условие в формате 'колонка оператор значение'.
    Возвращает кортеж: (column, operator, value).
    """
    for op in ['!=', '>=', '<=', '>', '<', '=']:
        if op in cond:
            col, val = cond.split(op, 1)
            return col.strip(), op, val.strip()
    raise ValueError(f'Невозможно разобрать условие: {cond}')


def compare(a, op, b):
    """
    Сравнивает два значения с учетом оператора.
    Поддерживает сравнение чисел и строк (только = и != для строк).
    """
    try:
        a_num = float(a)
        b_num = float(b)
        a, b = a_num, b_num
        numeric = True
    except ValueError:
        numeric = False

    if not numeric and op not in ('=', '==', '!='):
        print(
            'Для строк можно использовать только операторы "=" или "!=".'
        )
        return False

    if op in ('=', '=='):
        return a == b
    elif op == '!=':
        return a != b
    elif op == '<':
        return a < b
    elif op == '>':
        return a > b
    elif op == '<=':
        return a <= b
    elif op == '>=':
        return a >= b
    return False


def main():
    """
    Основная функция: парсит аргументы, читает CSV, применяет фильтрацию,
    сортировку и агрегацию (по одному из каждого), затем выводит результат.
    """
    parser = argparse.ArgumentParser(
        description=(
            'Фильтрация CSV с одним условием, сортировкой и агрегацией.')
    )
    parser.add_argument('--file', required=True, help='CSV файл')
    parser.add_argument('--where', help='Условие фильтра, например: price>100')
    parser.add_argument(
        '--order-by', help='Сортировка, например: price=asc или brand=desc')
    parser.add_argument('--aggregate', help='Агрегация, например: price=min')
    args = parser.parse_args()

    with open(args.file, encoding='utf-8') as f:
        data = list(csv.DictReader(f))
    if not data:
        print('Файл пуст или нет данных')
        return

    headers = data[0].keys()

    if args.where:
        col, op, val = parse_condition(args.where)
        if col not in headers:
            print(f'Колонка "{col}" не найдена')
            return
        data = [row for row in data if compare(row[col], op, val)]

    if args.order_by:
        if '=' not in args.order_by:
            print(
                'Формат --order-by должен быть "column=asc" или "column=desc"'
            )
            return
        col, direction = args.order_by.split('=', 1)
        col, direction = col.strip(), direction.strip().lower()
        if col not in headers:
            print(f'Колонка "{col}" не найдена')
            return
        if direction not in ('asc', 'desc'):
            print('Направление сортировки должно быть "asc" или "desc"')
            return

        def sort_key(row):
            v = row.get(col, '')
            try:
                return float(v)
            except ValueError:
                return v
        data = sorted(data, key=sort_key, reverse=(direction == 'desc'))

    if args.aggregate:
        col, op, stat = parse_condition(args.aggregate)
        if col not in headers:
            print(f'Колонка "{col}" не найдена')
            return
        if stat not in AGGREGATIONS:
            print('Агрегация должна быть одной из: min, max, avg')
            return

        vals = []
        for row in data:
            try:
                vals.append(float(row[col]))
            except (ValueError, KeyError):
                pass
        agg_func = AGGREGATIONS[stat]
        result = agg_func(vals) if vals else None
        if result is None:
            print(f'Нет данных для агрегации "{stat}" по колонке "{col}"')
            return

        print(tabulate([{stat: f'{result:.2f}'}],
              headers='keys', tablefmt='grid'))
        return

    if not data:
        print('По заданным условиям данных не найдено')
        return

    print(tabulate(data, headers='keys', tablefmt='grid'))


if __name__ == '__main__':
    main()
