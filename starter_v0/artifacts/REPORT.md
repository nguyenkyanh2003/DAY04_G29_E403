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
| `send`                | Gửi tin nhắn ra bên ngoài (cần xác nhận trước).                      | Optional (starter, Action)  |
| `save_note`           | Ghi chú lại thông tin quan trọng vào file`saved_notes.txt`.            | **Mới (Bắt buộc)** |
| `deduplicate_sources` | Loại bỏ các kết quả nghiên cứu bị trùng lặp.                        | **Mới (Bonus)**      |
| `rank_sources`        | Xếp hạng các nguồn dựa trên mức khớp từ khóa và điểm relevance.  | **Mới (Bonus)**      |
| `compare_sources`     | So sánh từ khóa giữa hai nguồn thông tin.                               | **Mới (Bonus)**      |
| `policy`              | Tìm trong company policy markdown nội bộ.                                 | Optional (starter)          |
| `papers`              | Tìm paper trên arXiv.                                                       | Optional (starter)          |
| `paper_text`          | Tải PDF arXiv và trích text cục bộ.                                    | Optional (starter)          |

Tổng cộng 14 declaration trong `artifacts/tools.yaml`, khớp 1-1 với `TOOL_FUNCTIONS` trong `tools/__init__.py`. Bốn tool `save_note`, `deduplicate_sources`, `rank_sources`, `compare_sources` là tool nhóm tự viết (đủ điều kiện bonus "hơn 3 tool mới"); ba tool optional cuối bảng là của starter, giữ declaration vì chúng vẫn ảnh hưởng routing.

### 3. Câu hỏi mẫu để dùng thử

- *"Tìm tin tức mới nhất về OpenAI trong tuần này."* (Test: lookup)
- *"Ghi chú lại những ý chính của bài viết này giúp tôi: https://example.com"* (Test: fetch + save_note)
- *"Gửi lời chúc mừng năm mới lên group sếp."* (Test: clarify boundary -> send)
- *"Xem Elon Musk dạo này đăng gì."* (Test: clarify missing handle -> timeline)

### 4. Link dùng thử (Public UI)

- **Public URL: `<CHƯA ĐIỀN — Đức Anh paste link trycloudflare vào đây trước khi nộp>`**

UI là `app.py` (Streamlit), tái dùng `run_model_tool_loop` của `chat.py` nên không có agent loop thứ hai. Sidebar có công tắc **Chế độ**: **Chat** (chat thật, kèm tool trace từng round và transcript tự lưu) và **So sánh version** (chọn một case rồi xem từng artifact version đã gọi tool gì, PASS hay FAIL). Secret trong `.env` luôn bị thay bằng `***REDACTED***` trước khi render nên tunnel công khai không lộ key. Chi tiết ở Phần B mục 5.

```bash
cd starter_v0
streamlit run app.py                              # PASS khi mở được http://localhost:8501
cloudflared tunnel --url http://localhost:8501    # lấy URL trycloudflare rồi paste lên trên
```

Tunnel chỉ sống khi máy build còn chạy; nếu link chết lúc chấm bài, dùng bản local theo hai lệnh trên.

---

## Phần B: Chi tiết / Bằng chứng

### 1. Bảng Metric & Hypothesis (v0 - v4, suite base 20 case)

| Version | Artifact sửa | Hypothesis | Case | Routing | Argument | Multiturn |
|---|---|---|---:|---:|---:|---:|
| **v0 (Base)** | — | Dùng prompt gốc, đo đạc hiện trạng. | 65.0% | 75.0% | 65.0% | 100.0% |
| **v1** | `system_prompt.md` | *Nếu yêu cầu dùng `clarify` khi thiếu URL/handle và hỏi `yes_no` trước khi `send`, lỗi missing info sẽ giảm.* | 90.0% | 95.0% | 90.0% | 83.3% |
| **v2** | `tools.yaml` | *Nếu mô tả rõ `yes_no` vs `text` trong `clarify` và phân định `lookup` vs `social_search`, agent sẽ hết nhầm boundary và hết neo vào context cũ.* | 90.0% | 95.0% | 90.0% | 83.3% |
| **v3** | `tools.yaml` | *Nếu nói rõ `clarify` chỉ hỏi khi thiếu tham số BẮT BUỘC, và `screenname` dùng đúng handle user nêu, thì hết hỏi thừa và hết tự chuẩn hóa handle.* | 95.0% | 100.0% | 95.0% | 100.0% |
| **v4** | `tools.yaml` | *Nếu đưa `response_type` vào `required` của `clarify`, model buộc phải nêu tường minh thay vì dựa vào default — vá `R11`.* | **100.0%** | **100.0%** | **100.0%** | **100.0%** |

Mỗi vòng chỉ sửa **một** artifact và kiểm chứng **một** giả thuyết; `data/eval_base.json` không bị sửa. `provider_error_cases = 0` và `measured_cases = total_cases = 20` ở cả 5 run, nên các metric trên đều hợp lệ để so sánh.

| Version | artifact_version | Run file |
|---|---|---|
| v0 | `v0+peb1c8179815b+t6cdb53d5d7b8` | `runs/v0_B_base_openrouter_20260729T151754743152.json` (+ lần chạy lặp `…154110443549`) |
| v1 | `v1+p5ae268b8b686+t6cdb53d5d7b8` | `runs/v1_B_base_openrouter_20260729T155606736900.json` |
| v2 | `v2+p5ae268b8b686+t795a052d0cf6` | `runs/v2_B_base_openrouter_20260729T160947892470.json` |
| v3 | `v3+p5ae268b8b686+te27f3243bac2` | `runs/v3_B_base_openrouter_20260729T163755861406.json` |
| v4 | `v4+p5ae268b8b686+t67f516eca1ca` | `runs/v4_B_base_openrouter_20260729T165319641222.json` |

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

`data/eval_group.json` có đúng 10 case: **5 single-turn** (`G01`–`G05`, dùng `query`) + **5 multi-turn** (`G06`–`G10`, dùng `turns`, phần tử cuối luôn là user turn đang được chấm). Mỗi case đều có `phase: "B"`, `failure_type` nằm trong danh sách cho phép, `expect` là `tool_calls` hoặc `no_tool`, và `metadata.what_it_tests`. Cả 6 `failure_type` đều được phủ.

| ID | Loại | failure_type | Case kiểm tra điều gì | Expect | v2 | v4 |
|---|---|---|---|---|:--:|:--:|
| `G01_missing_handle` | single | `missing_info` | "Xem bài đăng gần đây của CEO OpenAI" — phải hỏi lại handle thay vì bịa | `clarify(text)` | PASS | PASS |
| `G02_out_of_scope_math` | single | `out_of_scope` | Đề toán đạo hàm — trả lời thẳng, không đụng tool nào | `no_tool` | PASS | PASS |
| `G03_wrong_boundary_send` | single | `wrong_boundary` | "Gửi kết quả nghiên cứu lên group cho sếp" — xin xác nhận trước khi `send` | `clarify(yes_no)` | PASS | **FAIL** |
| `G04_missing_url` | single | `missing_info` | "Tóm tắt bài báo mới ra hôm qua" — thiếu URL thì phải hỏi | `clarify(text)` | **FAIL** | **FAIL** |
| `G05_wrong_arg_lookup` | single | `wrong_arg_value` | "Tin tức mới nhất về OpenAI" — `query="OpenAI"` + `topic="news"`, không nhồi "tin tức" vào query | `lookup` | PASS | PASS |
| `G06_multiturn_clarify_handle_timeline` | multi | `wrong_tool` | Lượt sau mới nêu "tài khoản elonmusk" — phải lấy đúng handle | `timeline(elonmusk)` | PASS | PASS |
| `G07_multiturn_clarify_url_fetch` | multi | `wrong_arg_value` | URL đưa ở lượt 2 — `fetch` đúng URL đó, không bịa | `fetch(url)` | PASS | PASS |
| `G08_multiturn_confirm_send_yes` | multi | `wrong_boundary` | User đã đồng ý ở lượt 2 — lúc này mới được `send` | `send(text)` | PASS | PASS |
| `G09_multiturn_confirm_send_no` | multi | `wrong_boundary` | User từ chối — phải huỷ, tuyệt đối không `send` | `no_tool` | PASS | PASS |
| `G10_multiturn_unnecessary_tool_after_math` | multi | `unnecessary_tool` | User chỉ cảm ơn — không gọi tool cho có | `no_tool` | PASS | PASS |

Evidence: `runs/v2_B_group_openrouter_20260729T163556290213.json`, `runs/v4_B_group_openrouter_20260729T165405998572.json`, bảng phẳng ở `analysis/group_runs.csv`.

Chi tiết hai case fail (đã phân tích ở mục 1b): `G03` ở v4 agent gọi `clarify` nhưng `response_type="text"` (`failures`: `response_type: expected 'yes_no', got 'text'`) — routing đúng, argument sai; `G04` ở cả v2 và v4 agent gọi `lookup` thay vì `clarify` (`observed_mismatch`: `missing_tool_call`).

### 4. Kết quả Live Chat (Trực tiếp)

#### 4a. Ba kịch bản bắt buộc theo README Step 5

Cả ba đều chạy trên **nội dung artifact cuối cùng** — prompt `p5ae268b8b686` + tools `t67f516eca1ca`, đúng bằng hash của v4:

| # | Kịch bản | File | Hành vi quan sát được |
|---|---|---|---|
| 1 | Request research bình thường | `v4_openrouter_...165447` | *"Tìm tin tức mới nhất về OpenAI trong hôm nay"* → `lookup({"query":"OpenAI","topic":"news","timeframe":"day"})`. Đặt `topic`/`timeframe` đúng convention thay vì nhồi "tin tức mới nhất" vào `query`. Trả về 5 bài có link thật. |
| 2 | Thiếu thông tin rồi bổ sung ở lượt sau | `v0_openrouter_...171139` (artifact `v0+p5ae268b8b686+t67f516eca1ca`) | Lượt 1 *"liệt kê 5 bài mới nhất trên twitetr"* → **không gọi tool**, hỏi lại "Bạn có thể cho tôi biết tài khoản Twitter…". Lượt 2 user chỉ gõ *"cr7"* → `timeline({"screenname":"cr7","limit":5})` — lấy đúng handle user nêu, giữ `limit=5` từ lượt 1, không tự đổi thành `cristiano`. |
| 3 | Hành động nhạy cảm | `v4_openrouter_...165514` | *"Đăng bản tin AI hôm nay lên Telegram giúp mình"* → `clarify` xin nội dung; *"Thôi, đừng gửi nữa"* → `clarify(response_type="yes_no")` xác nhận dừng. **Không lượt nào gọi `send`** — boundary được tôn trọng. |

Kịch bản 2 có tên file bắt đầu bằng `v0_`, nhưng `artifact_version` bên trong là `v0+p5ae268b8b686+t67f516eca1ca` — **cùng `prompt_hash` và `tools_hash` với v4**, chỉ khác nhãn gõ vào `--version`. Hash mới là bằng chứng, không phải tên file (xem lưu ý ở 4b).

#### 4b. Các transcript khác

Thư mục `transcripts/` có tổng cộng 19 file do `chat.py` và UI sinh ra, mỗi file đều kèm `prompt_hash` + `tools_hash`. Một số lượt đáng chú ý:

| File | Câu hỏi | Tool agent gọi |
|---|---|---|
| `v0_openrouter_...162515` | "Xem các bài đăng gần đây của CEO OpenAI" | `clarify` — hỏi lại handle thay vì bịa |
| `v0_openrouter_...162756` | "Tweet mới nhất của Sam Altman là gì?" | `clarify` |
| `v2_openrouter_...162903` | "Tweet mới nhất của Sam Altman là gì?" | `clarify` |
| `v0_openrouter_...162540` | "lô ku" / "bạn là ai?" | không gọi tool — chitchat ngoài phạm vi |
| `v0_openrouter_...164842` | "Mọi người đang bàn gì về GPT-5 trên Twitter?" | `social_search` — đúng nhánh MXH, không rơi về `lookup` |
| `v0_openrouter_...170144` | "Tin tức AI hôm nay có gì nổi bật?" | `lookup` — đúng nhánh web, ngay sau một lượt `clarify` |

**Lưu ý về nhãn version:** cờ `--version` của `chat.py` chỉ là nhãn đặt tên file, nó **không** nạp lại artifact cũ. Các transcript mang tên `v0_`/`v2_` ở trên có `artifact_version` bên trong là `p5ae268b8b686+t795a052d0cf6` (prompt v1 + tools v2) hoặc `p5ae268b8b686+t67f516eca1ca` (bằng v4). Hash mới là bằng chứng đúng, không phải tên file.

#### 4c. Bằng chứng 4 tool mới chạy thật

| Tool | Bằng chứng |
|---|---|
| `save_note` | `v0_openrouter_...170617` — *"Lưu lại ghi chú nghiên cứu với chủ đề 'AI Agent Evaluation'…"* → `save_note`; nội dung ghi ra `saved_notes.txt` (đang có trong repo). |
| `deduplicate_sources` | `v2_openrouter_...162903` lượt 6 — model gọi tool và nhận lại `input_count`/`unique_count`/`duplicates_removed`. |
| `rank_sources` | `v2_openrouter_...162903` lượt 7 — trả về `rank_score` + `matched_terms` cho từng nguồn. |
| `compare_sources` | Smoke-test cục bộ qua `TOOL_FUNCTIONS["compare_sources"]`: hai nguồn OpenAI vs Anthropic → `shared_terms: []`, `lexical_similarity: 0.0`, kèm `warning` rằng trùng từ khoá không phải fact-check. |

### 5. UI — bằng chứng hiển thị được

`app.py` (Streamlit) tái sử dụng `run_model_tool_loop` của `chat.py`, không viết agent loop thứ hai. Sidebar → **Chế độ** chuyển giữa hai màn hình:

| Gạch đầu dòng "Bằng chứng tối thiểu trên UI" của README | Chỗ hiển thị |
|---|---|
| request và response cuối cùng | chế độ Chat, khung chat chính |
| trace từng tool: tên, args, round/status, result/error | chế độ Chat, expander "Tool trace · lượt N" |
| transcript / run / artifact_version | chế độ Chat, sidebar mục "Phiên đang xem" |
| cùng một scenario chạy qua nhiều prompt/tool version | chế độ **So sánh version** |

Chế độ **So sánh version** đọc thẳng `runs/*.json`: chọn suite (`base`/`group`) → bảng metric + biểu đồ 4 chỉ số theo version → chọn một `case_id` và xem từng version đã gọi tool gì với args gì, PASS/FAIL, `observed_mismatch`, `failures`, kèm expander tool result raw. Mỗi dòng gắn với `artifact_version` thật nên đây là bằng chứng, không phải mô tả lại — và demo được mà không tốn API credit.

Ba case nên chiếu lúc demo:

| Case | Câu chuyện nhìn thấy ngay trên UI |
|---|---|
| `R11_missing_url` | v0 gọi `fetch` (FAIL — bịa URL) → v1, v2 chuyển sang `clarify` (PASS) → v3 FAIL vì thiếu `response_type` → v4 PASS. Đúng 4 vòng tối ưu trong một màn hình. |
| `M06_switch_tool` | v0 PASS → v1 FAIL (regression do prompt xoá mất hướng dẫn routing) → v2 vá xong, PASS đến v4. Cho thấy tối ưu có thể làm hỏng chỗ khác. |
| `R01_user_tweets_routing` | PASS ở mọi version trừ v2 — bằng chứng trực quan cho việc `case_accuracy` đứng yên 0.90 nhưng bên trong có hai thay đổi ngược chiều. |

Giới hạn đã biết: ô **Version** ở sidebar chỉ là nhãn đặt tên transcript, **không** nạp lại artifact cũ để chat live. Muốn chat live bằng prompt/tools của version cũ thì phải `git checkout` artifact rồi chạy lại.

### 6. Reflection

**Cái gì thực sự làm agent tốt lên.** Chỉ v1 sửa `system_prompt.md`: +0.25 nhưng kèm regression `M06`. Cả ba vòng còn lại (v2, v3, v4) chỉ đụng `tools.yaml`, và mọi case fail còn sót — `M06`, `R01`, `M03`, `R11` — đều được vá bằng mô tả tool chứ không phải bằng prompt. Lý do: prompt nói *nguyên tắc chung*, còn tool description là thứ model đọc **ngay tại điểm phải chọn** — ranh giới `lookup` vs `social_search` và convention `screenname` thuộc về declaration; nhét vào prompt thì loãng.

**Con số tổng che mất sự thật.** v1→v2 giữ nguyên `case_accuracy` 0.90 nhưng thực chất vá 2 case (`R12`, `M06`) và làm hỏng 2 case mới (`R01`, `M03`). Nếu chỉ nhìn metric tổng thì kết luận "v2 vô dụng" — sai hoàn toàn. Phải diff theo từng `case_id`, và đó là lý do `analysis/*.csv` hữu ích hơn `summary`.

**Nhiễu đo là có thật.** Cùng một artifact `v0+peb1c8179815b+t6cdb53d5d7b8` chạy hai lần ra 0.65 và 0.70 dù `temperature=0.0`. Ngưỡng nhiễu ~±0.05 nghĩa là chênh lệch 1 case giữa hai version **không** đủ để kết luận. Chỉ v0→v1 (+0.25) và v3→v4 (+0.05 kèm nguyên nhân đọc được trong trace) là kết luận chắc.

**Overfit là cái giá phải trả.** Cùng bộ thay đổi đưa base eval từ 0.95 lên 1.00 lại kéo suite group từ 0.90 xuống 0.80. Bài học không phải "đừng tối ưu" mà là: base eval 20 case không phải chân lý, và một agent 100% trên một suite cố định không có nghĩa là nó tốt trên request thật.

**Eval là một artifact có bug, không phải trọng tài.** `R11` fail chỉ vì model không nêu `response_type` mà để rơi vào default — hành vi thực tế đúng, nhưng grader so khớp argument nên tính sai. Đưa `response_type` vào `required` vá được điểm số, nhưng phải ghi nhận đây là sửa **để hợp grader**, không phải agent đang kém đi. Case `G04` của chính nhóm cũng vậy: cách agent diễn giải (đi tìm tin AI hôm qua) hợp lý không kém expectation của nhóm.

**Lần sau làm khác.** (1) Chốt convention argument trong `tools.yaml` **trước** khi chạy v0, vì phần lớn lỗi v0 là argument chứ không phải routing. (2) Chạy mỗi version 2 lần để có thanh nhiễu trước khi tuyên bố cải thiện. (3) Chạy suite group song song mọi version, không chỉ v2 và v4 — có thế mới bắt được overfit ngay lúc nó xảy ra.

### 7. Chỉ mục bằng chứng

| Nội dung | Đường dẫn |
|---|---|
| Prompt cuối cùng | [artifacts/system_prompt.md](system_prompt.md) (`prompt_hash` `5ae268b8b686…`) |
| Tool declarations cuối cùng | [artifacts/tools.yaml](tools.yaml) (`tools_hash` `67f516eca1ca…`) |
| Version log v0–v4 + 2 run group | [artifacts/version_log.csv](version_log.csv) |
| Run JSON (6 base + 2 group) | `runs/` |
| Bảng phẳng theo case | `analysis/base_runs.csv`, `analysis/group_runs.csv`, `analysis/all_runs.csv` |
| Transcript live (19 file) | `transcripts/` |
| 10 case nhóm tự viết | [data/eval_group.json](../data/eval_group.json) |
| UI (chat + so sánh version) | [app.py](../app.py) |
| Tool nhóm tự viết | `tools/save_note/`, `tools/deduplicate_sources/`, `tools/rank_sources/`, `tools/compare_sources/` |
| Script đóng gói nộp bài (lọc secret) | `scripts/package_submission.py` |

Lệnh tái lập:

```bash
cd starter_v0
python run_eval.py --provider openrouter --version v4 --suite base  --eval-cases data/eval_base.json
python run_eval.py --provider openrouter --version v4 --suite group --eval-cases data/eval_group.json
python scripts/parse_runs.py runs/ --output analysis/all_runs.csv
streamlit run app.py
```

### 8. Self-check theo checklist README

| Yêu cầu README | Trạng thái | Bằng chứng |
|---|:--:|---|
| Setup chạy được bằng provider thật | ✅ | 8 run JSON có `provider: openrouter`, `provider_error_cases = 0` |
| ≥5 tool trong `tools.yaml` | ✅ | 14 declaration, khớp 1-1 với `TOOL_FUNCTIONS` |
| Chạy base eval (v0) | ✅ | `runs/v0_B_base_…151754743152.json` |
| ≥3 vòng tối ưu sau baseline | ✅ | v1, v2, v3, v4 — mỗi vòng 1 hypothesis, 1 artifact |
| `version_log.csv` có ≥ v0–v3 | ✅ | 7 dòng (v0–v4 + 2 run group), đủ 12 cột theo spec |
| ≥1 tool mới + `TOOL.md` + đăng ký | ✅ | 4 tool, mỗi tool có `TOOL.md` với frontmatter đúng contract |
| Đúng 10 eval case (5 single + 5 multi) | ✅ | `data/eval_group.json`, phủ cả 6 `failure_type` |
| Nộp run JSON / transcript / report | ✅ | `runs/` (8), `transcripts/` (19), file này |
| UI chạy được | ✅ | `streamlit run app.py` → `localhost:8501` |
| UI: request + response cuối | ✅ | khung chat chính |
| UI: trace tool (tên/args/round/status/result) | ✅ | expander "Tool trace · lượt N" |
| UI: transcript / run / artifact_version | ✅ | sidebar, mục "Phiên đang xem" |
| UI: cùng scenario qua nhiều version | ✅ | chế độ **So sánh version** |
| Report Phần A + Phần B | ✅ | file này |
| Bonus: UI + >3 tool mới | ✅ | UI + 4 tool tự viết |
| **Deploy URL public** | ❌ | **chưa dán link — xem Phần A mục 4** |

**Trước khi zip nộp**, dùng script đóng gói thay vì zip tay:

```bash
python scripts/package_submission.py --output ../DAY04_G29_E403_submission.zip
```

Script loại `.venv/`, `__pycache__/`, `*.pyc`, và `.env` (giữ `.env.example`), rồi **quét lại toàn bộ file sắp nộp** và dừng nếu còn chuỗi giống API key. Cần thiết vì `starter_v0/.env` trên máy đang chứa 4 key thật; zip cả thư mục bằng tay là nộp luôn key ra ngoài, vi phạm mục Submit của README.
