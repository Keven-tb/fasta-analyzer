from django.db import models


class SequenciaFasta(models.Model):
    """
    Representa um arquivo FASTA enviado pelo usuário.
    Guarda o arquivo original (persistido em MEDIA_ROOT/volume) e os
    dados extraídos/calculados a partir da primeira sequência do arquivo.
    """

    arquivo = models.FileField(upload_to='fastas/')
    nome_sequencia = models.CharField(max_length=255, blank=True)
    sequencia = models.TextField(blank=True)
    tamanho = models.IntegerField(null=True, blank=True)
    gc_percentual = models.FloatField(null=True, blank=True)
    complemento_reverso = models.TextField(blank=True)
    enviado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-enviado_em']

    def __str__(self):
        return self.nome_sequencia or self.arquivo.name
