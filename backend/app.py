import os
import time
import random
import uuid
import json
from datetime import datetime, time as dt_time
from flask import Flask, request, jsonify
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from models.models import db, Message, Task

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wechat_message_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

scheduler = BackgroundScheduler()

class WeChatSender:
    def __init__(self):
        self.wx = None
        self.min_interval = 3
        self.max_interval = 15
        self.daily_limit = 50
        self.today_sent = 0
        self.last_reset_date = datetime.now().date()
        self.active_hours = (dt_time(9, 0), dt_time(21, 0))
        self._com_initialized = False

    def _ensure_com(self):
        if not self._com_initialized:
            try:
                import pythoncom
                pythoncom.CoInitialize()
                self._com_initialized = True
            except Exception:
                pass

    def initialize(self):
        try:
            self._ensure_com()
            from wxauto_patched import WeChat
            self.wx = WeChat()
            return self.wx is not None
        except Exception as e:
            print(f'微信初始化失败: {e}')
            return False

    def is_active_time(self):
        now = datetime.now().time()
        return self.active_hours[0] <= now <= self.active_hours[1]

    def check_rate_limit(self):
        today = datetime.now().date()
        if today != self.last_reset_date:
            self.today_sent = 0
            self.last_reset_date = today
        return self.is_active_time() and self.today_sent < self.daily_limit

    def send(self, receiver, content):
        if not self.check_rate_limit():
            return False, '超出发送限制或不在活跃时间段'

        self._ensure_com()

        try:
            if self.wx is None:
                from wxauto_patched import WeChat
                self.wx = WeChat()
                print('微信初始化成功')
            
            # 搜索并发送消息
            print(f'正在搜索接收人: {receiver}')
            
            # 先尝试从会话列表中查找
            try:
                sessions = self.wx.GetSessionList()
                print(f'找到 {len(sessions)} 个会话')
                
                # 查找匹配的会话
                for session in sessions:
                    if receiver in session:
                        print(f'找到匹配的会话: {session}')
                        # 直接使用会话名称打开
                        result = self.wx.ChatWith(session)
                        if result:
                            print(f'成功打开对话窗口')
                            break
                else:
                    # 如果没有找到，尝试直接搜索
                    print(f'会话列表中未找到，尝试直接搜索')
                    result = self.wx.ChatWith(receiver)
                    if not result:
                        raise Exception('未找到接收人')
                    print(f'直接搜索成功')
            except Exception as e:
                print(f'搜索失败: {e}')
                return False, f'未找到接收人: {receiver}'
            
            time.sleep(random.uniform(1, 2))
            self.wx.SendMsg(content, clear=True)
            print(f'消息发送成功')
            time.sleep(random.uniform(1, 2))
            self.today_sent += 1
            return True, None
        except Exception as e:
            print(f'发送失败: {str(e)}')
            return False, str(e)

sender = WeChatSender()

def init_db():
    with app.app_context():
        db.create_all()

def validate_input(data, required_fields):
    errors = []
    for field in required_fields:
        if not data.get(field):
            errors.append(f'{field} 不能为空')
        elif isinstance(data.get(field), str) and len(data[field]) > 5000:
            errors.append(f'{field} 超过最大长度限制')
    return errors

def run_scheduler():
    with app.app_context():
        tasks = Task.query.filter_by(enabled=True).all()
        for task in tasks:
            add_cron_job(task)

def add_cron_job(task):
    job_id = f'task_{task.id}'
    
    # 先移除可能存在的旧任务
    try:
        scheduler.remove_job(job_id)
        print(f'已移除旧任务 {job_id}')
    except Exception:
        pass
    
    def job():
        print(f'执行任务 {task.id}: 发送消息给 {task.receiver}')
        content = task.content
        if content == '测试':
            from datetime import datetime
            content = f"测试 {datetime.now().strftime('%H:%M:%S')}"
        send_message_task(task.receiver, content)

    print(f'开始添加任务 {task.id} 到调度器...')
    print(f'任务信息: id={task.id}, cron={task.cron}, enabled={task.enabled}')
    
    try:
        parts = task.cron.split(' ')
        print(f'解析cron表达式: {parts}')
        
        if len(parts) != 6:
            print(f'无效的cron表达式: {task.cron}，长度应为6，实际为{len(parts)}')
            return
        
        # 验证每个部分是否为有效数字、通配符或间隔格式(*/n)
        for i, part in enumerate(parts):
            if part == '*':
                continue
            if '/' in part:
                continue
            if ',' in part:
                continue
            if part.isdigit():
                continue
            print(f'cron表达式第{i+1}部分无效: {part}')
            return
        
        trigger = CronTrigger(
            second=parts[0],
            minute=parts[1],
            hour=parts[2],
            day=parts[3],
            month=parts[4],
            day_of_week=parts[5]
        )
        print(f'创建CronTrigger成功')
        
        scheduler.add_job(job, trigger, id=job_id)
        print(f'任务 {task.id} 已成功添加到调度器，cron表达式: {task.cron}')
    except Exception as e:
        print(f'添加任务到调度器失败: {str(e)}')
        import traceback
        traceback.print_exc()

def send_message_task(receiver, content):
    with app.app_context():
        message = Message(
            receiver=receiver,
            content=content,
            status='pending',
            task_id=f'task_{uuid.uuid4().hex[:12]}'
        )
        db.session.add(message)
        db.session.commit()

        success, error = sender.send(receiver, content)
        message.status = 'success' if success else 'failed'
        message.error = error
        db.session.commit()

@app.route('/api/messages', methods=['POST'])
def send_message():
    data = request.json
    receiver = data.get('receiver')
    content = data.get('content')

    errors = validate_input(data, ['receiver', 'content'])
    if errors:
        return jsonify({'errors': errors}), 400

    message = Message(
        receiver=receiver,
        content=content,
        status='pending',
        task_id=f'msg_{uuid.uuid4().hex[:12]}'
    )
    db.session.add(message)
    db.session.commit()

    success, error = sender.send(receiver, content)
    message.status = 'success' if success else 'failed'
    message.error = error
    db.session.commit()

    return jsonify({
        'id': message.id,
        'status': message.status,
        'error': error
    })

@app.route('/api/messages', methods=['GET'])
def get_messages():
    messages = Message.query.order_by(Message.created_at.desc()).limit(100).all()
    return jsonify([{
        'id': m.id,
        'receiver': m.receiver,
        'content': m.content,
        'status': m.status,
        'error': m.error,
        'created_at': m.created_at.isoformat()
    } for m in messages])

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.json

    errors = validate_input(data, ['name', 'receiver', 'content', 'cron'])
    if errors:
        return jsonify({'errors': errors}), 400

    task = Task(
        name=data.get('name'),
        receiver=data.get('receiver'),
        content=data.get('content'),
        cron=data.get('cron'),
        enabled=data.get('enabled', True)
    )
    db.session.add(task)
    db.session.commit()

    if task.enabled:
        add_cron_job(task)

    return jsonify({
        'id': task.id,
        'name': task.name,
        'receiver': task.receiver,
        'content': task.content,
        'cron': task.cron,
        'enabled': task.enabled
    })

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return jsonify([{
        'id': t.id,
        'name': t.name,
        'receiver': t.receiver,
        'content': t.content,
        'cron': t.cron,
        'enabled': t.enabled,
        'created_at': t.created_at.isoformat()
    } for t in tasks])

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    print(f'开始更新任务 {task_id}...')
    task = Task.query.get(task_id)
    if not task:
        print(f'任务 {task_id} 不存在')
        return jsonify({'error': 'Task not found'}), 404

    data = request.json
    print(f'更新前的任务信息: id={task.id}, cron={task.cron}, enabled={task.enabled}')
    print(f'更新数据: {data}')
    
    task.name = data.get('name', task.name)
    task.receiver = data.get('receiver', task.receiver)
    task.content = data.get('content', task.content)
    task.cron = data.get('cron', task.cron)
    task.enabled = data.get('enabled', task.enabled)
    db.session.commit()
    
    print(f'更新后的任务信息: id={task.id}, cron={task.cron}, enabled={task.enabled}')

    try:
        scheduler.remove_job(f'task_{task_id}')
        print(f'已从调度器中移除旧任务 {task_id}')
    except Exception as e:
        # 任务可能不存在于调度器中，忽略错误
        print(f'移除旧任务失败: {str(e)}')
        pass
    
    if task.enabled:
        print(f'添加更新后的任务 {task_id} 到调度器...')
        add_cron_job(task)
    else:
        print(f'任务 {task_id} 已禁用，不添加到调度器')

    return jsonify({
        'id': task.id,
        'name': task.name,
        'receiver': task.receiver,
        'content': task.content,
        'cron': task.cron,
        'enabled': task.enabled
    })

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    try:
        scheduler.remove_job(f'task_{task_id}')
    except Exception:
        # 任务可能不存在于调度器中，忽略错误
        pass
    db.session.delete(task)
    db.session.commit()

    return jsonify({'success': True})

@app.route('/api/messages/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    message = Message.query.get(message_id)
    if not message:
        return jsonify({'error': 'Message not found'}), 404
    
    db.session.delete(message)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/status', methods=['GET'])
def get_status():
    wx_connected = False
    try:
        if sender.wx and sender.wx.UiaAPI:
            try:
                title = sender.wx.UiaAPI.WindowText
                wx_connected = title and '微信' in title
            except Exception:
                wx_connected = False
    except Exception as e:
        print(f'状态检测错误: {e}')

    return jsonify({
        'wx_connected': wx_connected,
        'today_sent': sender.today_sent,
        'daily_limit': sender.daily_limit,
        'is_active_time': sender.is_active_time()
    })

@app.route('/api/status/init', methods=['POST'])
def init_wechat():
    success = sender.initialize()
    return jsonify({'success': success})

@app.route('/api/test-send', methods=['POST'])
def test_send():
    data = request.json
    receiver = data.get('receiver', os.environ.get('WECHAT_TEST_RECEIVER', '文件传输助手'))
    now = datetime.now()
    content = data.get('content', f"手动测试消息 - {now.strftime('%Y-%m-%d %H:%M:%S')}")

    success, error = sender.send(receiver, content)
    return jsonify({
        'success': success,
        'receiver': receiver,
        'content': content,
        'error': error,
        'timestamp': now.isoformat()
    })

def run_periodic_test():
    def test_job():
        test_receiver = 'wxz'
        test_content = '测试'
        print(f"[定时测试] 发送给 {test_receiver}: {test_content}")
        
        with app.app_context():
            message = Message(
                receiver=test_receiver,
                content=test_content,
                status='pending',
                task_id=f'periodic_{uuid.uuid4().hex[:8]}'
            )
            db.session.add(message)
            db.session.commit()
            
            success, error = sender.send(test_receiver, test_content)
            message.status = 'success' if success else 'failed'
            message.error = error
            db.session.commit()
        
        if success:
            print(f"[定时测试] 发送成功")
        else:
            print(f"[定时测试] 发送失败: {error}")

    scheduler.add_job(test_job, 'interval', minutes=3, id='periodic_test')
    print('已添加定时测试任务（每3分钟，发送人：wxz，内容：测试）')

@app.errorhandler(Exception)
def handle_error(error):
    import traceback
    print(f'服务器错误: {str(error)}')
    traceback.print_exc()
    return jsonify({'error': str(error), 'type': type(error).__name__}), 500

if __name__ == '__main__':
    init_db()
    sender.initialize()
    scheduler.start()
    run_scheduler()
    run_periodic_test()
    app.run(host='0.0.0.0', port=5000, debug=True)