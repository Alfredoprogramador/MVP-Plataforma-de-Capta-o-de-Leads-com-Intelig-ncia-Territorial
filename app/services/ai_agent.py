from openai import AsyncOpenAI
from app.config import settings
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class AIAgentService:
    """Service for AI-powered lead qualification and conversation"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4"
        
    async def qualify_lead(
        self,
        conversation_history: List[Dict[str, str]],
        lead_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Qualify a lead based on conversation and information
        Returns: {temperature: "hot/warm/cold", score: int, summary: str}
        """
        system_prompt = """Você é um agente de qualificação de leads especializado em vendas.
        Sua tarefa é analisar a conversa com o lead e classificá-lo como:
        - QUENTE (hot): Lead muito interessado, pronto para comprar, respondeu positivamente
        - MORNO (warm): Lead interessado mas precisa de mais informações, tem objeções
        - FRIO (cold): Lead pouco interessado, apenas pesquisando, sem urgência
        
        Também forneça uma pontuação de 0-100 e um resumo da qualificação.
        
        Responda APENAS em formato JSON:
        {
            "temperature": "hot|warm|cold",
            "score": 0-100,
            "summary": "Resumo da qualificação",
            "next_action": "Próxima ação recomendada"
        }
        """
        
        # Build context
        context = f"Informações do lead:\n"
        context += f"- Nome: {lead_info.get('name', 'N/A')}\n"
        context += f"- Bairro: {lead_info.get('neighborhood', 'N/A')}\n"
        context += f"- Origem: {lead_info.get('source', 'N/A')}\n\n"
        context += "Histórico da conversa:\n"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context}
        ]
        
        # Add conversation history
        for msg in conversation_history:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.error(f"Error qualifying lead: {e}")
            return {
                "temperature": "cold",
                "score": 0,
                "summary": "Erro na qualificação",
                "next_action": "Revisar manualmente"
            }
    
    async def generate_response(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        lead_info: Dict[str, Any]
    ) -> str:
        """Generate AI response to lead message"""
        system_prompt = f"""Você é um assistente de vendas amigável e profissional.
        Você está conversando com um lead interessado em serviços.
        
        Informações do lead:
        - Nome: {lead_info.get('name', 'N/A')}
        - Bairro: {lead_info.get('neighborhood', 'N/A')}
        - Cidade: {lead_info.get('city', 'N/A')}
        
        Suas responsabilidades:
        1. Responder de forma educada e prestativa
        2. Coletar informações relevantes do lead
        3. Apresentar soluções adequadas ao bairro do lead
        4. Criar senso de urgência quando apropriado
        5. Encaminhar para proposta quando o lead estiver pronto
        
        Mantenha respostas concisas e objetivas (máximo 2-3 parágrafos).
        Use linguagem natural e amigável.
        """
        
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add conversation history
        for msg in conversation_history[-10:]:  # Last 10 messages
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": message
        })
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.8,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return "Desculpe, ocorreu um erro. Um atendente entrará em contato em breve."
    
    async def should_escalate_to_human(
        self,
        conversation_history: List[Dict[str, str]],
        lead_info: Dict[str, Any]
    ) -> bool:
        """Determine if conversation should be escalated to human"""
        system_prompt = """Analise a conversa e determine se deve ser encaminhada para atendimento humano.
        
        Encaminhe para humano se:
        - Lead demonstra interesse muito alto (temperatura quente)
        - Lead tem dúvidas complexas que requerem especialista
        - Lead solicitou falar com atendente
        - Conversa tem mais de 10 mensagens sem progresso
        
        Responda APENAS: true ou false
        """
        
        context = "Histórico da conversa:\n"
        for msg in conversation_history:
            role = "Lead" if msg.get("role") == "user" else "IA"
            context += f"{role}: {msg.get('content', '')}\n"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context}
        ]
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=10
            )
            
            answer = response.choices[0].message.content.strip().lower()
            return "true" in answer
            
        except Exception as e:
            logger.error(f"Error checking escalation: {e}")
            return False


# Singleton instance
ai_agent_service = AIAgentService()
