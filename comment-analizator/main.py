from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import time
import re


app = FastAPI()

# Разрешаем все запросы
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

# Модели для запросов
class CommentRequest(BaseModel):
    text: str
    language: str = "ru"

# База данных в памяти
all_analyses = []

# Функция для проверки слов с ошибками
def find_similar_word(word, word_list):
    for correct_word in word_list:
        # Простая проверка на похожесть слов
        if word in correct_word or correct_word in word:
            return correct_word
        # Проверка на common опечатки
        if len(word) > 3 and len(correct_word) > 3:
            if word[:-1] == correct_word[:-1] or word[1:] == correct_word[1:]:
                return correct_word
    return None

# Анализируем текст
def analyze_text(text: str):
    text_lower = text.lower()
    
    # Списки слов с вариациями и ошибками
    good_words = ['спасибо', 'спс', 'спасиб', 'отлично', 'отл', 'супер', 'суппер', 'хорошо', 'хоршо', 'рекомендую', 'рекоммендую', 'нравится', 'нравиться', 'нраится', 'люблю', 'люблу', 'прекрасно', 'прекрасно', 'замечательно']
    bad_words = ['плохо', 'плохо', 'плоха', 'ужасно', 'ужасна', 'кошмар', 'кошмарно', 'разочарован', 'разочарована', 'негодую', 'негодуйте', 'не нравится', 'не нравиться', 'ненавижу', 'ненавижу', 'отвратительно', 'отвратительна']
    
    # Проверяем слова с учетом возможных ошибок
    found_good = False
    found_bad = False
    
    words_in_text = re.findall(r'\w+', text_lower)
    for word in words_in_text:
        if find_similar_word(word, good_words):
            found_good = True
        if find_similar_word(word, bad_words):
            found_bad = True
    
    if found_good:
        mood = "позитивный"
    elif found_bad:
        mood = "негативный"
    else:
        mood = "нейтральный"
    
    # Определяем тип с учетом вариаций
    question_words = ['?', 'как', 'какже', 'почему', 'почемy', 'подскажите', 'подскажите', 'помогите', 'помогите', 'возможно', 'возможно', 'можно ли', 'можноли']
    complaint_words = ['жалоба', 'жалоба', 'претензия', 'претензия', 'не работает', 'неработает', 'сломал', 'сломалась', 'проблема', 'проблема', 'ошибка', 'ошибка', 'баг', 'баги']
    thanks_words = ['спасибо', 'спс', 'спасиб', 'благодарю', 'благодарю', 'благодарность', 'благодарность', 'thanks', 'thank you']
    
    theme = "отзыв"
    for word in words_in_text:
        if find_similar_word(word, question_words):
            theme = "вопрос"
            break
        elif find_similar_word(word, complaint_words):
            theme = "жалоба"
            break
        elif find_similar_word(word, thanks_words):
            theme = "благодарность"
            break
    
    # Срочность с вариациями
    urgency_words_high = ['срочно', 'срочно!', 'срочна', 'немедленно', 'немедленно!', 'быстрее', 'быстрей', 'скорее', 'скорей', '!!!']
    urgency_words_medium = ['пожалуйста', 'пожалуйста!', 'помогите', 'помогите!', 'нужно', 'нужно!', 'необходимо', 'необходимо!']
    
    urgency = "низкая"
    for word in words_in_text:
        if find_similar_word(word, urgency_words_high):
            urgency = "высокая"
            break
        elif find_similar_word(word, urgency_words_medium):
            urgency = "средняя"
            break
    
    # Метки
    labels = [mood, theme]
    if len(text) > 100:
        labels.append("развернутый")
    elif len(text) < 20:
        labels.append("короткий")
    
    tech_words = ['техни', 'тех', 'програм', 'прог', 'приложен', 'приложение', 'сайт', 'сайт', 'софт', 'код', 'кодинг']
    money_words = ['цена', 'ценник', 'стоимость', 'стоимсть', 'куп', 'купить', 'прода', 'продать', 'деньги', 'деньги', 'рубль', 'рубли', '₽']
    
    for word in words_in_text:
        if find_similar_word(word, tech_words):
            labels.append("технический")
            break
    
    for word in words_in_text:
        if find_similar_word(word, money_words):
            labels.append("финансовый")
            break
    
    # Плохие слова с вариациями
    toxic_words = ['дурак', 'дура', 'идиот', 'идиотка', 'мудак', 'муда', 'дерьмо', 'дерьмище', 'отстой', 'отстойный', 'ублюдок', 'сволоч', 'сволочь', 'хрень', 'херня']
    has_bad = any(find_similar_word(word, toxic_words) for word in words_in_text)
    
    # Анализ
    if mood == "позитивный":
        summary = f"Хороший отзыв, пользователь доволен ({theme})"
    elif mood == "негативный":
        summary = f"Плохой отзыв, пользователь недоволен ({theme})"
    else:
        summary = f"Нейтральный комментарий ({theme})"
    
    # Проверка на спам
    spam_indicators = ['http', 'www.', '.com', '.ru', '.рф', 'купить', 'дешево', 'скидка', 'акция', 'бесплатно']
    is_spam = len(text) < 50 and any(indicator in text_lower for indicator in spam_indicators)
    
    # Проверка на личные данные
    personal_data_indicators = ['телефон', 'тел.', 'адрес', 'паспорт', 'карта', 'карточка', 'пароль', 'логин']
    has_personal = any(indicator in text_lower for indicator in personal_data_indicators)
    
    return {
        "categories": {
            "theme": theme,
            "sentiment": mood,
            "urgency": urgency,
            "has_violation": has_bad
        },
        "labels": labels,
        "analysis": {
            "summary": summary,
            "key_points": [
                f"Настроение: {mood}",
                f"Тема: {theme}",
                f"Срочность: {urgency}",
                f"Длина: {len(text)} символов",
                f"Нарушения: {'есть' if has_bad else 'нет'}"
            ],
            "recommendation": "Ответить в течение часа" if urgency == "высокая" else "Ответить сегодня" if urgency == "средняя" else "Ответить когда будет время"
        },
        "moderation": {
            "is_toxic": has_bad,
            "is_spam": is_spam,
            "needs_review": has_bad or is_spam or has_personal
        },
        "confidence": 0.85
    }

# Главная страница
@app.get("/")
async def main_page():
    return FileResponse("index.html")

# Анализ комментария
@app.post("/api/analyze")
async def analyze_comment(comment: CommentRequest):
    start_time = time.time()
    
    try:
        text = comment.text.strip()
        if not text:
            return {"success": False, "error": "Пустой текст"}
        
        if len(text) > 10000:
            return {"success": False, "error": "Слишком длинный текст"}
        
        # Анализируем
        result = analyze_text(text)
        
        # Сохраняем
        all_analyses.append({
            "id": len(all_analyses) + 1,
            "time": time.time(),
            "text": text[:200],
            "result": result
        })
        
        # Время обработки
        time_took = time.time() - start_time
        
        return {
            "success": True,
            "data": result,
            "processing_time": round(time_took, 2)
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# История анализов
@app.get("/api/history")
async def get_history():
    return all_analyses[-10:]

# Проверка работы
@app.get("/api/health")
async def health_check():
    return {"status": "работает", "analyses_count": len(all_analyses)}

# Запуск
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# В main.py убедитесь что путь правильный
app.mount("/static", StaticFiles(directory="static"), name="static")