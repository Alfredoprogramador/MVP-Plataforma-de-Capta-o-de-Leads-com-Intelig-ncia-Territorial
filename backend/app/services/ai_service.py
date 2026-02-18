"""
AI Service for lead qualification and conversation handling
"""
import logging
from typing import Dict, Any, List, Optional
import openai

logger = logging.getLogger(__name__)


class AILeadAgent:
    """AI agent for lead qualification using GPT"""
    
    def __init__(self, config):
        self.api_key = config.OPENAI_API_KEY
        self.model = config.OPENAI_MODEL
        self.hot_threshold = config.HOT_LEAD_THRESHOLD
        self.warm_threshold = config.WARM_LEAD_THRESHOLD
        openai.api_key = self.api_key
        
        # System prompt for lead qualification
        self.system_prompt = """Você é um assistente inteligente de vendas especializado em qualificação de leads para serviços locais. 

Suas responsabilidades:
1. Conversar de forma natural e profissional com potenciais clientes
2. Fazer perguntas para entender as necessidades do cliente
3. Classificar o interesse do lead (quente/morno/frio)
4. Identificar sinais de compra e urgência
5. Coletar informações importantes: nome, localização, tipo de serviço desejado, orçamento, prazo

Diretrizes:
- Seja amigável mas profissional
- Faça perguntas abertas para engajar
- Identifique objeções e responda adequadamente
- Não seja muito insistente
- Mantenha as respostas concisas (máximo 3-4 frases)
- Use linguagem brasileira informal mas respeitosa

Sinais de lead QUENTE:
- Menciona urgência ou necessidade imediata
- Pergunta sobre preços ou disponibilidade
- Já sabe exatamente o que quer
- Está comparando opções
- Menciona orçamento disponível

Sinais de lead MORNO:
- Está pesquisando e comparando
- Tem interesse mas sem urgência
- Faz perguntas gerais
- Pede mais informações

Sinais de lead FRIO:
- Apenas curiosidade
- Não tem orçamento definido
- Não tem urgência
- Respostas monossilábicas
"""
    
    def classify_lead(
        self, 
        conversation_history: List[Dict[str, str]],
        lead_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Classify lead based on conversation history
        Returns: {
            'score': int (0-100),
            'temperature': str ('hot', 'warm', 'cold'),
            'intent': str,
            'sentiment': str,
            'key_interests': list,
            'next_action': str
        }
        """
        try:
            # Prepare analysis prompt
            conversation_text = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in conversation_history
            ])
            
            analysis_prompt = f"""Analise a seguinte conversa e classifique o lead:

{conversation_text}

Forneça a análise no seguinte formato JSON:
{{
    "score": [0-100],
    "temperature": ["hot", "warm", "cold"],
    "intent": "descrição da intenção principal",
    "sentiment": ["positive", "neutral", "negative"],
    "key_interests": ["lista", "de", "interesses"],
    "next_action": "próxima ação recomendada",
    "reasoning": "breve justificativa da classificação"
}}
"""
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um especialista em análise de leads. Retorne apenas JSON válido."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            
            # Ensure score is within range
            result['score'] = max(0, min(100, result.get('score', 0)))
            
            # Map score to temperature if not already set correctly
            if result['score'] >= self.hot_threshold:
                result['temperature'] = 'hot'
            elif result['score'] >= self.warm_threshold:
                result['temperature'] = 'warm'
            else:
                result['temperature'] = 'cold'
            
            logger.info(f"Lead classified: {result['temperature']} (score: {result['score']})")
            return result
            
        except Exception as e:
            logger.error(f"Failed to classify lead: {str(e)}")
            return {
                'score': 0,
                'temperature': 'cold',
                'intent': 'unknown',
                'sentiment': 'neutral',
                'key_interests': [],
                'next_action': 'follow_up',
                'error': str(e)
            }
    
    def generate_response(
        self, 
        conversation_history: List[Dict[str, str]],
        lead_data: Optional[Dict[str, Any]] = None,
        context: Optional[str] = None
    ) -> str:
        """
        Generate AI response based on conversation history
        """
        try:
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add context if provided
            if context:
                messages.append({"role": "system", "content": f"Contexto adicional: {context}"})
            
            # Add lead data context if available
            if lead_data:
                lead_context = f"Informações do lead: Nome: {lead_data.get('name', 'Desconhecido')}, Bairro: {lead_data.get('neighborhood', 'Não informado')}"
                messages.append({"role": "system", "content": lead_context})
            
            # Add conversation history
            messages.extend(conversation_history)
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=200
            )
            
            ai_message = response.choices[0].message.content.strip()
            logger.info("AI response generated successfully")
            return ai_message
            
        except Exception as e:
            logger.error(f"Failed to generate AI response: {str(e)}")
            return "Desculpe, estou tendo dificuldades técnicas no momento. Um de nossos atendentes entrará em contato em breve."
    
    def extract_lead_info(self, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Extract structured lead information from conversation
        """
        try:
            conversation_text = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in conversation_history
            ])
            
            extraction_prompt = f"""Extraia as seguintes informações da conversa:

{conversation_text}

Retorne no formato JSON:
{{
    "name": "nome completo ou null",
    "email": "email ou null",
    "neighborhood": "bairro mencionado ou null",
    "city": "cidade ou null",
    "service_interest": "tipo de serviço de interesse",
    "budget_range": "faixa de orçamento mencionada ou null",
    "urgency": "urgência (alta/média/baixa/nenhuma)",
    "specific_needs": ["lista", "de", "necessidades", "específicas"]
}}
"""
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um especialista em extração de informações. Retorne apenas JSON válido."},
                    {"role": "user", "content": extraction_prompt}
                ],
                temperature=0.2,
                max_tokens=300
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            logger.info("Lead information extracted successfully")
            return result
            
        except Exception as e:
            logger.error(f"Failed to extract lead info: {str(e)}")
            return {}
    
    def should_escalate_to_human(
        self, 
        conversation_history: List[Dict[str, str]],
        lead_score: int
    ) -> Dict[str, Any]:
        """
        Determine if conversation should be escalated to human agent
        """
        try:
            # Automatic escalation for hot leads
            if lead_score >= self.hot_threshold:
                return {
                    'should_escalate': True,
                    'reason': 'high_score',
                    'priority': 'high'
                }
            
            # Check for escalation signals in conversation
            conversation_text = "\n".join([
                f"{msg['content']}" 
                for msg in conversation_history 
                if msg['role'] == 'user'
            ])
            
            escalation_keywords = [
                'falar com atendente',
                'falar com humano',
                'falar com vendedor',
                'ligar para mim',
                'atendimento humano',
                'não entendi',
                'não está ajudando'
            ]
            
            for keyword in escalation_keywords:
                if keyword.lower() in conversation_text.lower():
                    return {
                        'should_escalate': True,
                        'reason': 'customer_request',
                        'priority': 'medium'
                    }
            
            # Check conversation length - escalate if too long
            if len(conversation_history) > 20:
                return {
                    'should_escalate': True,
                    'reason': 'long_conversation',
                    'priority': 'low'
                }
            
            return {
                'should_escalate': False,
                'reason': None,
                'priority': None
            }
            
        except Exception as e:
            logger.error(f"Failed to determine escalation: {str(e)}")
            return {
                'should_escalate': False,
                'reason': 'error',
                'priority': None
            }
