import subprocess

CSV_PATH = 'products.csv'
SCRIPT = 'csv_reader.py'


def run(args):
    result = subprocess.run(
        ['python3', SCRIPT] + args,
        capture_output=True,
        text=True
    )
    return result.stdout.strip(), result.stderr.strip()


def test_where_filter():
    out, _ = run(['--file', CSV_PATH, '--where', 'brand=apple'])
    assert 'iphone' in out
    assert 'samsung' not in out
    assert 'xiaomi' not in out


def test_aggregate_min():
    out, _ = run(['--file', CSV_PATH, '--aggregate', 'price=min'])
    assert 'min' in out and '149' in out


def test_aggregate_avg():
    out, _ = run(['--file', CSV_PATH, '--aggregate', 'price=avg'])
    assert 'avg' in out


def test_order_by_desc():
    out, _ = run(['--file', CSV_PATH, '--order-by', 'price=desc'])
    assert 'galaxy s23 ultra' in out.splitlines()[3].lower()


def test_order_by_asc():
    out, _ = run(['--file', CSV_PATH, '--order-by', 'price=asc'])
    assert 'redmi 10c' in out.splitlines()[3].lower()


def test_where_and_aggregate():
    out, _ = run(['--file', CSV_PATH, '--where',
                 'brand=xiaomi', '--aggregate', 'price=max'])
    assert 'max' in out and '299' in out


def test_invalid_column():
    out, _ = run(['--file', CSV_PATH, '--where', 'brend=apple'])
    assert 'не найдена' in out.lower()


def test_invalid_aggregate_type():
    out, _ = run(['--file', CSV_PATH, '--aggregate', 'price=mediana'])
    assert 'агрегация должна быть' in out.lower()


def test_empty_result():
    out, _ = run(['--file', CSV_PATH, '--where', 'brand=nonexistent'])
    assert 'не найдено' in out.lower()
