# Ghi chú của Tuấn Anh (Tool Dev A)

## Thông tin Tool
- **Tên tool:** `save_note`
- **Chức năng chính:** Ghi chú lại các thông tin nghiên cứu hoặc phát hiện quan trọng vào một file văn bản (`saved_notes.txt`). File này được dùng để lưu trữ lâu dài.

## Agent Guidelines (Khi nào nên gọi tool này)
- Agent nên dùng tool này khi người dùng yêu cầu rõ ràng như "lưu lại", "ghi chú lại", "lưu nháp" một thông tin cụ thể nào đó.
- Khuyến nghị Agent **tổng hợp** thông tin trước, sau đó mới gọi lệnh ghi một lần cho mỗi chủ đề, tránh việc gọi tool này liên tục, vụn vặt và thiếu mạch lạc.
