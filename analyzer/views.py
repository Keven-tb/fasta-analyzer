from django.contrib import messages
from django.shortcuts import redirect, render

from .bio_utils import calcular_complemento_reverso, calcular_gc_percentual, extrair_primeira_sequencia
from .forms import UploadFastaForm
from .models import SequenciaFasta


def upload_fasta(request):
    if request.method == 'POST':
        form = UploadFastaForm(request.POST, request.FILES)

        if form.is_valid():
            instancia = form.save(commit=False)

            try:
                conteudo = instancia.arquivo.read().decode('utf-8')
                nome_sequencia, sequencia = extrair_primeira_sequencia(conteudo)

                instancia.nome_sequencia = nome_sequencia
                instancia.sequencia = sequencia
                instancia.tamanho = len(sequencia)
                instancia.gc_percentual = calcular_gc_percentual(sequencia)
                instancia.complemento_reverso = calcular_complemento_reverso(sequencia)

                instancia.save()
                messages.success(request, f'Sequência "{nome_sequencia}" processada com sucesso.')
                return redirect('listar_sequencias')

            except (ValueError, UnicodeDecodeError) as erro:
                messages.error(request, f'Erro ao processar o arquivo: {erro}')
    else:
        form = UploadFastaForm()

    return render(request, 'analyzer/upload.html', {'form': form})


def listar_sequencias(request):
    sequencias = SequenciaFasta.objects.all()
    return render(request, 'analyzer/listar.html', {'sequencias': sequencias})
