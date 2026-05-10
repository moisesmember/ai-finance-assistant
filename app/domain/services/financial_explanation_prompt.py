from decimal import Decimal

from app.domain.services.insight_generator import FinancialSummary


def build_financial_explanation_prompt(summary: FinancialSummary) -> str:
    account_lines = _build_account_lines(summary.expenses_by_account)
    insight_lines = _build_insight_lines(summary)

    return "\n".join(
        [
            "Voce e um assistente financeiro educativo.",
            "Explique os dados financeiros em linguagem natural, clara e nao alarmista.",
            "Nao calcule novas metricas financeiras.",
            "Use apenas as agregacoes e os insights ja calculados pelo sistema.",
            (
                "Nao solicite nem mencione transacoes brutas, descricoes de compras "
                "ou dados pessoais."
            ),
            "",
            "Dados agregados:",
            f"- Mes analisado: {summary.month}",
            f"- Total de receitas: {_format_decimal(summary.total_income)}",
            f"- Total de despesas: {_format_decimal(summary.total_expenses)}",
            f"- Saldo consolidado: {_format_decimal(summary.consolidated_balance)}",
            (
                "- Categoria com maior despesa: "
                f"{summary.largest_expense_category or 'nao identificada'}"
            ),
            (
                "- Variacao das despesas vs. mes anterior: "
                f"{_format_decimal(summary.previous_month_expense_delta)}"
            ),
            (
                "- Participacao de cartoes nas despesas: "
                f"{_format_decimal(summary.credit_card_usage_percentage)}%"
            ),
            "",
            "Despesas por conta anonimizada:",
            *account_lines,
            "",
            "Insights calculados pelo sistema:",
            *insight_lines,
            "",
            "Gere uma explicacao com:",
            "- resumo do mes;",
            "- principais mudancas;",
            "- possiveis alertas financeiros;",
            "- orientacoes educativas e praticas.",
        ]
    )


def _build_account_lines(expenses_by_account: dict[str, Decimal]) -> list[str]:
    if not expenses_by_account:
        return ["- Nenhuma despesa por conta informada."]

    ordered_expenses = sorted(
        expenses_by_account.values(),
        reverse=True,
    )
    return [
        f"- Conta {index}: {_format_decimal(amount)}"
        for index, amount in enumerate(ordered_expenses, start=1)
    ]


def _build_insight_lines(summary: FinancialSummary) -> list[str]:
    if not summary.insights:
        return ["- Nenhum insight calculado."]

    return [
        f"- {insight.metric}: {insight.message} Valor: {_format_decimal(insight.value)}"
        for insight in summary.insights
    ]


def _format_decimal(value: Decimal | int | float | str) -> str:
    if isinstance(value, Decimal):
        return f"{value:.2f}"
    return str(value)
