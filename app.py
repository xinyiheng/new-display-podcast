from flask import Flask, render_template, jsonify, request, send_from_directory, send_file
import os
import json
import requests
from datetime import datetime
import hashlib
import hmac
import urllib.parse
from pathlib import Path
import threading
import time

app = Flask(__name__, static_folder='public', template_folder='public')

# 配置 - 从环境变量读取，提供默认值
CONFIG = {
    # 主数据源 - 直接从GitHub Pages获取
    'DATA_SOURCE': os.environ.get('DATA_SOURCE', 'https://xinyiheng.github.io/newpody/podcast_index.json'),
    # 备用数据源 - 从GitHub Raw获取
    'BACKUP_DATA_SOURCE': os.environ.get('BACKUP_DATA_SOURCE', 'https://raw.githubusercontent.com/xinyiheng/newpody/gh-pages/podcast_index.json'),
    'BASE_URL': os.environ.get('BASE_URL', 'https://xinyiheng.github.io/newpody'),
    'CACHE_DURATION': 3600  # 1小时缓存
}

# 缓存变量
cache = {
    'data': None,
    'timestamp': 0
}

# 文件存储配置 - 使用持久化存储路径
FILE_STORAGE = {
    'base_dir': '/tmp/podcast_files',  # Zeabur持久化目录
    'audio_dir': '/tmp/podcast_files/audio',
    'transcript_dir': '/tmp/podcast_files/transcripts',
    'download_lock': threading.Lock(),
    'downloading_files': set()
}

# 环境变量配置
PERSISTENT_STORAGE = os.environ.get('PERSISTENT_STORAGE', '/tmp/podcast_files')
USE_PERSISTENT_STORAGE = os.environ.get('USE_PERSISTENT_STORAGE', 'true').lower() == 'true'


# 确保文件存储目录存在
def ensure_storage_directories():
    """确保文件存储目录存在"""
    if USE_PERSISTENT_STORAGE:
        # 使用持久化存储
        os.makedirs(FILE_STORAGE['audio_dir'], exist_ok=True)
        os.makedirs(FILE_STORAGE['transcript_dir'], exist_ok=True)
        print(f"📁 使用持久化存储: {PERSISTENT_STORAGE}")
    else:
        # 使用临时存储（用于测试）
        FILE_STORAGE['base_dir'] = 'static_files'
        FILE_STORAGE['audio_dir'] = 'static_files/audio'
        FILE_STORAGE['transcript_dir'] = 'static_files/transcripts'
        os.makedirs(FILE_STORAGE['audio_dir'], exist_ok=True)
        os.makedirs(FILE_STORAGE['transcript_dir'], exist_ok=True)
        print("📁 使用临时存储（测试模式）")

    # 确保静态文件目录存在
    os.makedirs('static', exist_ok=True)

# 在模块导入时确保目录就绪（以便 gunicorn 模式也能创建目录）
ensure_storage_directories()

def get_local_file_path(remote_path, file_type):
    """将远程路径转换为本地路径"""
    if not remote_path:
        return None

    # 解析远程路径
    parsed = urllib.parse.urlparse(remote_path)
    if parsed.path:
        # 从路径中提取文件名
        path_parts = parsed.path.split('/')
        filename = path_parts[-1] if path_parts[-1] else path_parts[-2]

        # 获取文件所在的目录名作为子目录
        dir_name = path_parts[-2] if len(path_parts) > 2 else ''

        if file_type == 'audio':
            return os.path.join(FILE_STORAGE['audio_dir'], dir_name, filename)
        elif file_type == 'transcript':
            return os.path.join(FILE_STORAGE['transcript_dir'], dir_name, filename)

    return None

def download_file_if_needed(remote_url, local_path, file_type):
    """如果需要，下载文件到本地"""
    if not remote_url or not local_path:
        return False

    # 如果文件已存在，直接返回
    if os.path.exists(local_path):
        return True

    # 防止重复下载
    file_key = f"{remote_url}:{local_path}"
    with FILE_STORAGE['download_lock']:
        if file_key in FILE_STORAGE['downloading_files']:
            return False
        FILE_STORAGE['downloading_files'].add(file_key)

    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        print(f"正在下载 {file_type} 文件: {remote_url}")

        # 下载文件
        response = requests.get(remote_url, timeout=30)
        if response.status_code == 200:
            with open(local_path, 'wb') as f:
                f.write(response.content)
            print(f"下载完成: {local_path}")
            return True
        else:
            print(f"下载失败: {response.status_code}")
            return False

    except Exception as e:
        print(f"下载出错 {remote_url}: {e}")
        return False
    finally:
        with FILE_STORAGE['download_lock']:
            FILE_STORAGE['downloading_files'].discard(file_key)

def get_storage_info():
    """获取存储空间信息"""
    try:
        import shutil

        if not os.path.exists(FILE_STORAGE['base_dir']):
            return {
                'total_space': 0,
                'used_space': 0,
                'free_space': 0,
                'usage_percent': 0
            }

        total, used, free = shutil.disk_usage(FILE_STORAGE['base_dir'])
        usage_percent = (used / total) * 100 if total > 0 else 0

        return {
            'total_space': total,
            'used_space': used,
            'free_space': free,
            'usage_percent': usage_percent
        }
    except Exception as e:
        print(f"获取存储信息失败: {e}")
        return None

def cleanup_old_files(max_age_days=30):
    """清理旧文件以释放空间"""
    try:
        import time
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        cleaned_files = []

        for root, dirs, files in os.walk(FILE_STORAGE['base_dir']):
            for file in files:
                file_path = os.path.join(root, file)
                file_age = current_time - os.path.getctime(file_path)

                if file_age > max_age_seconds:
                    os.remove(file_path)
                    cleaned_files.append(file_path)
                    print(f"已清理旧文件: {file_path}")

        # 清理空目录
        for root, dirs, files in os.walk(FILE_STORAGE['base_dir'], topdown=False):
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    print(f"已清理空目录: {dir_path}")

        return len(cleaned_files)
    except Exception as e:
        print(f"清理文件失败: {e}")
        return 0

def process_podcast_files(podcasts_data):
    """处理播客文件，确保所有文件都在本地"""
    processed_podcasts = []

    # 检查存储空间
    storage_info = get_storage_info()
    if storage_info and storage_info['usage_percent'] > 90:
        print(f"⚠️  存储空间使用率过高: {storage_info['usage_percent']:.1f}%")
        # 清理30天前的文件
        cleaned_count = cleanup_old_files(30)
        print(f"🧹 已清理 {cleaned_count} 个旧文件")

    for podcast in podcasts_data:
        processed_podcast = podcast.copy()

        # 处理音频文件
        if podcast.get('audio_path'):
            audio_url = f"{CONFIG['BASE_URL']}{podcast['audio_path'].replace('./', '/')}"
            local_audio_path = get_local_file_path(podcast['audio_path'], 'audio')

            # 异步下载音频文件
            def download_audio():
                download_file_if_needed(audio_url, local_audio_path, 'audio')

            thread = threading.Thread(target=download_audio)
            thread.daemon = True
            thread.start()

            if local_audio_path:
                processed_podcast['local_audio_path'] = f"/files/audio/{os.path.basename(os.path.dirname(local_audio_path))}/{os.path.basename(local_audio_path)}"

        # 处理文稿文件
        if podcast.get('transcript_path'):
            transcript_url = f"{CONFIG['BASE_URL']}{podcast['transcript_path'].replace('./', '/')}"
            local_transcript_path = get_local_file_path(podcast['transcript_path'], 'transcript')

            # 异步下载文稿文件
            def download_transcript():
                download_file_if_needed(transcript_url, local_transcript_path, 'transcript')

            thread = threading.Thread(target=download_transcript)
            thread.daemon = True
            thread.start()

            if local_transcript_path:
                processed_podcast['local_transcript_path'] = f"/files/transcripts/{os.path.basename(os.path.dirname(local_transcript_path))}/{os.path.basename(local_transcript_path)}"

        processed_podcasts.append(processed_podcast)

    return processed_podcasts

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
        
        # 处理播客文件 - 下载到本地
        processed_data = process_podcast_files(data.get('podcasts', []))

        # 更新缓存
        cache['data'] = {'podcasts': processed_data}
        cache['timestamp'] = current_time

        return jsonify({'podcasts': processed_data})
        
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
        return jsonify({
            'message': 'Webhook endpoint is working',
            'timestamp': datetime.now().isoformat(),
            'data_source': CONFIG['DATA_SOURCE'],
            'base_url': CONFIG['BASE_URL']
        })

    try:
        payload = request.get_json()
        event = request.headers.get('X-GitHub-Event', 'unknown')

        print(f"收到GitHub Webhook: {event}")

        # 验证Webhook签名（可选，增强安全性）
        signature = request.headers.get('X-Hub-Signature-256')
        webhook_secret = os.environ.get('GITHUB_WEBHOOK_SECRET')

        if webhook_secret and signature:
            # 验证签名
            expected_signature = 'sha256=' + hmac.new(
                webhook_secret.encode(),
                request.data,
                hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(signature, expected_signature):
                print("Webhook签名验证失败")
                return jsonify({'error': 'Invalid signature'}), 401

        # 清除缓存，强制重新获取数据
        cache['data'] = None
        cache['timestamp'] = 0

        response_data = {
            'success': True,
            'message': f'Webhook processed for event: {event}',
            'timestamp': datetime.now().isoformat(),
            'cache_cleared': True
        }

        # 检查是否有播客相关文件更新
        if event == 'push' and payload:
            commits = payload.get('commits', [])
            modified_files = []

            for commit in commits:
                modified_files.extend(commit.get('added', []))
                modified_files.extend(commit.get('modified', []))
                modified_files.extend(commit.get('removed', []))

            # 检查是否包含播客相关文件
            podcast_patterns = ['podcast', 'pody', '.json', '.mp3', '.html', 'gh-pages']
            podcast_files = [f for f in modified_files if any(pattern in f for pattern in podcast_patterns)]

            if podcast_files:
                response_data['podcast_files_updated'] = podcast_files
                print(f"检测到播客文件更新: {podcast_files}")

                # 尝试重新获取数据以验证更新
                try:
                    test_response = requests.get(CONFIG['DATA_SOURCE'], timeout=5)
                    if test_response.status_code == 200:
                        cache['data'] = test_response.json()
                        cache['timestamp'] = datetime.now().timestamp()
                        response_data['data_refreshed'] = True
                        print("数据已成功刷新")
                except Exception as refresh_error:
                    print(f"数据刷新失败: {refresh_error}")
                    response_data['data_refresh_error'] = str(refresh_error)

        response = jsonify(response_data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    except Exception as e:
        print(f"Webhook处理错误: {e}")
        error_response = jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        return error_response, 500

# 文件服务端点
@app.route('/files/audio/<path:filename>')
def serve_audio_file(filename):
    """提供本地音频文件"""
    return send_from_directory(FILE_STORAGE['audio_dir'], filename)

@app.route('/files/transcripts/<path:filename>')
def serve_transcript_file(filename):
    """提供本地文稿文件"""
    return send_from_directory(FILE_STORAGE['transcript_dir'], filename)

@app.route('/api/files/status')
def files_status():
    """获取文件下载状态"""
    try:
        audio_files = []
        transcript_files = []

        # 统计音频文件
        for root, dirs, files in os.walk(FILE_STORAGE['audio_dir']):
            for file in files:
                if file.endswith('.mp3'):
                    file_path = os.path.join(root, file)
                    audio_files.append({
                        'filename': file,
                        'path': os.path.relpath(file_path, FILE_STORAGE['audio_dir']),
                        'size': os.path.getsize(file_path)
                    })

        # 统计文稿文件
        for root, dirs, files in os.walk(FILE_STORAGE['transcript_dir']):
            for file in files:
                if file.endswith(('.html', '.txt')):
                    file_path = os.path.join(root, file)
                    transcript_files.append({
                        'filename': file,
                        'path': os.path.relpath(file_path, FILE_STORAGE['transcript_dir']),
                        'size': os.path.getsize(file_path)
                    })

        response_data = {
            'audio_files': len(audio_files),
            'transcript_files': len(transcript_files),
            'audio_details': audio_files[:5],  # 只返回前5个文件详情
            'transcript_details': transcript_files[:5],
            'total_size': sum(f['size'] for f in audio_files + transcript_files),
            'storage_mode': 'persistent' if USE_PERSISTENT_STORAGE else 'temporary',
            'storage_path': FILE_STORAGE['base_dir']
        }

        # 添加存储空间信息
        storage_info = get_storage_info()
        if storage_info:
            response_data['storage'] = {
                'total_space': storage_info['total_space'],
                'used_space': storage_info['used_space'],
                'free_space': storage_info['free_space'],
                'usage_percent': storage_info['usage_percent']
            }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/refresh')
def refresh_files():
    """手动刷新文件下载"""
    try:
        # 清除缓存
        cache['data'] = None
        cache['timestamp'] = 0

        # 重新获取数据并下载文件
        response = requests.get(CONFIG['DATA_SOURCE'], timeout=10)
        if response.status_code == 200:
            data = response.json()
            processed_data = process_podcast_files(data.get('podcasts', []))
            cache['data'] = {'podcasts': processed_data}
            cache['timestamp'] = datetime.now().timestamp()

            return jsonify({
                'success': True,
                'message': '文件刷新完成',
                'processed_podcasts': len(processed_data)
            })
        else:
            return jsonify({'error': '无法获取播客数据'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/cleanup', methods=['POST'])
def cleanup_files():
    """手动清理旧文件"""
    try:
        data = request.get_json() or {}
        max_age_days = data.get('max_age_days', 30)

        cleaned_count = cleanup_old_files(max_age_days)

        # 获取清理后的存储信息
        storage_info = get_storage_info()

        return jsonify({
            'success': True,
            'message': f'已清理 {cleaned_count} 个旧文件',
            'cleaned_files': cleaned_count,
            'storage_info': storage_info
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/storage')
def storage_info():
    """获取存储详细信息"""
    try:
        storage_data = get_storage_info()
        if not storage_data:
            return jsonify({'error': '无法获取存储信息'}), 500

        # 获取文件统计
        audio_count = 0
        transcript_count = 0
        total_size = 0

        for root, dirs, files in os.walk(FILE_STORAGE['base_dir']):
            for file in files:
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                total_size += file_size

                if file.endswith('.mp3'):
                    audio_count += 1
                elif file.endswith(('.html', '.txt')):
                    transcript_count += 1

        return jsonify({
            'storage': storage_data,
            'files': {
                'audio_count': audio_count,
                'transcript_count': transcript_count,
                'total_count': audio_count + transcript_count,
                'total_size': total_size
            },
            'configuration': {
                'persistent_storage': USE_PERSISTENT_STORAGE,
                'storage_path': PERSISTENT_STORAGE,
                'current_base_dir': FILE_STORAGE['base_dir']
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
    # 确保存储目录存在（本地启动时再次确保）
    ensure_storage_directories()

    port = int(os.environ.get('PORT', 8080))
    host = '0.0.0.0'

    # 检测运行环境
    env = os.environ.get('FLASK_ENV', 'development')

    print(f"🎧 播客展示应用启动")
    print(f"📡 监听地址: {host}:{port}")
    print(f"🌍 环境: {env}")
    print(f"🔗 数据源: {CONFIG['DATA_SOURCE']}")
    print(f"📁 文件存储目录: {FILE_STORAGE['base_dir']}")
    print(f"💾 持久化存储: {'启用' if USE_PERSISTENT_STORAGE else '禁用'}")

    # 生产环境使用 Flask 内置服务器仅用于本地调试（容器内通过 gunicorn 启动）
    if env == 'production':
        print("🔄 生产模式启动")
        app.run(host=host, port=port, debug=False)
    else:
        print("🔧 开发模式启动")
        app.run(host=host, port=port, debug=True)
