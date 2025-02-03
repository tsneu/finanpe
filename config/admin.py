from django.contrib import admin
from django.db.models import Sum
from . import models 
from .utils import dates
from django.core.exceptions import ObjectDoesNotExist
from datetime import date

admin.site.site_header = 'Finanpe - Finanças pessoais'
admin.site.site_title = 'FINANPE'


# layout padrão:
#admin.site.register(models.CentroCusto)

# layout personalizado:

@admin.register(models.Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sigla')
    search_fields = ('nome', 'descricao')

@admin.register(models.CentroCusto)
class CentroCustoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sigla', 'vl_teto')
    search_fields = ('nome', 'descricao')


@admin.register(models.Conta)
class ContaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sigla', 'saldo', 'limite', 'atualizacao')
    search_fields = ('nome', 'sigla')
    actions = ['atualizar_saldo',]

    @admin.action(description='Atualizar saldo')
    def atualizar_saldo(self, request, queryset):
        cont = 0
        for item in queryset:
            try:
                # transações da conta ainda não consolidadas:
                obj = models.Transacao.objects.filter(conta=item, data_vencimento__lte=date.today(), consolidado=False)
                if obj.count() > 0:
                    cont += 1
                    # atualizar o saldo com a soma das transações
                    obj_soma = obj.annotate(total=Sum('vl_parcela'))
                    item.saldo = item.saldo - obj_soma[0].total
                    item.save()
                    # atualizar transações para consolidadas
                    obj.update(consolidado=True)

            except ObjectDoesNotExist as e:
                print(f'nenhum lançamento encontrado para conta: {item.nome}')

        if cont == 1:
            msg = '{} conta foi atualizada'
        else:
            msg = '{} contas foram atualizadas'
        self.message_user(request, msg.format(cont))




@admin.register(models.FormaPagamento)
class FormaPagamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sigla')
    search_fields = ('nome', 'descricao')


@admin.register(models.Formula)
class FormulaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'forma_pagto', 'centro_custo')
    list_filter = ('forma_pagto', 'centro_custo')


@admin.register(models.MovimentoConta)
class MovimentoContaAdmin(admin.ModelAdmin):
    list_display = ('conta_origem', 'conta_destino', 'tipo', 'valor', 'data')
    

@admin.register(models.Recorrente)
class RecorrenteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'valor', 'frequencia', 'data', 'situacao', 'atualizacao')
    list_filter = ('frequencia', 'situacao')
    actions = ('criar_lancamento',)

    @admin.action(description='Criar próximo lançamento')
    def criar_lancamento(self, request, queryset):
        cont = 0
        for item in queryset:
            try:
                obj = models.Transacao.objects.filter(recorrente=item).latest('data_vencimento')
                if obj.data_compra != item.data:
                    # verificar qual a frequencia da recorrencia
                    cont += 1
                    obj.pk = None
                    obj.data_compra = item.data
                    obj.data_vencimento = dates.add_date(obj.data_vencimento, item.frequencia)
                    obj.save()
                    # atualiza a próxima data:
                    item.data = dates.add_date(item.data, item.frequencia)
                    item.save()

            except ObjectDoesNotExist as e:
                print(f'lançamento não encontrado para {item.nome}')

        if cont == 1:
            msg = '{} lançamento foi criado'
        else:
            msg = '{} lançamentos foram criados'
        self.message_user(request, msg.format(cont))


@admin.register(models.Transacao)
class TransacaoAdmin(admin.ModelAdmin):   
    list_display = ('data_compra', 'data_vencimento', 'descricao','parcelas', 'vl_parcela', 'categoria__sigla', 'consolidado')
    list_filter = ('data_vencimento', 'conta', 'recorrente', 'tipo', 'forma_pagto')
    readonly_fields = ('consolidado', )
    actions = ['duplicar_proximo_mes', ]

    @admin.display()
    def parcelas(self, obj):
        return f'{obj.nr_parcela}/{obj.qt_parcelas}'
    
    @admin.action(description='Duplicar para o próximo mês')
    def duplicar_proximo_mes(self, request, queryset):
        cont = 0
        for item in queryset:
            cont += 1
            item.pk = None
            item.nr_parcela += 1 if item.qt_parcelas != item.nr_parcela else 0
            item.data_vencimento = dates.add_date(item.data_vencimento, 'M')
            item.save()

        if cont == 1:
            msg = '{} lançamento foi criado'
        else:
            msg = '{} lançamentos foram criados'
        self.message_user(request, msg.format(cont))
