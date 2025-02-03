from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from datetime import date

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    sigla = models.CharField(max_length=15)
    descricao = models.TextField('descrição', max_length=255)

    def __str__(self):
        return self.nome


class CentroCusto(models.Model):
    nome = models.CharField(max_length=100)
    sigla = models.CharField(max_length=15)
    descricao = models.TextField('descrição', max_length=255)
    vl_teto = models.DecimalField('valor teto', max_digits=18, decimal_places=2)

    def __str__(self):
        return self.nome


class FormaPagamento(models.Model):
    nome = models.CharField(max_length=100)
    sigla = models.CharField(max_length=15)
    descricao = models.TextField('descrição', max_length=255)

    centro_custo = models.ManyToManyField(
        CentroCusto,
        through="Formula",
        through_fields=("forma_pagto", 'centro_custo')    
    )
    def __str__(self):
        return self.nome



class Conta(models.Model):
    nome = models.CharField(max_length=100)
    sigla = models.CharField(max_length=15)
    descricao = models.TextField('descrição', max_length=255)
    saldo = models.DecimalField(max_digits=18, decimal_places=2)
    limite = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    atualizacao = models.DateTimeField('atualização', auto_now=True)

    def __str__(self):
        return self.nome


class MovimentoConta(models.Model):
    ENTRADA = 'E'
    SAIDA = 'S'
    TIPO_CHOICES = {
        ENTRADA : 'Entrada',
        SAIDA : 'Saida'
    }
    conta_origem = models.ForeignKey(Conta, on_delete=models.DO_NOTHING, null=True, blank=True)
    conta_destino = models.ForeignKey(Conta, on_delete=models.DO_NOTHING, related_name="conta_destino")
    descricao = models.TextField('descrição', max_length=255)
    data = models.DateField()
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES, default=ENTRADA)
    valor = models.DecimalField(max_digits=18, decimal_places=2)
    atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.descricao



# atualiza valor do saldo
@receiver(pre_save, sender=MovimentoConta)
def update_saldo(sender, instance, **kwargs):
    # restaura saldo anterior
    if instance.pk:
        mov = MovimentoConta.objects.get(pk = instance.pk)
        if instance.conta_origem is not None:
            instance.conta_origem.saldo += mov.valor # devolve ao saldo origem
            instance.conta_origem.save()
        
        instance.conta_destino.saldo -= mov.valor # retira do saldo destino
        instance.conta_destino.save()       



# atualiza valor do saldo
@receiver(post_save, sender=MovimentoConta)
def update_saldo(sender, instance, created, **kwargs):
    # atualiza saldo
    if instance.conta_origem is not None:
        instance.conta_origem.saldo -= instance.valor # retira do saldo da origem
        instance.conta_origem.save()

    instance.conta_destino.saldo += instance.valor # adiciona ao saldo do destino
    instance.conta_destino.save()



class Formula(models.Model):

    centro_custo = models.ForeignKey(CentroCusto, on_delete=models.DO_NOTHING)
    forma_pagto = models.ForeignKey(FormaPagamento, on_delete=models.DO_NOTHING)
    nome = models.CharField(max_length=100, default='--')
    
    def __str__(self):
        return self.nome


class Recorrente(models.Model):
    ANUAL = 'A'
    MENSAL = 'M'
    SEMANAL = 'W'
    BIMESTRAL = 'B'
    TRIMESTRAL = 'T'
    SEMESTRAL = 'S'

    FREQUENCIA_CHOICES = {
        ANUAL : 'Anual',
        MENSAL : 'Mensal',
        SEMANAL : 'Semanal',
        BIMESTRAL : 'Bimestral',
        TRIMESTRAL : 'Trimestral',
        SEMESTRAL : 'Semestral',
    }
    ATIVO = 'A'
    INATIVO = 'I'
    SITUACAO_CHOICES = {
        ATIVO : 'Ativo',
        INATIVO : 'Inativo'
    }
    nome = models.CharField(max_length=100)
    valor = models.DecimalField(max_digits=18, decimal_places=2)
    frequencia = models.CharField(max_length=1, choices=FREQUENCIA_CHOICES, default='M')
    data = models.DateField()
    situacao = models.CharField(max_length=1, choices=SITUACAO_CHOICES, default=ATIVO)
    atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome




class Transacao(models.Model):
    AVISTA = 'V'
    PARCELADO = 'P'
    RECORRENTE = 'R'
    TIPO_CHOICES = {
        AVISTA : 'A Vista',
        PARCELADO : 'Parcelado',
        RECORRENTE : 'Recorrente',
    }

    SIT_INATIVO = 0
    SIT_ATIVO = 1
    SIT_NEGOCIADO = 2
    SIT_CANCELADO = 3
    SIT_PAGO = 4
    SIT_NAO_PAGO = 5
    SITUACAO_CHOICES = {
        SIT_ATIVO : 'Ativo',
        SIT_INATIVO : 'Inativo',
        SIT_NEGOCIADO : 'Negociado',
        SIT_CANCELADO : 'Cancelado',
        SIT_PAGO : 'Pago',
        SIT_NAO_PAGO : 'Não Pago'
    }
    descricao = models.CharField('descrição', max_length=100)
    data_compra = models.DateField()
    data_vencimento = models.DateField(null=True, blank=True)
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES, default=AVISTA)
    vl_total = models.DecimalField('valor total', max_digits=18, decimal_places=2)
    vl_parcela = models.DecimalField('valor parcela', max_digits=15, decimal_places=2)
    qt_parcelas = models.SmallIntegerField('qtd parcelas', default=1)
    nr_parcela = models.SmallIntegerField('nr parcela', default=1)
    categoria = models.ForeignKey(Categoria, on_delete=models.DO_NOTHING)
    forma_pagto = models.ForeignKey(FormaPagamento, on_delete=models.DO_NOTHING)
    conta = models.ForeignKey(Conta, on_delete=models.DO_NOTHING)
    recorrente = models.ForeignKey(Recorrente, on_delete=models.DO_NOTHING, null=True, blank=True)
    situacao = models.SmallIntegerField('situação', choices=SITUACAO_CHOICES, default=SIT_ATIVO)
    atualizacao = models.DateTimeField('atualização', auto_now=True)
    consolidado = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "lançamento"
        verbose_name_plural = "lançamentos"
        ordering = ["-data_compra"]

    def __str__(self):
        return self.descricao
    
    def was_buy_recently(self):
        return self.data_compra <= date.today()
