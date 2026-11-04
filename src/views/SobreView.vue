<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { BookOpen, Code, Mail, ExternalLink, CheckCircle, Server, Shield } from 'lucide-vue-next'

const versao = 'v1.2.0'
const dataReferencia = 'Novembro de 2026'

const changelog = [
  {
    versao: 'v1.2.0',
    data: 'Nov 2026',
    itens: [
      'Dashboard e CRM com carregamento paginado/resumido para bases grandes',
      'Migração de mandatos legados (CRM, atendimentos, agenda, anexos, acervo legislativo em Documentos)',
      'Agenda: eventos por período visível; calendário legível no tema escuro; layout mobile',
      'Documentos: seleção em massa para mover à pasta; listagem responsiva',
      'Mapa territorial: painéis acima do mapa; layout adaptado ao celular',
      'Configurações, Manual e Sobre atualizados',
    ],
  },
  {
    versao: 'v1.1.0',
    data: '30 Out 2026',
    itens: [
      'Auditoria e rastreabilidade em cadastros (última ação + histórico por registro)',
      'SLA de atendimentos configurável em dias ou horas',
      'Busca de cidadãos na API em convidados de eventos e segmentação de mailing por tags CRM',
      'Módulo Serviços & Entregas (talentos, benefícios, cursos) com matchmaking por tags',
      'Melhorias de permissões RBAC para cerimonial e comunicação',
    ],
  },
  {
    versao: 'v1.0.0',
    data: '29 Out 2026',
    itens: [
      'Plataforma multi-tenant com autenticação JWT e isolamento por mandato',
      'CRM, Atendimentos, Agenda, Documentos, Eventos & Cerimonial',
      'Dashboard operacional, mapa territorial e governança RBAC',
      'Credenciamento público, logística de evento e hub de configurações',
      'Interface responsiva com tema claro e escuro',
    ],
  },
]

const modulos = [
  {
    titulo: 'CRM (Cidadãos)',
    descricao: 'Cadastro 360º, nome social, perfis profissionais, marcadores, anexos e exportação.',
  },
  {
    titulo: 'Atendimentos',
    descricao: 'Protocolos, macrotemas, tags, responsáveis, SLA e workflow de status.',
  },
  {
    titulo: 'Serviços & Entregas',
    descricao: 'Banco de talentos, vagas, assistência social e turmas de capacitação.',
  },
  {
    titulo: 'Agenda',
    descricao: 'Calendário oficial, espaços, tipos de evento e integrações de calendário.',
  },
  {
    titulo: 'Eventos & Cerimonial',
    descricao: 'Checklist, convidados, credenciamento, comunicação segmentada e prismas.',
  },
  {
    titulo: 'Documentos',
    descricao: 'Pastas, templates, editor rich text, tipos e fluxo de assinatura.',
  },
  {
    titulo: 'Mapa & Inteligência',
    descricao: 'Visualização georreferenciada e recortes territoriais por macrotema.',
  },
  {
    titulo: 'Governança & Auditoria',
    descricao: 'Perfis RBAC, usuários da equipe e trilha de alterações nos registros.',
  },
]

const tecnologiasFrontend = [
  { nome: 'Vue 3', descricao: 'Interface reativa com Composition API' },
  { nome: 'TypeScript', descricao: 'Tipagem estática no cliente' },
  { nome: 'Pinia', descricao: 'Estado global e stores por módulo' },
  { nome: 'Tailwind CSS', descricao: 'Design system utility-first' },
  { nome: 'Vite', descricao: 'Build e dev server' },
  { nome: 'Leaflet', descricao: 'Mapas interativos (OpenStreetMap)' },
]

const tecnologiasBackend = [
  { nome: 'Django & DRF', descricao: 'API REST e regras de negócio' },
  { nome: 'PostgreSQL', descricao: 'Dados relacionais multi-tenant (schemas)' },
  { nome: 'JWT', descricao: 'Sessões autenticadas para a SPA' },
  { nome: 'RBAC', descricao: 'Permissões granulares por módulo e ação' },
]
</script>

<template>
  <div class="max-w-5xl mx-auto space-y-8">
    <div class="text-center py-12">
      <div class="inline-flex items-center justify-center mb-6">
        <img
          src="/logo_gt_tema_claro_completo.png"
          alt="GabTech"
          class="h-16 w-auto dark:hidden"
        />
        <img
          src="/logo_gt_tema_escuro_completo.png"
          alt="GabTech"
          class="h-16 w-auto hidden dark:block"
        />
      </div>
      <p class="text-xl text-gray-600 dark:text-slate-400 mb-2">
        Plataforma integrada de gestão para gabinetes e equipes de mandato
      </p>
      <div
        class="inline-flex items-center gap-2 px-4 py-2 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400 rounded-full"
      >
        <span class="font-semibold">{{ versao }}</span>
        <span class="text-sm">•</span>
        <span class="text-sm">{{ dataReferencia }}</span>
      </div>
    </div>

    <div class="card">
      <div class="flex items-center gap-3 mb-6">
        <div class="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
          <BookOpen class="w-6 h-6 text-blue-600 dark:text-blue-400" />
        </div>
        <div>
          <h2 class="text-2xl font-bold text-gray-900 dark:text-slate-100">Sobre o sistema</h2>
          <p class="text-sm text-gray-600 dark:text-slate-400">SaaS para operações de gabinete</p>
        </div>
      </div>

      <div class="space-y-4 text-gray-700 dark:text-slate-300">
        <p>
          O <strong class="text-gray-900 dark:text-slate-100">GabTech</strong> centraliza cidadãos,
          demandas, agenda, documentos, cerimonial e programas sociais em um único ambiente, com
          controle de acesso por perfil e registro de quem alterou cada dado.
        </p>
        <p>
          Cada mandato opera com dados isolados. O acesso é feito com
          <strong class="text-gray-900 dark:text-slate-100">login e senha</strong>.
        </p>
        <p>
          O produto prioriza <strong class="text-gray-900 dark:text-slate-100">LGPD</strong>,
          rastreabilidade, produtividade da equipe e integração entre módulos — o mesmo cidadão
          aparece no CRM, no atendimento, no evento e nos serviços.
        </p>
      </div>
    </div>

    <div class="card">
      <h3 class="text-xl font-bold text-gray-900 dark:text-slate-100 mb-6">Módulos principais</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          v-for="mod in modulos"
          :key="mod.titulo"
          class="flex items-start gap-3 p-4 bg-gray-50 dark:bg-slate-800/50 rounded-lg"
        >
          <CheckCircle class="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
          <div>
            <h4 class="font-semibold text-gray-900 dark:text-slate-100 mb-1">{{ mod.titulo }}</h4>
            <p class="text-sm text-gray-600 dark:text-slate-400">{{ mod.descricao }}</p>
          </div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="card">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
            <Code class="w-6 h-6 text-purple-600 dark:text-purple-400" />
          </div>
          <div>
            <h2 class="text-xl font-bold text-gray-900 dark:text-slate-100">Frontend</h2>
            <p class="text-sm text-gray-600 dark:text-slate-400">SPA Vue</p>
          </div>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div
            v-for="tech in tecnologiasFrontend"
            :key="tech.nome"
            class="p-3 bg-gray-50 dark:bg-slate-800/50 rounded-lg border border-gray-200 dark:border-slate-700"
          >
            <h4 class="font-semibold text-gray-900 dark:text-slate-100 text-sm">{{ tech.nome }}</h4>
            <p class="text-xs text-gray-600 dark:text-slate-400 mt-0.5">{{ tech.descricao }}</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-12 h-12 bg-emerald-100 dark:bg-emerald-900/30 rounded-lg flex items-center justify-center">
            <Server class="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
          </div>
          <div>
            <h2 class="text-xl font-bold text-gray-900 dark:text-slate-100">Backend</h2>
            <p class="text-sm text-gray-600 dark:text-slate-400">API e segurança</p>
          </div>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div
            v-for="tech in tecnologiasBackend"
            :key="tech.nome"
            class="p-3 bg-gray-50 dark:bg-slate-800/50 rounded-lg border border-gray-200 dark:border-slate-700"
          >
            <h4 class="font-semibold text-gray-900 dark:text-slate-100 text-sm">{{ tech.nome }}</h4>
            <p class="text-xs text-gray-600 dark:text-slate-400 mt-0.5">{{ tech.descricao }}</p>
          </div>
        </div>
      </div>
    </div>

    <div class="card border-l-4 border-primary-500">
      <div class="flex items-center gap-3 mb-4">
        <Shield class="w-6 h-6 text-primary-600 dark:text-primary-400" />
        <h3 class="text-xl font-bold text-gray-900 dark:text-slate-100">Privacidade e conformidade</h3>
      </div>
      <p class="text-sm text-gray-700 dark:text-slate-300">
        Consulte a
        <RouterLink to="/privacidade" class="text-primary-600 dark:text-primary-400 hover:underline">
          Política de Privacidade
        </RouterLink>
        para tratamento de dados pessoais. Operações sensíveis dependem das permissões atribuídas ao
        seu perfil (RBAC).
      </p>
    </div>

    <div class="card">
      <h3 class="text-xl font-bold text-gray-900 dark:text-slate-100 mb-6">Histórico de versões</h3>
      <div class="space-y-8">
        <div v-for="release in changelog" :key="release.versao">
          <div class="flex items-center gap-3 mb-3">
            <span
              class="px-3 py-1 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400 rounded-full text-sm font-semibold"
            >
              {{ release.versao }}
            </span>
            <span class="text-sm text-gray-500 dark:text-slate-400">{{ release.data }}</span>
          </div>
          <ul class="space-y-2 ml-1">
            <li
              v-for="(item, index) in release.itens"
              :key="index"
              class="flex items-start gap-2 text-sm text-gray-700 dark:text-slate-300"
            >
              <CheckCircle class="w-4 h-4 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
              <span>{{ item }}</span>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <div class="card">
      <h3 class="text-xl font-bold text-gray-900 dark:text-slate-100 mb-6">Links úteis</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <RouterLink
          to="/manual"
          class="flex items-center justify-between p-4 bg-gray-50 dark:bg-slate-800/50 hover:bg-gray-100 dark:hover:bg-slate-800 rounded-lg border border-gray-200 dark:border-slate-700 transition-colors group"
        >
          <div class="flex items-center gap-3">
            <BookOpen class="w-5 h-5 text-primary-600 dark:text-primary-400" />
            <span class="font-medium text-gray-900 dark:text-slate-100">Manual do usuário</span>
          </div>
          <ExternalLink class="w-4 h-4 text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300" />
        </RouterLink>

        <a
          href="mailto:suporte@gabtech.com"
          class="flex items-center justify-between p-4 bg-gray-50 dark:bg-slate-800/50 hover:bg-gray-100 dark:hover:bg-slate-800 rounded-lg border border-gray-200 dark:border-slate-700 transition-colors group"
        >
          <div class="flex items-center gap-3">
            <Mail class="w-5 h-5 text-primary-600 dark:text-primary-400" />
            <span class="font-medium text-gray-900 dark:text-slate-100">Suporte técnico</span>
          </div>
          <ExternalLink class="w-4 h-4 text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300" />
        </a>
      </div>
    </div>

    <div class="text-center py-8 text-sm text-gray-500 dark:text-slate-400">
      <p>&copy; {{ new Date().getFullYear() }} GabTech. Todos os direitos reservados.</p>
      <p class="mt-1">Gestão moderna para gabinetes públicos e equipes de mandato.</p>
    </div>
  </div>
</template>
