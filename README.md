# Chatbot de unhas — Antena Hair

Este projeto é um protótipo para o trabalho da disciplina. O bot atende clientes de um salão especializado em unhas, apresenta os preços, entende erros comuns de digitação e coleta os dados básicos para um pedido de agendamento.

## As três interações pedidas

O fluxo principal foi limitado a três interações, para ficar fácil de demonstrar:

| Interação | Cliente | Bot |
|---|---|---|
| 1 | “Oi” | Apresenta a Antena Hair e a tabela de serviços. |
| 2 | “Quero um alongameto” | Interpreta “alongameto” como “alongamento”, informa R$ 100,00 e pede nome e horário. |
| 3 | “Ana, sábado às 14h” | Resume o serviço, o valor e os dados enviados, avisando que o salão ainda precisa confirmar a disponibilidade. |

O código também aceita exemplos como “banh de gel” e “esmaltacao em gel”. Ele não confirma o horário automaticamente e não inventa preço.

## Serviços cadastrados

| Serviço | Preço | Observação |
|---|---:|---|
| Alongamento | R$ 100,00 | Cadastro entendido diretamente. |
| Manutenção | R$ 90,00 | Cadastro entendido diretamente. |
| Esmaltação em gel | R$ 70,00 | Cadastro entendido diretamente. |
| Habilidades | R$ 70,00 | Nome precisa ser confirmado. |
| Banho de gel | R$ 70,00 | Cadastro entendido diretamente. |
| Remoção | R$ 50,00 | Cadastro entendido diretamente. |
| Unhas tradicionais | R$ 30,00 | “Mutação tradicional” foi mantido como possível erro e precisa ser confirmado. |
| Cutilagem | R$ 20,00 | “Cut illa gen” foi interpretado como possível “cutilagem” e precisa ser confirmado. |

Os três nomes que precisam de confirmação foram marcados assim porque o cadastro original parece ter erros de transcrição. Antes de apresentar o trabalho, substitua esses nomes se a dona do salão confirmar outra descrição.

## Telegram ou WhatsApp?

As duas opções são viáveis, mas têm níveis diferentes de configuração:

| Canal | Vantagem | O que será necessário | Complexidade |
|---|---|---|---|
| Telegram | Mais simples para uma demonstração escolar; o bot pode receber atualizações por long polling e não exige uma conta comercial do salão. | Criar um bot no BotFather e copiar o token para `TELEGRAM_BOT_TOKEN`. | Baixa |
| WhatsApp Business Cloud API | Mais natural para clientes reais do salão e mais próximo de um atendimento profissional. | Criar uma aplicação na Meta, conectar uma conta WhatsApp Business, configurar token, permissões e um endereço HTTPS para webhook. | Média/alta |

A documentação oficial do Telegram informa que a Bot API permite receber atualizações por `getUpdates` ou por webhook [1]. A documentação oficial da Meta explica que a WhatsApp Cloud API envia mensagens e eventos por webhooks e exige uma aplicação Meta, uma conta WhatsApp Business e permissões apropriadas [2][3].

Para a apresentação do professor, o caminho com menos configuração é o Telegram. O código deste diretório já está preparado para ele. O prompt do Gemini também está incluído para demonstrar como o LLM pode ser conectado sem deixar o modelo inventar preços.

## Como executar no Telegram

Primeiro, instale Python 3.11 ou mais recente e execute:

```bash
cd antena-hair-bot
python -m venv .venv
source .venv/bin/activate       # no Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

No Telegram, converse com `@BotFather`, use `/newbot`, escolha um nome e copie o token. Depois, no terminal:

```bash
export TELEGRAM_BOT_TOKEN="COLE_SEU_TOKEN_AQUI"
python bot_telegram.py
```

Abra o nome do bot no Telegram e envie `/start`. Para interromper o programa, pressione `Ctrl+C`.

Não publique o token em um trabalho, GitHub ou print. Ele funciona como uma senha do bot.

## Ativar o Gemini, se o professor exigir LLM

O fluxo de serviços é propositalmente determinístico para proteger a tabela de preços. O Gemini fica como camada opcional para mensagens gerais que não foram reconhecidas. A integração usa o pacote oficial `google-genai` e o modelo padrão configurado no arquivo `gemini_client.py`.

Para ativar essa camada, crie uma chave na documentação do Gemini, instale a dependência e defina a variável de ambiente:

```bash
pip install google-genai
export GEMINI_API_KEY="SUA_CHAVE_DO_GEMINI"
export GEMINI_MODEL="gemini-3.8-flash"
python bot_telegram.py
```

O arquivo `prompt_gemini.txt` contém a instrução de sistema. Ele orienta o modelo a responder em português, compreender erros, não inventar preços e nunca prometer que um horário foi reservado. A API oficial mostra o uso de `genai.Client` e `client.interactions.create` para geração de texto [4].

## Testar sem Telegram e sem chave de API

O reconhecimento de erros e o fluxo podem ser testados localmente:

```bash
cd antena-hair-bot
python test_bot.py
python salon_logic.py
```

## Arquivos

| Arquivo | Função |
|---|---|
| `salon_logic.py` | Menu, preços, correção de acentos/erros e as três etapas do atendimento. |
| `bot_telegram.py` | Integração com o Telegram. |
| `gemini_client.py` | Integração opcional com Gemini. |
| `prompt_gemini.txt` | Prompt de sistema do LLM. |
| `test_bot.py` | Testes do fluxo e dos erros de digitação. |
| `requirements.txt` | Dependência do Telegram. |

## Referências

[1]: https://core.telegram.org/bots/api "Telegram Bot API"

[2]: https://developers.facebook.com/documentation/business-messaging/whatsapp/get-started "WhatsApp Cloud API Get Started"

[3]: https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/overview "WhatsApp Webhooks"

[4]: https://ai.google.dev/gemini-api/docs/text-generation "Gemini text generation"
