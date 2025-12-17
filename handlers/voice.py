"""
Voice Message Handler.
Handles voice messages with STT and TTS using pyTelegramBotAPI.
"""

from telebot import types
from bot import bot
from services.router import route_voice_request
from services.tts import get_available_voices, get_voice_info
from utils.logging import logger
from utils.helpers import user_sessions, save_file_async, cleanup_files
from config import VoiceType


@bot.message_handler(commands=['voice'])
async def cmd_voice(message: types.Message):
    """Handle /voice command - change TTS voice with inline buttons."""
    user_id = message.from_user.id
    current_voice = user_sessions.get_voice(user_id)
    
    # Create inline keyboard with voice options
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    voices = [
        ("🎵 Alloy", VoiceType.ALLOY, "Нейтральный"),
        ("👨 Echo", VoiceType.ECHO, "Мужской"),
        ("👩 Nova", VoiceType.NOVA, "Женский"),
        ("🎭 Fable", VoiceType.FABLE, "Британский"),
        ("🎤 Onyx", VoiceType.ONYX, "Глубокий"),
        ("✨ Shimmer", VoiceType.SHIMMER, "Теплый"),
    ]
    
    buttons = []
    for emoji_name, voice_value, voice_type in voices:
        # Add checkmark to current voice
        button_text = f"✅ {emoji_name}" if voice_value == current_voice else emoji_name
        button = types.InlineKeyboardButton(
            text=button_text,
            callback_data=f"voice_{voice_value}"
        )
        buttons.append(button)
    
    # Add buttons in rows of 2
    keyboard.add(buttons[0], buttons[1])
    keyboard.add(buttons[2], buttons[3])
    keyboard.add(buttons[4], buttons[5])
    
    current_info = get_voice_info(current_voice)
    
    voice_info = f"""🔊 Выберите голос для ответов

Текущий голос: {current_info['name']} ({current_voice})
Тип: {current_info['type']}

🎵 Alloy - нейтральный голос
👨 Echo - мужской голос
👩 Nova - женский голос
🎭 Fable - британский акцент
🎤 Onyx - глубокий мужской
✨ Shimmer - теплый женский

Голос используется в голосовом режиме (/mode voice)
"""
    
    await bot.send_message(
        message.chat.id,
        voice_info,
        reply_markup=keyboard,
        parse_mode=None
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('voice_'))
async def callback_voice(call: types.CallbackQuery):
    """Handle voice selection from inline buttons."""
    user_id = call.from_user.id
    new_voice = call.data.replace('voice_', '')
    
    # Set new voice
    user_sessions.set_voice(user_id, new_voice)
    logger.info(f"User {user_id} switched to voice: {new_voice}")
    
    # Answer callback query
    await bot.answer_callback_query(call.id, "✅ Голос изменен!")
    
    # Update message with new selection
    current_voice = new_voice
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    voices = [
        ("🎵 Alloy", VoiceType.ALLOY),
        ("👨 Echo", VoiceType.ECHO),
        ("👩 Nova", VoiceType.NOVA),
        ("🎭 Fable", VoiceType.FABLE),
        ("🎤 Onyx", VoiceType.ONYX),
        ("✨ Shimmer", VoiceType.SHIMMER),
    ]
    
    buttons = []
    for emoji_name, voice_value in voices:
        button_text = f"✅ {emoji_name}" if voice_value == current_voice else emoji_name
        button = types.InlineKeyboardButton(
            text=button_text,
            callback_data=f"voice_{voice_value}"
        )
        buttons.append(button)
    
    keyboard.add(buttons[0], buttons[1])
    keyboard.add(buttons[2], buttons[3])
    keyboard.add(buttons[4], buttons[5])
    
    current_info = get_voice_info(current_voice)
    
    voice_info = f"""🔊 Выберите голос для ответов

Текущий голос: {current_info['name']} ({current_voice})
Тип: {current_info['type']}

🎵 Alloy - нейтральный голос
👨 Echo - мужской голос
👩 Nova - женский голос
🎭 Fable - британский акцент
🎤 Onyx - глубокий мужской
✨ Shimmer - теплый женский

Голос используется в голосовом режиме (/mode voice)
"""
    
    # Edit message
    await bot.edit_message_text(
        voice_info,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboard,
        parse_mode=None
    )
    
    # Send confirmation
    voice_info_detail = get_voice_info(new_voice)
    await bot.send_message(
        call.message.chat.id,
        f"✅ Голос изменен!\n\n"
        f"🔊 {voice_info_detail['name']} ({new_voice})\n"
        f"Тип: {voice_info_detail['type']}\n"
        f"{voice_info_detail['description']}",
        parse_mode=None
    )


@bot.message_handler(commands=['voices'])
async def cmd_voices(message: types.Message):
    """Handle /voices command - list all available voices."""
    voice_list = get_available_voices()
    await bot.send_message(message.chat.id, voice_list, parse_mode=None)


@bot.message_handler(content_types=['voice'])
async def handle_voice_message(message: types.Message):
    """Handle voice messages."""
    user_id = message.from_user.id
    
    logger.info(f"Voice message from user {user_id}")
    
    # Show typing indicator
    await bot.send_chat_action(message.chat.id, 'typing')
    
    voice_file_path = None
    audio_response_path = None
    image_path = None
    
    try:
        # Download voice message
        file_info = await bot.get_file(message.voice.file_id)
        voice_bytes = await bot.download_file(file_info.file_path)
        
        # Save to temporary file
        voice_file_path = await save_file_async(voice_bytes, "ogg")
        
        logger.debug(f"Voice file saved: {voice_file_path}")
        
        # Process voice request
        response = await route_voice_request(user_id, voice_file_path)
        
        # Check if there was an error
        if 'error' in response:
            error_msg = response.get('text', '❌ Ошибка обработки голосового сообщения. Попробуйте еще раз.')
            await bot.send_message(message.chat.id, error_msg, parse_mode=None)
            return
        
        # Send transcription
        if 'transcription' in response:
            await bot.send_message(
                message.chat.id,
                f"🎤 Распознано:\n{response['transcription']}\n",
                parse_mode=None
            )
        
        # Check if response contains an image
        if response.get('has_image') and response.get('image_path'):
            # Send text response first
            await bot.send_message(message.chat.id, response["text"])
            
            # Then send the generated image
            image_path = response['image_path']
            
            try:
                # Show uploading photo action
                await bot.send_chat_action(message.chat.id, 'upload_photo')
                
                # Send image
                with open(image_path, 'rb') as photo:
                    caption = response.get('revised_prompt', '')
                    if len(caption) > 1024:
                        caption = caption[:1021] + "..."
                    
                    await bot.send_photo(
                        message.chat.id, 
                        photo,
                        caption=caption if caption else None
                    )
                
                logger.info(f"Image sent to user {user_id} (from voice message)")
                
            except Exception as img_error:
                logger.error(f"Error sending image: {img_error}")
            
            return
        
        # Show voice action
        await bot.send_chat_action(message.chat.id, 'record_voice')
        
        # Send text response
        await bot.send_message(message.chat.id, response["text"])
        
        # Send voice response
        audio_response_path = response.get("voice_path")
        if audio_response_path:
            with open(audio_response_path, 'rb') as audio:
                await bot.send_voice(message.chat.id, audio)
    
    except Exception as e:
        logger.error(f"Error handling voice message: {e}", exc_info=True)
        await bot.send_message(
            message.chat.id,
            "❌ Произошла ошибка при обработке голосового сообщения.\n"
            "Попробуйте еще раз."
        )
    
    finally:
        # Cleanup temporary files
        cleanup_files(voice_file_path, audio_response_path, image_path)


@bot.message_handler(content_types=['audio'])
async def handle_audio_message(message: types.Message):
    """Handle audio files (similar to voice)."""
    await bot.send_message(
        message.chat.id,
        "ℹ️ Для обработки аудио используйте голосовые сообщения.\n"
        "Аудиофайлы в виде документов не поддерживаются."
    )
