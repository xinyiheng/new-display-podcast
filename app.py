from flask import Flask, render_template, jsonify, request, send_from_directory
import os
import json
import requests
from datetime import datetime
import hashlib
import hmac

app = Flask(__name__, static_folder='public', template_folder='public')

# 配置 - 从环境变量读取，提供默认值
CONFIG = {
    'DATA_SOURCE': os.environ.get('DATA_SOURCE', 'https://xinyiheng.github.io/newpody/podcast_index.json'),
    'BACKUP_DATA_SOURCE': os.environ.get('BACKUP_DATA_SOURCE', 'https://raw.githubusercontent.com/xinyiheng/newpody/gh-pages/podcast_index.json'),
    'BASE_URL': os.environ.get('BASE_URL', 'https://xinyiheng.github.io/newpody'),
    'CACHE_DURATION': 3600  # 1小时缓存
}

# 缓存变量
cache = {
    'data': None,
    'timestamp': 0
}

@app.route('/')
def index():
    """首页"""
    return send_from_directory('public', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    """静态文件服务"""
    return send_from_directory('public', filename)

@app.route('/api/podcasts')
def get_podcasts():
    """获取播客数据API"""
    try:
        # 检查缓存
        current_time = datetime.now().timestamp()
        if (cache['data'] is not None and 
            current_time - cache['timestamp'] < CONFIG['CACHE_DURATION']):
            return jsonify(cache['data'])
        
        # 尝试获取数据
        data = None
        
        # 首先尝试主数据源
        try:
            response = requests.get(CONFIG['DATA_SOURCE'], timeout=10)
            if response.status_code == 200:
                data = response.json()
        except Exception as e:
            print(f"主数据源失败: {e}")
        
        # 如果主数据源失败，尝试备用数据源
        if data is None:
            try:
                response = requests.get(CONFIG['BACKUP_DATA_SOURCE'], timeout=10)
                if response.status_code == 200:
                    data = response.json()
            except Exception as e:
                print(f"备用数据源失败: {e}")
        
        if data is None:
            return jsonify({'error': '无法获取播客数据'}), 500
        
        # 更新缓存
        cache['data'] = data
        cache['timestamp'] = current_time
        
        return jsonify(data)
        
    except Exception as e:
        print(f"获取播客数据失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/webhook', methods=['POST', 'GET', 'OPTIONS'])
def webhook():
    """GitHub Webhook处理"""
    
    # 处理CORS
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,X-Hub-Signature-256')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
    
    if request.method == 'GET':
        return jsonify({'message': 'Webhook endpoint is working', 'timestamp': datetime.now().isoformat()})
    
    try:
        payload = request.get_json()
        event = request.headers.get('X-GitHub-Event', 'unknown')
        
        print(f"收到GitHub Webhook: {event}")
        print(f"Payload: {payload}")
        
        # 清除缓存，强制重新获取数据
        cache['data'] = None
        cache['timestamp'] = 0
        
        response_data = {
            'success': True,
            'message': f'Webhook processed for event: {event}',
            'timestamp': datetime.now().isoformat()
        }
        
        # 检查是否有播客相关文件更新
        if event == 'push' and payload:
            commits = payload.get('commits', [])
            modified_files = []
            
            for commit in commits:
                modified_files.extend(commit.get('added', []))
                modified_files.extend(commit.get('modified', []))
                modified_files.extend(commit.get('removed', []))
            
            podcast_files = [f for f in modified_files if 
                           'podcast' in f or 'web/public' in f or 
                           f.endswith('.json') or f.endswith('.mp3') or f.endswith('.html')]
            
            if podcast_files:
                response_data['podcast_files_updated'] = podcast_files
                print(f"检测到播客文件更新: {podcast_files}")
        
        response = jsonify(response_data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        print(f"Webhook处理错误: {e}")
        error_response = jsonify({'error': str(e), 'timestamp': datetime.now().isoformat()})
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        return error_response, 500

@app.route('/api/status')
def status():
    """服务状态检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'cache_status': 'active' if cache['data'] is not None else 'empty',
        'config': {
            'data_source': CONFIG['DATA_SOURCE'],
            'base_url': CONFIG['BASE_URL']
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    host = '0.0.0.0'
    
    print(f"🎧 播客展示应用启动")
    print(f"📡 监听地址: {host}:{port}")
    print(f"🔗 数据源: {CONFIG['DATA_SOURCE']}")
    
    app.run(host=host, port=port, debug=False)
