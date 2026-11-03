<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  Users,
  Inbox,
  Calendar,
  FileText,
  Settings,
  PartyPopper,
  Search,
  ChevronRight,
  Briefcase,
  MapPin,
  Shield,
  LayoutDashboard,
  LogIn,
} from 'lucide-vue-next'

const busca = ref('')
const secaoAtiva = ref('introducao')

interface Artigo {
  id: string
  titulo: string
  icone: typeof Users
  conteudo: string[]
}

const artigos: Artigo[] = [
  {
    id: 'introducao',
    titulo: 'Introdução',
    icone: Search,
    conteudo: [
      'Bem-vindo ao Manual do Usuário do GabTech.',
      'Esta plataforma integra CRM, atendimentos, serviços, agenda, documentos e cerimonial em um ambiente <strong>multi-tenant</strong> (cada mandato com dados isolados).',
      'O acesso é feito com <strong>login e senha</strong>; as telas e ações disponíveis dependem do <strong>perfil RBAC</strong> atribuído ao seu usuário.',
      'Use o menu lateral do manual para ir direto ao módulo desejado. A busca acima filtra tópicos pelo título ou pelo texto.',
    ],
  },
  {
    id: 'acesso',
    titulo: 'Acesso e perfil',
    icone: LogIn,
    conteudo: [
      '<strong>Login</strong>',
      'Informe e-mail e senha na tela inicial. Em caso de sessão expirada, faça login novamente.',
      '',
      '<strong>Meu perfil</strong>',
      'Altere nome, avatar e senha em Meu Perfil. Dados de cargo e permissões são gerenciados pela equipe de governança.',
      '',
      '<strong>Permissões</strong>',
      'Se um botão ou menu não aparecer, seu perfil pode não ter a permissão necessária (ex.: ler CRM, gerenciar convidados, disparar comunicação). Solicite ajuste ao administrador do mandato.',
    ],
  },
  {
    id: 'dashboard',
    titulo: 'Dashboard',
    icone: LayoutDashboard,
    conteudo: [
      '<strong>Visão operacional</strong>',
      'Indicadores de atendimentos, produtividade, macrotemas e alertas conforme seu nível de acesso.',
      '',
      '<strong>Inteligência territorial</strong>',
      'Gráficos e recortes ajudam a priorizar demandas por região ou tema (quando habilitado no perfil).',
    ],
  },
  {
    id: 'crm',
    titulo: 'CRM (Cidadãos)',
    icone: Users,
    conteudo: [
      '<strong>Cadastro 360º</strong>',
      'Nome, contatos, endereço (com geocodificação quando disponível), foto, observações e anexos (documentos, currículo etc.).',
      '',
      '<strong>Nome social</strong>',
      'Quando informado, o nome social tem prioridade na exibição (Decreto 8.727/2016).',
      '',
      '<strong>Tags e perfis</strong>',
      '• <strong>Segmentação:</strong> marcadores do cidadão (Idoso, PCD, liderança…)',
      '• <strong>Contexto institucional:</strong> vínculo órgão/cargo nos perfis profissionais',
      '• <strong>Contexto profissional:</strong> currículos, vagas e turmas (Serviços)',
      '• <strong>Ambos:</strong> uso combinado em marcadores e perfis',
      '',
      '<strong>Busca</strong>',
      'Listagem paginada e busca na API por nome, CPF ou telefone (mín. 2 caracteres) — não depende só da página carregada.',
      '',
      '<strong>Rastreabilidade</strong>',
      'Registros exibem última alteração (data, hora, usuário). O histórico completo pode ser consultado quando disponível na tela.',
    ],
  },
  {
    id: 'atendimentos',
    titulo: 'Atendimentos',
    icone: Inbox,
    conteudo: [
      '<strong>Protocolos e demandas</strong>',
      'Registre solicitações vinculadas a cidadãos, macrotemas e tags de atendimento.',
      '',
      '<strong>Status</strong>',
      'Fluxo típico: Aberto → Em andamento → Aguardando terceiros → Concluído. Reatribua responsáveis quando necessário.',
      '',
      '<strong>SLA</strong>',
      'Em Configurações → SLA de Atendimentos, prazos por prioridade podem ser definidos em <strong>dias</strong> ou <strong>horas</strong> (convertidos automaticamente no sistema).',
      '',
      '<strong>Exclusão</strong>',
      'Regra comum: exclusão permitida apenas enquanto o protocolo estiver em status Aberto (conforme permissão).',
    ],
  },
  {
    id: 'servicos',
    titulo: 'Serviços & Entregas',
    icone: Briefcase,
    conteudo: [
      '<strong>Visão geral</strong>',
      'Programas de emprego, assistência e capacitação com público-alvo por tags do CRM.',
      '',
      '<strong>Banco de talentos</strong>',
      'Vagas, candidatos e matchmaking por interseção de tags e currículos.',
      '',
      '<strong>Benefícios / Assistência</strong>',
      'Itens de programa social com sugestão de público elegível.',
      '',
      '<strong>Cursos</strong>',
      'Turmas, vagas e convocação de participantes alinhada às tags cadastradas.',
    ],
  },
  {
    id: 'agenda',
    titulo: 'Agenda',
    icone: Calendar,
    conteudo: [
      '<strong>Calendário</strong>',
      'Visualizações mês, semana e dia (FullCalendar). Compromissos oficiais do gabinete.',
      '',
      '<strong>Espaços e tipos</strong>',
      'Cadastre salas/auditórios e categorias de evento em Configurações → Agenda & Cerimonial.',
      '',
      '<strong>Integrações</strong>',
      'Google Calendar e Outlook: configure credenciais em Integrações (requer permissão de administrador).',
    ],
  },
  {
    id: 'eventos',
    titulo: 'Eventos & Cerimonial',
    icone: PartyPopper,
    conteudo: [
      '<strong>Dashboard do evento</strong>',
      'Abas: Geral, Logística, Convidados, Credenciamento e Comunicação.',
      '',
      '<strong>Convidados</strong>',
      'Busque cidadãos no CRM (API), cadastre novos contatos, escolha perfil quando houver vários cargos, ordene precedência (arrastar) e marque VIP.',
      '',
      '<strong>Credenciamento</strong>',
      'QR Code e check-in; página pública de credenciamento por link do evento.',
      '',
      '<strong>Comunicação & mailing</strong>',
      'Segmentação: convidados confirmados + tags do CRM (todas as tags do módulo CRM). Estimativa de audiência por contagem na base. Canais: e-mail, WhatsApp ou SMS (conforme integrações). Variáveis como {{Nome_Contato}}, {{Titulo_Evento}}, {{Data_Evento}}.',
      '',
      '<strong>Logística</strong>',
      'Checklist por categoria, link público para fornecedores (quando configurado) e relatórios de impressão.',
    ],
  },
  {
    id: 'documentos',
    titulo: 'Documentos',
    icone: FileText,
    conteudo: [
      '<strong>Organização</strong>',
      'Pastas, tipos de documento e templates oficiais.',
      '',
      '<strong>Editor</strong>',
      'Rich text, variáveis dinâmicas, imagens e tabelas. Status: rascunho, pendente, assinado, enviado.',
      '',
      '<strong>Assinatura</strong>',
      'Fluxo de finalização conforme permissões do módulo Documentos.',
    ],
  },
  {
    id: 'mapa',
    titulo: 'Mapa territorial',
    icone: MapPin,
    conteudo: [
      '<strong>Mapa</strong>',
      'Pins de cidadãos georreferenciados e zonas de calor por macrotema ou bairro (OpenStreetMap / Leaflet).',
      '',
      '<strong>Filtros</strong>',
      'Refine macrotemas e bairros para análise de concentração de demandas.',
    ],
  },
  {
    id: 'auditoria',
    titulo: 'Auditoria e rastreabilidade',
    icone: Shield,
    conteudo: [
      '<strong>O que é registrado</strong>',
      'Criação, alteração e exclusão em cadastros principais (CRM, atendimentos, agenda, documentos, cerimonial, serviços, usuários etc.).',
      '',
      '<strong>Na interface</strong>',
      'Metadado de “última ação” nos formulários e listagens. Modal de histórico com linha do tempo por registro (quando o módulo expõe o botão).',
      '',
      '<strong>Boas práticas</strong>',
      'Use contas individuais (não compartilhe login) para que a trilha reflita quem realmente executou a ação.',
    ],
  },
  {
    id: 'configuracoes',
    titulo: 'Configurações',
    icone: Settings,
    conteudo: [
      '<strong>Hub central</strong>',
      'Seções visíveis conforme permissão (Classificações, Macrotemas, SLA, Documentos, Agenda, Integrações, Comunicação, Usuários, Governança).',
      '',
      '<strong>Classificações (Tags)</strong>',
      'Tipos: segmentação, contexto institucional, contexto profissional ou ambos. Módulos CRM e/ou Atendimentos.',
      '',
      '<strong>Macrotemas</strong>',
      'Grandes categorias estatísticas dos atendimentos.',
      '',
      '<strong>SLA de atendimentos</strong>',
      'Prazos por prioridade em dias ou horas.',
      '',
      '<strong>Governança</strong>',
      'Matriz RBAC: perfis, permissões atômicas e vínculo de usuários.',
      '',
      '<strong>Comunicação</strong>',
      'SMTP, WhatsApp Business e SMS — necessários para disparos reais a partir do cerimonial.',
    ],
  },
]

const artigosFiltrados = computed(() => {
  if (!busca.value.trim()) return artigos

  const query = busca.value.toLowerCase()
  return artigos.filter(
    artigo =>
      artigo.titulo.toLowerCase().includes(query) ||
      artigo.conteudo.some(linha => linha.toLowerCase().includes(query)),
  )
})

const artigoAtivo = computed(() => artigos.find(a => a.id === secaoAtiva.value))

const corSecao: Record<string, string> = {
  introducao: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400',
  acesso: 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400',
  dashboard: 'bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400',
  crm: 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400',
  atendimentos: 'bg-sky-100 dark:bg-sky-900/30 text-sky-600 dark:text-sky-400',
  servicos: 'bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400',
  agenda: 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400',
  eventos: 'bg-pink-100 dark:bg-pink-900/30 text-pink-600 dark:text-pink-400',
  documentos: 'bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400',
  mapa: 'bg-teal-100 dark:bg-teal-900/30 text-teal-600 dark:text-teal-400',
  auditoria: 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400',
  configuracoes: 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400',
}
</script>

<template>
  <div class="flex gap-6 h-[calc(100vh-120px)]">
    <aside class="w-72 flex-shrink-0">
      <div class="card sticky top-6 max-h-[calc(100vh-150px)] overflow-y-auto">
        <div class="mb-4">
          <h2 class="text-lg font-bold text-gray-900 dark:text-slate-100 mb-2">Manual do usuário</h2>
          <div class="relative">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              v-model="busca"
              type="search"
              placeholder="Buscar..."
              class="input pl-10 text-sm"
              autocomplete="off"
            />
          </div>
        </div>

        <nav class="space-y-1">
          <button
            v-for="artigo in artigosFiltrados"
            :key="artigo.id"
            type="button"
            @click="secaoAtiva = artigo.id"
            :class="[
              secaoAtiva === artigo.id
                ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 border-primary-500 dark:border-primary-600'
                : 'bg-white dark:bg-slate-800 text-gray-700 dark:text-slate-300 border-transparent hover:bg-gray-50 dark:hover:bg-slate-700',
              'w-full flex items-center gap-3 p-3 rounded-lg border-l-4 transition-colors text-left',
            ]"
          >
            <component :is="artigo.icone" class="w-5 h-5 flex-shrink-0" />
            <span class="font-medium text-sm">{{ artigo.titulo }}</span>
            <ChevronRight class="w-4 h-4 ml-auto opacity-50" />
          </button>
        </nav>
      </div>
    </aside>

    <main class="flex-1 overflow-y-auto">
      <div v-if="artigoAtivo" class="card prose prose-slate dark:prose-invert max-w-none">
        <div class="flex items-center gap-3 mb-6 pb-6 border-b border-gray-200 dark:border-slate-700">
          <div
            class="w-14 h-14 rounded-xl flex items-center justify-center"
            :class="corSecao[artigoAtivo.id] ?? corSecao.introducao"
          >
            <component :is="artigoAtivo.icone" class="w-7 h-7" />
          </div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-slate-100 m-0">
            {{ artigoAtivo.titulo }}
          </h1>
        </div>

        <div class="space-y-4 leading-relaxed">
          <p
            v-for="(linha, index) in artigoAtivo.conteudo"
            :key="index"
            v-html="linha"
            :class="linha === '' ? 'mb-0 h-0' : 'text-gray-700 dark:text-slate-300'"
          />
        </div>
      </div>

      <div v-else-if="busca" class="card text-center py-12">
        <Search class="w-16 h-16 text-gray-300 dark:text-slate-600 mx-auto mb-4" />
        <p class="text-gray-500 dark:text-slate-400">
          Nenhum artigo encontrado para «{{ busca }}»
        </p>
      </div>
    </main>
  </div>
</template>
