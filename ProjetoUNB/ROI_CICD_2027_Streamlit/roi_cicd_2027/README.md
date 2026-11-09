# ROI incremental da Plataforma CI/CD | 2027

Aplicação Streamlit em português para estimar e acompanhar o retorno do portfólio de evoluções de 2027.

## Executar

Use Python 3.10 ou superior. Extraia o ZIP e abra o terminal na pasta que contém `app.py`.

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Abra http://localhost:8501. Para experimentar o fluxo, escolha **Carregar exemplo ilustrativo** na lateral. Os dados de exemplo são fictícios. Para começar com tabelas vazias, use **Iniciar uma simulação vazia**.

## Preenchimento

1. Cadastre as iniciativas, seus IDs, orçamento e mês de entrada em operação.
2. Informe volumes de 2026 e crescimento anual ou use volumes próprios mensais em benefícios.
3. Cadastre custos mensais em A (sem evolução) e B (com evolução).
4. Cadastre cada benefício uma vez, pela tabela ou pelo formulário guiado, indicando as iniciativas contribuintes, cronograma, efeito unitário, adoção, fonte e evidência.
5. Ajuste taxa de desconto e hipóteses dos cenários.
6. Registre custos e benefícios incrementais efetivos por mês e ID. Marque como validado quando houver evidência. Cadastre indicadores operacionais.
7. Selecione horizonte, visão e cenário no painel e baixe o Excel.

## Regras de cálculo

- O ROI divide o resultado líquido pelos custos adicionais brutos. Reduções de desembolso entram como benefício. Com custo zero, o ROI fica indisponível.
- O VPL usa fluxos mensais ao fim de cada mês e uma taxa anual efetiva. O payback informa o mês de recuperação que se sustenta até o fim do horizonte.
- A visão financeira inclui desembolso, economia efetiva e custo evitado fundamentado. A visão econômica ampliada incorpora esforço interno, capacidade liberada monetizada e perdas esperadas.
- Os volumes anuais crescem de forma composta com distribuição mensal uniforme. Para modelar sazonalidade, utilize linhas com volume próprio por período.
- O cenário otimista admite benefícios com evidência estimada. Benefícios qualitativos ficam no cadastro.
- A comparação realizada usa registros validados até o corte e evidencia apuração parcial quando faltam lançamentos previstos.
- Use um ID único por lançamento de custo ou benefício e uma linha por mês e ID na realização. Evite repetir o mesmo efeito entre custos e benefícios.

As entradas ficam na sessão do navegador. Exporte antes de encerrar. O Excel é um relatório dos parâmetros e resultados da sessão, com valores calculados pela aplicação.

## Exemplo de transição para sete squads

O botão **Carregar exemplo ilustrativo** preenche a transição das quatro equipes de 2026 para as sete squads de 2027, a carteira INV01–INV08 e os lançamentos mensais. A coluna **Responsável** indica a squad líder e **Squads de apoio** descreve a contribuição de cada uma. Os lançamentos de custo e benefício preservam os IDs das iniciativas, com detalhamento por ano no painel e no Excel.

Na visão **Econômica ampliada**, cenário **Base**, horizonte **2027–2029**, o exemplo soma R$ 3 milhões de custos, R$ 4,8 milhões de benefícios e R$ 1,8 milhão de resultado líquido, com ROI de 60%. A distribuição entre desembolso (75%) e esforço interno (25%) é uma premissa didática. A apuração realizada começa vazia. O VPL e o payback seguem os fluxos mensais do app.

Na **Linha de base**, registre quantidades de 2026 e a previsão de crescimento. O cenário A atende à demanda projetada com a operação de 2026. O cenário B atende à mesma demanda com as evoluções. Na Fase 4, use o ID do indicador para aproveitar essa projeção ou informe o volume mensal elegível do benefício.

A economia de runners (**INV06**) usa o indicador **L01**. No exemplo de 2027, 1,2 milhão de execuções de 2026 com crescimento de 10% resulta em 110 mil execuções mensais. Uma economia de R$ 0,20 por execução de março a dezembro resulta em R$ 220 mil.
