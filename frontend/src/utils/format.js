export function formatAngka(nilai, desimal = 2) {
  return Number(nilai).toLocaleString('id-ID', {
    minimumFractionDigits: 0,
    maximumFractionDigits: desimal,
  })
}

export function formatPersenBertanda(nilai, desimal = 1) {
  const tanda = nilai >= 0 ? '+' : '-'
  return `${tanda}${formatAngka(Math.abs(nilai), desimal)}%`
}