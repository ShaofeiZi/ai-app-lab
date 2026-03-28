from mobile_agent.agent.skills.registry import SkillRegistry


def test_registry_contains_core_mobile_skills():
    registry = SkillRegistry()
    skills = registry.list_all()
    names = {skill.name for skill in skills}
    assert "mobile:tap" in names
    assert "mobile:take_screenshot" in names
    assert "mobile:swipe" in names
    assert "mobile:text_input" in names
    assert "mobile:launch_app" in names
    assert "mobile:close_app" in names
    assert "mobile:list_apps" in names
    assert "mobile:back" in names
    assert "mobile:home" in names
    assert "mobile:menu" in names
