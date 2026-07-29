# Notes — Đức Anh (UI & Deploy)

> Bản nháp dựng từ code thật trong `app.py`. Đức Anh xem lại và bổ sung phần deploy/URL.

## Kiến trúc

`app.py` (308 dòng, Streamlit) **tái sử dụng `run_model_tool_loop` từ `chat.py`** thay vì viết agent loop thứ hai — đúng yêu cầu README. Artifact được nạp từ `artifacts/system_prompt.md` và `artifacts/tools.yaml` qua `build_artifact_version()` trong `versioning.py`, nên UI luôn chạy đúng bộ artifact đang có trên đĩa và hash hiển thị khớp với run JSON.

## Bằng chứng UI hiển thị được

Theo checklist "Bằng chứng tối thiểu trên UI" của README:

| Yêu cầu | Chỗ hiển thị |
|---|---|
| request + response cuối | khung chat chính, `st.chat_input` |
| trace từng tool: tên, args, round/status, result/error | expander "Tool trace · lượt N" |
| transcript / run / artifact_version | sidebar, `st.code` |

Transcript được ghi ra `transcripts/*.transcript.json` sau mỗi lượt, cùng định dạng với `chat.py`.

## Giới hạn đã biết — quan trọng khi demo

Ô **"Version"** trong sidebar chỉ là `text_input` dùng để đặt tên file transcript. Nó **không** nạp lại artifact của version cũ — prompt và tools luôn đọc từ file hiện tại.

Hệ quả: gõ "v0" vào ô đó rồi chat sẽ **không** tái hiện hành vi v0. Đây là lý do các transcript đầu buổi mang tên `v0_` nhưng hash bên trong lại là prompt v1 + tools v2.

**Đã bù bằng chế độ "So sánh version"** (sidebar → Chế độ). Màn hình này đọc `runs/*.json` đã lưu và cho chọn một `case_id` để xem từng version thật sự đã gọi tool gì, PASS/FAIL, `observed_mismatch`, `failures` — đúng gạch đầu dòng "cùng một scenario demo được chạy qua nhiều prompt/tool version" trong README. Cách này chính xác hơn việc replay live vì mỗi dòng gắn với `artifact_version` thật, lại không tốn API credit khi demo.

Muốn *chat live* bằng artifact cũ thì vẫn phải `git checkout` artifact rồi chạy lại — chưa làm, và cũng không cần cho phần chấm.

## Setup để chạy

```bash
pip install -r requirements.txt      # đã có streamlit>=1.30.0
streamlit run app.py                 # PASS khi mở được http://localhost:8501
```

Lưu ý: `streamlit` phải được cài trong đúng `.venv` đang dùng — máy TL từng thiếu gói này và `streamlit run` báo `ModuleNotFoundError` dù `requirements.txt` đã ghi đủ.

## Deploy

```bash
cloudflared tunnel --url http://localhost:8501
```

Lấy URL `trycloudflare.com`, test lại từ thiết bị khác, rồi dán vào `REPORT.md` Phần A.

**Chưa hoàn thành:** URL public chưa được điền vào `REPORT.md` Phần A mục 4 — chỗ cần dán đã đánh dấu rõ `<CHƯA ĐIỀN …>`, mở tunnel xong thì thay chuỗi đó bằng link.

**Đã xử lý:** rò rỉ secret trên tunnel công khai. `redact_secrets()` ở [app.py](../../app.py#L37) thay mọi giá trị của 8 biến môi trường nhạy cảm (`OPENROUTER_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `TAVILY_API_KEY`, `FIRECRAWL_API_KEY`, `RAPIDAPI_KEY`, `TELEGRAM_BOT_TOKEN`) bằng `***REDACTED***` trước khi render args, tool result, và cả message lỗi của provider.
