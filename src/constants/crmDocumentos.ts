export type CategoriaDocumentoCidadao =
  | 'curriculo'
  | 'documento_pessoal'
  | 'laudo_medico'
  | 'comprovante_residencia'
  | 'outros'

export const CATEGORIAS_DOCUMENTO_CIDADAO: Array<{
  value: CategoriaDocumentoCidadao
  label: string
}> = [
  { value: 'curriculo', label: 'Currículo' },
  { value: 'documento_pessoal', label: 'Documento pessoal' },
  { value: 'laudo_medico', label: 'Laudo médico' },
  { value: 'comprovante_residencia', label: 'Comprovante de residência' },
  { value: 'outros', label: 'Outros' },
]

export function labelCategoriaDocumento(categoria: CategoriaDocumentoCidadao): string {
  return CATEGORIAS_DOCUMENTO_CIDADAO.find(c => c.value === categoria)?.label ?? categoria
}
