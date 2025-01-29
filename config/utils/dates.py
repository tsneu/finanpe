from dateutil.relativedelta import relativedelta

"""
função para adicionar/retroceder datas
"""
def add_date(date, freq, qtd=1):
    match freq:
        case 'A':
            new_date = date + relativedelta(years=1)
        case 'M':
            new_date = date + relativedelta(months=qtd)
        case 'W':
            new_date = date + relativedelta(weeks=qtd)
        case 'B':
            new_date = date + relativedelta(months=2)
        case 'T':
            new_date = date + relativedelta(months=3)
        case 'S':
            new_date = date + relativedelta(months=6)
        case 'D':
            new_date = date + relativedelta(days=qtd)
    return new_date
