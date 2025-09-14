// 配置
const CONFIG = {
    // 使用本站的API端点获取数据
    DATA_SOURCE: '/api/podcasts',
    // 播客文件基础URL
    BASE_URL: 'https://xinyiheng.github.io/newpody',
    // 每页显示的播客数量
    EPISODES_PER_PAGE: 6
};

// 全局变量
let allEpisodes = [];
let displayedEpisodes = [];
let currentPage = 0;

// DOM 元素
const elements = {
    latestEpisode: document.getElementById('latest-episode'),
    episodesContainer: document.getElementById('episodes-container'),
    searchInput: document.getElementById('search-input'),
    dateFilter: document.getElementById('date-filter'),
    loadMoreBtn: document.getElementById('load-more-btn'),
    totalEpisodes: document.getElementById('total-episodes'),
    totalDuration: document.getElementById('total-duration'),
    lastUpdate: document.getElementById('last-update'),
    autoUpdateTime: document.getElementById('auto-update-time')
};

// 初始化应用
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🎧 播客展示应用启动');
    
    // 显示加载状态
    showLoading();
    
    try {
        // 加载播客数据
        await loadPodcastData();
        
        // 渲染最新播客
        renderLatestEpisode();
        
        // 渲染播客列表
        renderEpisodesList();
        
        // 更新统计信息
        updateStats();
        
        // 绑定事件监听器
        bindEventListeners();
        
        console.log('✅ 应用初始化完成');
        
    } catch (error) {
        console.error('❌ 应用初始化失败:', error);
        showError('加载播客数据失败，请稍后重试');
    }
});

// 加载播客数据
async function loadPodcastData() {
    try {
        console.log('📡 正在加载播客数据...');
        
        const response = await fetch(CONFIG.DATA_SOURCE);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // 检查是否有错误
        if (data.error) {
            throw new Error(data.error);
        }
        
        allEpisodes = data.podcasts || [];
        
        console.log(`📚 成功加载 ${allEpisodes.length} 个播客`);
        
        // 按日期排序 (最新的在前)
        allEpisodes.sort((a, b) => new Date(b.date) - new Date(a.date));
        
    } catch (error) {
        console.error('❌ 加载播客数据失败:', error);
        throw error;
    }
}

// 渲染最新播客
function renderLatestEpisode() {
    if (allEpisodes.length === 0) {
        elements.latestEpisode.innerHTML = '<p>暂无播客内容</p>';
        return;
    }
    
    const latest = allEpisodes[0];
    const audioUrl = latest.audio_path ? `${CONFIG.BASE_URL}${latest.audio_path}` : '';
    const transcriptUrl = latest.transcript_path ? `${CONFIG.BASE_URL}${latest.transcript_path}` : '';
    
    elements.latestEpisode.innerHTML = `
        <div class="episode-info">
            <h3 class="episode-title">${latest.title}</h3>
            <p class="episode-date">📅 ${formatDate(latest.date)}</p>
            <p class="episode-description">${latest.highlight || '探索出版行业的最新动态，聆听行业专家的深度解析'}</p>
        </div>
        <div class="episode-controls">
            ${audioUrl ? `
                <audio controls class="audio-player">
                    <source src="${audioUrl}" type="audio/mpeg">
                    您的浏览器不支持音频播放。
                </audio>
            ` : '<p>音频文件暂不可用</p>'}
            <div class="episode-actions">
                ${transcriptUrl ? `<a href="${transcriptUrl}" class="btn btn-primary transcript-btn" target="_blank">📄 查看文稿</a>` : ''}
                ${audioUrl ? `<a href="${audioUrl}" class="btn btn-secondary download-btn" download>⬇️ 下载音频</a>` : ''}
            </div>
        </div>
    `;
}

// 渲染播客列表
function renderEpisodesList() {
    const filteredEpisodes = filterEpisodes();
    displayedEpisodes = filteredEpisodes.slice(0, (currentPage + 1) * CONFIG.EPISODES_PER_PAGE);
    
    if (displayedEpisodes.length === 0) {
        elements.episodesContainer.innerHTML = '<div class="loading"><p>没有找到匹配的播客</p></div>';
        elements.loadMoreBtn.style.display = 'none';
        return;
    }
    
    const episodesHTML = displayedEpisodes.slice(1).map(episode => createEpisodeCard(episode)).join('');
    elements.episodesContainer.innerHTML = episodesHTML;
    
    // 控制"加载更多"按钮显示
    elements.loadMoreBtn.style.display = 
        displayedEpisodes.length < filteredEpisodes.length ? 'block' : 'none';
}

// 创建播客卡片
function createEpisodeCard(episode) {
    const audioUrl = episode.audio_path ? `${CONFIG.BASE_URL}${episode.audio_path}` : '';
    const transcriptUrl = episode.transcript_path ? `${CONFIG.BASE_URL}${episode.transcript_path}` : '';
    
    return `
        <div class="episode-item" data-episode-id="${episode.id}">
            <h3 class="episode-title">${episode.title}</h3>
            <p class="episode-date">📅 ${formatDate(episode.date)}</p>
            <p class="episode-description">${episode.highlight || '探索出版行业的最新动态'}</p>
            <div class="episode-actions">
                ${audioUrl ? `
                    <audio controls style="width: 100%; margin-bottom: 0.5rem;">
                        <source src="${audioUrl}" type="audio/mpeg">
                    </audio>
                ` : ''}
                <div style="display: flex; gap: 0.5rem;">
                    ${transcriptUrl ? `<a href="${transcriptUrl}" class="btn btn-primary" target="_blank">📄 文稿</a>` : ''}
                    ${audioUrl ? `<a href="${audioUrl}" class="btn btn-secondary" download>⬇️ 下载</a>` : ''}
                </div>
            </div>
        </div>
    `;
}

// 过滤播客
function filterEpisodes() {
    let filtered = [...allEpisodes];
    
    // 搜索过滤
    const searchTerm = elements.searchInput.value.toLowerCase().trim();
    if (searchTerm) {
        filtered = filtered.filter(episode =>
            episode.title.toLowerCase().includes(searchTerm) ||
            (episode.highlight && episode.highlight.toLowerCase().includes(searchTerm))
        );
    }
    
    // 日期过滤
    const dateFilter = elements.dateFilter.value;
    if (dateFilter) {
        const daysAgo = parseInt(dateFilter);
        const cutoffDate = new Date();
        cutoffDate.setDate(cutoffDate.getDate() - daysAgo);
        
        filtered = filtered.filter(episode => new Date(episode.date) >= cutoffDate);
    }
    
    return filtered;
}

// 绑定事件监听器
function bindEventListeners() {
    // 搜索输入
    elements.searchInput.addEventListener('input', debounce(() => {
        currentPage = 0;
        renderEpisodesList();
    }, 300));
    
    // 日期过滤
    elements.dateFilter.addEventListener('change', () => {
        currentPage = 0;
        renderEpisodesList();
    });
    
    // 加载更多
    elements.loadMoreBtn.addEventListener('click', () => {
        currentPage++;
        renderEpisodesList();
    });
    
    // 平滑滚动
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
}

// 更新统计信息
function updateStats() {
    elements.totalEpisodes.textContent = allEpisodes.length;
    
    // 估算总时长 (假设每个播客15分钟)
    const estimatedMinutes = allEpisodes.length * 15;
    const hours = Math.floor(estimatedMinutes / 60);
    const minutes = estimatedMinutes % 60;
    elements.totalDuration.textContent = `${hours}h ${minutes}m`;
    
    // 最后更新时间
    if (allEpisodes.length > 0) {
        elements.lastUpdate.textContent = formatDate(allEpisodes[0].date);
    }
    
    // 自动更新时间
    elements.autoUpdateTime.textContent = new Date().toLocaleString('zh-CN');
}

// 工具函数
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showLoading() {
    elements.episodesContainer.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>正在加载播客列表...</p>
        </div>
    `;
}

function showError(message) {
    elements.episodesContainer.innerHTML = `
        <div class="loading">
            <p style="color: #e53e3e;">❌ ${message}</p>
            <button onclick="location.reload()" class="btn btn-primary" style="margin-top: 1rem;">重新加载</button>
        </div>
    `;
}

// 自动刷新功能 (每30分钟检查一次更新)
setInterval(async () => {
    try {
        console.log('🔄 检查播客更新...');
        const oldCount = allEpisodes.length;
        await loadPodcastData();
        
        if (allEpisodes.length > oldCount) {
            console.log('🆕 发现新播客，自动刷新页面');
            location.reload();
        }
    } catch (error) {
        console.log('⚠️ 自动更新检查失败:', error);
    }
}, 30 * 60 * 1000); // 30分钟

// 键盘快捷键
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + F 快速搜索
    if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault();
        elements.searchInput.focus();
    }
    
    // ESC 清空搜索
    if (e.key === 'Escape') {
        elements.searchInput.value = '';
        elements.searchInput.dispatchEvent(new Event('input'));
    }
});

console.log('🎧 出版电台播客展示应用已加载');
