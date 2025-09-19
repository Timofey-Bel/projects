// Всё просто и быстро
const form = document.getElementById('analyzeForm');
const textInput = document.getElementById('commentText');
const button = document.getElementById('analyzeBtn');
const loading = document.getElementById('loading');
const error = document.getElementById('error');
const results = document.getElementById('results');

let lastData = null;

// Когда жмут кнопку - ОБЯЗАТЕЛЬНО предотвращаем перезагрузку
form.onsubmit = async (e) => {
    e.preventDefault(); // ← ЭТО САМОЕ ВАЖНОЕ!
    
    const text = textInput.value.trim();
    if (!text) {
        error.textContent = 'Напишите что-нибудь';
        error.style.display = 'block';
        return;
    }
    
    // Показываем загрузку
    button.disabled = true;
    loading.style.display = 'block';
    error.style.display = 'none';
    results.style.display = 'none';
    
    try {
        // Шлём запрос
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text, language: 'ru'})
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Показываем результат
            showResult(data);
            document.getElementById('processingTime').textContent = data.processing_time;
            results.style.display = 'block';
        } else {
            throw new Error(data.error);
        }
        
    } catch (err) {
        error.textContent = 'Ошибка: ' + err.message;
        error.style.display = 'block';
    } finally {
        button.disabled = false;
        loading.style.display = 'none';
    }
};

// Показываем что получилось
function showResult(data) {
    lastData = data.data;
    
    // Категории
    document.getElementById('categories').innerHTML = `
        <p><b>Тема:</b> ${data.data.categories?.theme || '?'}</p>
        <p><b>Настрой:</b> ${data.data.categories?.sentiment || '?'}</p>
        <p><b>Срочно:</b> ${data.data.categories?.urgency || '?'}</p>
        <p><b>Проблемы:</b> ${data.data.categories?.has_violation ? 'Да' : 'Нет'}</p>
    `;
    
    // Метки
    const labelsDiv = document.getElementById('labels');
    if (data.data.labels?.length) {
        labelsDiv.innerHTML = data.data.labels.map(label => 
            `<span class="label">${label}</span>`
        ).join(' ');
    } else {
        labelsDiv.innerHTML = '<p>Нет меток</p>';
    }
    
    // Анализ
    const analysisDiv = document.getElementById('analysis');
    analysisDiv.innerHTML = `
        <p><b>Анализ:</b> ${data.data.analysis?.summary || 'Нет'}</p>
        ${data.data.analysis?.key_points ? `
            <p><b>Основное:</b></p>
            <ul>${data.data.analysis.key_points.map(p => `<li>${p}</li>`).join('')}</ul>
        ` : ''}
    `;
    
    // Модерация
    document.getElementById('moderation').innerHTML = `
        <p><b>Токсично:</b> ${data.data.moderation?.is_toxic ? 'Да' : 'Нет'}</p>
        <p><b>Спам:</b> ${data.data.moderation?.is_spam ? 'Да' : 'Нет'}</p>
        <p><b>Проверить:</b> ${data.data.moderation?.needs_review ? 'Да' : 'Нет'}</p>
    `;
}

// Копирование JSON
document.getElementById('copyJsonBtn').onclick = () => {
    if (!lastData) {
        alert('Сначала анализируй');
        return;
    }
    
    const text = JSON.stringify(lastData, null, 2);
    navigator.clipboard.writeText(text).then(() => {
        alert('Скопировано!');
    }).catch(() => {
        // Простой способ если не работает
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        alert('Скопировано вручную');
    });
};

// Готово
console.log('Всё работает!');