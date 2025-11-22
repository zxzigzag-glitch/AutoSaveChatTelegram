from telethon import TelegramClient, events
from datetime import datetime
import os
from dotenv import load_dotenv

# โหลดค่าจากไฟล์ product.env
load_dotenv('product.env')

api_id = int(os.getenv('api_id'))
api_hash = os.getenv('api_hash').strip("'\"")

client = TelegramClient('session', api_id, api_hash)

@client.on(events.NewMessage)
async def handler(event):
    
    # ดึงข้อมูลผู้ส่ง
    sender = await event.get_sender()
    sender_name = sender.first_name if sender.first_name else "Unknown"
    if sender.last_name:
        sender_name += f" {sender.last_name}"
    
    # ดึงข้อมูลแชท
    chat = await event.get_chat()
    
    # ถ้าเป็นกลุ่ม ใช้ชื่อกลุ่ม ถ้าเป็นแชทส่วนตัว ใช้ชื่อของอีกฝ่าย
    if hasattr(chat, 'title'):
        # เป็นกลุ่ม/ช่อง
        chat_name = chat.title
    else:
        # เป็นแชทส่วนตัว - ใช้ชื่อของอีกฝ่าย (คนที่แชทด้วย)
        chat_name = chat.first_name if chat.first_name else "Unknown"
        if chat.last_name:
            chat_name += f" {chat.last_name}"
    
    # Format datetime
    timestamp = event.date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + event.date.strftime("%z")
    if timestamp[-2:] != "00":
        timestamp = timestamp[:-2] + ":" + timestamp[-2:]
    timestamp += f"[{event.date.tzname()}]"
    
    # สร้างโฟลเดอร์สำหรับแชทนี้
    date_str = event.date.strftime('%Y-%m-%d')
    chat_folder = f"stock/{chat_name}/{date_str}"
    os.makedirs(chat_folder, exist_ok=True)
    
    # ตรวจสอบว่ามี media หรือไม่ (รองรับทุกประเภท)
    media_path = None
    media_type = None
    
    if event.media:
        # ดาวน์โหลด media โดยให้ Telethon เลือกนามสกุลไฟล์เอง
        timestamp_str = event.date.strftime('%Y%m%d_%H%M%S')
        filename = f"{chat_folder}/{timestamp_str}_{event.sender_id}"
        media_path = await event.download_media(filename)
        
        # ระบุประเภทของ media
        if event.photo:
            media_type = "Photo"
        elif event.video:
            media_type = "Video"
        elif event.gif:
            media_type = "GIF"
        elif event.document:
            # ตรวจสอบ MIME type ของ document
            if hasattr(event.document, 'mime_type'):
                mime = event.document.mime_type
                if mime.startswith('image/'):
                    media_type = "Image"
                elif mime.startswith('video/'):
                    media_type = "Video"
                else:
                    media_type = "Document"
            else:
                media_type = "Document"
        elif event.audio:
            media_type = "Audio"
        elif event.voice:
            media_type = "Voice"
        elif event.sticker:
            media_type = "Sticker"
        else:
            media_type = "Media"
    
    # สร้างชื่อไฟล์ log
    log_file = f"{chat_folder}/{date_str}_log.txt"
    
    # บันทึก log
    log_text = f"{timestamp} [{chat_name}] {sender_name} ({event.sender_id}): {event.raw_text}"
    if media_path and media_type:
        log_text += f" [{media_type}: {media_path}]"
    log_text += "\n"
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_text)

client.start()
client.run_until_disconnected()