from django.views.generic import ListView
from .models import Transacao, MovimentoConta
from django.db.models import Count, Sum, Value, CharField
from django.db.models.functions import ExtractYear, ExtractMonth, Concat
from django.http import JsonResponse
from .utils.charts import months, colorSuccess, colorDanger, generate_color_palette
from .forms import FilterData
from datetime import date


class FilterDataView(ListView):
    ano = date.today().year
    mes = date.today().month
    mes = months[mes]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ano_list = self.get_filter_year_options()
        mes_list = self.get_filter_month_options()
        context['form_filter'] = FilterData().render(
            context={
                'ano_list': ano_list, 
                'mes_list': mes_list,
                'ano_selected': self.ano,
                'mes_selected': self.mes
            }
        )
        return context

    def get_queryset(self):
        ano = self.request.GET.get('ano')
        mes = self.request.GET.get('mes') # palavra
        self.ano = int(ano) if ano else self.ano
        self.mes = mes if mes else self.mes
        
        dados = None
        if ano and mes:
            mes = months.index(mes)
            dados = Transacao.objects.filter(data_vencimento__year=ano)
            dados = dados.filter(data_vencimento__month=mes)
        else:
            hoje = date.today()
            ano = hoje.year
            mes = hoje.month
            dados = Transacao.objects.filter(data_vencimento__year=ano, data_vencimento__month=mes)
        
        return dados
    
    def get_filter_year_options(self):
        grouped_transactions = Transacao.objects.annotate(year=ExtractYear("data_vencimento"))\
            .values("year").order_by("-year").distinct()
        options = [transaction["year"] for transaction in grouped_transactions]

        return options


    def get_filter_month_options(self):
        grouped_transactions = Transacao.objects.annotate(month=ExtractMonth("data_vencimento"))\
            .values("month").order_by("month").distinct()
        option_list = [transaction["month"] for transaction in grouped_transactions]
        month_options = [months[option] for option in option_list]
        return month_options



class IndexView(ListView):
    template_name = "config/index.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ano'] = date.today().year
        context['mes'] = months[date.today().month]
        return context


    def get_queryset(self):
        hoje = date.today()
        movimento = MovimentoConta.objects.filter(data__year=hoje.year)\
                .values('data__month', 'tipo', 'conta_destino__sigla').annotate(total=Sum('valor'))\
                .order_by('tipo')
        return movimento


    def get_consumo(self):
        hoje = date.today()
        consumo = Transacao.objects.filter(data_vencimento__year=hoje.year)\
                .values('data_vencimento__month').annotate(total=Sum('vl_parcela'))

        consumo_list = dict()
        for c in consumo:
            consumo_list[months[c['data_vencimento__month']]] = round(c['total'], 2)

        return JsonResponse({
            "title": f"Consumo ao mês em {hoje.year}",
            "data": {
                "labels": list(consumo_list.keys()),
                "datasets": [{
                    "label": "Total (R$)",
                    "backgroundColor": generate_color_palette(len(consumo_list)),
                    "borderColor": generate_color_palette(len(consumo_list)),
                    "data": list(consumo_list.values()),
                }]
            },
        })



class CategoriaDataView(FilterDataView):
    template_name = 'config/categoria_data_list.html'
    context_object_name = 'transacao_list'       

    def get_queryset(self):
        dados = super().get_queryset()
        cat_list = dados.values("categoria__sigla")\
            .annotate(total=Sum('vl_parcela'))\
            .order_by("categoria__sigla")
        return cat_list
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        if context['object_list']:
            total = context['object_list'].aggregate(Sum('total'))
            context['total_rows'] = {
                'total_sum': total['total__sum'],
                'total_count': context['object_list'].count()
            }
        
        return context
        

class ContaDataView(FilterDataView):
    template_name = 'config/conta_data_list.html'

    def get_queryset(self):
        dados = super().get_queryset()
        cat_list = dados.values("conta__nome", "conta__saldo", "conta__limite")\
            .annotate(total=Sum('vl_parcela'))\
            .order_by("conta__nome")
        return cat_list
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        if context['object_list']:
            total = context['object_list'].aggregate(Sum('total'))
            context['total_rows'] = {
                'total_sum': total['total__sum'],
                'total_count': context['object_list'].count()
            }
        mes = months.index(self.mes)
        movimento = MovimentoConta.objects.filter(data__year=self.ano, data__month=mes)
        context['movimento_list'] = movimento
        
        return context
    
    def get_contas_chart(self, month, year):
        mes = months.index(month)
        consumo = Transacao.objects.filter(data_vencimento__year=year, data_vencimento__month=mes)\
                .values('conta__nome').annotate(total=Sum('vl_parcela'))

        consumo_list = dict()
        for c in consumo:
            consumo_list[c['conta__nome']] = round(c['total'], 2)

        return JsonResponse({
            "title": f"Consumo por conta em {month}/{year}",
            "data": {
                "labels": list(consumo_list.keys()),
                "datasets": [{
                    "label": "Conta",
                    "backgroundColor": generate_color_palette(len(consumo_list)),
                    "borderColor": generate_color_palette(len(consumo_list)),
                    "data": list(consumo_list.values()),
                }]
            },
        })



class MovimentoContaView(FilterDataView):
    template_name = 'config/movimento_conta_data.html'
    context_object_name = 'movimento_list'

    

class TransacaoDataView(FilterDataView):
    template_name = 'config/operacao_data_list.html'

    def get_queryset(self):
        dados = super().get_queryset()
        lanc_list = dados.values("tipo")\
            .annotate(label=Concat("tipo", Value(None), output_field=CharField()))\
            .annotate(total=Sum('vl_parcela'), qtde=Count('id'))
        
        for query in lanc_list:
            query['label'] = lanc_list.model(tipo=query['tipo']).get_tipo_display()

        return lanc_list
    
    def get_operacao_chart(self, month, year):
        mes = months.index(month)
        consumo = Transacao.objects.filter(data_vencimento__year=year, data_vencimento__month=mes)\
                .values('tipo').annotate(total=Sum('vl_parcela'))

        oper_keys = list()
        oper_values = list()
        for c in consumo:
            oper_keys.append(consumo.model(tipo=c['tipo']).get_tipo_display())
            oper_values.append(round(c['total'],2)) #"{:.2f}".format(c['total'])

        return JsonResponse({
            "title": f"Operações em {month}/{year}",
            "data": {
                "labels": oper_keys,
                "datasets": [{
                    "label": "Tipo operação",
                    "backgroundColor": generate_color_palette(len(oper_keys)),
                    "borderColor": generate_color_palette(len(oper_keys)),
                    "data": oper_values,
                }]
            },
        })    

    
class CentroCustoView(FilterDataView):
    template_name = 'config/centro_custo_list.html'
    context_object_name = 'transacao_list'
    
    def get_queryset(self):
        dados = super().get_queryset()
        cc_list = dados.values("forma_pagto__centro_custo__sigla").annotate(total=Sum('vl_parcela')).order_by("forma_pagto__centro_custo__sigla")

        return cc_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        if context['transacao_list']:
            total = context['transacao_list'].aggregate(Sum('total'))
            context['total_rows'] = {
                'total_sum': total['total__sum'],
                'total_count': context['transacao_list'].count()
            }
        
        return context
    
    def get_resumo_chart(self, month, year):
        mes = months.index(month)
        consumo = Transacao.objects.filter(data_vencimento__year=year, data_vencimento__month=mes)\
                .values('forma_pagto__centro_custo__sigla').annotate(total=Sum('vl_parcela'))

        consumo_list = dict()
        for c in consumo:
            consumo_list[c['forma_pagto__centro_custo__sigla']] = round(c['total'], 2)

        return JsonResponse({
            "title": f"Consumo por centro de custo em {month}/{year}",
            "data": {
                "labels": list(consumo_list.keys()),
                "datasets": [{
                    "label": "Centro de custo",
                    "backgroundColor": generate_color_palette(len(consumo_list)),
                    "borderColor": generate_color_palette(len(consumo_list)),
                    "data": list(consumo_list.values()),
                }]
            },
        })



class FilterTransactions(ListView):
    template_name = 'config/transacao_detalhes.html'

    def get_queryset(self):
        ano = self.request.GET.get('ano')
        mes = self.request.GET.get('mes') # palavra
        chave = self.request.GET.get('chave')
        valor = self.request.GET.get('valor')
        mes = months.index(mes)

        parameters = { 'data_vencimento__year': ano, 'data_vencimento__month' : mes, chave: valor }
        print(parameters)
        dados = Transacao.objects.filter(**parameters)
        return dados
    
    