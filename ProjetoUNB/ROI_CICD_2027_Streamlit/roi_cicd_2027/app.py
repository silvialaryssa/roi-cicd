"""Aplicação Streamlit para o portfólio de evoluções CI/CD de 2027."""
import pandas as pd
import plotly.express as px
import streamlit as st

from example import TRANSITION, TRANSITION_COLUMNS
from guide import render_guide
from model import CLASSES, DEFAULTS, MONTHS, NUMBERS, TYPES, VIEWS, calculate, export_excel, frames, summary, validate

st.set_page_config(page_title="ROI CI/CD 2027", page_icon="📊", layout="wide")
st.markdown("""
<style>
.block-container {max-width: 1440px; padding-top: 2rem;}
.hero {background:linear-gradient(115deg,#221c35,#193f9c 75%,#1653fd); color:white;
       padding:1.6rem 2rem; border-radius:1.1rem; margin-bottom:1rem;}
.hero strong {letter-spacing:.14em; font-size:.78rem; color:#dbeaff;}
.hero h1 {margin:.2rem 0; padding:0; color:white;}
.hero p {margin:.35rem 0 0; color:#e2edff;}
[data-testid="stMetric"] {background:#fff; border:1px solid #e0e7f4;
                         border-radius:.9rem; padding:.85rem 1rem;}
[data-testid="stMetricValue"] {font-size:clamp(1rem,2vw,1.8rem);}
</style>
<div class="hero"><strong>CUSTO PLATAFORMA · PLANEJAMENTO 2027</strong>
<h1>ROI incremental de CI/CD</h1>
<p>Da linha de base ao painel executivo do portfólio.</p></div>
""", unsafe_allow_html=True)

SCENARIOS = ("Conservador", "Base", "Otimista")
EVIDENCE = ("A — Comprovado", "B — Fundamentado", "C — Estimado", "D — Qualitativo")
SELECT = {
    "Entrada em operação": MONTHS[:12], "Início": MONTHS, "Fim": MONTHS, "Mês": MONTHS,
    "Tipo": list(TYPES), "Classe": CLASSES, "Evidência": EVIDENCE,
    "Natureza": ["Desembolso", "Esforço interno"],
    "Validação": ["Pendente", "Validado"],
}
HELP = {
    "Responsável": "Squad líder, responsável pela entrega e pela apuração do resultado.",
    "Squads de apoio": "Squads contribuintes e respectivas responsabilidades. Campo opcional.",
    "Entrada em operação": "Primeiro mês em que a capacidade está disponível.",
    "Aprovado R$": "Orçamento aprovado para a iniciativa em 2027. Informativo no painel.",
    "Volume 2026": "Volume anual observado em 2026, na unidade indicada.",
    "Crescimento % a.a.": "Crescimento composto anual. Use valores negativos para retração.",
    "A R$/mês": "Custo no cenário sem as evoluções.",
    "B R$/mês": "Custo com as evoluções, na mesma conta e no mesmo período de A.",
    "Iniciativas": "IDs separados por vírgulas. Cadastre uma única linha por benefício compartilhado.",
    "Linha de base": "ID do indicador de volume. Em branco, use o volume próprio por mês.",
    "Volume próprio/mês": "Use 1 quando A e B já forem quantidades totais mensais.",
    "A por unidade": "Quanto se gasta, consome ou demora para uma ocorrência no cenário sem a evolução. Ex.: 0,50 hora por pipeline. Para taxa de 5%, digite 0,05.",
    "B por unidade": "A mesma medida do campo A, para a mesma ocorrência, com a evolução. Ex.: 0,25 hora por pipeline.",
    "B mensal R$": "Custo mensal fixo com a evolução. Preencha para infraestrutura com A em reais por execução e R$/unidade igual a 1. Tem prioridade sobre B por unidade.",
    "R$/unidade": "Preço de uma unidade do efeito medido em A e B. Se A e B estão em horas, informe R$/hora. Se já estão em reais por ocorrência, informe 1.",
    "Meses de rampa": "Número de meses, incluindo o inicial, para atingir a adoção alvo. Zero ou 1 aplica o alvo imediatamente.",
    "Atribuição %": "Parcela do efeito atribuível ao portfólio, considerando outras mudanças.",
    "Monetização %": "Parcela atribuída com conversão em valor demonstrável.",
    "ID de origem": "ID do custo ou benefício previsto. Use uma linha por mês e ID.",
    "Valor R$": "Valor incremental bruto validado. Benefício negativo representa perda ou reversão.",
}


def reset(example):
    st.session_state["initial"] = frames(example)
    st.session_state["example"] = example
    st.session_state["revision"] = st.session_state.get("revision", 0) + 1


if "initial" not in st.session_state:
    reset(False)

with st.sidebar:
    st.title("Configuração")
    st.caption("Comece pelo portfólio ou explore o cenário didático.")
    if st.button("Carregar exemplo ilustrativo", width="stretch"):
        reset(True)
    with st.expander("Iniciar uma simulação vazia"):
        if st.button("Limpar tabelas desta sessão", width="stretch"):
            reset(False)
    st.divider()
    rate = st.number_input("Taxa de desconto anual (%)", 0.0, 1000.0, 10.0, step=0.5,
                           help="Substitua a taxa ilustrativa pela taxa aprovada. O VPL desconta fluxos no fim de cada mês, com base em janeiro de 2027.")
    cutoff = st.selectbox("Último mês da apuração realizada", MONTHS, index=11)
    st.caption("Os dados digitados ficam nesta sessão. Baixe o Excel para guardar os parâmetros e resultados.")

if st.session_state["example"]:
    st.info("Modo demonstração · Quatro equipes em 2026, sete squads a partir de 2027 e oito iniciativas. Os valores são fictícios e editáveis.")


def cards(*items):
    for column, (title, body) in zip(st.columns(len(items)), items):
        with column:
            with st.container(border=True):
                st.markdown(f"**{title}**")
                st.caption(body)


def editor(name, *, baseline_options=None):
    source = st.session_state["initial"][name]
    columns = {}
    for column in source:
        kwargs = {"help": HELP.get(column), "default": DEFAULTS.get(column)}
        if name == "Linha de base" and column == "Responsável":
            columns[column] = st.column_config.TextColumn(help="Squad que mantém a definição, a fonte e a qualidade do indicador.")
        elif column == "Linha de base" and baseline_options is not None:
            columns[column] = st.column_config.SelectboxColumn(options=baseline_options, **kwargs)
        elif column in SELECT:
            columns[column] = st.column_config.SelectboxColumn(options=list(SELECT[column]), **kwargs)
        elif column in NUMBERS:
            columns[column] = st.column_config.NumberColumn(step=1 if column == "Meses de rampa" else None, **kwargs)
        else:
            columns[column] = st.column_config.TextColumn(**kwargs)
    revision = st.session_state.get(f"rev:{name}", 0)
    result = st.data_editor(source, key=f"{name}:{st.session_state['revision']}:{revision}", num_rows="dynamic",
                            hide_index=True, width="stretch", column_config=columns)
    return result.reset_index(drop=True)


def money(value):
    result = f"{abs(value):,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"{'−' if value < 0 else ''}R$ {result}"


def percent(value):
    return "—" if value is None or pd.isna(value) else f"{value:.1%}".replace(".", ",")


def chart(frame, x, y, label, *, color=None, kind="line"):
    if frame.empty:
        st.caption("Adicione dados para gerar este gráfico.")
        return
    draw = px.line if kind == "line" else px.bar
    options = {"markers": True} if kind == "line" else {"barmode": "group"}
    figure = draw(frame, x=x, y=y, color=color, color_discrete_sequence=["#1653FD", "#7D54C8", "#008777", "#D36A2C"], **options)
    figure.update_layout(margin=dict(l=8, r=8, t=8, b=10), height=315, legend_title_text="",
                         xaxis_title=None, yaxis_title=label, separators=",.", hovermode="x unified")
    st.plotly_chart(figure, width="stretch")


tabs = st.tabs(["1 · Portfólio", "2 · Linha de base", "3 · Custos", "4 · Benefícios", "5 · Cenários",
                "6 · Realização", "7 · Painel executivo", "Cartilha"])
with tabs[7]:
    render_guide()

data = {}
with tabs[0]:
    st.subheader("Delimite as evoluções de 2027")
    cards(("Iniciativa e domínio", "Dê um ID único a cada evolução. Agrupe por domínio, como DevSecOps, jornada do desenvolvedor ou eficiência operacional."),
          ("Entrada em operação", "Informe o primeiro mês em que a capacidade pode gerar resultado. Custos de implantação podem começar antes."),
          ("Orçamento aprovado", "Registre o valor de 2027 por iniciativa. O ROI usa os custos incrementais da etapa 3."))
    data["Portfólio"] = editor("Portfólio")
    if st.session_state["example"]:
        st.caption("Responsável indica a squad líder. O exemplo deixa o orçamento aprovado em zero e usa os custos projetados nas contas de ROI.")

with tabs[1]:
    st.subheader("2 · Linha de base: conte a demanda que será atendida")
    st.markdown("""
A linha de base registra **quanto trabalho foi feito em 2026**. O app usa esse histórico e a taxa de crescimento
para projetar a demanda anual de 2027 a 2029. Em cada comparação, os dois cenários atendem à mesma demanda.

- **Cenário A · Sem as iniciativas:** a plataforma atende à demanda projetada usando o modo de operação de 2026.
- **Cenário B · Com as iniciativas:** a plataforma atende à mesma demanda usando os recursos e processos novos.

A demanda diz **quantas vezes** o trabalho acontece. O custo ou o esforço **por unidade**, nos cenários A e B,
é informado na Fase 4. Na Fase 3, preencha os custos mensais de cada cenário diretamente.
    """)
    st.markdown("**Como preencher a tabela**")
    st.markdown("""
1. **Escolha o que contar.** Use a unidade do benefício que deseja medir, como execução de pipeline, deploy ou provisionamento.
2. **Extraia o total de 2026.** Defina quais ambientes, aplicações e eventos entram na contagem. Registre a fonte e o filtro usado.
   Em **Responsável**, indique a squad que mantém a definição e valida o volume do indicador.
3. **Informe a projeção.** Use a taxa anual prevista para a população medida. Com 0%, o volume anual fica constante.
4. **Vincule na Fase 4.** No campo **Linha de base** do benefício, informe o ID do indicador. Para uma população mais restrita
   ou para meses com volumes diferentes, deixe esse campo em branco e informe o **Volume próprio/mês** para o período correspondente.
    """)
    with st.expander("Onde buscar os indicadores de 2026 e para que servem", expanded=True):
        st.table(pd.DataFrame([
            ("L01 · Execuções de pipelines", "Histórico da ferramenta de CI, como GitHub Actions, Jenkins ou GitLab CI. Conte IDs de execução únicos com o filtro de escopo definido.",
             "Economia de runners (INV06), quando o custo é medido por execução."),
            ("L02 · Deploys em produção", "Histórico do orquestrador de implantação ou ITSM reconciliado com os eventos de implantação. Filtre produção e deduplique pelo ID do deploy.",
             "Benefício calculado por deploy, como redução de esforço de verificação pós-implantação (INV04)."),
            ("L03 · Pipelines provisionados", "Logs de provisionamento do catálogo/IDP ou inventário com data de criação. Conte novas esteiras no período.",
             "Benefício de provisionamento medido por nova esteira criada (INV01)."),
            ("L04 · Análises de dependências", "Histórico do Xray. Conte IDs únicos de análises concluídas no escopo.",
             "Esforço de revisão por análise de dependências (INV03)."),
            ("L05 · Solicitações de acesso a ferramentas de IA", "Catálogo de acessos ou chamados. Conte solicitações únicas de acesso a ferramentas de IA.",
             "Tempo poupado por solicitação com autosserviço (INV05)."),
            ("L06 · Solicitações de mudança avaliadas", "ITSM e Motor de Liberação. Conte IDs únicos de mudanças avaliadas.",
             "Tempo poupado por avaliação de mudança (INV07)."),
            ("L07 · Registros de ativos revisados no inventário", "Histórico do Inventário de Software. Conte eventos únicos de revisão cadastral.",
             "Tempo poupado por revisão ou conciliação cadastral (INV08)."),
            ("L08 · Licenças de IA elegíveis à revisão", "Some o total de licenças elegíveis em cada mês. Uma licença elegível durante 12 meses soma 12 licenças-mês.",
             "Redução da parcela de licenças ociosas que continuam faturadas (INV05)."),
        ], columns=["Indicador", "Fonte sugerida e como contar", "Quando usar no cálculo"]))
    transition = pd.DataFrame(TRANSITION, columns=TRANSITION_COLUMNS)
    if st.session_state["example"]:
        with st.expander("Quatro equipes em 2026 e sete squads a partir de 2027"):
            st.dataframe(transition, hide_index=True, width="stretch")
        st.info("Exemplo INV06 · L01: 1.200.000 execuções em 2026 × 1,10 = 1.320.000 em 2027. "
                "O app distribui 110.000 execuções por mês. Com economia de R$ 0,20 por execução "
                "de março a dezembro, o benefício é 110.000 × R$ 0,20 × 10 = R$ 220.000. "
                "O custo A por execução e o custo mensal de B estão na linha B-INV06-2027 da Fase 4.")
    data["Linha de base"] = editor("Linha de base")
    baseline = data["Linha de base"].copy()
    for year in (2027, 2028, 2029):
        baseline[str(year)] = baseline["Volume 2026"] * (1 + baseline["Crescimento % a.a."] / 100) ** (year - 2026)
    st.markdown("**Projeção anual e vínculo com a Fase 4**")
    st.markdown("""
- **ID, indicador, unidade e responsável** identificam o que foi contado e qual squad mantém o indicador.
- **2027, 2028 e 2029** mostram quantidades anuais projetadas. A cada ano, o app aplica a taxa de crescimento ao volume do ano anterior.
  No exemplo, **L01** passa de 1,2 milhão em 2026 para 1,32 milhão em 2027, 1,452 milhão em 2028 e 1,5972 milhão em 2029.
- **Benefícios vinculados** mostra os IDs das linhas que selecionaram aquele indicador na Fase 4. Ao calcular um desses benefícios,
  o app usa o volume projetado do ano dividido por 12 e aplica esse volume apenas nos meses entre **Início** e **Fim** do benefício.
  Por exemplo, **B-INV06-2027** usa o volume de **L01** de março a dezembro.
- **Sem vínculo** significa que o indicador está disponível para seleção. Ele só alimenta o cálculo quando for selecionado
  em uma linha de benefício. Linhas que usam **Volume próprio/mês** podem ser calculadas sem esse vínculo.
    """)
    baseline_preview = st.empty()


with tabs[2]:
    st.subheader("Compare custos mensais com e sem evolução")
    cards(("Cenário A e cenário B", "Informe o custo da mesma conta nos dois cenários. B maior que A gera custo adicional bruto. B menor que A, em desembolso, gera economia."),
          ("Natureza do custo", "Desembolso entra nas duas visões. Esforço interno realocado entra na econômica ampliada pelo custo de oportunidade validado."),
          ("Período e evidência", "Inclua implantação, sustentação, transição e encerramento. Para gasto único, repita o mesmo mês no início e no fim."))
    st.caption("Se a redução de uma despesa já foi apurada em A e B nesta etapa, mantenha o lançamento apenas aqui.")
    if st.session_state["example"]:
        st.caption("Premissa didática: 75% do custo incremental é desembolso e 25% é esforço interno. Os custos de liderança e apoio já estão consolidados por iniciativa.")
    data["Custos"] = editor("Custos")

with tabs[3]:
    st.subheader("Modele os benefícios e a qualidade da evidência")
    cards(("Magnitude e tarifa", "Diferença entre A e B × volume elegível × valor unitário. Use horas de trabalho ativo para esforço e preço marginal faturável para infraestrutura."),
          ("Adoção e atribuição", "A rampa acompanha o uso da capacidade. A atribuição isola o efeito do portfólio. A monetização representa a parcela com valor demonstrável."),
          ("Classe e evidência", "Na visão financeira entram economias efetivas e custos evitados fundamentados. Capacidade monetizada e perda esperada ficam na visão econômica ampliada."))
    with st.expander("O que preencher em A por unidade, B por unidade e R$/unidade", expanded=True):
        st.markdown("""
Primeiro, identifique o que você está contando no volume, como execuções ou pipelines provisionados.
Depois, escolha o que vai medir **por ocorrência**, como custo em reais, horas de trabalho ou taxa de falhas.

- **A por unidade** é o valor por ocorrência **sem a evolução**. Use uma medição do processo atual ou uma estimativa fundamentada.
- **B por unidade** é o valor por ocorrência **com a evolução**, na mesma unidade de A. Use um piloto, uma medição após implantação ou uma estimativa.
- O campo `R$/unidade` informa **quanto vale uma unidade da diferença entre A e B**. Se a diferença é em horas, use o valor em reais por hora.
  Se A e B já são custos em reais por ocorrência, preencha **1**. A diferença já está em reais.

**Benefício bruto mensal = volume mensal × (A − B) × valor unitário.** O app aplica depois os ajustes de adoção, atribuição e monetização.
        """)
        st.dataframe(pd.DataFrame([
            ("Runners · INV06", "110.000 execuções", "R$ 0,4545/execução", "R$ 0,2545/execução", "1", "R$ 22.000"),
            ("Provisionamento de pipelines", "100 pipelines", "0,50 h/pipeline (30 min)", "0,25 h/pipeline (15 min)", "R$ 120/h", "R$ 3.000"),
            ("Tratamento de falhas", "1.000 execuções", "0,05 (5%)", "0,03 (3%)", "R$ 500/falha", "R$ 10.000"),
        ], columns=["Exemplo", "Volume mensal", "A por unidade", "B por unidade", "R$/unidade", "Benefício bruto mensal"]), hide_index=True, width="stretch")
    with st.expander("Como preencher cada tipo de benefício"):
        for name, explanation in TYPES.items():
            st.markdown(f"**{name}**")
            st.text(explanation)
    with st.expander("Como classificar evidência e evitar dupla contagem"):
        st.markdown("""
- **A — Comprovado** e **B — Fundamentado** entram na projeção quando a classe for elegível.
- **C — Estimado** entra somente no cenário otimista. **D — Qualitativo** fica no cadastro para acompanhamento.
- Em benefícios compartilhados, vincule todos os IDs na mesma linha. Registre um custo evitado quando a despesa de referência estiver documentada.
- Capacidade liberada deve ter plano de realocação para ser monetizada. Risco esperado representa perda probabilística.
        """)
    st.markdown("**Escolha de onde vem o volume do benefício**")
    baseline_choices = {
        row["ID"]: f'{row["ID"]} · {row["Indicador"]} ({row["Unidade"]})'
        for row in data["Linha de base"].to_dict("records")
        if pd.notna(row["ID"]) and str(row["ID"]).strip()
    }
    baseline_ids = list(baseline_choices)
    if baseline_ids:
        st.caption("Na coluna **Linha de base**, selecione um dos IDs cadastrados na Fase 2. "
                   "No formulário guiado, a lista também mostra o nome e a unidade do indicador.")
        with st.expander("Consultar indicadores disponíveis"):
            st.dataframe(data["Linha de base"][["ID", "Indicador", "Unidade"]],
                         hide_index=True, width="stretch")
    else:
        st.info("Cadastre um indicador na Fase 2 para habilitar o vínculo ou use um volume mensal próprio.")
    st.caption("Para usar um volume próprio, limpe a seleção em **Linha de base** e preencha **Volume próprio/mês**. "
               "Quando um indicador é selecionado, o app usa a projeção dele e ignora o volume próprio.")
    if st.session_state["example"]:
        with st.expander("Exemplo guiado: do indicador ao benefício", expanded=True):
            st.markdown("""
**INV01 · Provisionamento de pipelines.** Na Fase 2, **L03** projeta 3.960 novos pipelines em 2027.
Na Fase 4, a linha **B-INV01-2027** seleciona L03, então o app usa **330 pipelines por mês**.
No exemplo, cada pipeline economiza cerca de **0,303 hora** (diferença entre A e B), valorada a **100 reais por hora**.
Com os valores completos e os ajustes do exemplo em 100%, isso resulta em **10 mil reais de capacidade liberada por mês**.

**Escolha a unidade que combina com o benefício.** Se o ganho é por deploy, use o indicador de deploys.
Se é por mudança avaliada, use o de mudanças. Duas iniciativas podem usar o mesmo volume quando medem efeitos distintos,
como horas de correção de defeitos e custo de runners por execução.
            """)
            st.caption("Os efeitos unitários do exemplo foram calibrados para preservar os benefícios ilustrativos. Use dados medidos ou estimativas fundamentadas em uma avaliação real.")
    st.markdown("**Simular o custo mensal com a otimização**")
    st.markdown("Para infraestrutura, você pode informar `B mensal R$` diretamente. Use **A por unidade** em reais por execução "
                "e `R$/unidade` igual a **1**. Quando o custo mensal está preenchido, o cálculo é o custo de A para o volume do mês "
                "menos o custo mensal de B. O campo **B por unidade** pode ficar vazio.")
    if st.session_state["example"]:
        st.text("Para simular runners, edite B mensal R$ nas linhas B-INV06-2027, B-INV06-2028 e B-INV06-2029. O exemplo começa com R$ 28.000 em cada ano.")
    data["Benefícios"] = editor("Benefícios", baseline_options=["", *baseline_ids])
    with st.expander("Conferir os vínculos cadastrados"):
        links_preview = data["Benefícios"][["ID", "Iniciativas", "Descrição", "Linha de base"]].copy()
        links_preview["Indicador usado"] = links_preview["Linha de base"].map(baseline_choices)
        uses_own_volume = links_preview["Linha de base"].fillna("").eq("")
        links_preview.loc[uses_own_volume, "Indicador usado"] = "Volume próprio"
        links_preview["Indicador usado"] = links_preview["Indicador usado"].fillna("ID não encontrado na Fase 2")
        st.dataframe(links_preview, hide_index=True, width="stretch")
    initiative_ids = data["Portfólio"]["ID"].dropna().unique().tolist()
    with st.expander("Adicionar benefício pelo formulário guiado"):
        if not initiative_ids:
            st.caption("Cadastre primeiro uma iniciativa na etapa 1.")
        else:
            with st.form("novo_beneficio", clear_on_submit=False):
                st.markdown("**Identificação e cronograma**")
                left, right = st.columns(2)
                item = left.text_input("ID do benefício", placeholder="B01")
                description = right.text_input("Descrição do resultado")
                links = st.multiselect("Iniciativas contribuintes", initiative_ids)
                c1, c2, c3 = st.columns(3)
                kind = c1.selectbox("Tipo", list(TYPES))
                category = c2.selectbox("Classe", CLASSES)
                evidence = c3.selectbox("Nível de evidência", EVIDENCE, index=1)
                left, right = st.columns(2)
                start = left.selectbox("Primeiro mês de realização", MONTHS)
                finish = right.selectbox("Último mês de realização", MONTHS, index=35)

                st.markdown("**Volume, efeito por unidade e valor**")
                left, right = st.columns(2)
                baseline_id = left.selectbox("Vincular volume da linha de base", [""] + baseline_ids,
                                             format_func=lambda value: baseline_choices.get(value, "Usar volume mensal próprio"))
                volume = right.number_input("Volume mensal próprio", min_value=0.0, value=1.0, help=HELP["Volume próprio/mês"])
                c1, c2, c3 = st.columns(3)
                unit_a = c1.number_input("A por unidade", min_value=0.0, format="%.4f", help=HELP["A por unidade"])
                unit_b = c2.number_input("B por unidade", min_value=0.0, format="%.4f", help=HELP["B por unidade"])
                unit_price = c3.number_input("R$/unidade", min_value=0.0, format="%.4f", help=HELP["R$/unidade"])

                monthly_b = st.number_input("B mensal R$ (opcional)", min_value=0.0, value=None,
                                            format="%.2f", help=HELP["B mensal R$"])

                st.markdown("**Adoção, atribuição e monetização**")
                c1, c2, c3 = st.columns(3)
                initial_adoption = c1.number_input("Adoção inicial (%)", 0, 100, 100)
                target_adoption = c2.number_input("Adoção alvo (%)", 0, 100, 100)
                ramp = c3.number_input("Meses até a adoção alvo", 0, 36, 0, help=HELP["Meses de rampa"])
                left, right = st.columns(2)
                attribution = left.number_input("Atribuição ao portfólio (%)", 0, 100, 100)
                monetization = right.number_input("Parcela monetizável (%)", 0, 100, 100)
                source = st.text_input("Fonte e justificativa da monetização")
                owner = st.text_input("Responsável pela validação")
                submitted = st.form_submit_button("Adicionar à tabela", type="primary")
            if submitted:
                if not all([item.strip(), description.strip(), links, source.strip(), owner.strip()]):
                    st.error("Preencha ID, descrição, iniciativas, fonte e responsável.")
                elif item.strip() in set(data["Benefícios"]["ID"]):
                    st.error("O ID já existe na tabela de benefícios.")
                else:
                    record = [
                        item.strip(), ", ".join(links), description.strip(), kind, category, evidence, start, finish,
                        baseline_id, volume, unit_a, unit_b, monthly_b, unit_price, initial_adoption, target_adoption, ramp,
                        attribution, monetization, source.strip(), owner.strip(),
                    ]
                    row = pd.DataFrame([record], columns=data["Benefícios"].columns)
                    st.session_state["initial"]["Benefícios"] = pd.concat([data["Benefícios"], row], ignore_index=True)
                    st.session_state["rev:Benefícios"] = st.session_state.get("rev:Benefícios", 0) + 1
                    st.session_state["beneficio_adicionado"] = item.strip()
                    st.rerun()
    if "beneficio_adicionado" in st.session_state:
        st.success(f"Benefício {st.session_state.pop('beneficio_adicionado')} adicionado à tabela.")

baseline_links = (data["Benefícios"].dropna(subset=["Linha de base"])
                  .groupby("Linha de base")["ID"].agg(lambda ids: ", ".join(ids.dropna().astype(str))))
baseline["Benefícios vinculados"] = baseline["ID"].map(baseline_links).fillna("").replace("", "Sem vínculo")
baseline_preview.dataframe(
    baseline[["ID", "Indicador", "Responsável", "Unidade", "2027", "2028", "2029", "Benefícios vinculados"]],
    hide_index=True, width="stretch",
)


with tabs[4]:
    st.subheader("Teste hipóteses de realização, sobrecusto e atraso")
    cards(("Realização dos benefícios", "Multiplica os ganhos positivos, incluindo economias identificadas nos custos. Perdas mantêm seu valor."),
          ("Custo bruto", "O percentual de variação é aplicado aos custos adicionais. O cronograma de desembolsos fica conforme cadastrado."),
          ("Atraso na geração de valor", "Desloca o início e a rampa dos ganhos operacionais, mantendo o fim cadastrado. Economias de contas de custo e perdas mantêm as datas."))
    settings = {"Taxa %": rate, "Corte": cutoff}
    scenario_rows = []
    for scenario, realization, markup, delay in [("Conservador", 70, 15, 2), ("Base", 100, 0, 0), ("Otimista", 115, -5, 0)]:
        with st.container(border=True):
            st.markdown(f"**{scenario}**")
            col1, col2, col3 = st.columns(3)
            fixed = scenario == "Base"
            r = col1.number_input("Realização dos benefícios (%)", 0, 300, realization, key=f"real{scenario}", disabled=fixed)
            c = col2.number_input("Variação do custo bruto (%)", -100, 300, markup, key=f"cost{scenario}", disabled=fixed)
            d = col3.number_input("Atraso dos benefícios (meses)", 0, 36, delay, key=f"delay{scenario}", disabled=fixed)
            settings[scenario] = (r / 100, 1 + c / 100, d)
            scenario_rows.append((scenario, r, c, d))

with tabs[5]:
    st.subheader("Acompanhe resultados mensais e valide as evidências")
    cards(("Lançamento realizado", "Use o ID cadastrado e o mês do registro. Informe custo bruto realizado ou benefício incremental realizado, em reais."),
          ("Validação", "O painel considera lançamentos validados até o mês de corte. Compare com o previsto até a mesma data."),
          ("Indicadores operacionais", "Registre adoção, lead time, frequência de deploy, falhas em mudanças ou outros indicadores com unidade e fonte."))
    st.markdown("**Custos e benefícios realizados**")
    if st.session_state["example"]:
        with st.expander("Simulação de realização · INV06", expanded=True):
            st.markdown("""
Os registros abaixo são **fictícios** e mostram uma apuração **parcial** de março e abril de 2027.
Cada linha usa o ID do lançamento de custo da **Fase 3** ou do benefício da **Fase 4**.

- **Março:** a referência sem otimização é de 50 mil reais. A fatura simulada com otimização é de 30 mil reais.
  A diferença de **20 mil reais** está marcada como **Validado**.
- **Abril:** o volume subiu para 115.500 execuções. Aplicando o mesmo custo de referência por execução de março,
  o cenário sem otimização teria custado 52.500 reais. A fatura simulada foi de 29 mil reais. A diferença de **23.500 reais**
  está **Pendente** até a conciliação.
- Os custos de implantação e o esforço interno aparecem em linhas próprias. Na visão econômica ampliada, o total
  validado dos dois meses é de **65 mil reais**. A economia com a fatura de runners entra uma vez, como benefício.
            """)
            st.caption("Para testar a validação, use corte em abril de 2027 ou posterior e mude o benefício de abril para Validado. O benefício validado passa de 20 mil para 43.500 reais.")
    data["Realização"] = editor("Realização")
    st.markdown("**Indicadores operacionais**")
    with st.expander("Como registrar e interpretar os indicadores operacionais", expanded=True):
        st.markdown("""
Indicadores operacionais mostram **o que aconteceu na operação** em cada mês. Eles ajudam a investigar por que um
resultado ficou acima ou abaixo do esperado e dão contexto à validação. O painel os exibe separadamente dos valores
em reais. O preenchimento desta tabela, por si só, **não altera o ROI**.

Preencha **Mês**, **Indicador**, **Unidade**, **Previsto** (meta ou projeção para aquele mês), **Realizado** (medição do mês)
e **Fonte** (sistema ou relatório com o recorte usado). Mantenha a mesma população e unidade na comparação.
Para percentuais, informe **5** para representar **5%**. Se a medição ainda não chegou, deixe **Realizado** em branco.
        """)
        st.table(pd.DataFrame([
            ("Execuções de pipelines no escopo", "Conte execuções únicas dos pipelines elegíveis no mês.", "Acima da previsão pode indicar maior demanda. Use o volume real para estimar o custo sem otimização."),
            ("Custo faturado de runners por execução", "Divida a fatura de runners pelas execuções elegíveis no mesmo período.", "Um custo por execução menor pode indicar eficiência. Confira o perfil das cargas e a conciliação da fatura."),
            ("Adoção de templates padronizados", "Divida os pipelines ativos que usam o template pelos pipelines ativos elegíveis e multiplique por 100.", "Adoção abaixo da meta reduz o alcance do ganho esperado."),
            ("Taxa de mudanças com falha", "Divida as mudanças em produção com falha pelas mudanças em produção no escopo e multiplique por 100.", "Uma taxa menor indica menos falhas nesse recorte. Confira o critério de falha e a quantidade de mudanças."),
        ], columns=["Indicador", "Como medir", "Como interpretar"]))
        st.caption("Na Fase 7, abra Indicadores operacionais e selecione uma série para comparar o previsto com o realizado.")
    data["Indicadores"] = editor("Indicadores")

with tabs[6]:
    st.subheader("Painel executivo")
    errors = validate(data)
    if errors:
        st.error("Corrija os campos indicados para atualizar o painel e liberar a exportação.")
        with st.expander(f"Pendências de preenchimento ({len(errors)})", expanded=True):
            for error in errors:
                st.write("•", error)
        st.stop()
    if data["Portfólio"].empty:
        st.info("Cadastre uma iniciativa na etapa 1 ou carregue o exemplo ilustrativo.")
        st.stop()
    if data["Custos"].empty or data["Benefícios"].empty:
        st.warning("A projeção usa os registros disponíveis. Revise se todos os custos e benefícios do portfólio foram cadastrados.")

    first, second, third = st.columns(3)
    example_mode = st.session_state["example"]
    selection_key = st.session_state["revision"]
    horizon = first.selectbox("Horizonte", ["2027", "2027–2029"], index=int(example_mode), key=f"horizonte:{selection_key}")
    view = second.selectbox("Visão do retorno", VIEWS, index=int(example_mode), key=f"visão:{selection_key}")
    scenario = third.selectbox("Cenário projetado", ["Base", "Conservador", "Otimista"])
    end = "2027-12" if horizon == "2027" else MONTHS[-1]
    last_actual = min(end, cutoff)
    approved = data["Portfólio"]["Aprovado R$"].sum()
    all_plans = {(v, s): calculate(data, settings, v, s) for v in VIEWS for s in SCENARIOS}
    all_actuals = {v: calculate(data, settings, v, actual=True) for v in VIEWS}
    plan, detail = all_plans[view, scenario]
    actual, actual_detail = all_actuals[view]
    plan = plan[plan["Mês"] <= end]
    detail = detail[detail["Mês"] <= end]
    actual = actual[actual["Mês"] <= last_actual]
    actual_detail = actual_detail[actual_detail["Mês"] <= last_actual]
    planned = summary(plan)
    realized = summary(actual)
    has_cost = actual_detail["Classe"].isin(["Desembolso", "Esforço interno"]).any()
    has_benefit = actual_detail["Classe"].isin(CLASSES).any()
    expected_pairs = set(detail.loc[
        (detail["Mês"] <= last_actual) & ((detail["Custo R$"] != 0) | (detail["Benefício R$"] != 0)),
        ["Mês", "ID"],
    ].itertuples(index=False, name=None))
    actual_pairs = set(actual_detail[["Mês", "ID"]].itertuples(index=False, name=None))
    missing = expected_pairs - actual_pairs
    if not actual_detail.empty and missing:
        st.warning(f"Apuração parcial até {last_actual}. Há {len(missing)} combinações de mês e lançamento previsto sem registro validado.")
    elif actual_detail.empty:
        st.caption(f"Apuração até {last_actual} · sem lançamentos validados nesta visão.")

    kpis = [
        ("Orçamento aprovado · 2027", money(approved),
         "Soma da coluna Aprovado da Fase 1 para todas as iniciativas. Mostra o orçamento registrado para 2027, "
         "inclusive quando o painel está no horizonte 2027–2029. O ROI usa os custos incrementais, apurados separadamente."),
        ("Custo incremental realizado", money(realized["Custo R$"]) if has_cost else "—",
         "Soma dos custos adicionais com evidência validada na Fase 6, até a data de corte e dentro da visão selecionada. "
         "Na visão financeira entram os desembolsos. A visão econômica ampliada inclui também o esforço interno. "
         "O traço indica ausência de registro validado de custo para a seleção."),
        ("Benefício validado", money(realized["Benefício R$"]) if has_benefit else "—",
         "Soma dos benefícios com evidência validada na Fase 6 até a data de corte. As categorias incluídas dependem "
         "da visão escolhida. Se a apuração estiver parcial, o valor representa apenas os registros já validados."),
        ("ROI incremental projetado", percent(planned["ROI"]),
         "Divide o resultado líquido projetado (benefícios incrementais menos custos incrementais) pelo custo incremental. "
         "Um ROI de 60% representa 60 centavos de resultado líquido por real de custo incremental. "
         "O indicador usa os valores do horizonte, da visão e do cenário selecionados. Sem custo incremental, o ROI fica indisponível."),
        ("VPL projetado", money(planned["VPL R$"]),
         f"Valor Presente Líquido. Soma o valor, no início de 2027, dos benefícios menos os custos incrementais de cada mês. "
         f"O app usa a taxa anual de {rate:g}% e considera os fluxos no fim de cada mês. "
         "VPL positivo indica que os benefícios superam os custos em valor presente. VPL negativo indica que os custos superam os benefícios."),
        ("Payback previsto", planned["Payback"] or ("Fora do horizonte" if planned["Custo R$"] else "—"),
         "Primeiro mês em que o saldo acumulado de benefícios menos custos fica igual ou acima de zero e permanece assim "
         "até o fim do horizonte selecionado. O cálculo usa fluxos sem desconto. Fora do horizonte indica que o custo projetado "
         "ainda não é recuperado de forma sustentada no período exibido."),
    ]
    for start in (0, 3):
        for column, (label, value, help_text) in zip(st.columns(3), kpis[start:start + 3]):
            column.metric(label, value, help=help_text)
    st.caption(f"Projeção {horizon} · {view} · {scenario}. Realizado até {last_actual}. "
               "Passe o cursor sobre o ícone de ajuda de cada indicador para consultar seu cálculo.")
    with st.expander("O que é VPL e como interpretar o valor"):
        st.markdown("""
**VPL significa Valor Presente Líquido.** Ele responde quanto vale, no início de 2027, o saldo de benefícios e custos
que o portfólio gera ao longo do tempo. Com uma taxa de desconto positiva, um benefício recebido mais tarde tem menor valor presente.

O app calcula o saldo de cada mês (**benefícios menos custos**), desconta esse saldo pela taxa anual configurada na barra lateral
e soma os valores descontados até o fim do horizonte selecionado.

- **VPL positivo:** os benefícios superam os custos em valor presente, à taxa escolhida.
- **VPL igual a zero:** benefícios e custos se equivalem em valor presente.
- **VPL negativo:** os custos superam os benefícios em valor presente, à taxa escolhida.
        """)
        st.text("Exemplo didático: com taxa de 10% ao ano, R$ 1.100 recebidos em um ano equivalem a R$ 1.000 na data-base.")
        st.caption("O VPL é expresso em reais. O ROI simples expressa em percentual o resultado líquido por real de custo incremental.")
    comparators = [
        {"Base de comparação": "Projeção do horizonte", **planned},
        {"Base de comparação": f"Previsto até {last_actual}", **summary(plan[plan["Mês"] <= last_actual])},
    ]
    if not actual_detail.empty:
        comparators.append({"Base de comparação": f"Validado até {last_actual}" + (" · parcial" if missing else ""), **realized})
    comparison = pd.DataFrame(comparators)

    flow_tab, portfolio_tab, operation_tab = st.tabs(["Fluxo e cenários", "Domínios e evidências", "Indicadores operacionais"])
    with flow_tab:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Custos e benefícios projetados por mês**")
            monthly_bars = plan.melt(id_vars="Mês", value_vars=["Custo R$", "Benefício R$"], var_name="Componente", value_name="Valor")
            chart(monthly_bars, "Mês", "Valor", "R$", color="Componente", kind="bar")
        with col2:
            st.markdown("**Saldo incremental acumulado**")
            balance = plan[["Mês", "Saldo R$"]].assign(Série="Previsto")
            if not actual_detail.empty:
                balance = pd.concat([balance, actual[["Mês", "Saldo R$"]].assign(Série="Validado")], ignore_index=True)
            chart(balance.sort_values("Mês"), "Mês", "Saldo R$", "R$", color="Série")

        if not actual_detail.empty:
            st.markdown("**Previsto × validado por mês**")
            component = st.radio("Componente da comparação", ["Custo R$", "Benefício R$", "Fluxo R$"], horizontal=True)
            month_comparison = pd.concat([
                plan.loc[plan["Mês"] <= last_actual, ["Mês", component]].assign(Série="Previsto"),
                actual.loc[actual["Mês"].isin(actual_detail["Mês"]), ["Mês", component]].assign(Série="Validado"),
            ], ignore_index=True)
            chart(month_comparison, "Mês", component, "R$", color="Série", kind="bar")
        st.markdown("**Previsto × realizado e métricas complementares**")
        st.dataframe(comparison, hide_index=True, width="stretch", column_config={
            key: st.column_config.NumberColumn(format="percent") for key in ("ROI", "ROI descontado")
        })
        scenario_table = pd.DataFrame([
            {"Visão": v, "Cenário": s, "Horizonte": label, **summary(monthly[monthly["Mês"] <= limit])}
            for (v, s), (monthly, _) in all_plans.items()
            for label, limit in [("2027", "2027-12"), ("2027–2029", MONTHS[-1])]
        ])
        st.markdown("**Sensibilidade do ROI e VPL**")
        selected_scenarios = scenario_table[(scenario_table["Visão"] == view) & (scenario_table["Horizonte"] == horizon)]
        chart(selected_scenarios, "Cenário", "VPL R$", "R$", kind="bar")
        st.dataframe(selected_scenarios[["Cenário", "ROI", "VPL R$", "Payback"]], hide_index=True, width="stretch",
                     column_config={"ROI": st.column_config.NumberColumn(format="percent")})

    with portfolio_tab:
        by_initiative = (detail.assign(Ano=detail["Mês"].str[:4])
                         .groupby(["Ano", "Iniciativas"], as_index=False)[["Custo R$", "Benefício R$"]].sum()
                         .merge(data["Portfólio"][["ID", "Iniciativa", "Responsável", "Squads de apoio"]],
                                how="left", left_on="Iniciativas", right_on="ID")
                         .drop(columns="ID").rename(columns={"Responsável": "Squad líder"}))
        by_initiative["Líquido R$"] = by_initiative["Benefício R$"] - by_initiative["Custo R$"]
        st.markdown("**Contribuição por iniciativa e ano**")
        st.dataframe(by_initiative, hide_index=True, width="stretch")
        domains = data["Portfólio"].set_index("ID")["Domínio"].to_dict()
        by_domain = detail.copy()
        by_domain["Domínio"] = by_domain["Iniciativas"].map(domains).fillna("Benefícios compartilhados")
        by_domain = by_domain.groupby("Domínio", as_index=False)[["Custo R$", "Benefício R$"]].sum()
        by_domain["Líquido R$"] = by_domain["Benefício R$"] - by_domain["Custo R$"]
        st.markdown("**Contribuição por domínio de investimento**")
        st.caption("Benefícios vinculados a várias iniciativas aparecem uma vez em uma categoria compartilhada.")
        chart(by_domain, "Domínio", "Líquido R$", "R$", kind="bar")
        by_category = detail[detail["Benefício R$"] != 0].groupby("Classe", as_index=False)["Benefício R$"].sum()
        st.markdown("**Benefícios por categoria**")
        chart(by_category, "Classe", "Benefício R$", "R$", kind="bar")
        evidence_table = data["Benefícios"][["ID", "Iniciativas", "Descrição", "Classe", "Evidência", "Fonte / justificativa", "Responsável"]]
        st.markdown("**Evidência e rastreabilidade**")
        st.dataframe(evidence_table, hide_index=True, width="stretch")
        adoption = detail.dropna(subset=["Adoção %"]).assign(Benefício=lambda df: df["ID"] + " · " + df["Descrição"])
        st.markdown("**Adoção projetada por benefício**")
        chart(adoption, "Mês", "Adoção %", "%", color="Benefício")
        with st.expander("Abrir lançamentos projetados por mês"):
            st.dataframe(detail, hide_index=True, width="stretch")

    with operation_tab:
        indicators = data["Indicadores"]
        indicators = indicators[indicators["Mês"] <= end]
        if indicators.empty:
            st.info("Preencha os indicadores mensais na etapa 6.")
        else:
            indicator = st.selectbox("Indicador", indicators["Indicador"].unique())
            series = indicators[indicators["Indicador"] == indicator].sort_values("Mês")
            if series["Unidade"].nunique() == 1:
                series = series.copy()
                series.loc[series["Mês"] > cutoff, "Realizado"] = None
                values = series.melt(id_vars="Mês", value_vars=["Previsto", "Realizado"], var_name="Série", value_name="Valor")
                chart(values.dropna(subset=["Valor"]), "Mês", "Valor", series["Unidade"].iloc[0], color="Série")
            else:
                st.warning("Padronize a unidade deste indicador para comparar a série.")
            st.dataframe(series, hide_index=True, width="stretch")

    st.divider()
    st.markdown("**Exportação executiva**")
    st.caption("O Excel reúne a seleção do painel, todos os cenários, parâmetros, evidências e fluxos mensais. Os resultados são registrados como valores calculados pela aplicação.")
    metadata = pd.DataFrame([
        ("Horizonte selecionado", horizon), ("Visão selecionada", view), ("Cenário selecionado", scenario),
        ("Taxa anual em %", rate), ("Corte da realização", cutoff), ("Orçamento aprovado 2027 em R$", approved),
        ("Dados ilustrativos de origem", "Sim" if st.session_state["example"] else "Não"),
        ("ROI simples", "(Benefícios incrementais − custos adicionais brutos) / custos adicionais brutos"),
        ("VPL", "Soma dos fluxos descontados no fim de cada mês, com base no início de 2027"),
        ("Payback", "Primeiro mês a partir do qual o saldo acumulado permanece recuperado"),
        ("Apuração realizada", "Lançamentos validados até o corte. Ausência de lançamento significa ausência de evidência."),
        ("Cobertura do realizado", f"{len(expected_pairs & actual_pairs)} de {len(expected_pairs)} lançamentos previstos com registro validado no corte da seleção"),
    ], columns=["Parâmetro", "Valor"])
    forecast_export = pd.concat([
        table.assign(Visão=v, Cenário=s)
        for (v, s), (table, _) in all_plans.items()
    ], ignore_index=True)
    actual_export = pd.concat([
        table[table["Mês"] <= cutoff].assign(Visão=v)
        for v, (table, _) in all_actuals.items()
    ], ignore_index=True)
    sheets = {
        "Resumo executivo": comparison, "Premissas": metadata, "Resultados por cenário": scenario_table,
        "Fluxos projetados": forecast_export, "Fluxos validados": actual_export, "Detalhe projetado": detail,
        "Detalhe validado": actual_detail, "Iniciativas por ano": by_initiative, "Contribuição por domínio": by_domain, "Benefícios por classe": by_category,
        "Parâmetros de cenário": pd.DataFrame(scenario_rows, columns=["Cenário", "Realização %", "Variação do custo %", "Atraso meses"]),
        "Projeção da demanda": baseline, **data,
    }
    if example_mode:
        sheets["Transição das squads"] = transition
    st.download_button("Baixar resultados e parâmetros em Excel", export_excel(sheets),
                       file_name="ROI_Incremental_CICD_2027.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary")
