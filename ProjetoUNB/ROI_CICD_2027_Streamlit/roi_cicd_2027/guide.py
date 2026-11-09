"""Cartilha didática do simulador de ROI."""

import streamlit as st


def render_guide():
    st.header("Cartilha do ROI da Plataforma CI/CD")
    st.markdown("""
**A pergunta do app** é quanto a evolução da plataforma acrescenta de custo e benefício entre 2027 e 2029.
O **cenário A** atende à demanda futura com a operação de referência. O **cenário B** atende a mesma demanda com as evoluções.

Para acompanhar os exemplos nas telas, clique em **Carregar exemplo ilustrativo** na barra lateral.
Os valores desta cartilha são simulados.
    """)
    st.markdown("**Siga o exemplo de runners pelas fases**")
    st.markdown("""
**INV06** identifica a iniciativa → **L01** fornece o volume de execuções → **C-INV06-2027-D** e
**C-INV06-2027-E** registram custos da iniciativa → **B-INV06-2027** estima a economia →
a **Fase 6** valida o realizado → a **Fase 7** reúne os resultados.
    """)

    with st.expander("1 · Portfólio — O que será entregue?", expanded=True):
        st.markdown("""
- **ID, iniciativa, domínio e entregável:** identifique a evolução, o tema de trabalho e a entrega concreta. Use o mesmo ID nas fases de custos e benefícios.
- **Responsável e squads de apoio:** indique quem lidera e quem contribui. Registre o esforço incremental de ambas as partes na Fase 3.
- **Entrada em operação:** mês em que a melhoria fica disponível. O custo de implantação pode começar antes. O benefício pode começar a partir desse mês.
- **Aprovado:** orçamento de 2027 exibido no painel. Para calcular ROI, o app usa os custos incrementais da Fase 3.

**Exemplo.** A **INV06** otimiza runners. A Fundação de Integração Contínua lidera. A melhoria entra em operação em **março de 2027**.
        """)

    with st.expander("2 · Linha de base — Quanto trabalho vai acontecer?"):
        st.markdown("""
- **ID, indicador e unidade:** identifique o que está sendo contado, como execuções por ano, deploys por ano ou licenças-mês por ano.
- **Volume 2026 e crescimento anual:** informe o histórico e a hipótese de crescimento. A taxa é aplicada ao volume do ano anterior.
- **Fonte e responsável:** registre de onde veio o número e qual squad o valida.
- **Benefícios vinculados:** a tabela de projeção mostra quais linhas da Fase 4 selecionaram o indicador. Indicadores sem vínculo ficam disponíveis para seleção.

**Exemplo.** O indicador **L01** parte de **1.200.000 execuções** e cresce **10% ao ano**.
Em 2027, são **1.320.000 execuções**, ou **110.000 por mês** na projeção uniforme do app.
        """)
        st.code("""Volume do ano = Volume 2026 × (1 + crescimento anual)^(ano − 2026)
Volume mensal = Volume do ano ÷ 12""", language=None)

    with st.expander("3 · Custos — Quanto a evolução acrescenta de custo?"):
        st.markdown("""
- **ID do lançamento e iniciativa:** use um ID único para cada linha de custo e vincule o ID da iniciativa.
- **Descrição, categoria, fonte, início e fim:** identifique a conta, o documento de referência e os meses de vigência. Início e fim entram na contagem.
- **A e B em reais por mês:** informe o custo da mesma conta sem e com a evolução.
- **Natureza:** desembolso inclui pagamentos adicionais, como contratos. Esforço interno pode ser estimado por horas adicionais × custo-hora e entra na visão econômica ampliada.

**Exemplo.** Se a conta de implantação tem **zero** no cenário A e **25 mil reais** no cenário B, o custo incremental é **25 mil reais naquele mês**.
Uma redução de desembolso registrada nesta fase entra como economia. Registre a mesma economia apenas uma vez, na Fase 3 ou na Fase 4.
        """)
        st.code("""Diferença mensal de custo = B mensal − A mensal
Diferença positiva → custo adicional
Diferença negativa em desembolso → economia efetiva""", language=None)

    with st.expander("4 · Benefícios — Quanto se ganha por ocorrência?"):
        st.markdown("""
- **ID, iniciativas, descrição, tipo e classe:** identifique o ganho e sua origem. A classe determina em quais visões ele entra.
- **Início e fim:** delimite os meses em que o ganho é esperado. A linha **B-INV06-2027** vai de março a dezembro, totalizando **10 meses**.
- **Linha de base ou volume próprio:** selecione um indicador da Fase 2 ou informe o volume elegível mensal. O vínculo usa a projeção anual dividida por 12.
- **A e B por unidade:** informe a medida sem e com a evolução, na mesma unidade. Pode ser tempo, custo ou frequência por ocorrência.
- **Valor unitário:** converte a diferença em reais. Para A e B em horas, use reais por hora. Se a diferença já está em reais, informe **1**.
- **Adoção inicial, adoção alvo e rampa:** representam quanto do volume usa a melhoria. A adoção evolui linearmente do valor inicial ao alvo ao longo da rampa. Com rampa de zero ou um mês, o alvo vale desde o início.
- **Atribuição e monetização:** indicam a parcela do efeito atribuída à iniciativa e a parcela que pode ser expressa em dinheiro. Informe **80** para 80% nos campos percentuais. Se A e B representam taxas por ocorrência, escreva **0,05** para 5%.
- **Evidência, fonte e responsável:** documente a origem das premissas e quem as valida. Níveis A e B entram nas projeções elegíveis. Nível C entra apenas no otimista. Nível D fica como qualitativo.
        """)
        st.code("""Ganho bruto = volume mensal × (A por unidade − B por unidade) × valor unitário
Benefício projetado = ganho bruto × adoção × atribuição × monetização""", language=None)
        st.markdown("""
**Exemplo em horas.** **L03** fornece **330 novos pipelines por mês** em 2027. Com cerca de **0,303 hora** poupada por pipeline e **100 reais por hora**, a **INV01** projeta aproximadamente **10 mil reais por mês em capacidade liberada**, com os ajustes em 100%.

**Exemplo com custo mensal fixo.** Na **INV06**, o custo sem otimização é **50 mil reais por mês** para 110 mil execuções.
Para infraestrutura, o campo **B mensal** aceita diretamente o custo com a evolução. Com esse campo preenchido, o app usa
**volume × A por unidade − B mensal**, com o valor unitário igual a **1**.
        """)
        monthly_b = st.number_input("Custo mensal simulado com a otimização (em reais)", min_value=0.0,
                                    value=28000.0, step=1000.0, key="guia_custo_runners")
        monthly_gain = 50000 - monthly_b
        annual_gain = monthly_gain * 10
        brl = f"{annual_gain:,.2f}".translate(str.maketrans(",.", ".,"))
        st.metric("Economia bruta de março a dezembro (10 meses)", f"R$ {brl}")
        st.caption("Este exercício usa as premissas de 2027 da cartilha e não modifica os dados do portfólio.")

    with st.expander("5 · Cenários — O que muda se as premissas variarem?"):
        st.markdown("""
- **Realização dos benefícios:** multiplica ganhos positivos. Um ganho bruto de 22 mil reais passa para 15.400 reais com realização de 70%, mantendo os outros ajustes em 100%.
- **Variação do custo bruto:** aplica um acréscimo ou uma redução ao custo incremental. Um custo de 25 mil reais com acréscimo de 15% passa a 28.750 reais.
- **Atraso dos benefícios:** posterga o início e a rampa dos ganhos da Fase 4 e mantém o mês final. Assim, um benefício de março a dezembro, atrasado dois meses, passa a contar de maio a dezembro. O calendário de custos permanece fixo.
- **Cenário Base:** realização de 100%, variação de custo de 0% e atraso de zero meses. Conservador e Otimista são ajustáveis.
        """)
        st.code("""Ganho positivo no cenário = benefício projetado × realização
Custo no cenário = custo incremental × (1 + variação do custo)""", language=None)

    with st.expander("6 · Realização — O que foi medido e validado?"):
        st.markdown("""
- **Mês, ID de origem e valor:** registre o custo incremental ou o benefício apurado e vincule o ID da Fase 3 ou da Fase 4.
- **Validação, evidência e corte:** marque Validado após a conferência. O painel soma somente os registros validados até o mês de corte da barra lateral.
- **Indicadores operacionais:** registre mês, nome, unidade, previsto, realizado e fonte. Execuções e custo de runners por execução ajudam a explicar o resultado. A tabela operacional é exibida separadamente do cálculo financeiro.

**Exemplo.** Em março, a referência de **50 mil reais** menos a fatura simulada de **30 mil reais** gera **20 mil reais validados**.
Em abril, os **23.500 reais** ficam pendentes. Se forem validados e o corte incluir abril, o benefício acumulado passa para **43.500 reais**.
Apuração parcial significa que há lançamentos previstos sem registro validado no período.
        """)

    with st.expander("7 · Painel Executivo — Como ler o retorno?"):
        st.markdown("""
- **Horizonte:** escolha 2027 ou 2027–2029. **Cenário:** escolha quais hipóteses projetadas aplicar. A comparação com o realizado usa o mês de corte.
- **Visão Financeira:** inclui desembolsos, economias efetivas e custos evitados elegíveis. **Econômica ampliada:** incorpora também esforço interno, capacidade liberada monetizada e perdas esperadas.
- **Taxa de desconto:** informe na barra lateral a taxa anual usada para trazer cada fluxo mensal ao início de 2027. Com 0%, o VPL equivale à soma do resultado líquido sem desconto.
- **Payback simples:** é o primeiro mês em que o saldo acumulado fica não negativo e permanece assim até o fim do horizonte. Quando fica fora do horizonte, o investimento ainda não foi recuperado de forma sustentada no período exibido.
        """)
        st.code("""Resultado líquido = benefícios incrementais − custos incrementais
ROI simples (%) = resultado líquido ÷ custos incrementais × 100
VPL = soma de [fluxo do mês ÷ (1 + taxa anual)^(mês/12)]
ROI descontado (%) = VPL ÷ valor presente dos custos incrementais × 100""", language=None)
        st.markdown("""
O ROI fica indisponível quando o custo do denominador é zero. **VPL** significa **Valor Presente Líquido**. Um VPL positivo indica
que os benefícios superam os custos em valor presente, à taxa selecionada.

**Exemplo.** No cenário Base, visão Econômica ampliada, 2027–2029, os **4,8 milhões de reais** em benefícios menos
**3 milhões de reais** em custos geram **1,8 milhão de reais** de resultado líquido. Dividindo por 3 milhões,
o **ROI simples é 60%**. Com desconto anual de 10%, o **VPL fica em cerca de 1,32 milhão de reais**.
        """)
