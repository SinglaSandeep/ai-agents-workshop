from app.agents import LocalOrchestrator


def test_orchestrator_routes_hr_question() -> None:
    result = LocalOrchestrator().answer("What is the PTO policy?")

    assert result.route == "hr"
    assert "paid time off" in result.answer.lower()


def test_orchestrator_routes_products_question() -> None:
    result = LocalOrchestrator().answer("How much is the fitness watch?")

    assert result.route == "products"
    assert "$149" in result.answer


def test_direct_marketing_agent() -> None:
    result = LocalOrchestrator().answer_with_agent("marketing", "What is the brand voice?")

    assert result.route == "marketing"
    assert "supportive" in result.answer.lower()
