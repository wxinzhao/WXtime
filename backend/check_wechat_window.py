import win32gui
import win32con

def enum_windows_callback(hwnd, results):
    if win32gui.IsWindowVisible(hwnd):
        window_text = win32gui.GetWindowText(hwnd)
        class_name = win32gui.GetClassName(hwnd)
        if '微信' in window_text or 'WeChat' in window_text:
            results.append((hwnd, window_text, class_name))

# 枚举所有可见窗口
windows = []
win32gui.EnumWindows(enum_windows_callback, windows)

print('找到的微信窗口：')
for hwnd, text, class_name in windows:
    print(f'窗口标题: {text}')
    print(f'窗口类名: {class_name}')
    print(f'窗口句柄: {hwnd}')
    print('---')

# 尝试使用不同的类名查找微信窗口
try:
    # 尝试原始类名
    hwnd = win32gui.FindWindow('WeChatMainWndForPC', None)
    if hwnd:
        print(f'使用 WeChatMainWndForPC 找到窗口: {hwnd}')
    else:
        print('未找到 WeChatMainWndForPC 窗口')
except Exception as e:
    print(f'查找 WeChatMainWndForPC 出错: {e}')

try:
    # 尝试新的类名
    hwnd = win32gui.FindWindow('WeChatAppEx', None)
    if hwnd:
        print(f'使用 WeChatAppEx 找到窗口: {hwnd}')
    else:
        print('未找到 WeChatAppEx 窗口')
except Exception as e:
    print(f'查找 WeChatAppEx 出错: {e}')