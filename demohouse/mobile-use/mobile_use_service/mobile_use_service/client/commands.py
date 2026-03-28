SCREENSHOT_COMMAND_TYPE = "root"
SHELL_COMMAND_TYPE = "shell"
SCREEN_SWIPE_TIME_MS = 300

# 这一组常量集中保存“兼容模式下要发给设备的底层命令”。
# 当新版 OpenAPI 没有某个高级动作封装，或者当前 client 选择走兼容分支时，
# service 会把这些命令透传给远端设备执行。

SELECT_INPUT_METHOD_COMMAND = (
    'settings put secure default_input_method "com.android.inputmethod.pinyin/.PinyinIME"'
)
CLEAR_INPUT_COMMAND = "am broadcast -a device.gameservice.keyevent.clear"
INPUT_TEXT_COMMAND = (
    'am broadcast -a device.gameservice.keyevent.value --es value "$(echo %s | base64 -d)"'
)
SCREEN_TAP_COMMAND = "input tap %d %d"
SCREEN_SWIPE_COMMAND = "input swipe %d %d %d %d %d"
SCREENSHOT_COMMAND = 'cap_tos -tos_conf "%s"'

ANDROID_KEY_EVENT_MAP = {
    # Android 系统按键都有固定 key code。
    # 这里统一维护映射，避免业务层到处写“魔法数字”。
    "back": 4,
    "home": 3,
    "menu": 82,
}
