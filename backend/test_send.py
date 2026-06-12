import pythoncom
import time
from datetime import datetime
from wxauto_patched import WeChat

def test_send_with_current_time():
    pythoncom.CoInitialize()

    wx = WeChat()
    current_time = datetime.now()

    test_messages = [
        f"中文测试消息 - {current_time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"English Test - {current_time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"混合测试 中文+English 123 - {current_time.strftime('%H:%M:%S')}",
        "这是一条包含特殊字符的测试消息！@#$%^&*()",
        f"时间戳测试: {current_time.timestamp()}",
    ]

    print(f"当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    print("开始测试消息发送...")
    print("=" * 50)

    for i, msg in enumerate(test_messages, 1):
        print(f"\n测试 {i}/{len(test_messages)}: {msg}")
        try:
            wx.SendMsg(msg)
            print(f"✓ 消息发送完成")
            time.sleep(2)
        except Exception as e:
            print(f"✗ 发送失败: {e}")

    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)

if __name__ == '__main__':
    test_send_with_current_time()