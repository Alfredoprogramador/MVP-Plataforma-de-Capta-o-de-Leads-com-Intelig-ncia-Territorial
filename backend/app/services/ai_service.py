import os
import json
from typing import Optional
from openai import OpenAI

_client: Optional[OpenAI] = None


def _get_client() -> Optional[OpenAI]:
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY", "")
        if api_key:
            _client = OpenAI(api_key=api_key)
    return _client


def qualify_lead(lead_data: dict) -> dict:
    """Use GPT to score a lead 0-100 and return qualification notes."""
    client = _get_client()
    if not client:
        return {"score": 50, "notes": "Qualificação automática indisponível (API key não configurada)."}

    prompt = f"""Você é um agente especializado em qualificação de leads imobiliários/comerciais.

Dados do lead:
{json.dumps(lead_data, ensure_ascii=False, indent=2)}

Analise o lead e retorne um JSON com:
- "score": número de 0 a 100 indicando o potencial do lead (0 = sem potencial, 100 = altíssimo potencial)
- "notes": string em português com análise e recomendações (máximo 3 frases)

Responda APENAS com o JSON, sem markdown.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300,
        )
        content = response.choices[0].message.content.strip()
        result = json.loads(content)
        score = max(0, min(100, int(result.get("score", 50))))
        notes = result.get("notes", "")
        return {"score": score, "notes": notes}
    except Exception as e:
        return {"score": 50, "notes": f"Erro na qualificação automática: {str(e)}"}


def generate_whatsapp_message(lead_data: dict, context: str = "") -> str:
    """Generate a personalized WhatsApp message for a lead."""
    client = _get_client()
    if not client:
        return (
            f"Olá {lead_data.get('name', 'cliente')}! "
            "Recebemos seu contato e em breve nossa equipe entrará em contato. Obrigado!"
        )

    prompt = f"""Você é um assistente de vendas. Crie uma mensagem de WhatsApp personalizada e profissional em português para o seguinte lead.

Dados do lead:
{json.dumps(lead_data, ensure_ascii=False, indent=2)}

Contexto adicional: {context or 'Primeiro contato após cadastro na plataforma.'}

A mensagem deve ser:
- Em português do Brasil
- Amigável e profissional
- Máximo 3 frases
- Incluir o nome do lead
- Não usar markdown

Responda APENAS com o texto da mensagem.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return (
            f"Olá {lead_data.get('name', 'cliente')}! "
            "Recebemos seu contato e em breve nossa equipe entrará em contato. Obrigado!"
        )


def analyze_territory(territory_data: dict, leads_data: list) -> str:
    """Generate AI insights about a territory based on its leads."""
    client = _get_client()
    if not client:
        return "Análise de território indisponível (API key não configurada)."

    prompt = f"""Você é um analista de inteligência territorial. Analise os dados do território e seus leads.

Território:
{json.dumps(territory_data, ensure_ascii=False, indent=2)}

Leads ({len(leads_data)} total):
{json.dumps(leads_data[:20], ensure_ascii=False, indent=2)}

Forneça insights em português sobre:
1. Distribuição e qualidade dos leads
2. Oportunidades identificadas
3. Recomendações para o agente responsável

Máximo 5 frases. Responda apenas com o texto, sem markdown.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=400,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Erro ao gerar análise: {str(e)}"
