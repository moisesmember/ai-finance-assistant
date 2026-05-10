from app.domain.services.llm_provider import LLMProvider


class FakeLLMProvider(LLMProvider):
    def generate_response(self, prompt: str) -> str:
        return (
            "Esta e uma explicacao simulada para testes locais. "
            "Com base nos agregados enviados, revise o saldo do mes, observe as maiores "
            "variacoes de despesas e acompanhe categorias ou formas de pagamento que concentram "
            "uma parte relevante dos gastos. Use esses pontos como apoio educativo para ajustar "
            "o planejamento financeiro sem conclusoes alarmistas."
        )
