from rest_framework.routers import DefaultRouter

from .views import (
    AgendamentoAssessoriaViewSet,
    CandidaturaTalentoViewSet,
    EntregaBeneficioViewSet,
    EixoServicoViewSet,
    InscricaoCursoViewSet,
    ItemBeneficioViewSet,
    TurmaCursoViewSet,
    VagaEmpregoViewSet,
)

router = DefaultRouter()
router.register('eixos', EixoServicoViewSet, basename='eixo-servico')
router.register('vagas', VagaEmpregoViewSet, basename='vaga-emprego')
router.register('candidaturas', CandidaturaTalentoViewSet, basename='candidatura-talento')
router.register('beneficios/itens', ItemBeneficioViewSet, basename='item-beneficio')
router.register('beneficios/entregas', EntregaBeneficioViewSet, basename='entrega-beneficio')
router.register('assessorias', AgendamentoAssessoriaViewSet, basename='agendamento-assessoria')
router.register('cursos/turmas', TurmaCursoViewSet, basename='turma-curso')
router.register('cursos/inscricoes', InscricaoCursoViewSet, basename='inscricao-curso')

urlpatterns = router.urls
