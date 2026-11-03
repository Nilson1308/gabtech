/**
 * Composable para formatação de dados
 */
export function useFormatters() {
  const formatDate = (
    dateString: string | undefined | null,
    includeTime = false
  ): string => {
    if (!dateString) return '—'

    const date = new Date(dateString)
    if (Number.isNaN(date.getTime())) return '—'

    if (includeTime) {
      return new Intl.DateTimeFormat('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      }).format(date)
    }
    
    return new Intl.DateTimeFormat('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    }).format(date)
  }
  
  const formatRelativeTime = (dateString: string | undefined | null): string => {
    if (!dateString) return '—'

    const date = new Date(dateString)
    if (Number.isNaN(date.getTime())) return '—'

    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffSecs = Math.floor(diffMs / 1000)
    const diffMins = Math.floor(diffSecs / 60)
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)
    
    if (diffSecs < 60) return 'agora mesmo'
    if (diffMins < 60) return `há ${diffMins} minuto${diffMins > 1 ? 's' : ''}`
    if (diffHours < 24) return `há ${diffHours} hora${diffHours > 1 ? 's' : ''}`
    if (diffDays < 7) return `há ${diffDays} dia${diffDays > 1 ? 's' : ''}`
    
    return formatDate(dateString)
  }
  
  const formatPhone = (phone: string): string => {
    return phone.replace(/\D/g, '')
      .replace(/^(\d{2})(\d{4,5})(\d{4})$/, '($1) $2-$3')
  }
  
  const formatCPF = (cpf: string): string => {
    return cpf.replace(/\D/g, '')
      .replace(/^(\d{3})(\d{3})(\d{3})(\d{2})$/, '$1.$2.$3-$4')
  }
  
  const formatCEP = (cep: string): string => {
    return cep.replace(/\D/g, '')
      .replace(/^(\d{5})(\d{3})$/, '$1-$2')
  }
  
  const getInitials = (name: string): string => {
    return name
      .split(' ')
      .filter(word => word.length > 0)
      .map(word => word[0])
      .slice(0, 2)
      .join('')
      .toUpperCase()
  }
  
  const truncate = (text: string, maxLength: number): string => {
    if (text.length <= maxLength) return text
    return text.slice(0, maxLength) + '...'
  }
  
  return {
    formatDate,
    formatRelativeTime,
    formatPhone,
    formatCPF,
    formatCEP,
    getInitials,
    truncate,
  }
}
