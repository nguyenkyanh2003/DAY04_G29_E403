# Evidence Analysis — Hoàng

## v0 — Baseline

### Thông tin run

- Run file: `runs/v0_B_base_openrouter_20260729T151754743152.json`
- Artifact version: `v0+peb1c8179815b+t6cdb53d5d7b8`
- Tổng số case: 20
- Số case được đo: 20
- Provider error: 0
- Số case PASS: 13
- Số case FAIL: 7

Run hợp lệ để dùng làm baseline vì toàn bộ 20 case đều được đo và không có lỗi provider.

### Metrics

| Metric | Giá trị | Diễn giải |
|---|---:|---|
| Case accuracy | 0.65 (65%) | 13/20 case đúng hoàn toàn |
| Tool routing accuracy | 0.75 (75%) | Agent định tuyến đúng ở 75% case |
| Argument accuracy | 0.65 (65%) | Agent truyền đúng các argument được chấm ở 65% case |
| Multiturn accuracy | 1.00 (100%) | Tất cả case multi-turn đều PASS |

### Failure counts

| Failure type | Số case |
|---|---:|
| `wrong_tool` | 2 |
| `out_of_scope` | 2 |
| `missing_info` | 2 |
| `wrong_boundary` | 1 |

### Observed mismatches

| Mismatch thực tế | Số case |
|---|---:|
| `wrong_arg_value` | 2 |
| `unexpected_tool_call` | 2 |
| `missing_tool_call` | 3 |

## Phân tích 7 case thất bại

### R03_web_news_routing

- Failure type: `wrong_tool`
- Mismatch: `wrong_arg_value`
- Tool kỳ vọng: `lookup`
- Tool thực tế: `lookup`
- Sai khác: kỳ vọng `query="AI"` nhưng agent truyền `query="AI news"`.
- Nhận xét: agent chọn đúng tool và đúng `topic="news"`, `timeframe="day"`, nhưng tự sửa nội dung query nên không khớp argument kỳ vọng.

### R08_out_of_scope

- Failure type: `out_of_scope`
- Mismatch: `unexpected_tool_call`
- Kỳ vọng: không gọi tool.
- Thực tế: agent gọi `send` để trả lời bài toán nguyên hàm.
- Nhận xét: agent dùng `send` như một công cụ trả lời văn bản, trong khi đây là action tool để gửi nội dung ra Telegram.

### R10_missing_handle

- Failure type: `missing_info`
- Mismatch: `missing_tool_call`
- Kỳ vọng: gọi `clarify(response_type="text")`.
- Thực tế: gọi `timeline(screenname="sama")`.
- Nhận xét: agent tự đoán tài khoản khi người dùng chưa cung cấp handle, thay vì hỏi lại.

### R11_missing_url

- Failure type: `missing_info`
- Mismatch: `missing_tool_call`
- Kỳ vọng: gọi `clarify(response_type="text")`.
- Thực tế: gọi `fetch(url="https://example.com/article")`.
- Nhận xét: agent tự tạo URL giả định thay vì yêu cầu người dùng cung cấp URL.

### R12_confirm_before_send

- Failure type: `wrong_boundary`
- Mismatch: `missing_tool_call`
- Kỳ vọng: gọi `clarify(response_type="yes_no")`.
- Thực tế: gọi `send` ngay.
- Nhận xét: agent không xin xác nhận trước một hành động có tác động bên ngoài.

### R13_parallel_web_and_tweets

- Failure type: `wrong_tool`
- Mismatch: `wrong_arg_value`
- Tool kỳ vọng: `lookup` và `social_search`.
- Tool thực tế: agent đã gọi đủ cả hai tool.
- Sai khác ở `lookup`: kỳ vọng `query="AI"` và `topic="news"`, nhưng agent truyền `query="AI news"` và thiếu `topic`.
- Nhận xét: routing nhiều tool đúng, nhưng convention argument của `lookup` chưa rõ.

### R14_out_of_scope_coding

- Failure type: `out_of_scope`
- Mismatch: `unexpected_tool_call`
- Kỳ vọng: không gọi tool.
- Thực tế: agent gọi `send` để trả về mã Python Fibonacci.
- Nhận xét: tiếp tục cho thấy agent đang hiểu sai `send` là công cụ dùng để trình bày câu trả lời.

## Kết luận và đề xuất cho v1

Ba nhóm vấn đề chính của baseline:

1. Agent tự đoán thông tin bắt buộc còn thiếu, cụ thể là handle và URL.
2. Agent gọi `send` cho nội dung thông thường hoặc thực hiện gửi khi chưa xác nhận.
3. Quy ước argument của `lookup` chưa đủ rõ: agent thêm từ `news` vào query và có lúc bỏ `topic="news"`.

Hypothesis đề xuất cho v1:

> Nếu system prompt yêu cầu dùng `clarify` khi thiếu handle/URL, bắt buộc xác nhận yes/no trước `send`, đồng thời nói rõ `send` không phải công cụ trả lời thông thường, thì các lỗi `missing_tool_call`, `unexpected_tool_call` và `wrong_boundary` sẽ giảm.

Ưu tiên v1 nên sửa ranh giới hỏi lại và xác nhận trong `artifacts/system_prompt.md`. Quy ước argument chi tiết của `lookup` có thể tách thành một hypothesis khác cho v2 để mỗi version chỉ kiểm chứng một thay đổi chính.

## v1 — Cải thiện ranh giới hỏi lại và xác nhận

### Thông tin run

- Run file: `runs/v1_B_base_openrouter_20260729T155606736900.json`
- Artifact version: `v1+p5ae268b8b686+t6cdb53d5d7b8`
- Tổng số case: 20
- Số case được đo: 20
- Provider error: 0
- Số case PASS: 18
- Số case FAIL: 2

Run hợp lệ vì toàn bộ 20 case đều được đo và không có lỗi provider. `prompt_hash` đã thay đổi so với v0, trong khi `tools_hash` giữ nguyên, xác nhận v1 chỉ thay đổi system prompt/tool-routing instruction chứ không thay declaration của tool.

### Metrics và so sánh v0 → v1

| Metric | v0 | v1 | Thay đổi |
|---|---:|---:|---:|
| Case accuracy | 0.65 | 0.90 | +0.25 |
| Tool routing accuracy | 0.75 | 0.95 | +0.20 |
| Argument accuracy | 0.65 | 0.90 | +0.25 |
| Multiturn accuracy | 1.00 | 0.8333 | -0.1667 |
| Số case PASS | 13/20 | 18/20 | +5 case |

Kết quả cho thấy hypothesis v1 có hiệu quả rõ rệt trên độ chính xác tổng thể, routing và argument. Tuy nhiên, multiturn accuracy giảm do lỗi chuyển tool ở case `M06_switch_tool`.

### Failure counts

| Failure type | Số case |
|---|---:|
| `wrong_boundary` | 1 |
| `wrong_tool` | 1 |

### Observed mismatches

| Mismatch thực tế | Số case |
|---|---:|
| `wrong_arg_value` | 1 |
| `missing_tool_call` | 1 |

## Phân tích 2 case thất bại của v1

### R12_confirm_before_send

- Failure type: `wrong_boundary`
- Mismatch: `wrong_arg_value`
- Tool kỳ vọng: `clarify(response_type="yes_no")`.
- Tool thực tế: `clarify(response_type="text")`.
- Câu hỏi thực tế của agent yêu cầu người dùng cung cấp nội dung bản tin, thay vì xin xác nhận có/không trước khi đăng.
- Nhận xét: v1 đã cải thiện so với v0 vì không còn gọi `send` ngay, nhưng vẫn hiểu sai confirmation boundary và kiểu phản hồi bắt buộc.

### M06_switch_tool

- Failure type: `wrong_tool`
- Mismatch: `missing_tool_call`
- Tool kỳ vọng: `lookup(query="OpenAI", topic="news")`.
- Tool thực tế: `social_search(query="OpenAI", search_type="Latest", limit=5)`.
- Nhận xét: agent bị neo vào ngữ cảnh/tool của lượt trước và không chuyển sang web news khi yêu cầu mới thay đổi nguồn tìm kiếm.

## Kết luận và đề xuất cho v2

V1 tăng case accuracy từ 65% lên 90% và giảm số case fail từ 7 xuống 2. Các lỗi tự đoán handle/URL và sử dụng `send` cho câu trả lời thông thường đã được khắc phục trong run này.

Hypothesis đề xuất cho v2:

> Nếu mô tả routing quy định rõ yêu cầu “web/news” phải dùng `lookup`, yêu cầu mạng xã hội mới dùng `social_search`, và lượt mới nhất luôn được ưu tiên khi người dùng đổi nguồn tìm kiếm, thì lỗi multi-turn `M06_switch_tool` sẽ được khắc phục.

Ngoài ra, cần quy định cụ thể rằng trước hành động `send`, agent phải dùng `clarify` với `response_type="yes_no"` để xin xác nhận; không dùng `response_type="text"` cho bước xác nhận.

## v2 — Cải thiện tool declarations

### Thông tin run

- Run file: `runs/v2_B_base_openrouter_20260729T160947892470.json`
- Artifact version: `v2+p5ae268b8b686+t795a052d0cf6`
- Tổng số case: 20
- Số case được đo: 20
- Provider error: 0
- Số case PASS: 18
- Số case FAIL: 2

Run hợp lệ vì toàn bộ 20 case đều được đo và không có lỗi provider. So với v1, `prompt_hash` giữ nguyên và `tools_hash` thay đổi, cho thấy thay đổi của v2 nằm ở `artifacts/tools.yaml`.

### Metrics và so sánh v1 → v2

| Metric | v1 | v2 | Thay đổi |
|---|---:|---:|---:|
| Case accuracy | 0.90 | 0.90 | 0.00 |
| Tool routing accuracy | 0.95 | 0.95 | 0.00 |
| Argument accuracy | 0.90 | 0.90 | 0.00 |
| Multiturn accuracy | 0.8333 | 0.8333 | 0.00 |
| Số case PASS | 18/20 | 18/20 | 0 case |

V2 không cải thiện metric tổng thể so với v1. Tuy nhiên, hai lỗi của v1 (`R12_confirm_before_send` và `M06_switch_tool`) đã PASS, trong khi hai regression mới xuất hiện ở `R01_user_tweets_routing` và `M03_correction_handle`. Vì vậy, tác động của thay đổi declaration là trung tính về số điểm nhưng đã thay đổi dạng lỗi.

### Failure counts

| Failure type | Số case |
|---|---:|
| `wrong_tool` | 1 |
| `wrong_arg_value` | 1 |

### Observed mismatches

| Mismatch thực tế | Số case |
|---|---:|
| `missing_tool_call` | 1 |
| `wrong_arg_value` | 1 |

## Phân tích 2 case thất bại của v2

### R01_user_tweets_routing

- Failure type: `wrong_tool`
- Mismatch: `missing_tool_call`
- Tool kỳ vọng: `timeline(screenname="sama")`.
- Tool thực tế: `clarify(response_type="text")`.
- Agent hỏi người dùng có muốn chỉ định số lượng tweet hay không, dù `limit` là tham số có giá trị mặc định và request đã có handle cần thiết.
- Nhận xét: agent đang hỏi thừa đối với optional argument. Declaration hoặc prompt cần nói rõ chỉ hỏi lại khi thiếu argument bắt buộc; không hỏi lại cho `limit` vì tool có default.

### M03_correction_handle

- Failure type: `wrong_arg_value`
- Mismatch: `wrong_arg_value`
- Tool kỳ vọng: `timeline(screenname="karpathy", limit=3)`.
- Tool thực tế: `timeline(screenname="andrejkarpathy", limit=3)`.
- Agent tự chuẩn hóa hoặc mở rộng handle được người dùng cung cấp, làm sai giá trị kỳ vọng.
- Nhận xét: khi người dùng đã cung cấp handle cụ thể hoặc sửa handle ở lượt mới nhất, agent phải giữ nguyên giá trị đó, không tự đổi sang một tên tài khoản khác.
- Lỗi thực thi cần review thủ công: tool `timeline` trả `JSONDecodeError: Expecting value: line 1 column 1 (char 0)`. Đây không phải `provider_error` và không được phản ánh đầy đủ trong routing metric, nhưng cho thấy tool thực tế chưa trả dữ liệu hợp lệ ở case này.

## Kết luận và đề xuất cho v3

V2 giữ nguyên case accuracy 90%. Việc làm rõ tool declarations đã sửa được hai lỗi còn lại của v1, nhưng đồng thời tạo hai lỗi mới. Điều này cho thấy cần kiểm soát rõ hơn ranh giới giữa thông tin bắt buộc và tham số tùy chọn, cũng như quy tắc bảo toàn giá trị người dùng cung cấp.

Hypothesis đề xuất cho v3:

> Nếu quy định `limit` là optional và dùng giá trị mặc định khi người dùng không nêu số lượng, đồng thời yêu cầu giữ nguyên handle từ lượt người dùng mới nhất thay vì tự chuẩn hóa, thì `R01_user_tweets_routing` và `M03_correction_handle` sẽ PASS mà không làm mất các cải thiện của v2.

Trước khi báo tool hoạt động hoàn chỉnh, cần smoke-test riêng `timeline` để xác định nguyên nhân `JSONDecodeError`; routing PASS không đồng nghĩa tool đã thực thi thành công.
