import csv
from django.core.management.base import BaseCommand
from config.models import Transacao

class Command(BaseCommand):
    help = 'Importe de transacoes de arquivo .CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Informe o caminho do arquivo .csv a ser importado: ')

    
    def handle(self, *args, **options):
        file_path = options['csv_file']

        try:
            with open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter=';')
                count = 0
                for row in reader:
                    data, created = Transacao.objects.get_or_create(
                        descricao = row['descricao'],
                        data_compra = row['data_compra'],
                        data_vencimento = row['vencimento'] if 'vencimento' in row else row['data_compra'],
                        tipo = row['tipo'] if 'tipo' in row else Transacao.AVISTA,
                        vl_total = row['valor_total'],
                        vl_parcela = row['valor_parcela'] if 'valor_parcela' in row else row['valor_total'],
                        qt_parcelas = int(row['qtd_parcelas']) if 'qtd_parcelas' in row else 1,
                        nr_parcela = int(row['nr_parcela']) if 'nr_parcela' in row else 1,
                        categoria_id = int(row['categoria']),
                        forma_pagto_id = int(row['forma_pagto']),
                        conta_id = int(row['conta']),
                        situacao = Transacao.SIT_ATIVO,
                    )
                    if created:
                        count += 1
                self.stdout.write(self.style.SUCCESS(f'Importado com sucesso "{count}" registros.'))
        except FileExistsError:
            self.stdout.write(self.style.ERROR(f'Arquivo não encontrado no caminho: "{file_path}"'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Um erro foi encontrado durente o processamento: {str(e)}'))