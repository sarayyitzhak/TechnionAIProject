import json
import decimal
import traceback
import sys


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


def write_to_file(data, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, cls=DecimalEncoder)


def read_from_file(data_path, try_func, error_func=None, finally_func=None):
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            try_func(json.load(f))
    except IOError:
        print(traceback.format_exc())
        if error_func is not None:
            except_type, value = sys.exc_info()[:2]
            error_func((except_type.__name__, f"{str(value)}\n\n{str(traceback.format_exc())}"))
    finally:
        if finally_func is not None:
            finally_func()
