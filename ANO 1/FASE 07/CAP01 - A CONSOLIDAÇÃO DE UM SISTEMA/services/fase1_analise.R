# =============================================================
# FarmTech Solutions - Fase 1: Análise Estatística em R
# -------------------------------------------------------------
# Recebe o caminho de um CSV como argumento e imprime média,
# desvio padrão, mínimo, máximo e quartis das colunas numéricas.
# Usa apenas R base (sem pacotes externos).
#
# Uso:
#   Rscript services/fase1_analise.R data/clima_atual.csv
#
# Autores: Grupo 37 - FIAP - 1TIAOS
# FIAP - Fase 7 - 2026
# =============================================================

args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 1) {
  cat("Uso: Rscript fase1_analise.R <caminho_para_csv>\n")
  quit(status = 1)
}

caminho <- args[1]

if (!file.exists(caminho)) {
  cat(sprintf("Arquivo nao encontrado: %s\n", caminho))
  quit(status = 2)
}

# Leitura do CSV (R base) -----------------------------------
dados <- tryCatch(
  read.csv(caminho, stringsAsFactors = FALSE, check.names = FALSE),
  error = function(e) {
    cat(sprintf("Erro ao ler CSV: %s\n", conditionMessage(e)))
    quit(status = 3)
  }
)

cat("============================================================\n")
cat("  FarmTech Solutions - Analise Estatistica (R)\n")
cat("============================================================\n")
cat(sprintf("Arquivo:        %s\n", caminho))
cat(sprintf("Linhas:         %d\n", nrow(dados)))
cat(sprintf("Colunas totais: %d\n", ncol(dados)))

# Selecionar apenas colunas numericas -----------------------
mascara_num <- vapply(dados, is.numeric, logical(1))
numericas <- dados[, mascara_num, drop = FALSE]

if (ncol(numericas) == 0) {
  cat("\nNenhuma coluna numerica encontrada no CSV.\n")
  quit(status = 0)
}

cat(sprintf("Colunas numericas analisadas: %d\n", ncol(numericas)))
cat("------------------------------------------------------------\n")

# Estatisticas por coluna -----------------------------------
for (nome in colnames(numericas)) {
  valores <- numericas[[nome]]
  valores <- valores[!is.na(valores)]

  if (length(valores) == 0) {
    cat(sprintf("\n[%s] sem valores validos.\n", nome))
    next
  }

  media   <- mean(valores)
  desvio  <- if (length(valores) > 1) sd(valores) else 0
  minimo  <- min(valores)
  maximo  <- max(valores)
  quartis <- quantile(valores, probs = c(0.25, 0.50, 0.75), names = FALSE)

  cat(sprintf("\nColuna: %s\n", nome))
  cat(sprintf("  N validos        : %d\n", length(valores)))
  cat(sprintf("  Media            : %.4f\n", media))
  cat(sprintf("  Desvio padrao    : %.4f\n", desvio))
  cat(sprintf("  Minimo           : %.4f\n", minimo))
  cat(sprintf("  Q1 (25%%)         : %.4f\n", quartis[1]))
  cat(sprintf("  Mediana (Q2/50%%) : %.4f\n", quartis[2]))
  cat(sprintf("  Q3 (75%%)         : %.4f\n", quartis[3]))
  cat(sprintf("  Maximo           : %.4f\n", maximo))
}

cat("\n============================================================\n")
cat("  Analise concluida com sucesso.\n")
cat("============================================================\n")
