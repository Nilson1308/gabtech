export type LogoFormato = '1:1' | '1:3' | '3:1'

export const LOGO_FORMATOS: {
  id: LogoFormato
  label: string
  descricao: string
}[] = [
  { id: '1:1', label: 'Quadrado (1:1)', descricao: 'Brasão ou símbolo compacto' },
  { id: '1:3', label: 'Vertical (1:3)', descricao: 'Faixa alta — estreita e alta' },
  { id: '3:1', label: 'Horizontal (3:1)', descricao: 'Faixa larga — logotipo estendido' },
]

export function logoAspectRatio(formato: LogoFormato): number {
  const [w, h] = formato.split(':').map(Number)
  return w / h
}

/** Borda longa 480 px; mantém a proporção escolhida. */
export function logoOutputSize(formato: LogoFormato): { width: number; height: number } {
  const ar = logoAspectRatio(formato)
  const longEdge = 480
  if (ar >= 1) {
    return { width: longEdge, height: Math.round(longEdge / ar) }
  }
  return { width: Math.round(longEdge * ar), height: longEdge }
}

/** Tamanho do preview no formulário (px). */
export function logoPreviewStyle(formato: LogoFormato): { width: string; height: string } {
  const { width, height } = logoOutputSize(formato)
  const scale = 96 / Math.max(width, height)
  return {
    width: `${Math.round(width * scale)}px`,
    height: `${Math.round(height * scale)}px`,
  }
}
