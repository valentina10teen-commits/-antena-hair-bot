from salon_logic import SalonBot, find_service


def test_typo_is_understood():
    assert find_service("quero um alongameto") is not None
    assert find_service("banh de gel") is not None
    assert find_service("esmaltacao em gel") is not None


def test_three_interactions():
    bot = SalonBot()
    first = bot.respond(10, "oi")
    second = bot.respond(10, "quero um alongameto")
    third = bot.respond(10, "Ana, sábado às 14h")

    assert "Tabela de serviços" in first
    assert "Alongamento" in second
    assert "R$ 100,00" in second
    assert "Anotei seu pedido" in third
    assert "Ana, sábado às 14h" in third


def test_unknown_message_does_not_invent_service():
    bot = SalonBot()
    response = bot.respond(11, "quero uma coisa diferente")
    assert "Não consegui identificar" in response


if __name__ == "__main__":
    test_typo_is_understood()
    test_three_interactions()
    test_unknown_message_does_not_invent_service()
    print("Todos os testes passaram.")
