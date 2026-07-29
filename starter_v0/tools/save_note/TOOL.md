---
name: save_note
track: bonus
kind: action
requires_env: []
inputs: [topic, content]
outputs: [error, message, topic]
side_effect: local_file_write
---
# save_note

Tool để ghi chú lại các thông tin nghiên cứu hoặc phát hiện quan trọng vào một file văn bản. File này được dùng để lưu trữ lâu dài.

## Implementation logic
- Mở (hoặc tạo) file `saved_notes.txt` tại thư mục hiện tại.
- Append tiêu đề (topic) và nội dung (content).
- Trả về thông báo thành công hoặc lỗi.

## Agent Guidelines
- Dùng khi người dùng yêu cầu "lưu lại", "ghi chú lại", "lưu nháp" một thông tin cụ thể.
- Tránh gọi tool này quá nhiều lần lắt nhắt; thay vì thế, hãy tổng hợp thông tin trước rồi gọi lưu 1 lần cho mỗi chủ đề.
- Ghi vào file cục bộ, không gửi ra ngoài, nên **không** cần `clarify(response_type="yes_no")` trước khi gọi — khác với `send`.
