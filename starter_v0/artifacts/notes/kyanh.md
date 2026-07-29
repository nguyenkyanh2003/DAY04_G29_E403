# Notes — Kỳ Anh (TL / Prompt & Routing Owner, Run Captain)

Ghi chép hypothesis và bằng chứng theo từng version. Dùng để ráp REPORT Phần B.

## Bảng metric

| Version | Đổi gì | case_acc | routing | argument | multiturn |
|---|---|---|---|---|---|
| v0 | baseline | 0.65 | 0.75 | 0.70 | 1.00 |
| v1 | `system_prompt.md` | 0.90 | 0.95 | 0.90 | 0.83 |
| v2 | `tools.yaml` | 0.90 | 0.95 | 0.90 | 0.83 |
| v3 | `tools.yaml` | **0.95** | **1.00** | **0.95** | **1.00** |

Suite group (10 case của Khánh, chạy ở artifact v2): `case_accuracy` 0.90, `multiturn_accuracy` 1.00, `provider_error_cases` 0.

## v0 — baseline

`artifact_version: v0+peb1c8179815b+t6cdb53d5d7b8`

6 case fail: R08, R10, R11, R12, R13, R14.

Đọc `actual_tool_calls` thì thấy prompt v0 **chủ động dạy agent làm sai**, từng câu map 1:1 với case fail:

| Câu trong prompt v0 | Case | Hành vi quan sát được |
|---|---|---|
| "pick a well-known account like Sam Altman" | R10 | `timeline(screenname="sama")` — bịa handle |
| "assume a likely URL and read it" | R11 | `fetch(url="https://example.com/article")` — bịa URL |
| "wants to send... just go ahead and do it" | R12 | gọi thẳng `send`, bỏ qua xác nhận |
| "Always finish in a single step. Pick one tool" | R08, R14 | dùng `send` làm **kênh trả lời**, gửi cả code Fibonacci ra ngoài |

### Ghi chú về nhiễu đo

Chạy v0 hai lần trên **cùng** `artifact_version`: 0.65 và 0.70. Metric có nhiễu khoảng ±0.05, nên chênh lệch dưới mức đó giữa hai version không đủ để kết luận là cải thiện thật. Cả hai run đều nằm trong `runs/`.

## v1 — sửa system prompt

`artifact_version: v1+p5ae268b8b686+t6cdb53d5d7b8` · 0.65 → 0.90

**Giả thuyết:** prompt cấm agent hỏi lại và ép gọi tool trong một bước, nên agent bịa argument và dùng `send` như hộp thoại trả lời. Thêm boundary "khi nào KHÔNG hành động" sẽ vá nhóm case này.

**Thay đổi:** viết lại `system_prompt.md` với 3 rule — thiếu tham số bắt buộc thì `clarify(text)`; hành động gửi ra ngoài thì `clarify(yes_no)` trước; yêu cầu ngoài phạm vi research thì trả lời bằng text và không gọi tool nào.

**Kết quả:** vá được R08, R10, R11, R13, R14.

**Regression:** `multiturn_accuracy` 1.00 → 0.83. M06 hỏng — user nói rõ "bỏ Twitter, chuyển sang web tin tức" nhưng agent vẫn gọi `social_search`. Prompt mới chỉ dạy *khi nào dừng*, đã xoá mất phần hướng dẫn routing, nên việc phân biệt `lookup` vs `social_search` rơi hết về mô tả trong `tools.yaml` — vốn đang là "Tìm trên mạng xã hội." và "Tra cứu thông tin trên internet.", gần như vô nghĩa với model.

R12 tiến bộ một nửa: agent đã chịu gọi `clarify` nhưng chọn `response_type="text"`, hỏi xin nội dung thay vì hỏi yes/no. Nguyên nhân là **xung đột giữa rule 1 và rule 2** — câu "Đăng bản tin này lên Telegram" vừa thiếu nội dung vừa là hành động gửi.

## v2 — sửa tool declaration

`artifact_version: v2+p5ae268b8b686+t795a052d0cf6` · 0.90 → 0.90

**Giả thuyết:** phần còn lại không giải được bằng prompt. Mô tả tool quá mơ hồ nên model không phân biệt được `yes_no` vs `text`, cũng không phân biệt được `lookup` vs `social_search`.

**Thay đổi:** viết lại mô tả toàn bộ tool theo công thức *nói rõ khi nào dùng / khi nào không*, thêm luật ưu tiên `yes_no` khi request vừa thiếu info vừa là hành động gửi, nêu convention arg cho `lookup` (`topic`, `timeframe`, query giữ gọn), và khai báo 4 tool mới của nhóm.

**Kết quả:** R12 và M06 đều PASS — giả thuyết đúng.

**Nhưng tổng số đứng yên ở 0.90** vì phát sinh 2 lỗi mới:

- **R01** — mô tả `clarify` viết quá mạnh khiến agent coi cả tham số **tùy chọn có default** (`limit`) là "thiếu thông tin", hỏi thừa "bạn muốn bao nhiêu tweet?" thay vì gọi `timeline`. Vá quá tay theo hướng ngược lại với v0.
- **M03** — user nói "Karpathy", agent tự chuẩn hóa thành handle thật `andrejkarpathy`, trong khi eval chờ `karpathy`. Chưa có convention name→handle.

Bài học: **một con số tổng không đổi che mất hai thay đổi ngược chiều nhau.** Phải đọc từng case, không nhìn mỗi `case_accuracy`.

## v3 — siết lại ranh giới clarify

`artifact_version: v3+p5ae268b8b686+te27f3243bac2` · 0.90 → 0.95

**Giả thuyết:** hai lỗi của v2 đều là lỗi convention trong `tools.yaml`, không phải lỗi prompt.

**Thay đổi:** trong mô tả `clarify`, nói rõ chỉ hỏi khi thiếu tham số **bắt buộc**, còn tham số tùy chọn thì dùng default và tuyệt đối không hỏi. Trong `screenname` của `timeline`, thêm convention dùng đúng handle người dùng nêu, không tự mở rộng sang handle thật.

**Kết quả:** R01 và M03 đều PASS. `tool_routing_accuracy` đạt **1.00**, `multiturn_accuracy` về lại **1.00**.

**Còn lại 1 case fail — R11.** Agent gọi `clarify` đúng, câu hỏi đúng ("Vui lòng cung cấp URL của bài viết"), nhưng **không truyền `response_type`** mà để rơi vào default. Eval so khớp argument nên tính là sai. Hướng sửa nếu có thêm vòng: đưa `response_type` vào `required` của `clarify` để buộc model nêu tường minh thay vì dựa vào default.

## Kết luận

Vòng lặp hiệu quả nhất không phải "sửa prompt cho hay hơn" mà là: đọc `actual_tool_calls` của case fail → đặt một giả thuyết → sửa đúng một artifact → chạy lại → so từng case chứ không so mỗi số tổng.

Hai lần cần đọc kỹ mới thấy: (1) v1 tăng tổng nhưng làm hỏng multi-turn; (2) v2 tổng đứng yên nhưng thực chất vá 2 case và hỏng 2 case khác. Cả hai đều vô hình nếu chỉ nhìn `case_accuracy`.
