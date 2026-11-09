"""Cenário didático da transição organizacional e do ROI de 2027–2029."""

TRANSITION = (
    ("1 · Inventário de Software", "Correção e manutenção da base de dados do inventário.",
     "1 · Estratégia e Inteligência", "INV08"),
    ("2 · Esteira de CI/CD", "Operação e evolução das esteiras existentes.",
     "2 · Fundação de Integração Contínua; 4 · Ativos de Software; 5 · Integração Contínua",
     "INV01, INV02, INV03, INV06"),
    ("3 · Copilot e IA para Desenvolvimento de Software", "Copilot e capacidades de IA já ofertadas.",
     "3 · IA para Desenvolvimento de Software", "INV05"),
    ("4 · Entrega de Software", "Release e Motor de Liberação.",
     "6 · Entrega Contínua; 7 · Implantação Contínua", "INV04, INV07"),
)
TRANSITION_COLUMNS = ("Equipe em 2026", "Escopo em 2026", "Squads a partir de 2027", "Iniciativas")
SQUADS = {
    1: "1 · Estratégia e Inteligência",
    2: "2 · Fundação de Integração Contínua",
    3: "3 · IA para Desenvolvimento de Software",
    4: "4 · Ativos de Software",
    5: "5 · Integração Contínua",
    6: "6 · Entrega Contínua",
    7: "7 · Implantação Contínua",
}
PORTFOLIO = (
    ("INV01", "Padronização de CI/CD", "Construção", 5,
     {2: "compatibilizar os ambientes de execução", 7: "validar a transição da construção para a implantação"},
     "Metamodelo, templates e componentes reutilizáveis"),
    ("INV02", "Qualidade contínua", "Qualidade", 5,
     {6: "definir as evidências consumidas na avaliação do software"}, "Controles de qualidade integrados à construção"),
    ("INV03", "Segurança integrada", "Segurança", 4,
     {2: "viabilizar acessos e integrações", 5: "incorporar análise e políticas aos pipelines"},
     "Análise de composição e políticas de dependências na esteira"),
    ("INV04", "Observabilidade", "Implantação", 7,
     {1: "integrar dados aos indicadores da cadeia", 6: "vincular resultados pós-implantação às mudanças"},
     "Telemetria, verificação pós-implantação e rollback"),
    ("INV05", "Experiência do desenvolvedor", "Desenvolvimento assistido por IA", 3,
     {5: "validar as jornadas de construção assistidas por IA"}, "Gestão de acesso, licenças e jornadas de uso de IA"),
    ("INV06", "Eficiência operacional", "Fundação", 2,
     {5: "ajustar workloads e validar o desempenho", 1: "consolidar consumo e custo por execução"},
     "Otimização do consumo de runners"),
    ("INV07", "Governança e conformidade", "Entrega", 6,
     {1: "fornecer vínculos de ativos e responsáveis", 5: "disponibilizar evidências da construção"},
     "Avaliação do software, registro da mudança e autorização"),
    ("INV08", "Evolução do Inventário e Inteligência da Plataforma", "Estratégia e inteligência", 1,
     {4: "fornecer dados de componentes e dependências", 5: "validar dados de construção",
      6: "validar dados de mudança", 7: "validar dados de implantação"},
     "Taxonomia, vínculos entre ativos, modelo de dados e indicadores da cadeia"),
)
# Custos e benefícios anuais, em R$ mil.
COSTS = {
    "INV01": (350, 80, 80), "INV02": (220, 50, 50), "INV03": (300, 70, 70),
    "INV04": (280, 80, 80), "INV05": (180, 50, 50), "INV06": (400, 100, 100),
    "INV07": (170, 40, 40), "INV08": (100, 30, 30),
}
BENEFITS = {
    "INV01": (120, 300, 360), "INV02": (60, 150, 190), "INV03": (100, 230, 280),
    "INV04": (80, 200, 260), "INV05": (60, 120, 150), "INV06": (220, 450, 540),
    "INV07": (110, 250, 300), "INV08": (50, 100, 120),
}
BENEFIT_BASELINES = {
    "INV01": "L03", "INV02": "L01", "INV03": "L04", "INV04": "L02",
    "INV05": "L08", "INV06": "L01", "INV07": "L06", "INV08": "L07",
}
# Níveis de B por ocorrência escolhidos para o exemplo, antes de somar a diferença ilustrativa.
UNIT_B = {"INV01": 0.25, "INV02": 0.001, "INV03": 0.001, "INV04": 0.02,
          "INV05": 0.10, "INV07": 0.15, "INV08": 0.10}
DRIVERS = {
    "INV01": ("Esforço de provisionamento de novos pipelines", "Esforço manual", "Capacidade liberada", 100,
              "horas de engenharia e histórico de alterações"),
    "INV02": ("Esforço médio de correção de defeitos por execução", "Esforço manual", "Capacidade liberada", 100,
              "evidências de testes e registros de correção"),
    "INV03": ("Taxa de remediações tardias por análise de dependências", "Outros", "Custo evitado", 1000,
              "Xray, chamados e diferencial de custo por remediação"),
    "INV04": ("Esforço médio de diagnóstico e recuperação por deploy", "Esforço manual", "Capacidade liberada", 100,
              "logs de implantação e registros de incidentes"),
    "INV05": ("Parcela de licenças de IA ociosas faturadas", "Contratos e licenças", "Economia efetiva", 100,
              "faturas e telemetria de utilização"),
    "INV06": ("Custo faturado de runners", "Infraestrutura", "Economia efetiva", 1,
              "faturas e telemetria para workloads equivalentes"),
    "INV07": ("Esforço de preparação de evidências e avaliação de mudanças", "Esforço manual", "Capacidade liberada", 100,
              "registros do motor e do ITSM"),
    "INV08": ("Esforço de conciliação por revisão cadastral", "Esforço manual", "Capacidade liberada", 100,
              "registros do inventário e apontamento de horas"),
}


def example_data():
    data = {
        "Portfólio": [],
        "Linha de base": [
            ("L01", "Execuções de pipelines", "execuções/ano", 1200000, 10, "Exemplo · logs CI/CD", SQUADS[2]),
            ("L02", "Deploys em produção", "deploys/ano", 24000, 8, "Exemplo · orquestrador de implantação", SQUADS[7]),
            ("L03", "Pipelines provisionados", "pipelines/ano", 3600, 10, "Exemplo · catálogo IDP", SQUADS[5]),
            ("L04", "Análises de dependências", "análises/ano", 120000, 12, "Exemplo · histórico do Xray", SQUADS[4]),
            ("L05", "Solicitações de acesso a ferramentas de IA", "solicitações/ano", 2400, 15, "Exemplo · catálogo de acessos", SQUADS[3]),
            ("L06", "Solicitações de mudança avaliadas", "mudanças/ano", 18000, 8, "Exemplo · ITSM e Motor de Liberação", SQUADS[6]),
            ("L07", "Registros de ativos revisados no inventário", "revisões/ano", 6000, 5, "Exemplo · histórico do inventário", SQUADS[1]),
            ("L08", "Licenças de IA elegíveis à revisão", "licenças-mês/ano", 12000, 5, "Exemplo · faturas e telemetria de IA", SQUADS[3]),
        ],
        "Custos": [],
        "Benefícios": [],
        "Realização": [
            ("2027-03", "C-INV06-2027-D", 25000, "Validado", "Simulação · comprovantes de implantação de março"),
            ("2027-03", "C-INV06-2027-E", 8000, "Validado", "Simulação · apontamento de horas internas de março"),
            ("2027-03", "B-INV06-2027", 20000, "Validado", "Simulação · referência de 50.000 reais menos fatura de 30.000 reais"),
            ("2027-04", "C-INV06-2027-D", 24000, "Validado", "Simulação · comprovantes de implantação de abril"),
            ("2027-04", "C-INV06-2027-E", 8000, "Validado", "Simulação · apontamento de horas internas de abril"),
            ("2027-04", "B-INV06-2027", 23500, "Pendente", "Simulação · referência de 52.500 reais menos fatura de 29.000 reais, em conciliação"),
        ],
        "Indicadores": [
            ("2027-03", "Execuções de pipelines no escopo (INV06)", "execuções/mês", 110000, 110000, "Simulação · logs de CI/CD"),
            ("2027-04", "Execuções de pipelines no escopo (INV06)", "execuções/mês", 110000, 115500, "Simulação · logs de CI/CD"),
            ("2027-03", "Custo faturado de runners por execução (INV06)", "reais/execução", 28000 / 110000, 30000 / 110000, "Simulação · fatura conciliada com logs de CI/CD"),
            ("2027-04", "Custo faturado de runners por execução (INV06)", "reais/execução", 28000 / 110000, 29000 / 115500, "Simulação · valor preliminar da fatura e logs de CI/CD"),
            ("2027-03", "Adoção de templates padronizados (INV01)", "%", 60, 54, "Simulação · catálogo de pipelines e inventário de repositórios"),
            ("2027-04", "Adoção de templates padronizados (INV01)", "%", 65, 62, "Simulação · catálogo de pipelines e inventário de repositórios"),
            ("2027-03", "Taxa de mudanças com falha (INV07)", "%", 5, 6, "Simulação · mudanças de produção e incidentes vinculados no ITSM"),
            ("2027-04", "Taxa de mudanças com falha (INV07)", "%", 5, 4, "Simulação · mudanças de produção e incidentes vinculados no ITSM"),
        ],
    }
    baseline_by_id = {row[0]: row for row in data["Linha de base"]}
    for item, name, domain, lead, support, deliverable in PORTFOLIO:
        operation = "2027-03" if item == "INV06" else "2027-01"
        support_text = "; ".join(f"{SQUADS[squad]} — {role}" for squad, role in support.items())
        data["Portfólio"].append((item, name, domain, SQUADS[lead], operation, 0, deliverable, support_text))
        description, kind, category, rate, source = DRIVERS[item]
        for offset, (cost, benefit) in enumerate(zip(COSTS[item], BENEFITS[item])):
            year = 2027 + offset
            start = operation if year == 2027 else f"{year}-01"
            end = f"{year}-12"
            period = 10 if item == "INV06" and year == 2027 else 12
            # Premissa didática separada do total econômico: 75% desembolso e 25% esforço interno.
            for suffix, nature, fraction in (("D", "Desembolso", 0.75), ("E", "Esforço interno", 0.25)):
                data["Custos"].append((
                    f"C-{item}-{year}-{suffix}", item, f"{name} · {nature.lower()}",
                    "Implantação e operação" if year == 2027 else "Sustentação",
                    nature, f"{year}-01", end, 0, cost * 1000 * fraction / 12,
                    "Exemplo · custo adicional de liderança e apoio consolidado no ID",
                ))
            baseline_id = BENEFIT_BASELINES[item]
            volume_2026, growth = baseline_by_id[baseline_id][3:5]
            monthly_volume = volume_2026 * (1 + growth / 100) ** (year - 2026) / 12
            delta = benefit * 1000 / (period * rate * monthly_volume)
            monthly_b = 28000 if item == "INV06" else None
            after = monthly_b / monthly_volume if monthly_b is not None else UNIT_B[item]
            data["Benefícios"].append((
                f"B-{item}-{year}", item, description, kind, category, "B — Fundamentado",
                start, end, baseline_id, None, after + delta, after if monthly_b is None else None, monthly_b, rate, 100, 100, 0, 100, 100,
                f"Fonte de referência para validação: {source}. Valores simulados.", SQUADS[lead],
            ))
    return data
