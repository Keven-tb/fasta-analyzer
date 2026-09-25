"""
Funções auxiliares para leitura e análise de sequências no formato FASTA.
"""

BASES_VALIDAS = set("ATCG")
COMPLEMENTO = {"A": "T", "T": "A", "C": "G", "G": "C"}


def extrair_primeira_sequencia(conteudo_arquivo: str):
    """
    Recebe o conteúdo textual de um arquivo FASTA e retorna
    (nome_sequencia, sequencia) referentes apenas à primeira
    sequência encontrada no arquivo.

    Levanta ValueError se o arquivo estiver vazio ou mal formatado.
    """
    linhas = conteudo_arquivo.splitlines()

    nome_sequencia = None
    partes_sequencia = []

    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue

        if linha.startswith(">"):
            if nome_sequencia is not None:
                # já tínhamos capturado a primeira sequência inteira;
                # uma segunda linha de cabeçalho marca o início da próxima,
                # que estamos ignorando de propósito (processamos só a 1ª)
                break
            nome_sequencia = linha[1:].strip() or "sem_nome"
            continue

        if nome_sequencia is None:
            raise ValueError(
                "Arquivo FASTA inválido: esperava uma linha de cabeçalho "
                "iniciando com '>' antes da sequência."
            )

        partes_sequencia.append(linha)

    if nome_sequencia is None or not partes_sequencia:
        raise ValueError("Arquivo FASTA vazio ou sem sequência válida.")

    sequencia = "".join(partes_sequencia).upper()

    bases_invalidas = set(sequencia) - BASES_VALIDAS
    if bases_invalidas:
        raise ValueError(
            f"Sequência contém bases inválidas: {sorted(bases_invalidas)}. "
            f"Eram esperadas apenas A, T, C, G."
        )

    return nome_sequencia, sequencia


def calcular_gc_percentual(sequencia: str) -> float:
    total = len(sequencia)
    if total == 0:
        return 0.0
    gc = sum(1 for base in sequencia if base in "GC")
    return round((gc / total) * 100, 2)


def calcular_complemento_reverso(sequencia: str) -> str:
    complemento = "".join(COMPLEMENTO[base] for base in sequencia)
    return complemento[::-1]
