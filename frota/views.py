from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import formset_factory # Este import já existe
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm, UserCreationForm
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.views import LogoutView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Importações para Class-Based Views (CBVs)
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView # <-- ADICIONADO

from django.db.models import Q, Sum, Count # Sum e Count já existiam
from django.db.models.functions import TruncMonth # Já existia

from .models import (
    Manutencao, ManutencaoPeca, ManutencaoServico,
    Peca, Servico, Setor, Veiculo, Motorista, CentroDeCusto, Multa
) # Todos já existiam

from .forms import (
    ManutencaoForm, ManutencaoServicoFormSet, PecaForm, ManutencaoPecaFormSet,
    ManutencaoServicoForm, SetorForm, VeiculoForm, MotoristaForm, CentroDeCustoForm,
    ServicoForm, MultaForm # <-- ADICIONADO (MultaForm autônomo)
)

from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages

# Apenas superusuários podem acessar
@user_passes_test(lambda u: u.is_superuser)
def adicionar_usuario(request):
    if request.method == 'POST':
        username = request.POST['username']
        senha = request.POST['senha']
        grupo = request.POST['grupo']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Usuário já existe.')
        else:
            user = User.objects.create_user(username=username, password=senha)
            grupo_obj = Group.objects.get(name=grupo)
            user.groups.add(grupo_obj)
            messages.success(request, 'Usuário criado com sucesso!')
            return redirect('listar_usuarios')  # Alterado para redirecionar para lista de usuários

    grupos = Group.objects.all()
    return render(request, 'usuarios/adicionar_usuario.html', {'grupos': grupos})

@user_passes_test(lambda u: u.is_superuser)
def listar_usuarios(request):
    usuarios = User.objects.all()
    return render(request, 'usuarios/listar_usuarios.html', {'usuarios': usuarios})

@user_passes_test(lambda u: u.is_superuser)
def editar_usuario(request, id):
    usuario = get_object_or_404(User, id=id)
    grupos = Group.objects.all()
    
    if request.method == 'POST':
        username = request.POST.get('username')
        is_active = request.POST.get('is_active') == 'on'
        is_superuser = request.POST.get('is_superuser') == 'on'
        grupo_id = request.POST.get('grupo')
        
        # Atualizar usuário
        usuario.username = username
        usuario.is_active = is_active
        usuario.is_superuser = is_superuser
        usuario.save()
        
        # Atualizar grupos
        usuario.groups.clear()
        if grupo_id:
            grupo = Group.objects.get(id=grupo_id)
            usuario.groups.add(grupo)
        
        messages.success(request, 'Usuário atualizado com sucesso!')
        return redirect('listar_usuarios')
    
    # Obter o grupo atual do usuário (se houver)
    grupo_atual = None
    if usuario.groups.exists():
        grupo_atual = usuario.groups.first()
    
    return render(request, 'usuarios/editar_usuario.html', {
        'usuario': usuario,
        'grupos': grupos,
        'grupo_atual': grupo_atual
    })

@user_passes_test(lambda u: u.is_superuser)
def alterar_senha(request, id):
    usuario = get_object_or_404(User, id=id)
    
    if request.method == 'POST':
        nova_senha = request.POST.get('nova_senha')
        if nova_senha:
            usuario.set_password(nova_senha)
            usuario.save()
            messages.success(request, 'Senha alterada com sucesso!')
            return redirect('listar_usuarios')
    
    return render(request, 'usuarios/alterar_senha.html', {'usuario': usuario})

@user_passes_test(lambda u: u.is_superuser)
def excluir_usuario(request, id):
    usuario = get_object_or_404(User, id=id)
    
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Usuário excluído com sucesso!')
        return redirect('listar_usuarios')
    
    return render(request, 'usuarios/excluir_usuario.html', {'usuario': usuario})

from django.http import HttpResponse
from reportlab.pdfgen import canvas

def exportar_relatorio_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_manutencao.pdf"'

    p = canvas.Canvas(response)
    p.setFont("Helvetica", 12)

    y = 800
    p.drawString(100, y, "Relatório de Manutenções")
    y -= 30

    manutencoes = Manutencao.objects.all()

    for m in manutencoes:
        p.drawString(100, y, f"{m.veiculo} | {m.data_manutencao.strftime('%d/%m/%Y')} | R$ {m.valor_total:.2f}")
        y -= 20
        if y < 100:
            p.showPage()
            y = 800

    p.save()
    return response

from openpyxl import Workbook

def exportar_relatorio_excel(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Relatório de Manutenções"

    ws.append(["Veículo", "Data", "Valor Total", "Fornecedor", "Vale"])

    manutencoes = Manutencao.objects.all()
    for m in manutencoes:
        ws.append([str(m.veiculo), m.data_manutencao.strftime('%d/%m/%Y'), float(m.valor_total), m.fornecedor, m.vale])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=relatorio_manutencao.xlsx'
    wb.save(response)
    return response


# --- VIEWS EXISTENTES ---

def relatorio_manutencoes(request):
    manutencoes = Manutencao.objects.all() # [cite: 1]
    veiculos = Veiculo.objects.all() # [cite: 1]
    centros_de_custo = CentroDeCusto.objects.all()

    # Novos dados para os dropdowns de filtro
    pecas = Peca.objects.all() # [cite: 1]
    motoristas = Motorista.objects.all() # [cite: 1]
    # Para fornecedor, pegaremos os nomes únicos já usados nas manutenções
    fornecedores_manutencao = Manutencao.objects.values_list('fornecedor', flat=True).distinct() # [cite: 151]

    # Filtros existentes
    veiculo_id = request.POST.get('veiculo') # [cite: 1]
    data_inicio = request.POST.get('data_inicio') # [cite: 1]
    data_fim = request.POST.get('data_fim') # [cite: 1]

    # NOVOS FILTROS
    peca_id = request.POST.get('peca') # [cite: 158]
    fornecedor_nome = request.POST.get('fornecedor_filtro') # [cite: 160] (usei fornecedor_filtro para não confundir com o campo 'fornecedor' da Manutencao)
    motorista_id = request.POST.get('motorista') # [cite: 160]

    # Aplicação dos filtros
    if veiculo_id:
        manutencoes = manutencoes.filter(veiculo_id=veiculo_id) # [cite: 1]
    if data_inicio:
        manutencoes = manutencoes.filter(data_manutencao__gte=data_inicio) # [cite: 1]
    if data_fim:
        manutencoes = manutencoes.filter(data_manutencao__lte=data_fim) # [cite: 1]

    # NOVAS CONDIÇÕES DE FILTRO
    if peca_id:
        # Filtra manutenções que usaram uma peça específica através do ManutencaoPeca
        manutencoes = manutencoes.filter(manutencaopeca__peca_id=peca_id).distinct() # [cite: 158]
    if fornecedor_nome:
        manutencoes = manutencoes.filter(fornecedor__icontains=fornecedor_nome) # [cite: 160]
    if motorista_id:
        # Filtra manutenções de veículos associados a um motorista específico
        manutencoes = manutencoes.filter(veiculo__motorista_id=motorista_id).distinct() # [cite: 148, 151, 160]
    centro_id = request.POST.get('centros_de_custo')
    if centro_id:
        manutencoes = manutencoes.filter(centros_de_custo_id=centro_id).distinct()


    context = {
        'manutencoes': manutencoes, # [cite: 1]
        'veiculos': veiculos, # [cite: 1]
        'pecas': pecas, # ADICIONADO
        'motoristas': motoristas, # ADICIONADO
        'fornecedores_manutencao': fornecedores_manutencao, # ADICIONADO
        'centros_de_custo': centros_de_custo,
        # ... outros dados de contexto (gráficos, etc. se estiverem aqui) ...
    }
    return render(request, 'relatorio/relatorio_manutencoes.html', context)

def tela_login(request):
    # Se for uma requisição HEAD, retornar uma resposta vazia com status 200
    if request.method == 'HEAD':
        from django.http import HttpResponse
        return HttpResponse()
        
    next_url = request.GET.get('next', 'painel_frota')
    
    if request.user.is_authenticated:
        return redirect('painel_frota')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Primeiro verifica se o usuário existe
        try:
            user = User.objects.get(username=username)
            # Se o usuário existe, tenta autenticar
            user_auth = authenticate(request, username=username, password=password)
            if user_auth is not None:
                auth_login(request, user_auth)
                return redirect(request.POST.get('next', 'painel_frota'))
            else:
                messages.error(request, 'Senha incorreta. Por favor, tente novamente.')
        except User.DoesNotExist:
            messages.error(request, 'Usuário não encontrado. Verifique se digitou corretamente.')
    
    return render(request, 'login.html', {'next': next_url})

@login_required
def painel_frota(request):
    veiculos_ativos = Veiculo.objects.filter(ativo=True).count()
    veiculos_inativos = Veiculo.objects.filter(ativo=False).count()
    valor_total_frota = Veiculo.objects.aggregate(total=Sum('valor_fipe'))['total'] or 0
    valor_total_manutencao = Manutencao.objects.aggregate(total=Sum('valor_total'))['total'] or 0

    manutencoes_por_mes = (
        Manutencao.objects
        .annotate(mes=TruncMonth('data_manutencao'))
        .values('mes')
        .annotate(total=Sum('valor_total'))
        .order_by('mes')
    )

    labels_meses = [item['mes'].strftime('%b/%y') for item in manutencoes_por_mes]
    valores_meses = [float(item['total']) for item in manutencoes_por_mes]

    tipo1_data = (
        Manutencao.objects
        .values('tipo_manutencao_1')
        .annotate(qtd=Count('id'))
    )
    labels_tipo1 = [d['tipo_manutencao_1'] for d in tipo1_data]
    valores_tipo1 = [d['qtd'] for d in tipo1_data]

    tipo2_data = (
        Manutencao.objects
        .values('tipo_manutencao_2')
        .annotate(qtd=Count('id'))
    )
    labels_tipo2 = [d['tipo_manutencao_2'] for d in tipo2_data]
    valores_tipo2 = [d['qtd'] for d in tipo2_data]

    # --- NOVAS DASHES ---

    # 1. Peças mais utilizadas
    pecas_mais_utilizadas_data = (
        ManutencaoPeca.objects
        .values('peca__nome')
        .annotate(total_quantidade=Sum('quantidade'))
        .order_by('-total_quantidade')
    )[:5]

    # 2. Motoristas com CNH vencida
    data_atual = date.today()
    motoristas_cnh_vencida_lista = Motorista.objects.filter(
        validade_cnh__lt=data_atual
    )

    # --- DADOS PARA O NOVO GRÁFICO: VEÍCULOS POR SETOR ---
    veiculos_por_setor_data = (
        Veiculo.objects
        .values('setor__nome')
        .annotate(total_veiculos=Count('id'))
        .order_by('setor__nome')
    )
    labels_setores = [item['setor__nome'] if item['setor__nome'] else 'Sem Setor' for item in veiculos_por_setor_data]
    valores_setores = [item['total_veiculos'] for item in veiculos_por_setor_data]

    context = {
        'veiculos_ativos': veiculos_ativos,
        'veiculos_inativos': veiculos_inativos,
        'valor_total_frota': valor_total_frota,
        'valor_total_manutencao': valor_total_manutencao,
        'labels_meses': labels_meses,
        'valores_meses': valores_meses,
        'labels_tipo1': labels_tipo1,
        'valores_tipo1': valores_tipo1,
        'labels_tipo2': labels_tipo2,
        'valores_tipo2': valores_tipo2,
        'pecas_mais_utilizadas_data': pecas_mais_utilizadas_data,
        'motoristas_cnh_vencida_lista': motoristas_cnh_vencida_lista,
        'data_atual': data_atual,
        'labels_setores': labels_setores,
        'valores_setores': valores_setores,
    }
    return render(request, 'painel.html', context)

# --- VIEWS PARA VEÍCULOS ---
def cadastrar_veiculo(request):
    if request.method == 'POST':
        form = VeiculoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_veiculos')
    else:
        form = VeiculoForm()
    return render(request, 'veiculo/cadastrar_veiculo.html', {'form': form})

def listar_veiculos(request):
    veiculos = Veiculo.objects.all()
    return render(request, 'veiculo/listar_veiculos.html', {'veiculos': veiculos})

def editar_veiculo(request, id):
    veiculo = get_object_or_404(Veiculo, id=id)
    if request.method == "POST":
        form = VeiculoForm(request.POST, instance=veiculo)
        if form.is_valid():
            form.save()
            return redirect('listar_veiculos')
    else:
        form = VeiculoForm(instance=veiculo)
    return render(request, 'veiculo/editar_veiculo.html', {'form': form, 'veiculo_id': id})

def excluir_veiculo(request, id):
    veiculo = get_object_or_404(Veiculo, id=id)
    veiculo.delete()
    return redirect('listar_veiculos')

# --- VIEWS PARA MOTORISTAS ---
def cadastrar_motorista(request):
    if request.method == 'POST':
        form = MotoristaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_motoristas')
    else:
        form = MotoristaForm()
    return render(request, 'motorista/cadastrar_motorista.html', {'form': form})

def listar_motoristas(request):
    motoristas = Motorista.objects.all()
    context = {
        'motoristas': motoristas,
        'data_atual': date.today(), # <-- ADICIONADO: Passa a data de hoje para o template
    }
    return render(request, 'motorista/listar_motoristas.html', context)

def editar_motorista(request, id):
    motorista = get_object_or_404(Motorista, id=id)
    if request.method == "POST":
        form = MotoristaForm(request.POST, instance=motorista)
        if form.is_valid():
            form.save()
            return redirect('listar_motoristas')
    else:
        form = MotoristaForm(instance=motorista)
    return render(request, 'motorista/editar_motorista.html', {'form': form, 'motorista_id': id, 'data_atual':  date.today()})

def excluir_motorista(request, id):
    motorista = get_object_or_404(Motorista, id=id)
    motorista.delete()
    return redirect('listar_motoristas')

# --- VIEWS PARA MANUTENÇÕES ---
def cadastrar_manutencao(request):
    # Import local para evitar circular import se usado com ManutencaoFormSet
    from .forms import ManutencaoForm, ManutencaoPecaFormSet, ManutencaoServicoFormSet # <-- ADICIONADO ManutencaoServicoFormSet aqui

    if request.method == 'POST':
        manutencao_form = ManutencaoForm(request.POST, request.FILES)
        peca_formset = ManutencaoPecaFormSet(request.POST, prefix='peca') # <-- Adicionado prefix
        servico_formset = ManutencaoServicoFormSet(request.POST, prefix='servico') # <-- ADICIONADO prefix e reativado

        if manutencao_form.is_valid() and peca_formset.is_valid() and servico_formset.is_valid(): # <-- ADICIONADO servico_formset.is_valid()
            manutencao = manutencao_form.save()

            # Salvar peças (Lógica simplificada para formsets)
            peca_formset.instance = manutencao # Associa o formset à instância de Manutencao
            peca_formset.save() # Salva as instâncias de ManutencaoPeca

            # Salvar serviços (Lógica simplificada para formsets com ForeignKey)
            servico_formset.instance = manutencao # Associa o formset à instância de Manutencao
            # O save do formset com ForeignKey já cuida de criar o objeto Servico automaticamente
            # quando a opção é selecionada no dropdown.
            servico_formset.save() # Salva as instâncias de ManutencaoServico

            return redirect('listar_manutencoes')
        else:
            # Em caso de erro, os formulários com os dados submetidos são passados para renderização
            context = {
                'manutencao_form': manutencao_form,
                'peca_formset': peca_formset,
                'servico_formset': servico_formset,
                'pecas_disponiveis': Peca.objects.all(),
                'servicos_disponiveis': Servico.objects.all(),
            }
            return render(request, 'manutencao/cadastrar_manutencao.html', context)

    else: # GET request
        manutencao_form = ManutencaoForm()
        peca_formset = ManutencaoPecaFormSet(prefix='peca') # <-- Adicionado prefix
        servico_formset = ManutencaoServicoFormSet(prefix='servico') # <-- ADICIONADO prefix e reativado

        context = {
            'manutencao_form': manutencao_form,
            'peca_formset': peca_formset,
            'servico_formset': servico_formset,
            'pecas_disponiveis': Peca.objects.all(),
            'servicos_disponiveis': Servico.objects.all(),
        }
        return render(request, 'manutencao/cadastrar_manutencao.html', context)

def listar_manutencoes(request):
    termo_busca = ''
    manutencoes = Manutencao.objects.all()

    if request.method == 'POST':
        termo_busca = request.POST.get('q', '')
        if termo_busca:
            manutencoes = manutencoes.filter(
                Q(veiculo__modelo__icontains=termo_busca) |
                Q(fornecedor__nome__icontains=termo_busca) |
                Q(vale__icontains=termo_busca)
            )

    context = {
        'manutencoes': manutencoes,
        'termo_busca': termo_busca
    }
    return render(request, 'manutencao/listar_manutencoes.html', context)

def editar_manutencao(request, id):
    # Import local para evitar circular import se usado com ManutencaoFormSet
    from .forms import ManutencaoForm, ManutencaoPecaFormSet, ManutencaoServicoFormSet # <-- ADICIONADO ManutencaoServicoFormSet aqui
    manutencao = get_object_or_404(Manutencao, id=id)

    if request.method == 'POST':
        manutencao_form = ManutencaoForm(request.POST, request.FILES, instance=manutencao)
        peca_formset = ManutencaoPecaFormSet(request.POST, instance=manutencao, prefix='peca') # <-- Adicionado prefix
        servico_formset = ManutencaoServicoFormSet(request.POST, instance=manutencao, prefix='servico') # <-- ADICIONADO prefix e reativado

        if manutencao_form.is_valid() and peca_formset.is_valid() and servico_formset.is_valid():
            manutencao = manutencao_form.save()

            # Salva peças
            peca_formset.save() # Save do formset já cuida de tudo

            # Salva serviços
            servico_formset.save() # Save do formset já cuida de tudo

            return redirect('listar_manutencoes')
        else:
            # Em caso de erro, os formulários com os dados submetidos são passados para renderização
            context = {
                'manutencao_form': manutencao_form,
                'manutencao_peca_formset': peca_formset, # Renomeado para peca_formset para consistência
                'manutencao_servico_formset': servico_formset,
                'manutencao_id': id,
                'pecas_disponiveis': Peca.objects.all(),
                'servicos_disponiveis': Servico.objects.all(),
            }
            return render(request, 'manutencao/editar_manutencao.html', context)
    else: # GET request
        manutencao_form = ManutencaoForm(instance=manutencao)
        peca_formset = ManutencaoPecaFormSet(instance=manutencao, prefix='peca') # <-- Adicionado prefix
        servico_formset = ManutencaoServicoFormSet(instance=manutencao, prefix='servico') # <-- ADICIONADO prefix e reativado

        context = {
            'manutencao_form': manutencao_form,
            'peca_formset': peca_formset, # Renomeado para peca_formset para consistência
            'servico_formset': servico_formset,
            'manutencao_id': id,
            'pecas_disponiveis': Peca.objects.all(),
            'servicos_disponiveis': Servico.objects.all(),
        }
    return render(request, 'manutencao/editar_manutencao.html', context)

def excluir_manutencao(request, id):
    manutencao = get_object_or_404(Manutencao, id=id)
    manutencao.delete()
    return redirect('listar_manutencoes')

# --- VIEWS PARA CENTROS DE CUSTO ---
def cadastrar_centro_de_custo(request):
    if request.method == 'POST':
        form = CentroDeCustoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_centros_de_custo')
    else:
        form = CentroDeCustoForm()
    return render(request, 'centro_de_custo/cadastrar_centro_de_custo.html', {'form': form})

def listar_centros_de_custo(request):
    centros_de_custo = CentroDeCusto.objects.all()
    return render(request, 'centro_de_custo/listar_centros_de_custo.html', {'centros_de_custo': centros_de_custo})

def editar_centro_de_custo(request, id):
    centro_de_custo = get_object_or_404(CentroDeCusto, id=id)
    if request.method == "POST":
        form = CentroDeCustoForm(request.POST, instance=centro_de_custo)
        if form.is_valid():
            form.save()
            return redirect('listar_centros_de_custo')
    else:
        form = CentroDeCustoForm(instance=centro_de_custo)
    return render(request, 'centro_de_custo/editar_centro_de_custo.html', {'form': form, 'centro_de_custo_id': id})

def excluir_centro_de_custo(request, id):
    centro_de_custo = get_object_or_404(CentroDeCusto, id=id)
    centro_de_custo.delete()
    return redirect('listar_centros_de_custo')

# --- VIEWS PARA SETORES ---
def cadastrar_setor(request):
    if request.method == 'POST':
        form = SetorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_setores')
    else:
        form = SetorForm()
    return render(request, 'setor/cadastrar_setor.html', {'form': form})

def listar_setores(request):
    setores = Setor.objects.all()
    return render(request, 'setor/listar_setores.html', {'setores': setores})

def editar_setor(request, id):
    setor = get_object_or_404(Setor, id=id)
    if request.method == "POST":
        form = SetorForm(request.POST, instance=setor)
        if form.is_valid():
            form.save()
            return redirect('listar_setores')
    else:
        form = SetorForm(instance=setor)
    return render(request, 'setor/editar_setor.html', {'form': form, 'setor_id': id})

def excluir_setor(request, id):
    setor = get_object_or_404(Setor, id=id)
    setor.delete()
    return redirect('listar_setores')

# --- VIEWS PARA PEÇAS (Autônomo) ---
def cadastrar_peca(request):
    if request.method == 'POST':
        form = PecaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_pecas')
    else:
        form = PecaForm()
    return render(request, 'peca/cadastrar_peca.html', {'form': form})

def listar_pecas(request):
    pecas = Peca.objects.all()
    return render(request, 'peca/listar_pecas.html', {'pecas': pecas, 'request': request})

def editar_peca(request, id):
    peca = get_object_or_404(Peca, id=id)
    if request.method == "POST":
        form = PecaForm(request.POST, instance=peca)
        if form.is_valid():
            form.save()
            return redirect('listar_pecas')
    else:
        form = PecaForm(instance=peca)
    return render(request, 'peca/editar_peca.html', {'form': form, 'peca_id': id})

def excluir_peca(request, id):
    peca = get_object_or_404(Peca, id=id)
    peca.delete()
    return redirect('listar_pecas')

# --- VIEWS AJAX ---
@csrf_exempt
def criar_peca(request):
    """
    View para criar uma nova peça via AJAX.
    """
    from .forms import PecaForm
    if request.method == 'POST':
        data = json.loads(request.body)
        form = PecaForm(data)
        if form.is_valid():
            peca = form.save()
            return JsonResponse({'status': 'success', 'id': peca.id, 'nome': peca.nome})
        else:
            return JsonResponse({'status': 'error', 'message': form.errors})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def criar_servico(request):
    """
    View para criar um novo serviço via AJAX.
    """
    from .models import Servico
    if request.method == 'POST':
        data = json.loads(request.body)
        nome_servico = data.get('nome')
        if nome_servico:
            servico = Servico.objects.create(nome=nome_servico)
            return JsonResponse({'status': 'success', 'id': servico.id, 'nome': servico.nome})
        else:
            return JsonResponse({'status': 'error', 'message': 'Nome do serviço não fornecido'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

# --- REMOVER ESTA VIEW ---
# def cadastrar_servicos(request):
#     from .forms import ManutencaoServicoForm # Import local
#     if request.method == 'POST':
#         form = ManutencaoServicoForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('lista_servicos') # ou outra view de destino
#     else:
#         form = ManutencaoServicoForm()
    
#     return render(request, 'cadastrar_servicos.html', {'form': form})

# --- NOVAS VIEWS PARA SERVIÇOS (Autônomo) - ADICIONADO ---
class ServicoListView(ListView):
    model = Servico
    template_name = 'servicos/servico_list.html'
    context_object_name = 'servicos'

class ServicoCreateView(CreateView):
    model = Servico
    form_class = ServicoForm # Usa o formulário para o modelo Servico autônomo
    template_name = 'servicos/servico_form.html'
    success_url = reverse_lazy('listar_servicos')

class ServicoUpdateView(UpdateView):
    model = Servico
    form_class = ServicoForm
    template_name = 'servicos/servico_form.html'
    success_url = reverse_lazy('listar_servicos')

class ServicoDeleteView(DeleteView):
    model = Servico
    template_name = 'servicos/servico_confirm_delete.html'
    success_url = reverse_lazy('listar_servicos')

# --- VIEWS PARA MULTAS ---
@login_required
def listar_multas(request):
    if request.method == 'POST':
        termo_busca = request.POST.get('q', '')
        multas = Multa.objects.filter(
            Q(veiculo__placa__icontains=termo_busca) |
            Q(motorista__nome__icontains=termo_busca)
        )
    else:
        multas = Multa.objects.all()
    return render(request, 'multa/listar_multas.html', {'multas': multas})

@login_required
def cadastrar_multa(request):
    if request.method == 'POST':
        form = MultaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Multa cadastrada com sucesso!')
            return redirect('listar_multas')
    else:
        form = MultaForm()
    return render(request, 'multa/cadastrar_multa.html', {'form': form})

@login_required
def editar_multa(request, pk):
    multa = get_object_or_404(Multa, pk=pk)
    if request.method == 'POST':
        form = MultaForm(request.POST, instance=multa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Multa atualizada com sucesso!')
            return redirect('listar_multas')
    else:
        form = MultaForm(instance=multa)
    return render(request, 'multa/editar_multa.html', {'form': form})

@login_required
def excluir_multa(request, pk):
    multa = get_object_or_404(Multa, pk=pk)
    if request.method == 'POST':
        multa.delete()
        messages.success(request, 'Multa excluída com sucesso!')
        return redirect('listar_multas')
    return render(request, 'multa/excluir_multa.html', {'multa': multa})