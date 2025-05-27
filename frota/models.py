from django.db import models

class Veiculo(models.Model):
    placa = models.CharField(max_length=10, unique=True, verbose_name='Placa')
    modelo = models.CharField(max_length=100, verbose_name='Modelo')
    combustivel = models.CharField(max_length=50, verbose_name='Combustível')
    motorista = models.ForeignKey('Motorista', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Motorista')
    setor = models.ForeignKey('Setor', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Setor')
    valor_fipe = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Valor FIPE')
    observacoes = models.TextField(blank=True, null=True, verbose_name='Observações')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    motivo_inativo = models.CharField(
        max_length=20,
        choices=(
            ('SEM_OPERACAO', 'Sem Operação'),
            ('EM_MANUTENCAO', 'Em Manutenção'),
        ),
        null=True,
        blank=True,
        verbose_name='Motivo Inativo'
    )

    def __str__(self):
        return f"{self.placa} - {self.modelo}"

class Motorista(models.Model):
    nome = models.CharField(max_length=200, verbose_name='Nome')
    cnh = models.CharField(max_length=20, unique=True, verbose_name='CNH')
    cpf = models.CharField(max_length=14, unique=True, verbose_name='CPF')
    validade_cnh = models.DateField(verbose_name='Validade CNH', null=True, blank=True)
    
    def __str__(self):
        return self.nome

class Setor(models.Model):
    nome = models.CharField(max_length=100, verbose_name='Nome')
    def __str__(self):
        return self.nome

class Peca(models.Model):
    nome = models.CharField(max_length=200, unique=True, verbose_name='Peça')

    def __str__(self):
        return self.nome
    
class Servico(models.Model):
    nome = models.CharField(max_length=200, unique=True, verbose_name='Serviço')

    def __str__(self):
        return self.nome
    
class Manutencao(models.Model):
    veiculo = models.ForeignKey('Veiculo', on_delete=models.CASCADE, verbose_name='Veículo')
    pecas = models.ManyToManyField(Peca, through='ManutencaoPeca', verbose_name='Peças')
    servicos = models.ManyToManyField(Servico, through='ManutencaoServico', verbose_name='Serviços')
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor Total')
    fornecedor = models.CharField(max_length=200, verbose_name='Fornecedor')
    vale = models.CharField(max_length=3, choices=(('SIM', 'Sim'), ('NAO', 'Não')), verbose_name='Vale')
    data_manutencao = models.DateField(auto_now_add=True, verbose_name='Data da Manutenção')
    orcamento = models.FileField(upload_to='orcamentos/', null=True, blank=True, verbose_name='Orçamento')
    quilometragem = models.IntegerField(verbose_name='Quilometragem')
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    motorista = models.ForeignKey(Motorista, on_delete=models.SET_NULL, null=True, blank=True)
    centro_custo = models.ForeignKey('CentroDeCusto', on_delete=models.SET_NULL, null=True, blank=True)

    TIPO1_CHOICES = [
        ('Corretiva', 'Corretiva'),
        ('Preventiva', 'Preventiva'),
        ('Personalização', 'Personalização'),
    ]

    TIPO2_CHOICES = [
        ('Borracharia', 'Borracharia'),
        ('Revisão', 'Revisão'),
        ('Pneus', 'Pneus'),
        ('Acessórios', 'Acessórios'),
        ('Manutenção', 'Manutenção'),
        ('Plotagem', 'Plotagem'),
        ('Bateria', 'Bateria'),
    ]

    tipo_manutencao_1 = models.CharField(
        max_length=20,
        choices=TIPO1_CHOICES,
        verbose_name="Tipo de Manutenção 1"
    )

    tipo_manutencao_2 = models.CharField(
        max_length=20,
        choices=TIPO2_CHOICES,
        verbose_name="Tipo de Manutenção 2"
    )

    def __str__(self):
        return f"Manutenção do veículo {self.veiculo.placa} em {self.data_manutencao}"
    
class ManutencaoPeca(models.Model):
    manutencao = models.ForeignKey(Manutencao, on_delete=models.CASCADE)
    peca = models.ForeignKey(Peca, on_delete=models.CASCADE, null=True)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor Unitário', null=True, blank=True)
    quantidade = models.PositiveIntegerField(default=1, verbose_name='Quantidade')

    def __str__(self):
        return f"{self.quantidade} x {self.peca.nome} em {self.manutencao}"
    
class ManutencaoServico(models.Model):
    manutencao = models.ForeignKey(Manutencao, on_delete=models.CASCADE)
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE, null=True)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor Unitário', null=True, blank=True)
    quantidade = models.PositiveIntegerField(default=1, verbose_name='Quantidade')
    
    def __str__(self):
        return f"{self.servico.nome} em {self.manutencao}"

class CentroDeCusto(models.Model):
    nome = models.CharField(max_length=200, unique=True, verbose_name='Nome')

    def __str__(self):
        return self.nome

class Multa(models.Model):
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE, verbose_name='Veículo')
    motorista = models.ForeignKey(Motorista, on_delete=models.SET_NULL, null=True, verbose_name='Motorista Responsável')
    data = models.DateField(verbose_name='Data da Multa')
    
    TIPO_CHOICES = [
        ('VELOCIDADE', 'Excesso de Velocidade'),
        ('ESTACIONAMENTO', 'Estacionamento Irregular'),
        ('SINAL', 'Avançar Sinal'),
        ('DOCUMENTACAO', 'Documentação Irregular'),
        ('OUTRAS', 'Outras Infrações'),
    ]
    
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name='Tipo da Multa')
    local = models.CharField(max_length=200, verbose_name='Local da Multa')
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor da Multa')
    paga = models.BooleanField(default=False, verbose_name='Multa Paga')
    observacoes = models.TextField(blank=True, null=True, verbose_name='Observações')

    def __str__(self):
        return f"Multa {self.tipo} - Veículo {self.veiculo.placa} em {self.data}"

    class Meta:
        verbose_name = 'Multa'
        verbose_name_plural = 'Multas'
        ordering = ['-data']

