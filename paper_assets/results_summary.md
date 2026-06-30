# Sintese interpretativa dos resultados oficiais

A execucao oficial com DeepSeek V4-Flash gerou 30 suites planejadas para 6 funcoes. Destas, 29 suites ficaram executaveis e 1 apresentou sintaxe invalida. O runner registrou 120 execucoes-alvo, das quais 116 foram realmente executadas e 4 foram puladas por invalidez sintatica.

Os resultados agregados mostram `correct_pass_rate` de 41.38%, `false_positive_rate` de 58.62%, `defect_detection_rate_raw` de 100.00% e `reliable_defect_detection_rate` de 41.38%. A leitura principal deve usar `reliable_defect_detection_rate`, porque ela exige que a mesma suite passe na implementacao correta e falhe em pelo menos um bug.

A melhor funcao em deteccao confiavel foi F05, com `reliable_defect_detection_rate` de 80.00%. A pior funcao foi F03, com `reliable_defect_detection_rate` de 0.00%.

O principal achado e que a taxa bruta de falha em bugs superestima a capacidade real dos testes gerados quando observada isoladamente. A interpretacao metodologica correta precisa distinguir falha bruta em bug de deteccao confiavel de defeito, separando falsos positivos e falhas contaminadas.

Limita??es: houve 1 suite invalida sintaticamente, a rodada usa apenas 5 execucoes por funcao e os resultados refletem uma unica rodada oficial com a configuracao congelada do modelo. Nao e apropriado generalizar estes numeros sem analise estatistica adicional.
