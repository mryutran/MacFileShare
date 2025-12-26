# 🍎 Mac File Share

**Chia sẻ file dễ dàng giữa các thiết bị qua WiFi - Mac, iPhone, Android, Windows, Linux**

---

## 📋 Mục lục

- [Giới thiệu](#-giới-thiệu)
- [Yêu cầu](#-yêu-cầu)
- [Cài đặt](#-cài-đặt)
- [Sử dụng](#-sử-dụng)
- [Khắc phục sự cố](#-khắc-phục-sự-cố)
- [Tính năng](#-tính-năng)

---

## 🎯 Giới thiệu

WiFi File Share là công cụ đơn giản giúp bạn chia sẻ file giữa các thiết bị thông qua mạng WiFi nội bộ. Không cần cài đặt app, không cần AirDrop, chỉ cần copy URL từ terminal và paste vào trình duyệt web trên bất kỳ thiết bị nào!

---

## 📌 Yêu cầu

- **Mac**: macOS với Python 3 (đã cài sẵn)
- **iPhone**: Safari hoặc trình duyệt bất kỳ
- **Mạng**: Mac và iPhone phải **cùng kết nối một mạng WiFi**

---

## 🚀 Cài đặt

### Bước 1: Cấp quyền truy cập (Quan trọng!)

macOS bảo vệ một số thư mục như Downloads, Documents, Desktop. Để chia sẻ các thư mục này, bạn cần cấp quyền:

1. Mở **System Settings** (Cài đặt hệ thống)
2. Vào **Privacy & Security** → **Full Disk Access**
3. Nhấn **+** và thêm **Terminal** (hoặc iTerm nếu bạn dùng)
4. **Khởi động lại Terminal**

> 💡 **Khuyến nghị**: Dùng `~/Public/ShareFiles` để không cần cấp quyền Full Disk Access

### Bước 2: Tải về

```bash
# Clone hoặc tải về thư mục MacFileShare
cd ~/MacFileShare
```

---

## 💻 Sử dụng

```bash
# Chia sẻ thư mục Public (không cần cấp quyền - khuyến nghị)
python3 server.py ~/Public/ShareFiles

# Chia sẻ thư mục Downloads
python3 server.py ~/Downloads

# Chia sẻ với port tùy chọn
python3 server.py ~/Pictures 9000
```

---

## 📱 Truy cập từ bất kỳ thiết bị nào

1. **Đảm bảo** máy Mac và thiết bị đích cùng kết nối **một mạng WiFi**

2. **Mở trình duyệt web** trên thiết bị đích (Safari, Chrome, Firefox, Edge...)

3. **Copy URL từ terminal** và paste vào trình duyệt

4. **Tải file**: Nhấn vào file bất kỳ để download về thiết bị

5. **Upload file**: Cuộn xuống cuối trang, chọn file và nhấn Upload

**✅ Hỗ trợ tất cả thiết bị:**
- 📱 iPhone / iPad
- 🤖 Android phones / tablets
- 💻 Windows PC / Laptop
- 🐧 Linux PC / Laptop
- 🍎 Mac khác

---

## 🔧 Khắc phục sự cố

### ❌ Lỗi "Permission Denied" hoặc "Operation not permitted"

**Nguyên nhân**: macOS chặn quyền truy cập thư mục Downloads/Documents/Desktop

**Giải pháp**:
1. Mở **System Settings** → **Privacy & Security** → **Full Disk Access**
2. Thêm **Terminal** vào danh sách
3. Khởi động lại Terminal
4. Chạy lại server

**Hoặc** dùng thư mục không cần quyền:
```bash
python3 server.py ~/Public/ShareFiles
```

---

### ❌ Lỗi "Address already in use"

**Nguyên nhân**: Port 8888 đang bị chiếm bởi process khác

**Giải pháp 1**: Dùng port khác
```bash
python3 server.py ~/Downloads 9999
```

**Giải pháp 2**: Kill process đang chiếm port
```bash
lsof -ti :8888 | xargs kill -9
```

---

### ❌ iPhone không truy cập được

**Kiểm tra**:
1. ✅ Mac và iPhone **cùng mạng WiFi**?
2. ✅ Đã nhập đúng địa chỉ IP?
3. ✅ Server đang chạy (không có lỗi trong Terminal)?
4. ✅ Firewall có chặn kết nối không?

**Tắt Firewall tạm thời**:
- **System Settings** → **Network** → **Firewall** → Tắt

---

### ❌ Upload file không hoạt động

**Nguyên nhân**: Lỗi phân tích dữ liệu multipart hoặc quyền truy cập file

**Giải pháp**:
1. Kiểm tra Terminal xem có lỗi khi upload không
2. Đảm bảo thư mục chia sẻ có quyền ghi
3. Thử upload file nhỏ trước (dưới 10MB)
4. Kiểm tra firewall không chặn kết nối

---

## ✨ Tính năng

| Tính năng | Mô tả |
|-----------|-------|
| 📥 **Download** | Tải file từ Mac về iPhone |
| 📤 **Upload** | Tải file từ iPhone lên Mac *(Đã cải thiện)* |
| 📁 **Duyệt thư mục** | Xem và mở các thư mục con |
| 🎨 **Giao diện đẹp** | Tối ưu cho mobile, dark theme |
| 🔍 **Icon thông minh** | Hiển thị icon theo loại file |

---

## 📝 Ví dụ sử dụng

### Chia sẻ thư mục Public (Khuyến nghị - không cần cấp quyền)
```bash
# Tạo thư mục chia sẻ
mkdir -p ~/Public/ShareFiles

# Chạy server
python3 server.py ~/Public/ShareFiles
```

### Chia sẻ thư mục Downloads
```bash
cd ~/MacFileShare
python3 server.py ~/Downloads
```

### Chia sẻ thư mục ảnh
```bash
python3 server.py ~/Pictures 8080
```

### Chia sẻ thư mục project
```bash
python3 server.py ~/Projects/MyApp
```

---

## ⌨️ Phím tắt

| Phím | Chức năng |
|------|-----------|
| `Ctrl + C` | Dừng server |

---

## 🔒 Bảo mật

⚠️ **Lưu ý quan trọng**:
- Server chỉ hoạt động trong mạng nội bộ (LAN)
- Bất kỳ ai trong cùng mạng WiFi đều có thể truy cập
- **Không nên** chạy server khi kết nối WiFi công cộng
- Tắt server ngay khi không sử dụng

---

## 📞 Hỗ trợ

Nếu gặp vấn đề, hãy kiểm tra:
1. Terminal có hiển thị lỗi gì không
2. Đã cấp quyền Full Disk Access chưa
3. Mac và iPhone có cùng mạng WiFi không

---

**Made with ❤️ by Phong Tran**  
📧 [mr.yutran@gmail.com](mailto:mr.yutran@gmail.com)
