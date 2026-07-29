# Báo cáo - Group 29 (E403)

## Phần A: Giới thiệu Agent

### 1. Agent làm được gì?
Agent của nhóm chúng tôi là một trợ lý nghiên cứu mạnh mẽ, có khả năng:
- Tìm kiếm thông tin mới nhất trên mạng internet (`lookup`).
- Truy xuất và tóm tắt nội dung từ các trang web cụ thể (`fetch`).
- Đọc bài đăng gần đây của một cá nhân cụ thể trên mạng xã hội (`timeline`).
- Tìm kiếm thông tin thảo luận trên mạng xã hội theo từ khóa (`social_search`).
- Định dạng và tổng hợp thông tin một cách ngăn nắp (`format`).
- Xác nhận các hành động nhạy cảm (như gửi tin nhắn) trước khi thực hiện để đảm bảo an toàn (`clarify`).
- Đặc biệt, Agent được trang bị thêm các công cụ quản lý và xử lý dữ liệu nghiên cứu nâng cao do nhóm tự phát triển (`save_note`, `deduplicate_sources`, `rank_sources`, `compare_sources`).

### 2. Danh sách các Tools

| Tên Tool | Chức năng | Phân loại |
|---|---|---|
| `lookup` | Tra cứu thông tin, tin tức mới nhất theo topic trên web. | Core |
| `fetch` | Trích xuất nội dung từ một URL cụ thể. | Core |
| `timeline` | Xem các bài đăng gần đây của một handle. | Core |
| `social_search` | Tìm kiếm bài đăng trên MXH bằng từ khóa. | Core |
| `format` | Định dạng các thông tin thành markdown digest. | Core |
| `clarify` | Hỏi lại khi thiếu thông tin hoặc xin xác nhận hành động nhạy cảm. | Core |
| `send` | Gửi tin nhắn ra bên ngoài (cần xác nhận trước). | Core (Action) |
| `save_note` | Ghi chú lại thông tin quan trọng vào file `saved_notes.txt`. | **Mới (Bắt buộc)** |
| `deduplicate_sources` | Loại bỏ các kết quả nghiên cứu bị trùng lặp. | **Mới (Bonus)** |
| `rank_sources` | Xếp hạng các nguồn dựa trên mức khớp từ khóa và điểm relevance. | **Mới (Bonus)** |
| `compare_sources` | So sánh từ khóa giữa hai nguồn thông tin. | **Mới (Bonus)** |

### 3. Câu hỏi mẫu để dùng thử
- *"Tìm tin tức mới nhất về OpenAI trong tuần này."* (Test: lookup)
- *"Ghi chú lại những ý chính của bài viết này giúp tôi: https://example.com"* (Test: fetch + save_note)
- *"Gửi lời chúc mừng năm mới lên group sếp."* (Test: clarify boundary -> send)
- *"Xem Elon Musk dạo này đăng gì."* (Test: clarify missing handle -> timeline)

### 4. Link dùng thử (Public UI)
- Trải nghiệm Agent tại đây: **[Chờ update URL từ Đức Anh]**

---

## Phần B: Chi tiết / Bằng chứng
*(Đang cập nhật - Sẽ hoàn thiện sau khi chạy xong v3 và có đầy đủ run logs).*
