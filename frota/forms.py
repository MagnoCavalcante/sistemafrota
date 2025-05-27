# app_name/forms.py

from django import forms
from django.forms import inlineformset_factory

# Importações de Modelos - Todas concentradas aqui no topo
from .models import (
    Servico, Veiculo, Motorista, Manutencao, Peca,
    ManutencaoPeca, ManutencaoServico, CentroDeCusto, Setor,
    Multa
)

# --- Formulários para Modelos Autônomos (CRUDs Principais) ---

class ServicoForm(forms.ModelForm):
    class Meta:
        model = Servico
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
        }

class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = ['placa', 'modelo', 'combustivel', 'motorista', 'setor', 'valor_fipe', 'ativo', 'motivo_inativo', 'observacoes']
        widgets = {
            'valor_fipe': forms.TextInput(attrs={'id': 'id_valor_fipe', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class MotoristaForm(forms.ModelForm):
    class Meta:
        model = Motorista
        fields = ['nome', 'cnh', 'cpf', 'validade_cnh']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cnh': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control'}),
            'validade_cnh': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class PecaForm(forms.ModelForm):
    class Meta:
        model = Peca
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
        }

class CentroDeCustoForm(forms.ModelForm):
    class Meta:
        model = CentroDeCusto
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
        }

class SetorForm(forms.ModelForm):
    class Meta:
        model = Setor
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
        }

class MultaForm(forms.ModelForm):
    class Meta:
        model = Multa
        fields = ['veiculo', 'motorista', 'data', 'tipo', 'local', 'valor', 'paga', 'observacoes']
        widgets = {
            'veiculo': forms.Select(attrs={'class': 'form-control'}),
            'motorista': forms.Select(attrs={'class': 'form-control'}),
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'local': forms.TextInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'paga': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# --- Formulários e FormSets para Manutenção ---

class ManutencaoForm(forms.ModelForm):
    class Meta:
        model = Manutencao
        exclude = ['pecas', 'servicos']
        widgets = {
            'veiculo': forms.Select(attrs={'class': 'form-control'}),
            'motorista': forms.Select(attrs={'class': 'form-control'}),
            'valor_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fornecedor': forms.TextInput(attrs={'class': 'form-control'}),
            'vale': forms.Select(attrs={'class': 'form-control'}),
            'data_manutencao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'orcamento': forms.FileInput(attrs={'class': 'form-control-file'}),
            'tipo_manutencao_1': forms.Select(attrs={'class': 'form-control'}),
            'tipo_manutencao_2': forms.Select(attrs={'class': 'form-control'}),
            'quilometragem': forms.NumberInput(attrs={'class': 'form-control'}),
            'centro_custo': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update({'class': 'form-control'})


    observacoes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        required=False,
        label="Observações"
    )

# Formulário para itens de Peça em Manutenção
class ManutencaoPecaForm(forms.ModelForm):
    class Meta:
        model = ManutencaoPeca
        fields = ['peca', 'valor_unitario', 'quantidade']
        widgets = {
            'peca': forms.Select(attrs={'class': 'form-control'}),
            'valor_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    # MÉTODO __init__ AGORA CORRETAMENTE DENTRO DA CLASSE E AJUSTADO
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk is None: # Se é um formulário 'extra' (novo)
            self.fields['peca'].required = False
            self.fields['valor_unitario'].required = False
            self.fields['quantidade'].required = False # Quantidade também pode ser opcional aqui
        else: # Se é um formulário existente
            # Os campos são requeridos, a menos que ele esteja marcado para DELETE
            if not self.initial.get('DELETE', False): # Se não está marcado para DELETE, é requerido
                self.fields['peca'].required = True
                self.fields['valor_unitario'].required = True
                self.fields['quantidade'].required = True
            else: # Se está marcado para DELETE, eles são opcionais
                self.fields['peca'].required = False
                self.fields['valor_unitario'].required = False
                self.fields['quantidade'].required = False

    # MÉTODO clean() AGORA CORRETAMENTE DENTRO DA CLASSE E AJUSTADO
    def clean_valor_fipe(self):
        valor = self.cleaned_data.get('valor_fipe')
        if isinstance(valor, str):
            valor = valor.replace(',', '.')
        try:
            return float(valor)
        except (ValueError, TypeError):
            raise forms.ValidationError("Insira um valor numérico válido.")

        
        # Lógica para determinar se a linha está "vazia" funcionalmente (para um novo form)
        is_completely_empty = not peca and \
                              (valor_unitario is None or valor_unitario == '') and \
                              (quantidade is None or quantidade == '')
        
        # Se for um formulário novo E completamente vazio, retorne sem erros.
        if self.instance.pk is None and is_completely_empty:
            return cleaned_data

        # Se a linha NÃO está completamente vazia, valide todos os campos
        if not is_completely_empty:
            if not peca:
                self.add_error('peca', "Peça é obrigatória.")
            if valor_unitario is None or valor_unitario == '':
                self.add_error('valor_unitario', "Valor Unitário é obrigatório.")
            if quantidade is None or quantidade == '' or quantidade <= 0:
                self.add_error('quantidade', "Quantidade é obrigatória e deve ser maior que zero.")
            
        return cleaned_data


# Formulário para itens de Serviço em Manutenção
class ManutencaoServicoForm(forms.ModelForm):
    class Meta:
        model = ManutencaoServico
        fields = ['servico', 'valor_unitario', 'quantidade']
        widgets = {
            'servico': forms.Select(attrs={'class': 'form-control'}),
            'valor_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    # MÉTODO __init__ AGORA CORRETAMENTE DENTRO DA CLASSE E AJUSTADO
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk is None: # Se é um formulário 'extra' (novo)
            self.fields['servico'].required = False
            self.fields['valor_unitario'].required = False
            self.fields['quantidade'].required = False # Quantidade também pode ser opcional aqui
        else: # Se é um formulário existente
            # Os campos são requeridos, a menos que ele esteja marcado para DELETE
            if not self.initial.get('DELETE', False):
                self.fields['servico'].required = True
                self.fields['valor_unitario'].required = True
                self.fields['quantidade'].required = True
            else:
                self.fields['servico'].required = False
                self.fields['valor_unitario'].required = False
                self.fields['quantidade'].required = False

    # MÉTODO clean() AGORA CORRETAMENTE DENTRO DA CLASSE E AJUSTADO
    def clean(self):
        cleaned_data = super().clean()
        servico = cleaned_data.get('servico')
        valor_unitario = cleaned_data.get('valor_unitario')
        quantidade = cleaned_data.get('quantidade')
        delete_form = cleaned_data.get('DELETE', False)

        if delete_form: # Se o formulário está marcado para exclusão, pule a validação
            return cleaned_data
        
        is_completely_empty = not servico and \
                              (valor_unitario is None or valor_unitario == '') and \
                              (quantidade is None or quantidade == '')
        
        if self.instance.pk is None and is_completely_empty:
            return cleaned_data

        if not is_completely_empty:
            if not servico:
                self.add_error('servico', "Serviço é obrigatório.")
            if valor_unitario is None or valor_unitario == '':
                self.add_error('valor_unitario', "Valor Unitário é obrigatório.")
            if quantidade is None or quantidade == '' or quantidade <= 0:
                self.add_error('quantidade', "Quantidade é obrigatória e deve ser maior que zero.")
        return cleaned_data

# --- FormSets para Manutenção ---
# Certifique-se de que extra=1 e can_delete=True estão definidos aqui.
# min_num=0 é o padrão para inlineformset_factory para permitir 0 forms.
ManutencaoPecaFormSet = inlineformset_factory(
    Manutencao,
    ManutencaoPeca,
    form=ManutencaoPecaForm,
    extra=1,
    can_delete=True
)

ManutencaoServicoFormSet = inlineformset_factory(
    Manutencao,
    ManutencaoServico,
    form=ManutencaoServicoForm,
    extra=1,
    can_delete=True
)