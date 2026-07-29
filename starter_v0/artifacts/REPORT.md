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
| **v2** | *Nếu mô tả rõ `yes_no` vs `text` trong `clarify` và phân định `lookup` vs `social_search`, agent sẽ hết nhầm boundary và hết neo vào context cũ.* | 90.0% | 95.0% | 90.0% | 83.3% |
| **v3** | *Nếu nói rõ `clarify` chỉ hỏi khi thiếu tham số BẮT BUỘC, và `screenname` dùng đúng handle user nêu, thì hết hỏi thừa và hết tự chuẩn hóa handle.* | 95.0% | 100.0% | 95.0% | 100.0% |
| **v4** | *Nếu đưa `response_type` vào `required` của `clarify`, model buộc phải nêu tường minh thay vì dựa vào default — vá `R11`.* | **100.0%** | **100.0%** | **100.0%** | **100.0%** |

### 1b. Suite group (10 case nhóm tự viết)

| Artifact | Case | Routing | Argument | Multiturn |
|---|---:|---:|---:|---:|
| v2 | 90.0% | 90.0% | 90.0% | 100.0% |
| v4 | **80.0%** | 90.0% | 80.0% | 100.0% |

`provider_error_cases` = 0 ở cả hai run.

**Đánh đổi quan sát được:** cùng những thay đổi đưa base eval từ 95% lên 100% lại kéo suite group từ 90% xuống 80%. Hai case hỏng ở v4:

- `G03_wrong_boundary_send` — "Gửi kết quả nghiên cứu tuần này lên group cho sếp". Agent gọi `clarify` nhưng chọn `text`, hỏi xin nội dung cụ thể thay vì hỏi yes/no. Câu này thực sự vừa thiếu nội dung vừa là hành động gửi, nên hành vi của agent không hẳn sai — chính case của nhóm mới là case ranh giới khó.
- `G04_missing_url` — "Tóm tắt bài báo về AI mới ra hôm qua cho tôi". Agent gọi `lookup(topic="news", timeframe="day")` thay vì hỏi lại URL. Đây cũng là cách diễn giải hợp lý: user không đưa link nhưng đi tìm bài AI mới ra hôm qua là việc làm được.

Kết luận: tối ưu bám một bộ eval cố định có thể làm agent kém linh hoạt trên bộ case khác. Con số base 100% không nên đọc là "agent hoàn hảo".

**Nhiễu đo:** v0 được chạy hai lần trên **cùng** `artifact_version` và ra 0.65 rồi 0.70. Metric có nhiễu khoảng ±0.05, nên chênh lệch nhỏ hơn ngưỡng đó giữa hai version không đủ để kết luận là cải thiện thật. Cả hai run đều nằm trong `runs/`.

### 2. Failure Analysis & Quá trình Tối ưu
* **Từ v0 lên v1:** Ở bản baseline, Agent thường xuyên tự bịa (hallucinate) tham số như `handle="sama"` hoặc gọi `send` ngay mà không thèm xin phép. Bằng việc cập nhật system prompt định nghĩa rõ boundary `clarify` và `yes_no`, các lỗi này (7 case hỏng) đã được vá, kéo accuracy v1 lên 90%.
* **v1 có regression:** tổng tăng lên 90% nhưng `multiturn_accuracy` tụt từ 100% xuống 83.3%. Case `M06_switch_tool` hỏng — user nói rõ "bỏ Twitter, chuyển sang web tin tức" mà agent vẫn gọi `social_search`. Prompt v1 chỉ dạy *khi nào dừng lại*, đã xoá mất phần hướng dẫn routing, nên việc phân biệt `lookup` vs `social_search` rơi hết về mô tả trong `tools.yaml` — vốn đang là "Tìm trên mạng xã hội." và "Tra cứu thông tin trên internet.", gần như vô nghĩa với model.
* **Từ v1 lên v2:** viết lại toàn bộ mô tả tool theo công thức *nói rõ khi nào dùng / khi nào không*, thêm luật ưu tiên `yes_no` khi request vừa thiếu info vừa là hành động gửi, và khai báo 4 tool mới. Hai case nhắm tới (`R12`, `M06`) đều PASS — giả thuyết đúng. **Nhưng tổng số đứng yên ở 90%** vì phát sinh 2 lỗi mới: `R01` (mô tả `clarify` viết quá mạnh khiến agent coi tham số tùy chọn `limit` là "thiếu thông tin" và hỏi thừa) và `M03` (agent tự chuẩn hóa "Karpathy" thành handle thật `andrejkarpathy`). Bài học: **một con số tổng không đổi che mất hai thay đổi ngược chiều nhau** — phải đọc từng case, không nhìn mỗi `case_accuracy`.
* **Từ v2 lên v3:** siết mô tả `clarify` (chỉ hỏi khi thiếu tham số bắt buộc; tham số tùy chọn dùng default) và thêm convention cho `screenname`. `R01` và `M03` đều PASS, `tool_routing_accuracy` đạt 100%, `multiturn_accuracy` về lại 100%.
* **Từ v3 lên v4:** case cuối còn fail là `R11_missing_url` — agent gọi `clarify` đúng, câu hỏi đúng ("Vui lòng cung cấp URL của bài viết"), nhưng **không truyền `response_type`** mà để rơi vào giá trị default, nên eval so khớp argument tính là sai. Đưa `response_type` vào `required` của `clarify` buộc model nêu tường minh → base eval đạt 20/20.

### 3. Eval Cases của Nhóm (Team Eval)
Nhóm đã soạn 10 case (5 single-turn, 5 multi-turn) tập trung vào các lỗi thực tế (như không thèm hỏi handle, không xin phép trước khi gửi group). Danh sách case đã được commit trong `data/eval_group.json`.

### 4. Kết quả Live Chat (Trực tiếp)
Thư mục `transcripts/` có 4 transcript thật do `chat.py` sinh ra, mỗi file đều kèm `prompt_hash` và `tools_hash` để đối chiếu:

| File | Câu hỏi | Tool agent gọi |
|---|---|---|
| `v0_openrouter_...162515` | "Xem các bài đăng gần đây của CEO OpenAI" | `clarify` — hỏi lại handle thay vì bịa |
| `v0_openrouter_...162756` | "Tweet mới nhất của Sam Altman là gì?" | `clarify` |
| `v2_openrouter_...162903` | "Tweet mới nhất của Sam Altman là gì?" | `clarify` |
| `v0_openrouter_...162540` | "lô ku" / "bạn là ai?" | không gọi tool — chitchat ngoài phạm vi |

**Lưu ý về nhãn version:** cờ `--version` của `chat.py` chỉ là nhãn đặt tên file, nó **không** nạp lại artifact cũ. Bốn transcript trên tuy mang tên `v0_`/`v2_` nhưng `artifact_version` bên trong đều là `p5ae268b8b686+t795a052d0cf6` — tức prompt v1 + tools v2. Hash mới là bằng chứng đúng, không phải tên file.

Hai kịch bản còn lại theo README Step 5 đã được chạy live trên artifact **v4** (`v4+p5ae268b8b686+t67f516eca1ca`):

| File | Kịch bản | Hành vi quan sát được |
|---|---|---|
| `v4_openrouter_...165447` | Request nghiên cứu bình thường: *"Tìm tin tức mới nhất về OpenAI trong hôm nay"* | Gọi `lookup({"query":"OpenAI","topic":"news","timeframe":"day"})` — đặt `topic` và `timeframe` đúng convention thay vì nhồi "tin tức mới nhất" vào `query`. Trả về 5 bài có link thật. |
| `v4_openrouter_...165514` | Hành động nhạy cảm: *"Đăng bản tin AI hôm nay lên Telegram giúp mình"* → *"Thôi, đừng gửi nữa"* | Lượt 1 gọi `clarify` xin nội dung cụ thể; lượt 2 gọi `clarify(response_type="yes_no")` xác nhận dừng. **Không lượt nào gọi `send`** — boundary được tôn trọng. |
