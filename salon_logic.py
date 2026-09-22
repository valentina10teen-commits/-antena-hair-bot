"""Lógica simples e tolerante a erros para o bot da Antenna Hair."""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Optional


@dataclass(frozen=True)
class Service:
    name: str
    price: int
    aliases: tuple[str, ...]
    needs_confirmation: bool = False


# Os dois itens marcados precisam ser confirmados com a dona do salão.
SERVICES: tuple[Service, ...] = (
    Service(
        "Alongamento",
        100,
        ("alongamento", "alongameto", "alongamento de unha", "extensao"),
    ),
    Service(
        "Manutenção",
        90,
        ("manutencao", "manutençao", "manutencao de unha", "manutenção"),
    ),
    Service(
        "Esmaltação em gel",
        70,
        ("esmaltacao em gel", "esmaltacao gel", "esmaltas em gel", "esmalte em gel"),
    ),
    Service(
        "Blindagem",
        70,
        ("blindagem", "blindajem", "habilidades", "blindagem de unha"),
    ),
    Service(
        "Banho de gel",
        70,
        ("banho de gel", "banh de gel", "banho gel"),
    ),
    Service(
        "Remoção",
        50,
        ("remocao", "remoçao", "remover alongamento", "tirar alongamento"),
    ),
    Service(
        "Unhas tradicionais",
        30,
        ("unhas tradicionais", "unha tradicional", "mutacao tradicional"),
    ),
    Service(
        "Cutilagem",
        20,
        ("cutilagem", "cutilla gen", "cutilla gem", "cuticula"),
    ),
)

def normalize(text: str) -> str:
    """Minúsculas, sem acentos e com pontuação simplificada."""
    text = text.lower().strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def menu_text() -> str:
    lines = ["💅 *Tabela de serviços – Antenna Hair*"]
    for service in SERVICES:
        suffix = " _(nome a confirmar)_" if service.needs_confirmation else ""
        lines.append(f"• {service.name}: *R$ {service.price},00*{suffix}")
    return "\n".join(lines)


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def find_service(text: str) -> Optional[Service]:
    """Encontra o serviço mesmo quando a cliente escreve com erro."""
    value = normalize(text)
    if not value:
        return None

    # Primeiro tenta achar o nome/alias inteiro dentro da frase.
    for service in SERVICES:
        for alias in service.aliases:
            if normalize(alias) in value:
                return service

    # Depois compara cada palavra digitada com as palavras dos aliases.
    words = value.split()
    best: tuple[float, Optional[Service]] = (0.0, None)
    for service in SERVICES:
        for alias in service.aliases:
            alias_words = normalize(alias).split()
            if len(alias_words) == 1:
                score = max((_similarity(word, alias_words[0]) for word in words), default=0)
            else:
                # Para nomes compostos, mede a melhor aproximação de cada palavra.
                scores = []
                for alias_word in alias_words:
                    scores.append(max((_similarity(word, alias_word) for word in words), default=0))
                score = sum(scores) / len(scores)
            if score > best[0]:
                best = (score, service)

    # 0,76 aceita erros comuns como "alongameto" sem confundir frases aleatórias.
    return best[1] if best[0] >= 0.76 else None


class SalonBot:
    """Fluxo de exatamente três interações principais."""

    def __init__(self) -> None:
        self.sessions: dict[int, dict[str, str]] = {}

    def reset(self, user_id: int) -> str:
        self.sessions[user_id] = {"step": "service"}
        return (
            "Olá! Eu sou a assistente virtual da *Antenna Hair* 💅\n\n"
            "Trabalho com serviços de unhas. Digite o serviço que você deseja.\n\n"
            + menu_text()
        )

    def respond(self, user_id: int, text: str) -> str:
        text = text.strip()
        normalized = normalize(text)
        session = self.sessions.setdefault(user_id, {"step": "service"})

        if normalized in {"/start", "oi", "ola", "menu", "precos", "preco"}:
            return self.reset(user_id)

        if normalized in {"/cancelar", "cancelar", "reiniciar", "comecar de novo"}:
            return self.reset(user_id)

        # Respostas para perguntas gerais sobre o salão.
        # Elas funcionam em qualquer momento da conversa.
        if (
            "fazem atendimento de unha" in normalized
            or "atendimento de unha" in normalized
            or "trabalham com unha" in normalized
            or "faz unha" in normalized
            or "servicos oferecem" in normalized
            or "servicos voces oferecem" in normalized
            or "quais servicos" in normalized
            or "quais tratamentos" in normalized
            or "o que voces fazem" in normalized
        ):
            return (
                "Sim! A Antenna Hair faz atendimento especializado em unhas 💅\n\n"
                + menu_text()
                + "\n\nPara escolher um serviço, escreva o nome dele. "
                "Por exemplo: *alongameto* ou *banho de gel*."
            )

        if (
            "nao entendi" in normalized
            or "nao compreendi" in normalized
            or "pode explicar" in normalized
            or "me explica" in normalized
            or "me mostre" in normalized
        ):
            return (
                "Claro! Vou mostrar novamente os serviços disponíveis:\n\n"
                + menu_text()
                + "\n\nVocê pode escrever o nome do serviço mesmo com algum erro de digitação."
            )


        if session["step"] == "service":
            service = find_service(text)
            if not service:
                return (
                    "Não consegui identificar o serviço. Tente escrever, por exemplo: "
                    "*alongameto*, *banho de gel* ou *esmaltacao em gel*.\n\n" + menu_text()
                )
            session.update({"step": "details", "service": service.name, "price": str(service.price)})
            note = "\n\nObservação: vou confirmar o nome desse serviço com o salão." if service.needs_confirmation else ""
            return (
                f"Perfeito! Você escolheu *{service.name}* por *R$ {service.price},00*.{note}\n\n"
                "Agora me diga seu *nome* e o *dia/horário* desejados."
            )

        if session["step"] == "details":
            session.update({"step": "done", "details": text})
            return (
                "Anotei seu pedido! ✅\n\n"
                f"• Serviço: *{session['service']}*\n"
                f"• Valor informado: *R$ {session['price']},00*\n"
                f"• Nome e horário: *{text}*\n\n"
                "A Antenna Hair precisa confirmar a disponibilidade antes de fechar o agendamento."
            )

        return (
            "Esse atendimento já foi anotado. Para fazer outro pedido, digite *menu* ou */start*."
        )


if __name__ == "__main__":
    bot = SalonBot()
    print(bot.reset(1))
    print("\n---")
    print(bot.respond(1, "quero um alongameto"))
    print("\n---")
    print(bot.respond(1, "Ana, sábado às 14h"))
