from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

urlpatterns = [
    path('', views.tela_login, name='index'),
    path('painel/', views.painel_frota, name='painel_frota'),
    path('login/', views.tela_login, name='tela_login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='tela_login'), name='logout'),
    path('veiculos/cadastrar/', views.cadastrar_veiculo, name='cadastrar_veiculo'),
    path('veiculos/listar/', views.listar_veiculos, name='listar_veiculos'),
    path('veiculos/editar/<int:id>/', views.editar_veiculo, name='editar_veiculo'),
    path('veiculos/excluir/<int:id>/', views.excluir_veiculo, name='excluir_veiculo'),

    path('motoristas/cadastrar/', views.cadastrar_motorista, name='cadastrar_motorista'),
    path('motoristas/listar/', views.listar_motoristas, name='listar_motoristas'),
    path('motoristas/editar/<int:id>/', views.editar_motorista, name='editar_motorista'),
    path('motoristas/excluir/<int:id>/', views.excluir_motorista, name='excluir_motorista'),

    path('manutencoes/cadastrar/', views.cadastrar_manutencao, name='cadastrar_manutencao'),
    path('manutencoes/listar/', views.listar_manutencoes, name='listar_manutencoes'),
    path('manutencoes/editar/<int:id>/', views.editar_manutencao, name='editar_manutencao'),
    path('manutencoes/excluir/<int:id>/', views.excluir_manutencao, name='excluir_manutencao'),

    path('centros_de_custo/cadastrar/', views.cadastrar_centro_de_custo, name='cadastrar_centro_de_custo'),
    path('centros_de_custo/listar/', views.listar_centros_de_custo, name='listar_centros_de_custo'),
    path('centros_de_custo/editar/<int:id>/', views.editar_centro_de_custo, name='editar_centro_de_custo'),
    path('centros_de_custo/excluir/<int:id>/', views.excluir_centro_de_custo, name='excluir_centro_de_custo'),

    path('setores/cadastrar/', views.cadastrar_setor, name='cadastrar_setor'),
    path('setores/listar/', views.listar_setores, name='listar_setores'),
    path('setores/editar/<int:id>/', views.editar_setor, name='editar_setor'),
    path('setores/excluir/<int:id>/', views.excluir_setor, name='excluir_setor'),

    path('pecas/criar/', views.criar_peca, name='criar_peca'),  # Nova URL para criar peça via AJAX
    path('servicos/criar/', views.criar_servico, name='criar_servico'),  # Nova URL para criar serviço via AJAX
    path('pecas/cadastrar/', views.cadastrar_peca, name='cadastrar_peca'),
    path('pecas/listar/', views.listar_pecas, name='listar_pecas'),
    path('pecas/editar/<int:id>/', views.editar_peca, name='editar_peca'),
    path('pecas/excluir/<int:id>/', views.excluir_peca, name='excluir_peca'),

    path('relatorios/manutencoes/', views.relatorio_manutencoes, name='relatorio_manutencoes'),
    path('relatorios/exportar/pdf/', views.exportar_relatorio_pdf, name='exportar_relatorio_pdf'),
    path('relatorios/exportar/excel/', views.exportar_relatorio_excel, name='exportar_relatorio_excel'),

    path('servicos/', views.ServicoListView.as_view(), name='listar_servicos'),
    path('servicos/cadastrar/', views.ServicoCreateView.as_view(), name='cadastrar_servico'),
    path('servicos/<int:pk>/editar/', views.ServicoUpdateView.as_view(), name='editar_servico'),
    path('servicos/<int:pk>/excluir/', views.ServicoDeleteView.as_view(), name='excluir_servico'),

    path('usuarios/adicionar/', views.adicionar_usuario, name='adicionar_usuario'),
    path('usuarios/listar/', views.listar_usuarios, name='listar_usuarios'),
    path('usuarios/editar/<int:id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/alterar-senha/<int:id>/', views.alterar_senha, name='alterar_senha'),
    path('usuarios/excluir/<int:id>/', views.excluir_usuario, name='excluir_usuario'),

    # URLs para Multas
    path('multas/', views.listar_multas, name='listar_multas'),
    path('multas/cadastrar/', views.cadastrar_multa, name='cadastrar_multa'),
    path('multas/<int:pk>/editar/', views.editar_multa, name='editar_multa'),
    path('multas/<int:pk>/excluir/', views.excluir_multa, name='excluir_multa'),
]
