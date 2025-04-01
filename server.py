from flask import Flask, request
import random
import string
import time

app = Flask(__name__)

# Lưu trữ thông tin về key, IP, và thời gian cấp key
keys = {}
# Danh sách key đã được cấp phát
used_keys = set()
# Giới hạn số lượng key mỗi ngày
max_keys_per_day = 2000
# Tổng số key cấp trong ngày
key_count_today = 0
# Thời gian reset key (mỗi ngày)
reset_time = time.time()

def generate_key():
    """Generate a random key."""
    return "MH-" + ''.join(random.choices(string.digits, k=10))

def reset_key_count():
    """Reset số lượng key cấp mỗi ngày khi ngày mới đến."""
    global key_count_today, reset_time
    if time.time() - reset_time >= 86400:  # 86400 giây = 1 ngày
        key_count_today = 0
        reset_time = time.time()

@app.route('/get-key', methods=['GET'])
def get_key():
    global key_count_today

    # Reset số lượng key nếu là ngày mới
    reset_key_count()

    # Kiểm tra xem request có đến từ link YeuMoney không
    referrer = request.headers.get("Referer", "")
    if "yeumoney" not in referrer:
        return "Bạn phải vượt link YeuMoney để lấy key!", 403

    # Kiểm tra giới hạn số lượng key mỗi ngày
    if key_count_today >= max_keys_per_day:
        return "Hết key, vui lòng thử lại sau!", 403

    # Lấy IP của người dùng
    ip = request.remote_addr

    # Kiểm tra xem IP đã lấy key chưa
    if ip in keys:
        # Kiểm tra xem key đã hết hạn chưa
        key_data = keys[ip]
        if time.time() > key_data["expires_at"]:
            del keys[ip]  # Xóa key nếu đã hết hạn
            return "Key của bạn đã hết hạn, vui lòng lấy lại key!", 403
        return f"Bạn đã có key hợp lệ. Key của bạn là: {key_data['key']}"

    # Tạo key mới
    new_key = generate_key()

    # Kiểm tra xem key đã được sử dụng cho IP khác chưa
    if new_key in used_keys:
        return "Key này đã được sử dụng rồi, vui lòng thử lại!"

    # Gán key cho IP và đánh dấu key đã sử dụng
    expiration_time = time.time() + 86400  # 86400 giây = 24h
    keys[ip] = {"key": new_key, "expires_at": expiration_time}
    used_keys.add(new_key)
    key_count_today += 1

    return f"Key của bạn là: {new_key}"

@app.route('/check-key', methods=['GET'])
def check_key():
    # Kiểm tra xem IP có key hợp lệ không
    ip = request.remote_addr
    if ip not in keys:
        return "Bạn chưa có key hoặc key đã hết hạn.", 403

    key_data = keys[ip]
    key = key_data["key"]
    expires_at = key_data["expires_at"]

    # Kiểm tra thời gian hết hạn
    if time.time() > expires_at:
        del keys[ip]  # Xóa key nếu đã hết hạn
        return "Key của bạn đã hết hạn.", 403

    return f"Key của bạn vẫn còn hiệu lực. Key: {key}"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
