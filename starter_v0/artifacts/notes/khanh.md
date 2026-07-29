# Notes — Khánh (Eval Author + Report)

> Bản nháp dựng từ `data/eval_group.json` và các run JSON thật. Khánh xem lại và bổ sung.

## Thiết kế 10 case

Đúng 10 case: 5 single-turn dùng `query`, 5 multi-turn dùng `turns`. Tất cả `phase: "B"`. Case được viết bám vào lỗi **thật** quan sát được ở run v0 chứ không bịa tình huống.

| ID | failure_type | Bám lỗi nào của v0 |
|---|---|---|
| G01 | `missing_info` | R10 — agent bịa `screenname="sama"` |
| G02 | `out_of_scope` | R14 — agent dùng `send` để trả lời câu hỏi lập trình |
| G03 | `wrong_boundary` | R12 — gọi thẳng `send` không xin xác nhận |
| G04 | `missing_info` | R11 — agent bịa URL `example.com/article` |
| G05 | `wrong_arg_value` | R13 — nhồi "news" vào `query` thay vì đặt `topic` |
| G06 | `wrong_tool` | multi-turn: lấy handle từ lượt sau |
| G07 | `wrong_arg_value` | multi-turn: dùng URL user cung cấp ở lượt trước |
| G08 | `wrong_boundary` | multi-turn: gọi `send` **sau khi** user đồng ý |
| G09 | `wrong_boundary` | multi-turn: hủy `send` khi user từ chối |
| G10 | `unnecessary_tool` | không gọi tool thừa chỉ để đáp lễ user |

Phủ đủ 6 `failure_type` cho phép, trừ `unnecessary_tool` chỉ có 1 case.

## Ba lỗi schema đã mắc và cách sửa — ghi lại để không lặp

Bản đầu tiên của file khiến 5/10 case crash và 5 case còn lại chấm sai âm thầm.

**1. `turns` viết bằng mảng chuỗi.** `run_eval.py:85` đọc `turns[-1]["content"]` nên cần mảng dict:

```jsonc
// SAI
"turns": ["Lấy bài đăng của ông ấy đi.", "Ai cơ?", "elonmusk"]
// ĐÚNG
"turns": [{"role": "user", "content": "..."}, {"role": "user", "content": "..."}]
```

**2. Nhét lượt assistant vào `turns`.** Bản đầu chèn chuỗi JSON `{"tool_calls": ...}` giả làm câu trả lời của agent. `eval_base.json` chỉ dùng **toàn user turn**; `run_eval.py:92` đọc các lượt trước làm context và không cần agent trả lời chúng. Phần tử cuối phải là user turn đang được chấm.

**3. Dùng key `arguments` thay vì `args`.** `run_eval.py:179` đọc `expected_call.get("args", {})`. Với key sai, expected args bị coi là rỗng → **không có gì được so khớp**, case PASS chỉ nhờ trùng tên tool. Đây là lỗi nguy hiểm nhất vì nó **không báo lỗi**, chỉ âm thầm thổi phồng `argument_accuracy`.

Kèm theo: G08 ban đầu chờ `send(content=...)` trong khi tool khai báo tham số là `text`.

Bài học: eval case cũng là code — phải chạy thử trước khi tin vào số nó sinh ra.

## Kết quả

| Artifact | Case | Routing | Argument | Multiturn |
|---|---:|---:|---:|---:|
| v2 | 90.0% | 90.0% | 90.0% | 100.0% |
| v4 | 80.0% | 90.0% | 80.0% | 100.0% |

Suite group **tụt** khi base eval lên 100%. Hai case hỏng ở v4 (`G03`, `G04`) đều là tình huống ranh giới mà hành vi của agent không hẳn sai — xem phần 1b của `REPORT.md`. Đây là bằng chứng cho thấy tối ưu bám một bộ eval cố định có thể làm agent kém linh hoạt ở bộ case khác.
