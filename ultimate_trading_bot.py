# -*- coding: utf-8 -*-
import os
import sys
import requests
import time
import json
import math
from datetime import datetime
from dotenv import load_dotenv

# Исправляем кодировку для Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

load_dotenv(override=True)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
YOUR_CHAT_ID = os.environ.get('YOUR_CHAT_ID')
HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY')

# Расширенный список лучших монет для фьючерсной торговли
TOP_FUTURES_COINS = [
    "BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "MATIC", "DOT", "AVAX",
    "LINK", "UNI", "LTC", "BCH", "ATOM", "FIL", "TRX", "ETC", "XLM", "ALGO",
    "TON", "PEPE", "WIF", "SHIB", "APT", "OP", "ARB", "SUI", "SEI", "ORDI"
]

class UltimateTradingBot:
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.offset = 0
        self.user_sessions = {}
        
    def send_message(self, chat_id, text, reply_markup=None):
        url = f"{self.base_url}/sendMessage"
        data = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
        if reply_markup:
            data['reply_markup'] = json.dumps(reply_markup)
        try:
            return requests.post(url, data=data, timeout=30).json()
        except Exception as e:
            print(f"❌ Send error: {e}")
            return None
    
    def edit_message(self, chat_id, message_id, text, reply_markup=None):
        url = f"{self.base_url}/editMessageText"
        data = {'chat_id': chat_id, 'message_id': message_id, 'text': text, 'parse_mode': 'Markdown'}
        if reply_markup:
            data['reply_markup'] = json.dumps(reply_markup)
        try:
            return requests.post(url, data=data, timeout=30).json()
        except Exception as e:
            return None
    
    def answer_callback_query(self, callback_query_id, text=""):
        url = f"{self.base_url}/answerCallbackQuery"
        try:
            return requests.post(url, {'callback_query_id': callback_query_id, 'text': text}, timeout=10).json()
        except:
            return None
    
    def get_updates(self):
        try:
            return requests.get(f"{self.base_url}/getUpdates", {'offset': self.offset, 'timeout': 10}, timeout=15).json()
        except:
            return None

class UltimateAnalyzer:
    def __init__(self):
        self.binance_base = "https://api.binance.com/api/v3"
        self.fear_greed_url = "https://api.alternative.me/fng/"
    
    def analyze_coin(self, coin):
        """Комплексный анализ монеты"""
        try:
            # Базовые данные
            basic_data = self._get_basic_data(coin)
            if not basic_data:
                return None
            
            # Технический анализ
            technical_data = self._get_technical_data(coin)
            
            # Настроения рынка
            sentiment_data = self._get_sentiment_data()
            
            # Объединяем данные
            return {
                'basic': basic_data,
                'technical': technical_data or {},
                'sentiment': sentiment_data or {}
            }
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            return None
    
    def get_quick_signals(self):
        """Быстрые сигналы по топ-5 монетам"""
        quick_coins = ["BTC", "ETH", "SOL", "BNB", "XRP"]
        signals = []
        
        for coin in quick_coins:
            try:
                analysis = self.analyze_coin(coin)
                if analysis:
                    signal = self._generate_quick_signal(analysis, coin)
                    signals.append(signal)
            except:
                continue
        
        return signals
    
    def _generate_quick_signal(self, analysis_data, coin):
        """Генерация быстрого сигнала"""
        basic = analysis_data['basic']
        tech = analysis_data.get('technical', {})
        
        price = basic['price']
        change_24h = basic['change_24h']
        rsi = tech.get('rsi', 50)
        
        # Простая логика для быстрого сигнала
        if rsi < 30 and change_24h > -10:
            signal = "🟢 BUY"
            reason = "Перепродано"
        elif rsi > 70 or change_24h < -15:
            signal = "🔴 SELL"
            reason = "Перекуплено"
        else:
            signal = "🟡 HOLD"
            reason = "Нейтрально"
        
        return {
            'coin': coin,
            'price': price,
            'change': change_24h,
            'signal': signal,
            'reason': reason,
            'rsi': rsi
        }
    
    def _get_basic_data(self, coin):
        """Базовые данные с Binance"""
        try:
            symbol = f"{coin}USDT"
            response = requests.get(f"{self.binance_base}/ticker/24hr", {'symbol': symbol}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'price': float(data['lastPrice']),
                    'change_24h': float(data['priceChangePercent']),
                    'volume_24h': float(data['volume']),
                    'high_24h': float(data['highPrice']),
                    'low_24h': float(data['lowPrice'])
                }
        except:
            pass
        return None
    
    def _get_technical_data(self, coin):
        """Технический анализ"""
        try:
            symbol = f"{coin}USDT"
            response = requests.get(f"{self.binance_base}/klines", {
                'symbol': symbol, 'interval': '1h', 'limit': 50
            }, timeout=10)
            
            if response.status_code == 200:
                klines = response.json()
                closes = [float(k[4]) for k in klines]
                
                rsi = self._calculate_rsi(closes)
                sma_20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else closes[-1]
                ema_12 = self._calculate_ema(closes, 12)
                ema_26 = self._calculate_ema(closes, 26)
                macd = ema_12 - ema_26
                
                return {
                    'rsi': rsi,
                    'sma_20': sma_20,
                    'macd': macd,
                    'trend': 'bullish' if closes[-1] > sma_20 else 'bearish'
                }
        except:
            pass
        return None
    
    def _get_sentiment_data(self):
        """Индекс страха и жадности"""
        try:
            response = requests.get(self.fear_greed_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('data'):
                    fng = data['data'][0]
                    return {
                        'fear_greed_index': int(fng['value']),
                        'fear_greed_text': fng['value_classification']
                    }
        except:
            pass
        return None
    
    def _calculate_rsi(self, prices, period=14):
        """Расчет RSI"""
        if len(prices) < period + 1:
            return 50
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        return round(100 - (100 / (1 + rs)), 2)
    
    def _calculate_ema(self, prices, period):
        """Расчет EMA"""
        if len(prices) < period:
            return prices[-1]
        multiplier = 2 / (period + 1)
        ema = prices[0]
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        return ema

class FixedAIAssistant:
    """Исправленный AI-ассистент"""
    
    def __init__(self, api_key):
        self.api_key = api_key
    
    def get_response(self, question):
        """Получить ответ от AI или заготовленный ответ"""
        fallback = self._get_fallback_response(question)
        
        if not self.api_key:
            return fallback
        
        try:
            ai_response = self._try_ai(question)
            if ai_response and len(ai_response) > 20:
                return ai_response
        except Exception as e:
            print(f"❌ AI error: {e}")
        
        return fallback
    
    def _try_ai(self, question):
        """Попытка получить ответ от AI"""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        
        payload = {
            "inputs": f"Q: {question}\nA:",
            "parameters": {"max_length": 100, "temperature": 0.7}
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and result:
                text = result[0].get('generated_text', '')
                clean = text.replace(f"Q: {question}\nA:", "").strip()
                return clean if clean else None
        
        return None
    
    def _get_fallback_response(self, question):
        """Заготовленные ответы"""
        q = question.lower()
        
        if 'rsi' in q:
            return "RSI (Relative Strength Index) - показывает перекупленность/перепроданность. RSI > 70 = перекуплено (продавать), RSI < 30 = перепродано (покупать)."
        elif 'macd' in q:
            return "MACD - индикатор тренда. Когда линия MACD пересекает сигнальную линию снизу вверх = сигнал на покупку, сверху вниз = на продажу."
        elif 'фьючерс' in q or 'futures' in q:
            return "Фьючерсы - контракты на покупку/продажу в будущем. Позволяют торговать с плечом, но увеличивают риски. Используйте стоп-лоссы!"
        elif 'плечо' in q or 'leverage' in q:
            return "Плечо увеличивает размер позиции за счет заемных средств. Плечо 10x означает, что ваши $100 работают как $1000. Увеличивает прибыль И убытки!"
        else:
            return f"Интересный вопрос о '{question}'. Рекомендую изучить основы технического анализа и риск-менеджмента. Всегда торгуйте осторожно!"

def generate_multi_leverage_orders(analysis_data, coin):
    """Генерация 5 ордеров с разными плечами"""
    if not analysis_data or not analysis_data.get('basic'):
        return f"❌ Нет данных для {coin}"
    
    basic = analysis_data['basic']
    tech = analysis_data.get('technical', {})
    sentiment = analysis_data.get('sentiment', {})
    
    price = basic['price']
    change_24h = basic['change_24h']
    rsi = tech.get('rsi', 50)
    macd = tech.get('macd', 0)
    trend = tech.get('trend', 'sideways')
    fng = sentiment.get('fear_greed_index', 50)
    
    # Подсчет сигналов
    buy_signals = 0
    sell_signals = 0
    
    if rsi < 30: buy_signals += 2
    elif rsi > 70: sell_signals += 2
    elif rsi < 40: buy_signals += 1
    elif rsi > 60: sell_signals += 1
    
    if macd > 0: buy_signals += 1
    else: sell_signals += 1
    
    if trend == 'bullish': buy_signals += 1
    elif trend == 'bearish': sell_signals += 1
    
    if fng < 25: buy_signals += 1
    elif fng > 75: sell_signals += 1
    
    if change_24h < -5: buy_signals += 1
    elif change_24h > 10: sell_signals += 1
    
    # Определяем направление
    if buy_signals > sell_signals + 1:
        direction = "LONG"
        confidence = min(90, 50 + (buy_signals - sell_signals) * 8)
    elif sell_signals > buy_signals + 1:
        direction = "SHORT"
        confidence = min(90, 50 + (sell_signals - buy_signals) * 8)
    else:
        return f"""
🟡 **{coin} - НЕТ ЧЕТКОГО СИГНАЛА**

**Текущие данные:**
• Цена: ${price:,.4f} ({change_24h:+.1f}%)
• RSI: {rsi} | MACD: {macd:.6f}
• Тренд: {trend} | F&G: {fng}/100

**Сигналы:** Покупка {buy_signals} | Продажа {sell_signals}
**Рекомендация:** Ждите более четкого сигнала
"""
    
    # Генерируем ордера для разных плеч
    leverages = [2, 5, 10, 20, 50]
    orders_text = f"""
🎯 **МУЛЬТИ-ПЛЕЧЕВЫЕ ОРДЕРА - {coin}**

**📊 АНАЛИЗ:**
• Направление: **{direction}**
• Уверенность: {confidence}%
• RSI: {rsi} | MACD: {macd:.6f}
• Тренд: {trend} | F&G: {fng}/100

**📋 ОРДЕРА ДЛЯ РАЗНЫХ ПЛЕЧ:**

"""
    
    for i, leverage in enumerate(leverages, 1):
        if direction == "LONG":
            entry = price * (1 - 0.001 * (leverage / 10))  # Более агрессивный вход для больших плеч
            tp1 = price * (1 + 0.01 * (50 / leverage))     # TP зависит от плеча
            tp2 = price * (1 + 0.02 * (50 / leverage))
            sl = price * (1 - 0.005 * (leverage / 10))     # SL зависит от плеча
        else:
            entry = price * (1 + 0.001 * (leverage / 10))
            tp1 = price * (1 - 0.01 * (50 / leverage))
            tp2 = price * (1 - 0.02 * (50 / leverage))
            sl = price * (1 + 0.005 * (leverage / 10))
        
        # Размер позиции зависит от плеча
        position_size = round(100 / leverage, 1)  # Чем больше плечо, тем меньше размер
        
        orders_text += f"""
**{i}. ПЛЕЧО {leverage}x** (Размер: {position_size}%)
```
{coin}USDT {direction} {leverage}x
Entry: {entry:.4f}
TP1: {tp1:.4f}
TP2: {tp2:.4f}
SL: {sl:.4f}
Size: {position_size}%
```
"""
    
    orders_text += f"""
**⚠️ РИСК-МЕНЕДЖМЕНТ:**
• Плечо 2-5x: Для новичков
• Плечо 10-20x: Для опытных
• Плечо 50x: Только для профи
• ВСЕГДА используйте стоп-лоссы!

_Время: {datetime.now().strftime('%H:%M:%S')}_
"""
    
    return orders_text

def create_main_menu():
    return {
        'inline_keyboard': [
            [{'text': '📊 Анализ монет', 'callback_data': 'analysis'}, {'text': '🤖 AI-Помощник', 'callback_data': 'ai'}],
            [{'text': '⚡ Быстрые сигналы', 'callback_data': 'quick_signals'}, {'text': '🔥 Топ монеты', 'callback_data': 'top_coins'}],
            [{'text': '❓ Помощь', 'callback_data': 'help'}]
        ]
    }

def create_coins_menu():
    # Создаем меню с расширенным списком монет
    coins_keyboard = []
    
    # Разбиваем монеты на группы по 3
    for i in range(0, len(TOP_FUTURES_COINS), 3):
        row = []
        for j in range(3):
            if i + j < len(TOP_FUTURES_COINS):
                coin = TOP_FUTURES_COINS[i + j]
                row.append({'text': coin, 'callback_data': f'coin_{coin}'})
        coins_keyboard.append(row)
    
    # Добавляем кнопку назад
    coins_keyboard.append([{'text': '🔙 Назад', 'callback_data': 'main'}])
    
    return {'inline_keyboard': coins_keyboard}

def format_quick_signals(signals):
    """Форматирование быстрых сигналов"""
    if not signals:
        return "❌ Не удалось получить быстрые сигналы"
    
    text = "⚡ **БЫСТРЫЕ СИГНАЛЫ**\n\n"
    
    for signal in signals:
        emoji = "🟢" if "BUY" in signal['signal'] else "🔴" if "SELL" in signal['signal'] else "🟡"
        
        text += f"""
{emoji} **{signal['coin']}** - {signal['signal']}
• Цена: ${signal['price']:,.4f}
• 24ч: {signal['change']:+.1f}%
• RSI: {signal['rsi']}
• Причина: {signal['reason']}

"""
    
    text += f"_Обновлено: {datetime.now().strftime('%H:%M:%S')}_"
    return text

def handle_start(chat_id, bot):
    text = """
🚀 **ULTIMATE TRADING BOT v3.0**

Самый продвинутый торговый бот!

**🔥 НОВЫЕ ВОЗМОЖНОСТИ:**
• 📊 30+ монет для анализа
• 🎯 5 ордеров с разными плечами
• ⚡ Исправленные быстрые сигналы
• 🤖 Улучшенный AI-помощник
• 📈 Мультисигнальный анализ

Выберите действие:
"""
    bot.send_message(chat_id, text, create_main_menu())

def handle_callback(callback_data, chat_id, message_id, callback_query_id, bot, analyzer, ai):
    bot.answer_callback_query(callback_query_id)
    
    if callback_data == 'main':
        text = "🚀 **ULTIMATE TRADING BOT v3.0**\n\nВыберите действие:"
        bot.edit_message(chat_id, message_id, text, create_main_menu())
    
    elif callback_data == 'analysis':
        text = "📊 **Выберите монету для анализа:**\n\n_30+ лучших монет для фьючерсной торговли_"
        bot.edit_message(chat_id, message_id, text, create_coins_menu())
    
    elif callback_data.startswith('coin_'):
        coin = callback_data.replace('coin_', '')
        bot.edit_message(chat_id, message_id, f"🔄 Генерирую 5 ордеров с разными плечами для {coin}...")
        
        analysis = analyzer.analyze_coin(coin)
        orders_text = generate_multi_leverage_orders(analysis, coin)
        
        back_menu = {'inline_keyboard': [[{'text': '🔙 К монетам', 'callback_data': 'analysis'}]]}
        bot.edit_message(chat_id, message_id, orders_text, back_menu)
    
    elif callback_data == 'quick_signals':
        bot.edit_message(chat_id, message_id, "⚡ Получаю быстрые сигналы по топ-5 монетам...")
        
        signals = analyzer.get_quick_signals()
        signals_text = format_quick_signals(signals)
        
        back_menu = {'inline_keyboard': [[{'text': '🔄 Обновить', 'callback_data': 'quick_signals'}, {'text': '🔙 Назад', 'callback_data': 'main'}]]}
        bot.edit_message(chat_id, message_id, signals_text, back_menu)
    
    elif callback_data == 'ai':
        text = """
🤖 **AI-ПОМОЩНИК**

Задайте любой вопрос о трейдинге!

**Популярные темы:**
• RSI, MACD, технический анализ
• Фьючерсы и плечо
• Риск-менеджмент
• Стоп-лоссы

**Напишите ваш вопрос следующим сообщением.**
"""
        bot.edit_message(chat_id, message_id, text, {'inline_keyboard': [[{'text': '🔙 Назад', 'callback_data': 'main'}]]})
        bot.user_sessions[chat_id] = {'mode': 'ai_question'}
    
    elif callback_data == 'help':
        help_text = """
❓ **СПРАВКА**

**🚀 Ultimate Trading Bot v3.0**

**Новые возможности:**
• 📊 30+ монет для анализа
• 🎯 5 ордеров с разными плечами (2x, 5x, 10x, 20x, 50x)
• ⚡ Быстрые сигналы (исправлены)
• 🤖 AI-помощник с заготовленными ответами
• 📈 Мультисигнальный анализ

**⚠️ ВАЖНО:**
• Начинайте с малых плеч (2-5x)
• Всегда используйте стоп-лоссы
• Не рискуйте более 1-2% депозита
• Торгуйте на свой страх и риск

**📞 Поддержка:** @your_support
"""
        bot.edit_message(chat_id, message_id, help_text, {'inline_keyboard': [[{'text': '🔙 Назад', 'callback_data': 'main'}]]})

def handle_text(text, chat_id, bot, ai):
    session = bot.user_sessions.get(chat_id, {})
    
    if session.get('mode') == 'ai_question':
        bot.send_message(chat_id, "🤖 Обрабатываю ваш вопрос...")
        response = ai.get_response(text)
        bot.send_message(chat_id, f"**❓ Вопрос:** {text}\n\n**🤖 Ответ:** {response}\n\n_Задайте еще вопрос или /start для меню_")
        bot.user_sessions[chat_id] = {}
    else:
        bot.send_message(chat_id, "Используйте /start для открытия меню")

def main():
    print("=== 🚀 ULTIMATE TRADING BOT v3.0 ===")
    print(f"TELEGRAM_TOKEN: {'✅' if TELEGRAM_TOKEN else '❌'}")
    print(f"YOUR_CHAT_ID: {'✅' if YOUR_CHAT_ID else '❌'}")
    print(f"HUGGINGFACE_API_KEY: {'✅ AI включен' if HUGGINGFACE_API_KEY else '⚠️ Только заготовленные ответы'}")
    print(f"COINS: {len(TOP_FUTURES_COINS)} монет доступно")
    
    if not TELEGRAM_TOKEN or not YOUR_CHAT_ID:
        print("❌ Нужны TELEGRAM_TOKEN и YOUR_CHAT_ID!")
        return
    
    bot = UltimateTradingBot(TELEGRAM_TOKEN)
    analyzer = UltimateAnalyzer()
    ai = FixedAIAssistant(HUGGINGFACE_API_KEY)
    
    bot.send_message(YOUR_CHAT_ID, f"""🚀 **Ultimate Trading Bot v3.0 запущен!**

✅ 30+ монет для анализа
✅ 5 ордеров с разными плечами
✅ Исправленные быстрые сигналы
✅ AI-помощник

Время: {datetime.now().strftime('%H:%M:%S')}""")
    
    print("🤖 Ultimate Bot запущен! Нажмите Ctrl+C для остановки")
    
    try:
        while True:
            updates = bot.get_updates()
            
            if updates and updates.get('ok'):
                for update in updates.get('result', []):
                    bot.offset = update['update_id'] + 1
                    
                    if 'message' in update:
                        message = update['message']
                        chat_id = message['chat']['id']
                        text = message.get('text', '')
                        
                        if text == '/start':
                            handle_start(chat_id, bot)
                        else:
                            handle_text(text, chat_id, bot, ai)
                    
                    elif 'callback_query' in update:
                        callback = update['callback_query']
                        handle_callback(
                            callback['data'],
                            callback['message']['chat']['id'],
                            callback['message']['message_id'],
                            callback['id'],
                            bot, analyzer, ai
                        )
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Ultimate Bot остановлен")
        bot.send_message(YOUR_CHAT_ID, "🛑 Ultimate Trading Bot остановлен")

if __name__ == "__main__":
    main()
