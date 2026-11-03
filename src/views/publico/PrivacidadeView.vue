<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import PublicBrandHeader from '@/components/public/PublicBrandHeader.vue'
import { Shield } from 'lucide-vue-next'

const route = useRoute()

const contexto = computed(() => (route.query.contexto as string) || 'geral')
const eventoId = computed(() => route.query.evento as string | undefined)

const tituloPagina = computed(() => {
  if (contexto.value === 'credenciamento') {
    return 'Privacidade — credenciamento de eventos'
  }
  return 'Política de privacidade'
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <header class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-10">
      <div class="max-w-3xl mx-auto px-4 py-5 flex justify-center">
        <PublicBrandHeader subtitle="Proteção de dados pessoais" />
      </div>
    </header>

    <main class="max-w-3xl mx-auto px-4 py-10 pb-16 prose prose-gray dark:prose-invert prose-headings:font-semibold">
      <div class="flex items-center gap-3 not-prose mb-8">
        <div class="p-3 rounded-xl bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300">
          <Shield class="w-8 h-8" />
        </div>
        <div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white m-0">
            {{ tituloPagina }}
          </h1>
          <p class="text-sm text-gray-500 dark:text-gray-400 mt-1 m-0">
            GabTech · em conformidade com a LGPD (Lei nº 13.709/2018)
          </p>
        </div>
      </div>

      <section v-if="contexto === 'credenciamento'" class="space-y-4">
        <h2>Credenciamento público</h2>
        <p>
          Ao preencher o formulário de credenciamento
          <span v-if="eventoId"> deste evento</span>,
          você informa dados para que a organização possa registrar sua presença,
          orientar o acesso ao local e, quando necessário, enviar comunicações
          relacionadas exclusivamente à participação no evento.
        </p>

        <h3>Dados coletados</h3>
        <ul>
          <li><strong>Nome completo</strong> — identificação na recepção e lista de presença.</li>
          <li><strong>Telefone / WhatsApp</strong> — contato operacional e confirmação de registro (um cadastro por telefone por evento).</li>
          <li><strong>E-mail, data de nascimento e órgão/instituição</strong> — somente se o organizador do evento tiver habilitado esses campos no formulário.</li>
        </ul>
        <p>
          <strong>Não solicitamos CPF</strong> no credenciamento público padrão do GabTech,
          salvo exigência legal específica definida pelo controlador do evento em outro canal.
        </p>

        <h3>Finalidade e base legal</h3>
        <p>
          O tratamento tem finalidade de <strong>execução de procedimentos preliminares
          relacionados a contrato ou participação em evento</strong> e
          <strong>legítimo interesse</strong> do gabinete/organização em garantir segurança,
          controle de acesso e comunicação com participantes (art. 7º, V e IX da LGPD),
          limitado ao necessário para o evento.
        </p>

        <h3>Compartilhamento e retenção</h3>
        <p>
          Os dados ficam acessíveis à equipe autorizada do tenant (gabinete/organização)
          que administra o evento no GabTech. Não vendemos dados pessoais.
          O prazo de guarda segue a política interna do controlador e a legislação aplicável;
          após o evento, recomenda-se revisão e eliminação ou anonimização quando não houver
          obrigação legal de manutenção.
        </p>

        <h3>Seus direitos</h3>
        <p>
          Você pode solicitar confirmação de tratamento, acesso, correção, eliminação,
          portabilidade ou revogação do consentimento (quando aplicável) junto ao
          <strong>encarregado ou canal de privacidade do gabinete responsável pelo evento</strong>.
        </p>
      </section>

      <section class="space-y-4">
        <h2>Plataforma GabTech</h2>
        <p>
          O GabTech é uma plataforma multi-tenant: cada gabinete ou organização cliente
          atua como <strong>controlador</strong> dos dados inseridos por sua equipe e
          coletados em formulários públicos vinculados aos seus eventos.
          A operação técnica da plataforma é realizada conforme contrato e medidas
          de segurança compatíveis com o estado da arte.
        </p>
        <p>
          Utilizamos cookies e tokens de autenticação apenas para usuários internos
          com login. Formulários públicos (credenciamento e checklist logística)
          não exigem conta de usuário.
        </p>
      </section>

      <section class="not-prose mt-10 pt-6 border-t border-gray-200 dark:border-gray-700">
        <RouterLink
          v-if="contexto === 'credenciamento' && eventoId"
          :to="`/evento/${eventoId}/credenciamento`"
          class="text-blue-600 dark:text-blue-400 font-medium hover:underline"
        >
          ← Voltar ao credenciamento
        </RouterLink>
        <p v-else class="text-sm text-gray-500 dark:text-gray-400">
          Dúvidas: entre em contato com o gabinete ou organização que convidou você ao evento.
        </p>
      </section>
    </main>
  </div>
</template>
