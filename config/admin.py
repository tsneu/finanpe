from django.contrib import admin
from . import models
from .utils import dates
from django.core.exceptions import ObjectDoesNotExist

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
    
    list_display = ('data_compra', 'data_vencimento', 'descricao','parcelas', 'vl_parcela', 'categoria__sigla', 'situacao')
    list_filter = ('data_vencimento', 'conta', 'recorrente', 'tipo', 'forma_pagto')
    #actions = ['duplicar_proximo_mes', ]

    @admin.display()
    def parcelas(self, obj):
        return f'{obj.nr_parcela}/{obj.qt_parcelas}'
    
    @admin.action(description='Duplicar para o próximo mês')
    def duplicar_proximo_mes(self, request, queryset):
        pass
