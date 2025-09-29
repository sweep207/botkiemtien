#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bot Telegram Kiếm Tiền Online - DEMO
"""
# --- Cấu hình game Tài Xỉu ---
TAIXIU_WIN_RATE = 0.5  # 50% cơ hội thắng user
MIN_BET = 500  # cược tối thiểu
# --- Cấu hình Admin ---
ADMIN_ID = 5645750335  # Telegram ID admin
BANK_INFO = """💰 Hướng dẫn nạp tiền:
• Chủ TK: sweep
• Số TK: thay vao day
• Ngân hàng: Amazon
• Nội dung chuyển khoản: <tuy ban>"""
# Cấu hình xổ số
XOSO_MIN = 1
XOSO_MAX = 50
XOSO_DURATION = 60  # thời gian 1 phiên
XOSO_WIN_AMOUNT = 2000  # tiền thưởng mỗi lần đoán đúng
current_xoso_number = None
xoso_active = False

# --- Import cần thiết ---
import asyncio
import sqlite3
import random
import datetime
import nest_asyncio
nest_asyncio.apply()

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# --- Khởi tạo database ---
conn = sqlite3.connect("vipbot.db")
c = conn.cursor()

# Xóa bảng tasks cũ nếu tồn tại
c.execute("DROP TABLE IF EXISTS tasks")

# --- Tạo bảng nhiệm vụ mới ---
c.execute('''
CREATE TABLE tasks (
    task_id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    reward INTEGER DEFAULT 0
)
''')

# --- Thêm nhiệm vụ cố định ---
fixed_tasks = [
    (1, "Tham Gia Nhom Telegram", "t.me/Shadowrocket2411", 500),
    (2, "Dang Ky Kenh Youtube", "https://youtube.com/@sweep207", 200),
    (3, "Theo Doi Tiktok", "https://tiktok.com/@sweep2712", 200)
]

for task in fixed_tasks:
    c.execute('''
    INSERT OR IGNORE INTO tasks (task_id, title, description, reward)
    VALUES (?, ?, ?, ?)
    ''', task)

conn.commit()

# --- Bảng trạng thái user nhiệm vụ ---
c.execute('''
CREATE TABLE IF NOT EXISTS user_tasks (
    user_id INTEGER,
    task_id INTEGER,
    status TEXT DEFAULT 'pending',
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, task_id)
)
''')

conn.commit()

# --- cấu hình cơ bản ---
TOKEN = "8272774983:AAEqFvW8p8QdNWQXzfNZCYPV-uahIxArjaQ"   # <-- thay bằng token BotFather cấp
ADMIN_ID = 5645750335      # <-- thay bằng Telegram ID của admin

# --- Kết nối Database (dùng chung vipbot.db) ---
conn = sqlite3.connect("vipbot.db", check_same_thread=False)
c = conn.cursor()

# Tạo bảng users để lưu thông tin người dùng
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    balance INTEGER DEFAULT 0,
    points INTEGER DEFAULT 0,
    last_daily TEXT DEFAULT ''
)
''')
conn.commit()

# --- Hàm hỗ trợ ---
def add_user(user_id, username):
    """Thêm user mới vào database (nếu chưa có)."""
    c.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()

def get_user(user_id):
    """Lấy thông tin user."""
    c.execute("SELECT user_id, username, balance, points, last_daily FROM users WHERE user_id=?", (user_id,))
    return c.fetchone()
    # PHẦN 2: Handler cho lệnh /start

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username)

    text = (
        f"👋 Xin chào {user.first_name}!\n\n"
        "Chào mừng bạn đến với **BOT KIẾM TIỀN ONLINE** 💸\n\n"
        "⚡ Làm nhiệm vụ nhỏ (like video, đăng ký kênh, vuot link...) để nhận xu.\n"
        "🎁 Rút tiền khi đạt tối thiểu **20.000đ**.\n\n"
        "📜 Gõ /menu để xem danh sách lệnh."
    )

    await update.message.reply_text(text, parse_mode="Markdown")
    # PHẦN 3: Handler cho lệnh /menu

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📌 Danh sách lệnh hỗ trợ:\n\n"
        "/start - Bắt đầu\n"
        "/menu - Xem hướng dẫn\n"
        "/diemdanh - Điểm danh hằng ngày\n"
        "/nhiemvu - Nhận nhiệm vụ\n"
        "/rut - Yêu cầu rút tiền\n"
        "/luat - Nội quy & luật\n"
        "/code - Nhập code từ admin\n"
        "/pet - Nuôi thú cưng (mini game)\n"
        "/gioithieu - Nhận link giới thiệu\n"
        "/lienhe - Liên hệ hỗ trợ\n"
    )
    await update.message.reply_text(text)
    # PHẦN 4: Handler cho lệnh /diemdanh

import datetime

async def diemdanh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    today = datetime.date.today().isoformat()

    # Lấy thông tin user
    data = get_user(user.id)

    if not data:
        add_user(user.id, user.username)
        data = get_user(user.id)

    last_daily = data[4]

    if last_daily == today:
        await update.message.reply_text("📅 Bạn đã điểm danh hôm nay rồi, hãy quay lại vào ngày mai nhé!")
    else:
        # Cộng điểm
        c.execute("UPDATE users SET points = points + 10, last_daily=? WHERE user_id=?", (today, user.id))
        conn.commit()
        await update.message.reply_text("✅ Điểm danh thành công! +100 Vnd 🎉")
        # --- PHẦN PROFILE ---
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Demo dữ liệu user (balance, hunger, happy)
    # Sau này có thể thay bằng get_user từ DB
    balance = 0
    hunger = 100
    happy = 100

    text = (
        f"👤 *Thông tin tài khoản*\n\n"
        f"ID: `{user.id}`\n"
        f"Tên: {user.first_name}\n"
        f"Số dư: {balance}đ\n\n"
        f"🐾 Thú cưng:\n"
        f"  • Đói: {hunger}/100\n"
        f"  • Vui vẻ: {happy}/100"
    )

    await update.message.reply_text(text, parse_mode="Markdown")

async def luat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📜 **Nội quy sử dụng bot:**\n"
        "1️⃣ Không spam, không gian lận nhiệm vụ.\n"
        "2️⃣ Thực hiện nhiệm vụ đúng yêu cầu.\n"
        "3️⃣ Admin có quyền khóa tài khoản gian lận.\n"
        "4️⃣ Rút tối thiểu 20.000đ.\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def lienhe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📞 Liên hệ hỗ trợ admin: @sweep207"
    await update.message.reply_text(text)

# --- PHẦN REF ---
async def ref(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Tạo link giới thiệu theo user ID
    ref_link = f"https://t.me/{context.bot.username}?start={user.id}"

    text = (
        f"🔗 *Link giới thiệu của bạn:*\n"
        f"{ref_link}\n\n"
        "👉 Mời bạn bè tham gia để nhận thưởng!"
    )

    await update.message.reply_text(text, parse_mode="Markdown")
    # PHẦN 6: /code (nhập code từ admin)

# --- Tạo bảng code ---
c.execute('''
CREATE TABLE IF NOT EXISTS codes (
    code TEXT PRIMARY KEY,
    reward INTEGER,
    is_active INTEGER DEFAULT 1
)
''')

# Tạo bảng lưu lịch sử user đã dùng code
c.execute('''
CREATE TABLE IF NOT EXISTS user_codes (
    user_id INTEGER,
    code TEXT,
    PRIMARY KEY(user_id, code)
)
''')
conn.commit()


# --- Admin thêm code mới ---
def add_code(code: str, reward: int):
    """Admin thêm code mới vào database"""
    c.execute("INSERT OR REPLACE INTO codes (code, reward, is_active) VALUES (?, ?, 1)", (code, reward))
    conn.commit()


# --- Handler /code ---
async def code_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if len(context.args) == 0:
        await update.message.reply_text("❌ Vui lòng nhập code.\nVí dụ: `/code CODE2025`", parse_mode="Markdown")
        return

    input_code = context.args[0].strip().upper()

    # Kiểm tra code có tồn tại không
    c.execute("SELECT reward, is_active FROM codes WHERE code=?", (input_code,))
    code_data = c.fetchone()

    if not code_data:
        await update.message.reply_text("❌ Code không tồn tại.")
        return

    reward, is_active = code_data

    if is_active == 0:
        await update.message.reply_text("⚠️ Code này đã hết hạn hoặc bị vô hiệu hóa.")
        return

    # Kiểm tra user đã nhập code này chưa
    c.execute("SELECT * FROM user_codes WHERE user_id=? AND code=?", (user.id, input_code))
    if c.fetchone():
        await update.message.reply_text("⚠️ Bạn đã sử dụng code này rồi.")
        return

    # Thêm vào user_codes
    c.execute("INSERT INTO user_codes (user_id, code) VALUES (?, ?)", (user.id, input_code))

    # Cộng điểm cho user
    c.execute("UPDATE users SET points = points + ? WHERE user_id=?", (reward, user.id))
    conn.commit()

    await update.message.reply_text(f"✅ Nhập code thành công! Bạn nhận được +{reward} điểm 🎉")
    # PHẦN 7: /nhiemvu - quản lý nhiệm vụ

# --- Tạo bảng nhiệm vụ ---
c.execute('''
CREATE TABLE IF NOT EXISTS missions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    reward INTEGER,
    is_active INTEGER DEFAULT 1
)
''')

# Lưu user đã nhận nhiệm vụ
c.execute('''
CREATE TABLE IF NOT EXISTS user_missions (
    user_id INTEGER,
    mission_id INTEGER,
    status TEXT DEFAULT "pending", -- pending | approved | rejected
    PRIMARY KEY(user_id, mission_id)
)
''')
conn.commit()


# --- Admin thêm nhiệm vụ ---
def add_mission(title: str, description: str, reward: int):
    c.execute("INSERT INTO missions (title, description, reward, is_active) VALUES (?, ?, ?, 1)",
              (title, description, reward))
    conn.commit()


# --- PHẦN: /nhiemvu ---
async def nhiemvu(update, context):
    user_id = update.effective_user.id

    # Lấy danh sách nhiệm vụ
    c.execute("SELECT task_id, title, description, reward FROM tasks")
    tasks = c.fetchall()

    if not tasks:
        await update.message.reply_text("📭 Hiện chưa có nhiệm vụ nào.\n👉 Hãy quay lại sau!")
        return

    msg = "🎯 **Danh sách nhiệm vụ hiện có:**\n\n"
    for t in tasks:
        task_id, title, desc, reward = t
        msg += f"📝 *{title}*\n{desc}\n💰 Phần thưởng: {reward} điểm\n✅ Gửi hoàn thành: /hoanthanh_{task_id}\n\n"

    await update.message.reply_text(msg, parse_mode='Markdown')

# --- Handler /hoanthanh_ (submit nhiệm vụ) ---
async def submit_task(update, context):
    user_id = update.effective_user.id
    text = update.message.text

    # Lấy task_id từ lệnh /hoanthanh_*
    try:
        task_id = int(text.split('_')[1])
    except:
        await update.message.reply_text("❌ Lệnh không hợp lệ.")
        return

    # Lưu trạng thái pending
    c.execute('''
    INSERT OR REPLACE INTO user_tasks (user_id, task_id, status)
    VALUES (?, ?, 'pending')
    ''', (user_id, task_id))
    conn.commit()

    await update.message.reply_text("📬 Nhiệm vụ đã được gửi, chờ admin duyệt")


# --- Lệnh /nhan <id> ---
async def nhan_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if len(context.args) == 0:
        await update.message.reply_text("❌ Vui lòng nhập ID nhiệm vụ.\nVí dụ: `/nhan 1`", parse_mode="Markdown")
        return

    try:
        mission_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("⚠️ ID nhiệm vụ phải là số.")
        return

    # Kiểm tra nhiệm vụ tồn tại
    c.execute("SELECT title, reward FROM missions WHERE id=? AND is_active=1", (mission_id,))
    mission = c.fetchone()

    if not mission:
        await update.message.reply_text("❌ Nhiệm vụ không tồn tại hoặc đã đóng.")
        return

    title, reward = mission

    # Kiểm tra user đã nhận chưa
    c.execute("SELECT status FROM user_missions WHERE user_id=? AND mission_id=?", (user.id, mission_id))
    if c.fetchone():
        await update.message.reply_text("⚠️ Bạn đã nhận nhiệm vụ này rồi, chờ admin duyệt.")
        return

    # Thêm user_missions (chờ admin duyệt)
    c.execute("INSERT INTO user_missions (user_id, mission_id, status) VALUES (?, ?, 'pending')", (user.id, mission_id))
    conn.commit()

    # Thông báo user
    await update.message.reply_text(f"📌 Bạn đã đăng ký nhiệm vụ: *{title}*\nVui lòng chờ admin duyệt.",
                                    parse_mode="Markdown")

    # Gửi thông báo cho admin
    for admin in ADMIN_IDS:
        await context.bot.send_message(
            chat_id=admin,
            text=f"👤 User {user.first_name} ({user.id}) đã nhận nhiệm vụ '{title}' (ID: {mission_id}).\n"
                 f"Hãy kiểm tra và duyệt."
        )
        # --- PHẦN REF ---
async def ref(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Lấy username bot chính xác
    bot_info = await context.bot.get_me()
    bot_username = bot_info.username

    # Tạo link giới thiệu
    ref_link = f"https://t.me/{bot_username}?start={user.id}"

    text = (
        f"🔗 *Link giới thiệu của bạn:*\n"
        f"{ref_link}\n\n"
        "👉 Mời bạn bè tham gia để nhận thưởng!"
    )
    conn.commit()  # Nếu quên lệnh này, dữ liệu không lưu
    # --- PHẦN CSKH: /support ---
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    admin_contact = "@sweep207"  # Thay bằng username Telegram của admin
    support_text = (
        f"📞 *Hỗ trợ / CSKH*\n\n"
        f"Chào {user.first_name}, nếu bạn gặp vấn đề hoặc cần hướng dẫn, vui lòng liên hệ:\n"
        f"• Admin: {admin_contact}\n\n"
        f"Bạn có thể gửi tin nhắn trực tiếp hoặc báo lỗi tại đây, admin sẽ phản hồi sớm nhất."
    )
    await update.message.reply_text(support_text, parse_mode="Markdown")

    await update.message.reply_text(text, parse_mode="Markdown")
    # --- PHẦN NẠP TIỀN ---
async def nap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # Gửi hướng dẫn
    await update.message.reply_text(f"{BANK_INFO}\n\nSau khi chuyển, gửi lệnh /nap <số tiền> để yêu cầu duyệt.")
    # xoor slos
async def start_xoso(update, context):
    global current_xoso_number, xoso_active, xoso_players

    if xoso_active:
        await update.message.reply_text("⚠️ Xổ số đang chạy, vui lòng chờ phiên hiện tại kết thúc.")
        return

    current_xoso_number = random.randint(XOSO_MIN, XOSO_MAX)
    xoso_active = True
    xoso_players = {}

    await update.message.reply_text(
        f"🎲 Xổ số bắt đầu! Đoán số từ {XOSO_MIN} đến {XOSO_MAX} bằng lệnh /xoso <số>.\n"
        f"⏱ Bạn có {XOSO_DURATION} giây!"
    )

    await asyncio.sleep(XOSO_DURATION)
    xoso_active = False

    if xoso_players:
        winners = [uid for uid, guess in xoso_players.items() if guess == current_xoso_number]
        if winners:
            win_text = "🎉 Người thắng:\n"
            for uid in winners:
                # TODO: cập nhật tiền thắng vào DB
                win_text += f"- User ID {uid} thắng {XOSO_WIN_AMOUNT}đ\n"
            await update.message.reply_text(win_text)
        else:
            await update.message.reply_text(f"⏰ Hết giờ! Không ai đoán đúng. Số may mắn là {current_xoso_number}")
    else:
        await update.message.reply_text(f"⏰ Hết giờ! Không ai tham gia. Số may mắn là {current_xoso_number}")

    current_xoso_number = None
    
async def xoso(update, context):
    global xoso_players, xoso_active
    user = update.effective_user
    args = context.args

    if not xoso_active:
        await update.message.reply_text("⚠️ Hiện không có phiên xổ số nào đang chạy.")
        return

    if not args or not args[0].isdigit():
        await update.message.reply_text(f"📌 Cú pháp: /xoso <số từ {XOSO_MIN}–{XOSO_MAX}>")
        return

    guess = int(args[0])
    if guess < XOSO_MIN or guess > XOSO_MAX:
        await update.message.reply_text(f"⚠️ Số dự đoán phải từ {XOSO_MIN} đến {XOSO_MAX}")
        return

    xoso_players[user.id] = guess
    await update.message.reply_text(f"✅ {user.first_name} đã đoán số {guess}. Chờ kết thúc phiên để biết kết quả!")

# --- Tạo bảng rút tiền ---
c.execute('''
CREATE TABLE IF NOT EXISTS withdraws (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount INTEGER,
    status TEXT DEFAULT "pending", -- pending | approved | rejected
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()


# --- /rut ---
async def rut(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("📌 Cú pháp: /rut <số điểm>")
        return
    amount = int(context.args[0])
    
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE user_id=?", (user.id,))
    row = c.fetchone()
    
    if not row or row[0] < amount:
        await update.message.reply_text("⚠ Số dư không đủ hoặc chưa có tài khoản.")
    else:
        # gửi thông báo admin duyệt
        ADMIN_ID = 6993504486
        await context.bot.send_message(chat_id=ADMIN_ID,
                                       text=f"💰 Yêu cầu rút {amount} xu từ @{user.username} (ID: {user.id})")
        await update.message.reply_text(f"✅ Yêu cầu rút {amount} xu đã gửi admin.")
    conn.close()

    # Thông báo cho admin
    for admin in ADMIN_IDS:
        await context.bot.send_message(
            chat_id=admin,
            text=f"💸 User {user.first_name} ({user.id}) yêu cầu rút {amount} điểm.\n"
                 f"Duyệt lệnh bằng: `/duyet_rut {user.id} {amount}` hoặc từ chối: `/huy_rut {user.id} {amount}`"
        )
        #tao lenh tai xiu
async def taixiu(update, context):
    user = update.effective_user
    args = context.args  # đọc tham số người dùng nhập

    # Kiểm tra cú pháp
    if len(args) != 2:
        await update.message.reply_text("📌 Cách dùng: /taixiu [tài/xỉu] [số tiền ≥100]")
        return

    choice = args[0].lower()
    try:
        bet = int(args[1])
    except:
        await update.message.reply_text("⚠️ Số tiền phải là số nguyên.")
        return

    if bet < MIN_BET:
        await update.message.reply_text(f"⚠️ Cược tối thiểu {MIN_BET}đ.")
        return

    # Demo số dư (thay bằng DB khi có)
    balance = 1000
    if bet > balance:
        await update.message.reply_text("⚠️ Bạn không đủ số dư để cược.")
        return

    # Quay 3 xúc xắc
    dices = [random.randint(1,6) for _ in range(3)]
    total = sum(dices)
    result = "tài" if total >= 11 else "xỉu"

    # Áp dụng tỉ lệ admin
    import random
    if random.random() <= TAIXIU_WIN_RATE:
        final_result = choice  # cố tình thắng user
    else:
        final_result = result  # bình thường

    # Tính thắng thua
    if choice == final_result:
        balance += bet
        msg = f"🎲 Kết quả: {dices} → {total} ({final_result})\n✅ Bạn thắng {bet}đ!"
    else:
        balance -= bet
        msg = f"🎲 Kết quả: {dices} → {total} ({final_result})\n❌ Bạn thua {bet}đ!"

    await update.message.reply_text(msg)
    # set nhkem vu
async def setnhiemvu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = 5645750335  # Thay bằng ID admin
    user = update.effective_user

    if user.id != admin_id:
        await update.message.reply_text("⚠️ Bạn không có quyền sử dụng lệnh này.")
        return

    if not context.args:
        await update.message.reply_text(
            "📌 Cú pháp: /setnhiemvu <nhiệm vụ 1> ; <nhiệm vụ 2> ; ... ; <nhiệm vụ N>\n"
            "Ví dụ: /setnhiemvu Tham gia kênh ; Mời 1 bạn ; Điểm danh ; Chơi mini game"
        )
        return

    new_tasks = " ".join(context.args).split(";")
    global tasks  # tasks là danh sách nhiệm vụ hiển thị cho user
    tasks = [task.strip() for task in new_tasks]
    conn.commit()  # Nếu quên lệnh này, dữ liệu không lưu

    await update.message.reply_text("✅ Nhiệm vụ đã được cập nhật thành công!")
        # PHẦN 9: /thu - thú cưng mini game

# --- Tạo bảng thú cưng ---
c.execute('''
CREATE TABLE IF NOT EXISTS pets (
    user_id INTEGER PRIMARY KEY,
    name TEXT DEFAULT "Thú cưng",
    hunger INTEGER DEFAULT 50,    -- 0 no, 100 đói
    happiness INTEGER DEFAULT 50, -- 0 buồn, 100 vui
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()


# --- Hàm cập nhật trạng thái thú cưng (thời gian trôi đi -> đói, buồn) ---
def update_pet_status(user_id: int):
    import datetime
    from datetime import datetime as dt

    c.execute("SELECT hunger, happiness, last_update FROM pets WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if not row:
        return

    hunger, happiness, last_update = row
    last_update = dt.fromisoformat(last_update)

    now = dt.now()
    diff = (now - last_update).seconds // 3600  # số giờ trôi qua

    if diff > 0:
        hunger = min(100, hunger + diff * 5)       # càng lâu càng đói
        happiness = max(0, happiness - diff * 3)   # càng lâu càng buồn

    # Lưu lại
    c.execute("UPDATE pets SET hunger=?, happiness=?, last_update=CURRENT_TIMESTAMP WHERE user_id=?",
              (hunger, happiness, user_id))
    conn.commit()

# --- Lệnh /thu ---
async def thu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        conn = sqlite3.connect("users.db")
        c = conn.cursor()

        c.execute("SELECT name, hunger, happiness FROM pets WHERE user_id=?", (user.id,))
        pet = c.fetchone()

        if not pet:
            c.execute(
                "INSERT INTO pets (user_id, name, hunger, happiness) VALUES (?, ?, ?, ?)",
                (user.id, "Thú cưng của bạn", 50, 50)
            )
            conn.commit()
            pet = ("Thú cưng của bạn", 50, 50)

        name, hunger, happiness = pet
        conn.close()

        text = (
            f"🐾 *{name}* của bạn:\n\n"
            f"🍖 Đói: {hunger}/100\n"
            f"😊 Vui vẻ: {happiness}/100\n\n"
            f"Lệnh chăm sóc:\n"
            f"- `/choan` → cho ăn\n"
            f"- `/choi` → chơi với thú cưng"
        )
        await update.message.reply_text(text, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"❌ Bao Tri ( Fix ): {e}")


# --- Lệnh /choan ---
async def choan_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    update_pet_status(user.id)

    c.execute("SELECT hunger FROM pets WHERE user_id=?", (user.id,))
    hunger = c.fetchone()[0]

    hunger = max(0, hunger - 30)  # cho ăn giảm đói
    c.execute("UPDATE pets SET hunger=?, last_update=CURRENT_TIMESTAMP WHERE user_id=?", (hunger, user.id))
    conn.commit()

    await update.message.reply_text("🍖 Bạn đã cho thú cưng ăn, nó đã no hơn!")


# --- Lệnh /choi ---
async def choi_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    update_pet_status(user.id)

    c.execute("SELECT happiness FROM pets WHERE user_id=?", (user.id,))
    happiness = c.fetchone()[0]

    happiness = min(100, happiness + 20)  # chơi tăng vui vẻ
    c.execute("UPDATE pets SET happiness=?, last_update=CURRENT_TIMESTAMP WHERE user_id=?", (happiness, user.id))
    conn.commit()

    await update.message.reply_text("🎲 Bạn đã chơi cùng thú cưng, nó rất vui vẻ!")
    # PHẦN 10: /admin - quản lý toàn hệ thống

# --- Lệnh /duyet <user_id> <mission_id> ---
async def duyet_mission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    if len(context.args) < 2:
        await update.message.reply_text("❌ Cú pháp: /duyet <user_id> <mission_id>")
        return

    try:
        user_id = int(context.args[0])
        mission_id = int(context.args[1])
    except ValueError:
        await update.message.reply_text("⚠️ user_id và mission_id phải là số.")
        return

    # Lấy thông tin nhiệm vụ
    c.execute("SELECT reward, title FROM missions WHERE id=?", (mission_id,))
    mission = c.fetchone()
    if not mission:
        await update.message.reply_text("❌ Nhiệm vụ không tồn tại.")
        return

    reward, title = mission

    # Kiểm tra user có pending không
    c.execute("SELECT status FROM user_missions WHERE user_id=? AND mission_id=?", (user_id, mission_id))
    status = c.fetchone()
    if not status or status[0] != "pending":
        await update.message.reply_text("⚠️ User chưa nhận hoặc đã duyệt nhiệm vụ này.")
        return

    # Cập nhật user_missions
    c.execute("UPDATE user_missions SET status='approved' WHERE user_id=? AND mission_id=?", (user_id, mission_id))

    # Cộng điểm
    c.execute("UPDATE users SET points = points + ? WHERE user_id=?", (reward, user_id))
    conn.commit()

    await update.message.reply_text(f"✅ Đã duyệt nhiệm vụ '{title}' cho user {user_id} (+{reward} điểm).")
    await context.bot.send_message(chat_id=user_id, text=f"🎉 Nhiệm vụ '{title}' đã được admin duyệt. Bạn nhận +{reward} điểm!")


# --- Lệnh /duyet_rut <user_id> <amount> ---
async def duyet_rut(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    if len(context.args) < 2:
        await update.message.reply_text("❌ Cú pháp: /duyet_rut <user_id> <amount>")
        return

    try:
        user_id = int(context.args[0])
        amount = int(context.args[1])
    except ValueError:
        await update.message.reply_text("⚠️ user_id và amount phải là số.")
        return

    # Cập nhật rút tiền
    c.execute("UPDATE withdraws SET status='approved' WHERE user_id=? AND amount=? AND status='pending'",
              (user_id, amount))
    conn.commit()

    await update.message.reply_text(f"💸 Đã duyệt rút {amount} điểm cho user {user_id}.")
    await context.bot.send_message(chat_id=user_id, text=f"✅ Yêu cầu rút {amount} điểm của bạn đã được duyệt!")


# --- Lệnh /huy_rut <user_id> <amount> ---
async def huy_rut(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    if len(context.args) < 2:
        await update.message.reply_text("❌ Cú pháp: /huy_rut <user_id> <amount>")
        return

    try:
        user_id = int(context.args[0])
        amount = int(context.args[1])
    except ValueError:
        await update.message.reply_text("⚠️ user_id và amount phải là số.")
        return

    c.execute("UPDATE withdraws SET status='rejected' WHERE user_id=? AND amount=? AND status='pending'",
              (user_id, amount))
    conn.commit()

    await update.message.reply_text(f"❌ Đã từ chối rút {amount} điểm của user {user_id}.")
    await context.bot.send_message(chat_id=user_id, text=f"⚠️ Yêu cầu rút {amount} điểm của bạn đã bị từ chối.")


# --- Lệnh /add_nv <title> | <desc> | <reward> ---
async def add_nv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    msg = " ".join(context.args)
    if "|" not in msg:
        await update.message.reply_text("❌ Cú pháp: /add_nv <tiêu đề> | <mô tả> | <điểm thưởng>")
        return

    try:
        title, desc, reward = [x.strip() for x in msg.split("|")]
        reward = int(reward)
    except:
        await update.message.reply_text("⚠️ Sai cú pháp hoặc reward không hợp lệ.")
        return

    add_mission(title, desc, reward)
    await update.message.reply_text(f"✅ Đã thêm nhiệm vụ: {title} (+{reward} điểm)")


# --- Lệnh /add_code <CODE> <reward> ---
async def add_code_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    if len(context.args) < 2:
        await update.message.reply_text("❌ Cú pháp: /add_code <CODE> <reward>")
        return

    code = context.args[0].upper()
    try:
        reward = int(context.args[1])
    except:
        await update.message.reply_text("⚠️ reward phải là số.")
        return

    add_code(code, reward)
    await update.message.reply_text(f"✅ Đã thêm code {code} (+{reward} điểm).")


# --- Lệnh /broadcast <nội dung> ---
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    msg = " ".join(context.args)
    if not msg:
        await update.message.reply_text("❌ Cú pháp: /broadcast <nội dung>")
        return

    c.execute("SELECT user_id FROM users")
    users = c.fetchall()

    count = 0
    for (uid,) in users:
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 Thông báo từ admin:\n\n{msg}")
            count += 1
        except:
            pass

    await update.message.reply_text(f"✅ Đã gửi thông báo cho {count} người dùng.")
    # PHẦN 11: /menu và /rules

# --- Lệnh /menu (chỉ user) ---
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 *Menu Hướng Dẫn Lệnh*\n\n"
        "👤 Tài khoản:\n"
        "  • /start → bắt đầu\n"
        "  • /menu → menu lệnh\n"
        "  • /rules → luật lệ\n"
        "  • /profile → xem thông tin tài khoản\n\n"
        "🎁 Điểm thưởng:\n"
        "  • /diemdanh → điểm danh hàng ngày\n"
        "  • /code <MÃ> → nhập code thưởng\n"
        "  • /ref → lấy link giới thiệu bạn bè\n\n"
        "📌 Nhiệm vụ:\n"
        "  • /nhiemvu → danh sách nhiệm vụ\n"
        "  • /nhan <ID> → nhận nhiệm vụ\n\n"
        "💸 Rút tiền:\n"
        "  • /rut <số điểm> → yêu cầu rút (tối thiểu 20k)\n\n"
        "💰 Nạp tiền:\n"
        "  • /nap → xem hướng dẫn nạp tiền\n\n"
        "🐾 Thú cưng:\n"
        "  • /thu → xem trạng thái thú cưng\n"
        "  • /choan → cho thú cưng ăn\n"
        "  • /choi → chơi với thú cưng\n"
        "🎲 Mini-game:\n"
        " • /taixiu <tài/xỉu> <số tiền>\n"
        " • /xoso <số từ 1–10> → đoán số may mắn (60 giây mỗi phiên)\n\n"
        "📞 Hỗ trợ / CSKH:\n"
        " • /support → liên hệ admin hoặc nhận hướng dẫn\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


# --- Lệnh /rules ---
async def rules_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📜 *Nội Quy & Luật Lệ*\n\n"
        "1. Không spam, gian lận hoặc dùng tool cheat.\n"
        "2. Mỗi nhiệm vụ phải hoàn thành thật, đúng yêu cầu.\n"
        "3. Nếu vi phạm → có thể bị khoá tài khoản và mất toàn bộ điểm.\n"
        "4. Điểm chỉ quy đổi thành tiền khi đủ số dư tối thiểu 20k.\n"
        "5. Admin có toàn quyền xử lý tranh chấp.\n\n"
        "👉 Khi sử dụng bot tức là bạn đã đồng ý với các điều khoản trên."
    )
    await update.message.reply_text(text, parse_mode="Markdown")
    # --- Người dùng xem nhiệm vụ ---
async def nhiemvu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect("vipbot.db")
    c = conn.cursor()
    c.execute("SELECT id, description FROM tasks")
    tasks = c.fetchall()
    conn.close()

    if not tasks:
        return await update.message.reply_text("📭 Hiện chưa có nhiệm vụ nào.\n👉 Hãy quay lại sau!")

    text = "🎯 *Nhiệm vụ hôm nay:*\n\n"
    for tid, desc in tasks:
        text += f"{tid}. {desc}\n"

    text += "\n👉 Hoàn thành nhiệm vụ và dung lenh #hoanthanh_1,2,3 (so nhiem vu) báo admin để nhận thưởng!"
    await update.message.reply_text(text, parse_mode="Markdown")
    # --- PHẦN: /choan ---
async def choan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    text = (
        f"🍖 Bạn {user} vừa cho thú cưng ăn!\n"
        "🐶 Thú cưng vui vẻ hơn và bạn nhận được +1 xu thưởng."
    )
    await update.message.reply_text(text)
    # --- /nhan ---
async def nhan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args:
        await update.message.reply_text("⚠️ Vui lòng nhập ID nhiệm vụ. Ví dụ: /nhan 1")
        return

    task_id = context.args[0]
    # Ở đây bạn có thể kiểm tra task_id có hợp lệ hay không
    # và cập nhật số nhiệm vụ đã làm trong DB
    await update.message.reply_text(f"✅ Bạn đã nhận nhiệm vụ {task_id}. Hoàn thành để nhận thưởng!")
    # --- PHẦN: /choi ---
async def choi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🎮 *Khu vui chơi mini game*\n\n"
        "1. Gõ /choan để cho thú cưng ăn.\n"
        "2. Gõ /diemdanh để nhận thưởng hàng ngày.\n"
        "3. Sắp tới sẽ có thêm nhiều game nhỏ khác..."
    )
    await update.message.reply_text(text, parse_mode="Markdown")
    # --- PHẦN: /addnv (Admin thêm nhiệm vụ) ---
async def addnv_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Chỉ cho admin dùng (thay YOUR_ADMIN_ID bằng ID Telegram của bạn)
    ADMIN_ID = 5645750335  
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")
        return
    
    if not context.args:
        await update.message.reply_text("📌 Cách dùng: /addnv [nội dung nhiệm vụ]")
        return
    
    task = " ".join(context.args)
    conn.commit()  # Nếu quên lệnh này, dữ liệu không lưu
    
    # Ở đây demo: chỉ in ra nhiệm vụ
    # Sau này bạn có thể lưu vào file JSON hoặc DB
    await update.message.reply_text(f"✅ Đã thêm nhiệm vụ mới:\n👉 {task}")
    # --- PHẦN: /delnv (Admin xoá nhiệm vụ) ---
async def delnv_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # ID admin, thay bằng ID Telegram của bạn
    ADMIN_ID = 5645750335 
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")
        return
    
    if not context.args:
        await update.message.reply_text("📌 Cách dùng: /delnv [tên nhiệm vụ]")
        return
    
    task = " ".join(context.args)
    
    # Demo: chỉ in ra nhiệm vụ bị xoá
    # Sau này bạn có thể xoá trong file JSON/DB
    await update.message.reply_text(f"🗑️ Đã xoá nhiệm vụ:\n👉 {task}")
    # --- PHẦN: /duyet (Admin duyệt yêu cầu) ---
async def duyet_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Thay bằng ID admin của bạn
    ADMIN_ID = 5645750335 
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")
        return
    
    if not context.args:
        await update.message.reply_text("📌 Cách dùng: /duyet [ID người dùng] [nội dung]")
        return
    
    target_id = context.args[0]
    reason = " ".join(context.args[1:]) if len(context.args) > 1 else "Không có ghi chú"
    
    text = (
        f"✅ Đã duyệt yêu cầu của user `{target_id}`\n"
        f"📌 Lý do: {reason}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")
    
    # --- PHẦN: /duyetrut (Admin duyệt rút tiền) ---
async def duyetrut_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # ID admin của bạn
    ADMIN_ID = 5645750335 
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("📌 Cách dùng: /duyetrut [ID người dùng] [số tiền]")
        return
    
    target_id = context.args[0]
    amount = context.args[1]
    
    # Demo: chỉ thông báo đã duyệt
    text = f"✅ Yêu cầu rút {amount}đ của user `{target_id}` đã được duyệt."
    await update.message.reply_text(text, parse_mode="Markdown")
    
    # Sau này có thể trừ số dư và gửi thông báo cho user
    # context.bot.send_message(chat_id=target_id, text=f"💸 Yêu cầu rút {amount}đ của bạn đã được duyệt!")
    # --- PHẦN: /thongbao (Admin gửi thông báo toàn server) ---
async def thongbao_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # ID admin của bạn
    ADMIN_ID = 5645750335 
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")
        return
    
    if not context.args:
        await update.message.reply_text("📌 Cách dùng: /thongbao [nội dung thông báo]")
        return
    
    message = " ".join(context.args)
    
    # Demo: chỉ gửi phản hồi cho admin
    # Sau này bạn có thể lặp qua DB users và gửi message cho tất cả
    await update.message.reply_text(f"📢 Thông báo đã gửi toàn server:\n\n{message}")
    # --- Hàm kiểm tra giới hạn nhiệm vụ hàng ngày ---
def check_daily_limit(user_id, username):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    # Thêm user nếu chưa có
    c.execute("SELECT tasks_done, last_reset FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if not row:
        c.execute(
            "INSERT INTO users (user_id, username, tasks_done, last_reset) VALUES (?, ?, 0, '')",
            (user_id, username)
        )
        conn.commit()
        tasks_done = 0
        last_reset = ''
    else:
        tasks_done, last_reset = row

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    if last_reset != today:
        # reset mỗi ngày
        tasks_done = 0
        c.execute(
            "UPDATE users SET tasks_done=0, last_reset=? WHERE user_id=?",
            (today, user_id)
        )
        conn.commit()

    conn.close()
    return tasks_done < 10  # True nếu chưa đạt giới hạn 10 nhiệm vụ
    # --- Admin xoá nhiệm vụ ---
async def delnhiemvu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")

    if not context.args or not context.args[0].isdigit():
        return await update.message.reply_text("⚠️ Dùng đúng cú pháp: /delnhiemvu <id>")

    task_id = int(context.args[0])

    conn = sqlite3.connect("vipbot.db")
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()

    await update.message.reply_text(f"🗑️ Đã xoá nhiệm vụ có ID {task_id}")


# --- Admin liệt kê nhiệm vụ ---
async def listnhiemvu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect("vipbot.db")
    c = conn.cursor()
    c.execute("SELECT id, description FROM tasks")
    tasks = c.fetchall()
    conn.close()

    if not tasks:
        return await update.message.reply_text("📭 Hiện chưa có nhiệm vụ nào.")

    text = "📋 *Danh sách nhiệm vụ:*\n\n"
    for tid, desc in tasks:
        text += f"{tid}. {desc}\n"

    await update.message.reply_text(text, parse_mode="Markdown")
    conn.commit()  # Nếu quên lệnh này, dữ liệu không lưu
        # --- PHẦN: /nap_request (gửi yêu cầu nạp cho admin) ---
async def nap_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ADMIN_ID = 5645750335  # Thay bằng ID admin
    if context.args:
        try:
            amount = int(context.args[0])
            if amount < 1000:
                await update.message.reply_text("⚠ Số tiền tối thiểu là 1.000đ.")
                return
            # Thông báo user
            await update.message.reply_text(
                f"✅ Yêu cầu nạp {amount}đ đã gửi đến admin, chờ duyệt."
            )
            # Thông báo admin
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"Người dùng {user.first_name} (@{user.username}, ID: {user.id}) muốn nạp {amount}đ."
            )
        except ValueError:
            await update.message.reply_text("⚠ Vui lòng nhập số hợp lệ, ví dụ: /nap_request 50000")
    else:
        await update.message.reply_text(
            "💳 Hướng dẫn nạp tiền:\n"
            "- Chuyển tiền vào TK: 123445799\n"
            "- Chủ TK: Nguyen Van A\n"
            "- Nội dung: nap <uid telegram bạn>\n\n"
            "Sau khi chuyển xong, dùng lệnh /nap_request <số tiền> để thông báo admin."
        )
 # --- Handler /duyet_task ---
async def approve_task(update, context):
    # Kiểm tra admin
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Bạn không phải admin!")
        return

    # Kiểm tra cú pháp: /duyet_task user_id task_id
    if len(context.args) != 2:
        await update.message.reply_text("Cú pháp: /duyet_task user_id task_id")
        return

    try:
        user_id = int(context.args[0])
        task_id = int(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ User ID và Task ID phải là số!")
        return

    # Cập nhật trạng thái nhiệm vụ
    c.execute('''
    UPDATE user_tasks SET status='approved'
    WHERE user_id=? AND task_id=?
    ''', (user_id, task_id))
    conn.commit()

    await update.message.reply_text(f"✅ Nhiệm vụ {task_id} của user {user_id} đã được duyệt!")
    # --- Handler /duyet_tasks (liệt kê tất cả nhiệm vụ pending) ---
async def list_pending_tasks(update, context):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Bạn không phải admin!")
        return

    c.execute("""
    SELECT user_id, task_id, status
    FROM user_tasks
    WHERE status='pending'
    """)
    rows = c.fetchall()

    if not rows:
        await update.message.reply_text("📭 Hiện không có nhiệm vụ nào đang chờ duyệt.")
        return

    msg = "📋 **Danh sách nhiệm vụ pending:**\n\n"
    for user_id, task_id, status in rows:
        msg += f"User: {user_id} | Task: {task_id} | Trạng thái: {status}\n"
    
    await update.message.reply_text(msg, parse_mode='Markdown')


# --- /duyetnap admin duyệt ---
async def duyetnap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ADMIN_ID = 5645750335
    if update.effective_user.id != ADMIN_ID:
        return
    if len(context.args) != 2:
        await update.message.reply_text("📌 Cú pháp: /duyetnap <user_id> <số tiền>")
        return
    user_id = int(context.args[0])
    amount = int(context.args[1])
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, user_id))
    conn.commit()
    conn.close()
    await update.message.reply_text(f"✅ Đã cộng {amount}đ cho user {user_id}.")
async def main():
    app = Application.builder().token(TOKEN).build()
    
    # --- Handler user ---
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_handler))
    app.add_handler(CommandHandler("rules", rules_handler))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("diemdanh", diemdanh))
    app.add_handler(CommandHandler("code", code_handler))
    app.add_handler(CommandHandler("ref", ref))
    app.add_handler(CommandHandler("thu", thu))
    app.add_handler(CommandHandler("nhiemvu", nhiemvu))
    app.add_handler(CommandHandler("choan", choan))
    app.add_handler(CommandHandler("choi", choi))
    app.add_handler(CommandHandler("taixiu", taixiu))
    app.add_handler(CommandHandler("nap", nap))
    app.add_handler(CommandHandler("xoso", xoso))
    app.add_handler(CommandHandler("support", support))
    app.add_handler(CommandHandler("nhan", nhan))
    app.add_handler(CommandHandler("rut", rut))
    app.add_handler(CommandHandler("hoanthanh_1", submit_task))

    # --- Handler admin ---
    app.add_handler(CommandHandler("duyet_tasks", list_pending_tasks))
    app.add_handler(CommandHandler("addnv", addnv_handler))
    app.add_handler(CommandHandler("delnv", delnv_handler))
    app.add_handler(CommandHandler("duyet", duyet_handler))
    app.add_handler(CommandHandler("duyetrut", duyetrut_handler))
    app.add_handler(CommandHandler("thongbao", thongbao_handler))
    app.add_handler(CommandHandler("nap_request", nap_request))
    app.add_handler(CommandHandler("start_xoso", start_xoso))
    app.add_handler(CommandHandler("duyetnap", duyetnap))
    app.add_handler(CommandHandler("setnhiemvu", setnhiemvu))
    app.add_handler(CommandHandler("delnhiemvu", delnhiemvu))
    app.add_handler(CommandHandler("listnhiemvu", listnhiemvu))

    print("🤖 Bot đang chạy...")
    await app.run_polling()


import asyncio

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())