from django.urls import path
from .views import IndexView, TransacaoDataView, CategoriaDataView, CentroCustoView, ContaDataView, FilterTransactions

urlpatterns = [
    path('', IndexView.as_view(), name='home_index'),
    path('chart/consumo', IndexView.get_consumo, name='chart_consumo'),
    path(
        "resumo/tipo-operacao",
        TransacaoDataView.as_view(),
        name="transactions_data",
    ),
    path(
        'resumo/tipo-operacao/<int:ano>/<str:mes>',
        TransacaoDataView.as_view(),
        name='transactions_per_date'
    ), 
    path('chart/operacao/<str:month>/<int:year>', TransacaoDataView.get_operacao_chart, name='chart_operacao'),
    path(
        'resumo/categorias', 
        CategoriaDataView.as_view(),
        name='categorias_data'
    ),
    path(
        'resumo/categorias/<int:ano>/<str:mes>', 
        CategoriaDataView.as_view(),
        name='categorias_data'
    ),
    path(
        'resumo/centrocusto', 
        CentroCustoView.as_view(),
        name='resumo_centro_custo'
    ),
    path(
        'resumo/centrocusto/<int:ano>/<int:mes>', 
        CentroCustoView.as_view(),
        name='resumo_centro_custo_data'
    ),
    path('chart/centro-custo/<str:month>/<int:year>', CentroCustoView.get_resumo_chart, name='chart_centro_custo'),
    path(
        'resumo/saldo-contas', 
        ContaDataView.as_view(),
        name='saldo_contas'
    ),
    path(
        'resumo/saldo-contas/<int:ano>/<int:mes>', 
        ContaDataView.as_view(),
        name='saldo_contas_data'
    ),
    path('chart/contas/<str:month>/<int:year>', ContaDataView.get_contas_chart, name='chart_contas'),
    path(
        'lancamentos/detalhes',
        FilterTransactions.as_view(),
        name='transactions_details'
    ),

]
