from mobile_agent.agent.skills.policy import SkillPolicyResolver
from mobile_agent.agent.skills.registry import SkillRegistry


def test_policy_can_filter_by_allowlist():
    resolver = SkillPolicyResolver(allowlist={"mobile:tap"})
    skills = SkillRegistry().list_all()
    filtered = resolver.filter(skills, context={})
    assert [skill.name for skill in filtered] == ["mobile:tap"]
