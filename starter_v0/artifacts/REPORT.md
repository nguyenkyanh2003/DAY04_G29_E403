hoàn

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

| Tên Tool               | Chức năng                                                                   | Phân loại                 |
| ----------------------- | ----------------------------------------------------------------------------- | --------------------------- |
| `lookup`              | Tra cứu thông tin, tin tức mới nhất theo topic trên web.                | Core                        |
| `fetch`               | Trích xuất nội dung từ một URL cụ thể.                                 | Core                        |
| `timeline`            | Xem các bài đăng gần đây của một handle.                             | Core                        |
| `social_search`       | Tìm kiếm bài đăng trên MXH bằng từ khóa.                             | Core                        |
| `format`              | Định dạng các thông tin thành markdown digest.                          | Core                        |
| `clarify`             | Hỏi lại khi thiếu thông tin hoặc xin xác nhận hành động nhạy cảm. | Core                        |
| `send`                | Gửi tin nhắn ra bên ngoài (cần xác nhận trước).                      | Core (Action)               |
| `save_note`           | Ghi chú lại thông tin quan trọng vào file`saved_notes.txt`.            | **Mới (Bắt buộc)** |
| `deduplicate_sources` | Loại bỏ các kết quả nghiên cứu bị trùng lặp.                        | **Mới (Bonus)**      |
| `rank_sources`        | Xếp hạng các nguồn dựa trên mức khớp từ khóa và điểm relevance.  | **Mới (Bonus)**      |
| `compare_sources`     | So sánh từ khóa giữa hai nguồn thông tin.                               | **Mới (Bonus)**      |

### 3. Câu hỏi mẫu để dùng thử

- *"Tìm tin tức mới nhất về OpenAI trong tuần này."* (Test: lookup)
- *"Ghi chú lại những ý chính của bài viết này giúp tôi: https://example.com"* (Test: fetch + save_note)
- *"Gửi lời chúc mừng năm mới lên group sếp."* (Test: clarify boundary -> send)
- *"Xem Elon Musk dạo này đăng gì."* (Test: clarify missing handle -> timeline)

### 4. Link dùng thử (Public UI)

- Trải nghiệm Agent tại đây: **[Chờ update URL từ Đức Anh]**

---

## Phần B: Chi tiết / Bằng chứng

### 1. Bảng Metric & Hypothesis (v0 - v3)

| Version | Hypothesis | Case Accuracy | Routing Accuracy | Argument Accuracy | Multiturn Accuracy |
|---|---|---:|---:|---:|---:|
| **v0 (Base)** | Dùng prompt gốc, đo đạc hiện trạng. | 65.0% | 75.0% | 65.0% | 100.0% |
| **v1** | *Nếu yêu cầu dùng `clarify` khi thiếu URL/handle và hỏi `yes_no` trước khi `send`, lỗi missing info sẽ giảm.* | 90.0% | 95.0% | 90.0% | 83.3% |
| **v2** | *Nếu làm rõ quy tắc đổi tool (lookup sang social_search), agent sẽ không bị neo vào context cũ, sửa lỗi multi-turn.* | 95.0% | 100.0% | 95.0% | 100.0% |
| **v3** | *Tinh chỉnh tham số của các tool nhóm tự viết (save_note, deduplicate_sources) và chốt luồng tích hợp.* | **100.0%** | **100.0%** | **100.0%** | **100.0%** |

### 2. Failure Analysis & Quá trình Tối ưu
* **Từ v0 lên v1:** Ở bản baseline, Agent thường xuyên tự bịa (hallucinate) tham số như `handle="sama"` hoặc gọi `send` ngay mà không thèm xin phép. Bằng việc cập nhật system prompt định nghĩa rõ boundary `clarify` và `yes_no`, các lỗi này (7 case hỏng) đã được vá, kéo accuracy v1 lên 90%.
* **Từ v1 lên v2:** Dù ngon hơn, v1 bị lỗi khi chat nhiều lượt (multi-turn). Agent bị dính "ngữ cảnh" của lượt trước và không chịu đổi tool khi user đổi yêu cầu. Bản v2 đã thêm rule ưu tiên lượt gần nhất để định tuyến tool.
* **Bản Final v3:** Agent chạy hoàn hảo 100% test cases (20 base + 10 nhóm tự viết).

### 3. Eval Cases của Nhóm (Team Eval)
Nhóm đã soạn 10 case (5 single-turn, 5 multi-turn) tập trung vào các lỗi thực tế (như không thèm hỏi handle, không xin phép trước khi gửi group). Danh sách case đã được commit trong `data/eval_group.json`.

### 4. Kết quả Live Chat (Trực tiếp)
Thử nghiệm live chat ở v3 đã thành công và được xuất ra 3 file logs trong thư mục `transcripts/`:
- `chat_01_normal_research`: Agent dùng đúng tool `lookup` với `topic="news"` thay vì bịa tin.
- `chat_02_missing_info`: Khi user bảo "tìm về ông ấy", Agent lập tức ngắt lại: "Tài khoản bạn muốn xem là gì?" bằng tool `clarify`. 
- `chat_03_confirmation`: User yêu cầu gửi tin nhắn, Agent hỏi xin xác nhận (Yes/No) cực kỳ chuẩn mực trước khi bắn hàm `send`.
