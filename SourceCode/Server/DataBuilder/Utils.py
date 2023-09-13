import json
import decimal


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


def write_to_file(data, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, cls=DecimalEncoder)


def write_dict_to_file(data, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump({", ".join(k): v for k, v in data.items()}, f, ensure_ascii=False, indent=4, cls=DecimalEncoder)
