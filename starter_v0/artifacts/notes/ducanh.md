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

Hệ quả: gõ "v0" vào ô đó rồi chat sẽ **không** tái hiện hành vi v0. Muốn so sánh version thì phải chiếu run JSON đã lưu, hoặc `git checkout` artifact cũ trước khi chạy. Đây là lý do các transcript đầu buổi mang tên `v0_` nhưng hash bên trong lại là prompt v1 + tools v2.

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

**Chưa hoàn thành:** URL public chưa được điền vào `REPORT.md` (dòng 44 vẫn là placeholder). `.env` chứa 4 API key thật nên khi mở tunnel phải chắc UI không in biến môi trường hay log chứa key ra màn hình.
