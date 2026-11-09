"""Regras do portfólio e exportação, independentes da interface."""
from io import BytesIO
import math
import re

import pandas as pd

from example import example_data

MONTHS = [str(month) for month in pd.period_range("2027-01", "2029-12", freq="M")]
VIEWS = ("Financeira", "Econômica ampliada")
CLASSES = ("Economia efetiva", "Custo evitado", "Capacidade liberada", "Risco esperado", "Qualitativo")
TYPES = {
    "Esforço manual": "Use horas de trabalho por atividade em A e B e R$/hora. Multiplique pelo volume elegível.",
    "Falhas e incidentes": "Use a taxa de eventos por unidade de exposição (5% = 0,05) e o custo por evento. Segmente por severidade.",
    "Infraestrutura": "Use consumo por execução ou por unidade de demanda e custo marginal faturável. Tarifas fixas exigem redução contratual.",
    "Contratos e licenças": "Use quantidades mensais em A e B e a tarifa unitária. Para pagamento pontual, selecione um único mês.",
    "Exposição a risco": "Use probabilidade por exposição no mês e perda média por evento. O resultado é uma perda esperada.",
    "Outros": "Use quantidades comparáveis em A e B e um valor unitário documentado.",
}
SCHEMAS = {
    "Portfólio": ("ID", "Iniciativa", "Domínio", "Responsável", "Entrada em operação", "Aprovado R$", "Entregável", "Squads de apoio"),
    "Linha de base": ("ID", "Indicador", "Unidade", "Volume 2026", "Crescimento % a.a.", "Fonte", "Responsável"),
    "Custos": ("ID", "Iniciativa", "Descrição", "Categoria", "Natureza", "Início", "Fim", "A R$/mês", "B R$/mês", "Fonte"),
    "Benefícios": ("ID", "Iniciativas", "Descrição", "Tipo", "Classe", "Evidência", "Início", "Fim", "Linha de base", "Volume próprio/mês", "A por unidade", "B por unidade", "B mensal R$", "R$/unidade", "Adoção inicial %", "Adoção alvo %", "Meses de rampa", "Atribuição %", "Monetização %", "Fonte / justificativa", "Responsável"),
    "Realização": ("Mês", "ID de origem", "Valor R$", "Validação", "Evidência / documento"),
    "Indicadores": ("Mês", "Indicador", "Unidade", "Previsto", "Realizado", "Fonte"),
}
NUMBERS = {"Aprovado R$", "Volume 2026", "Crescimento % a.a.", "A R$/mês", "B R$/mês", "Volume próprio/mês", "A por unidade", "B por unidade", "B mensal R$", "R$/unidade", "Adoção inicial %", "Adoção alvo %", "Meses de rampa", "Atribuição %", "Monetização %", "Valor R$", "Previsto", "Realizado"}
DEFAULTS = {"Início": "2027-01", "Fim": "2027-12", "Entrada em operação": "2027-01", "Mês": "2027-01", "Volume próprio/mês": 1, "Adoção inicial %": 100, "Adoção alvo %": 100, "Atribuição %": 100, "Monetização %": 100, "Evidência": "B — Fundamentado", "Validação": "Pendente", "Natureza": "Desembolso"}


def frames(example=False):
    sample = example_data() if example else {}
    return {
        name: pd.DataFrame(sample.get(name, []), columns=columns)
        .astype({column: "float64" if column in NUMBERS else "object" for column in columns})
        for name, columns in SCHEMAS.items()
    }


def validate(data):
    errors = []
    for sheet, table in data.items():
        for column in table.columns:
            optional = (sheet, column) in {
                ("Benefícios", "Linha de base"), ("Benefícios", "Volume próprio/mês"),
                ("Indicadores", "Realizado"), ("Portfólio", "Squads de apoio"),
                ("Benefícios", "B mensal R$"), ("Benefícios", "B por unidade"),
            }
            for index, value in enumerate(table[column], 1):
                empty = pd.isna(value) or not str(value).strip()
                if empty and not optional:
                    errors.append(f"{sheet}, linha {index} · preencha {column}.")
                elif not empty and column in NUMBERS and (
                    not math.isfinite(value) or
                    (value < 0 and column not in {"Crescimento % a.a.", "Valor R$", "Realizado", "Previsto"}) or
                    (column in {"Adoção inicial %", "Adoção alvo %", "Atribuição %", "Monetização %"} and value > 100) or
                    (column == "Crescimento % a.a." and value < -100)
                ):
                    errors.append(f"{sheet}, linha {index} · valor inválido em {column}.")
        if "ID" in table and table["ID"].duplicated().any():
            errors.append(f"{sheet} · use identificadores únicos.")
    if errors:
        return errors

    initiatives = data["Portfólio"].set_index("ID")["Entrada em operação"].to_dict()
    baselines = set(data["Linha de base"]["ID"])
    costs = set(data["Custos"]["ID"])
    benefits = set(data["Benefícios"]["ID"])
    if costs & benefits:
        errors.append("Use IDs distintos entre Custos e Benefícios para vincular a realização.")
    for sheet in ("Custos", "Benefícios"):
        for row in data[sheet].to_dict("records"):
            item = row["ID"]
            if row["Início"] > row["Fim"]:
                errors.append(f"{item} · fim anterior ao início.")
            links = [row["Iniciativa"]] if sheet == "Custos" else split_links(row["Iniciativas"])
            if not links or not set(links) <= initiatives.keys():
                errors.append(f"{item} · informe os IDs de iniciativas cadastradas.")
            elif sheet == "Benefícios" and row["Início"] < max(initiatives[link] for link in links):
                errors.append(f"{item} · início anterior à entrada em operação de uma iniciativa vinculada.")
            if sheet == "Benefícios":
                monthly_b = row.get("B mensal R$")
                if pd.notna(monthly_b):
                    if row["Tipo"] != "Infraestrutura" or row["R$/unidade"] != 1:
                        errors.append(f"{item} · B mensal R$ exige tipo Infraestrutura e valor unitário igual a 1.")
                elif pd.isna(row["B por unidade"]) or not str(row["B por unidade"]).strip():
                    errors.append(f"{item} · informe B por unidade ou B mensal R$.")
                baseline = row["Linha de base"]
                if pd.notna(baseline) and str(baseline).strip():
                    if baseline not in baselines:
                        errors.append(f"{item} · linha de base inexistente.")
                elif pd.isna(row["Volume próprio/mês"]):
                    errors.append(f"{item} · informe um volume mensal ou uma linha de base.")
                if row["Tipo"] == "Exposição a risco" and (
                    max(row["A por unidade"], row["B por unidade"]) > 1 or row["Classe"] != "Risco esperado"
                ):
                    errors.append(f"{item} · use probabilidades entre 0 e 1 e classe Risco esperado.")
    actual = data["Realização"]
    if actual.duplicated(["Mês", "ID de origem"]).any():
        errors.append("Realização · consolide os comprovantes em uma linha por mês e ID.")
    for item in set(actual["ID de origem"]) - (costs | benefits):
        errors.append(f"Realização · {item} não corresponde a custo ou benefício cadastrado.")
    for row in actual.to_dict("records"):
        if row["ID de origem"] in costs and row["Valor R$"] < 0:
            errors.append(f"Realização · {row['ID de origem']} deve informar custo bruto não negativo.")
    if data["Indicadores"].duplicated(["Mês", "Indicador"]).any():
        errors.append("Indicadores · use uma linha por mês e indicador.")
    return errors


def split_links(value):
    return [link.strip() for link in re.split(r"[,;]", value) if link.strip()]


def eligible(category, view):
    return category in CLASSES[:2] or (view == VIEWS[1] and category in CLASSES[2:4])


def calculate(data, settings, view, scenario="Base", actual=False):
    """Um lançamento por mês e ID. Reduções de TCO entram apenas como benefício."""
    if scenario == "Base" or actual:
        realization, markup, delay = 1, 1, 0
    else:
        realization, markup, delay = settings[scenario]
    baseline = data["Linha de base"].set_index("ID").to_dict("index")
    costs = data["Custos"].set_index("ID").to_dict("index")
    benefits = data["Benefícios"].set_index("ID").to_dict("index")
    rows = []
    for index, month in enumerate(MONTHS):
        for item, row in costs.items():
            if not row["Início"] <= month <= row["Fim"]:
                continue
            delta = row["B R$/mês"] - row["A R$/mês"]
            if delta < 0:
                if row["Natureza"] == "Desembolso":
                    add_row(rows, month, item, row, "Economia efetiva", 0, -delta * realization)
                continue
            if row["Natureza"] == "Desembolso" or view == VIEWS[1]:
                add_row(rows, month, item, row, row["Natureza"], delta * markup, 0)
        for item, row in benefits.items():
            line = baseline.get(row["Linha de base"])
            volume = row["Volume próprio/mês"]
            if line:
                volume = line["Volume 2026"] * (1 + line["Crescimento % a.a."] / 100) ** (int(month[:4]) - 2026) / 12
            monthly_b = row.get("B mensal R$")
            if pd.notna(monthly_b):
                difference = volume * row["A por unidade"] - monthly_b
                gain = difference >= 0
            else:
                unit_difference = row["A por unidade"] - row["B por unidade"]
                difference = volume * unit_difference
                gain = unit_difference >= 0
            start = MONTHS.index(row["Início"]) + (delay if gain else 0)
            if index < start or month > row["Fim"] or not eligible(row["Classe"], view):
                continue
            if row["Evidência"].startswith("D") or (row["Evidência"].startswith("C") and scenario != "Otimista"):
                continue
            ramp = int(row["Meses de rampa"])
            fraction = min((index - start) / (ramp - 1), 1) if ramp > 1 else 1
            adoption = row["Adoção inicial %"] + fraction * (row["Adoção alvo %"] - row["Adoção inicial %"])
            quantity = difference * adoption / 100 * row["Atribuição %"] / 100
            value = quantity * row["R$/unidade"] * row["Monetização %"] / 100
            add_row(rows, month, item, row, row["Classe"], 0, value * (realization if gain else 1), adoption, volume, quantity)
    if actual:
        rows = []
        for row in data["Realização"].to_dict("records"):
            if row["Validação"] != "Validado" or row["Mês"] > settings["Corte"]:
                continue
            item, month, value = row["ID de origem"], row["Mês"], row["Valor R$"]
            if item in costs:
                source = costs[item]
                if source["B R$/mês"] < source["A R$/mês"]:
                    if source["Natureza"] == "Desembolso":
                        add_row(rows, month, item, source, "Economia efetiva", 0, value)
                elif source["Natureza"] == "Desembolso" or view == VIEWS[1]:
                    add_row(rows, month, item, source, source["Natureza"], value, 0)
            elif eligible(benefits[item]["Classe"], view):
                source = benefits[item]
                add_row(rows, month, item, source, source["Classe"], 0, value)
    detail = pd.DataFrame(rows, columns=["Mês", "ID", "Iniciativas", "Descrição", "Classe", "Custo R$", "Benefício R$", "Adoção %", "Volume", "Variação atribuída"])
    monthly = detail.groupby("Mês")[["Custo R$", "Benefício R$"]].sum().reindex(MONTHS, fill_value=0.0)
    monthly["Fluxo R$"] = monthly["Benefício R$"] - monthly["Custo R$"]
    monthly["Saldo R$"] = monthly["Fluxo R$"].cumsum()
    monthly["Fator VP"] = [(1 + settings["Taxa %"] / 100) ** (-n / 12) for n in range(1, 37)]
    monthly["Fluxo VP R$"] = monthly["Fluxo R$"] * monthly["Fator VP"]
    return monthly.rename_axis("Mês").reset_index(), detail


def add_row(rows, month, item, source, category, cost, benefit, adoption=None, volume=None, quantity=None):
    rows.append((month, item, source.get("Iniciativas", source.get("Iniciativa")), source["Descrição"], category, cost, benefit, adoption, volume, quantity))


def summary(monthly):
    cost = monthly["Custo R$"].sum()
    benefit = monthly["Benefício R$"].sum()
    discounted_cost = (monthly["Custo R$"] * monthly["Fator VP"]).sum()
    vpl = monthly["Fluxo VP R$"].sum()
    payback = None
    if cost > 0 and monthly["Saldo R$"].iloc[-1] >= -1e-7:
        negative = monthly["Saldo R$"] < -1e-7
        if negative.any():
            payback = monthly.loc[negative[negative].index[-1] + 1, "Mês"]
        else:
            payback = monthly.loc[monthly["Custo R$"] > 0, "Mês"].iloc[0]
    return {
        "Custo R$": cost, "Benefício R$": benefit, "Resultado líquido R$": benefit - cost,
        "ROI": (benefit - cost) / cost if cost > 0 else None,
        "VPL R$": vpl, "ROI descontado": vpl / discounted_cost if discounted_cost > 0 else None,
        "Payback": payback,
    }


def export_excel(sheets):
    """Relatório Excel em memória para o download da sessão."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter", engine_kwargs={"options": {
        "strings_to_formulas": False, "strings_to_urls": False,
    }}) as writer:
        book = writer.book
        header = book.add_format({"bold": True, "bg_color": "#172B4D", "font_color": "#FFFFFF", "text_wrap": True, "valign": "vcenter"})
        money = book.add_format({"num_format": '"R$" #,##0.00;[Red]-"R$" #,##0.00'})
        percent = book.add_format({"num_format": "0.0%"})
        for name, frame in sheets.items():
            frame.to_excel(writer, sheet_name=name, index=False, startrow=1, header=False)
            sheet = writer.sheets[name]
            sheet.freeze_panes(1, 0)
            sheet.set_row(0, 30)
            sheet.autofilter(0, 0, len(frame), len(frame.columns) - 1)
            for index, column in enumerate(frame):
                sheet.write(0, index, column, header)
                fmt = money if "R$" in column else percent if column in {"ROI", "ROI descontado"} else None
                longest = max([len(column), *frame[column].dropna().astype(str).str.len()])
                sheet.set_column(index, index, min(55, max(13, longest + 2)), fmt)
    return output.getvalue()
