function verDetalhes(chave, valor, label=''){
    $.ajax({
        url: "/transacoes/detalhes",
        method: "GET",
        data: {
            ano: $('#select_year').val(), 
            mes: $('#select_month').val(), 
            chave: chave, 
            valor: valor
        },
        dataType: "html"
    }).done(function(data){
        title = label || valor;
        $('#title-detail').html('<i class="fa-regular fa-file-lines"></i> Lançamentos de ' + title)
        $('#transactions_detail').html(data);
    }).fail(function(error){
        alert('Algo deu errado...')
        console.log(error)
    });
}

$(document).ready(function() {
    $('.detail').on("click", function(){
        chave = $(this).data('chave');
        valor = $(this).data('filter');
        label = $(this).data('label');
        verDetalhes(chave, valor, label);
    })
});
