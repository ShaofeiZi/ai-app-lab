def test_service_package_imports():
    from mobile_use_service.config.settings import get_settings

    settings = get_settings()
    assert settings.app_name
