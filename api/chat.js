export default async function handler(req, res) {
    // Enable CORS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    
    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }
    
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }
    
    try {
        const { message } = req.body;
        
        if (!message) {
            return res.status(400).json({ error: 'Message is required' });
        }
        
        const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
        
        if (!OPENAI_API_KEY) {
            return res.status(500).json({ error: 'OpenAI API key not configured' });
        }
        
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${OPENAI_API_KEY}`
            },
            body: JSON.stringify({
                model: 'gpt-4o-mini',
                messages: [
                    {
                        role: 'system',
                        content: `Você é o Assistente Hospitalar, especializado no sistema Hospitalar Saúde (https://hospitalarsaude.app.br).
                        
Você ajuda os usuários a:
- Navegar pelo sistema
- Entender funcionalidades
- Resolver problemas
- Gerenciar pacientes, orçamentos e relatórios
- Configurar o sistema

Seja conciso, útil e profissional. Responda sempre em português brasileiro.`
                    },
                    {
                        role: 'user',
                        content: message
                    }
                ],
                max_tokens: 1000,
                temperature: 0.7
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            return res.status(500).json({ error: data.error.message });
        }
        
        const assistantMessage = data.choices?.[0]?.message?.content || 'Não foi possível gerar uma resposta.';
        
        return res.status(200).json({ response: assistantMessage });
        
    } catch (error) {
        console.error('Error:', error);
        return res.status(500).json({ error: 'Internal server error' });
    }
}
