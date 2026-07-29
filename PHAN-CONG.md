# Phân công — Day 04 Lab v2 (Group 29 / E403)

Nhóm 6 người, buổi chiều 14:00–18:00. Mọi yêu cầu deliverable bám theo [README.md](README.md).

## Bảng phân công

| Người | Vai | Sở hữu (độc quyền ghi) | Output commit |
|---|---|---|---|
| **Kỳ Anh (TL)** | Prompt/Routing Owner + Run Captain | `artifacts/system_prompt.md`, `artifacts/tools.yaml`, `.env` (không commit), mọi lệnh `run_eval.py` | `system_prompt.md`, `tools.yaml`, `runs/*.json` |
| **Hoàng** | Evidence Analyst | `artifacts/version_log.csv`, `analysis/*.csv` | `version_log.csv` (v0–v3), `analysis/base_runs.csv` |
| **Tuấn Anh** | Tool Dev A (tool bắt buộc) | `tools/<tool_A>/` | `tool.py`, `TOOL.md`, `tools/__init__.py` (đợt 1) |
| **Quyền** | Tool Dev B (bonus) + Final Gate | `tools/<tool_B..D>/` | 3 thư mục tool, `tools/__init__.py` (đợt 2) |
| **Đức Anh** | UI & Deploy | `app.py`, `requirements.txt` | `app.py`, `requirements.txt`, public URL |
| **Khánh** | Eval Author + Report | `data/eval_group.json`, `artifacts/REPORT.md`, `transcripts/` | 10 eval case, REPORT A+B, transcript |

**Luật vàng:** không ghi vào file người khác sở hữu. Cần đổi → nhắn chủ file, họ commit.

## 3 điểm giao nhau — phải bắt tay, không tự sửa

**1. Declaration của tool mới → `tools.yaml` là của TL**

Tuấn Anh / Quyền viết xong tool thì gửi TL **block YAML declaration** (name, description, parameters). TL paste vào `tools.yaml`.

TL lưu ý: **đừng paste tool mới vào giữa lúc đang đo một hypothesis prompt.** Thêm tool làm đổi `tools_hash` và nhiễu metric. Gộp việc thêm declaration vào đúng một mốc version và ghi rõ trong `version_log.csv` là version đó đổi cái gì.

**2. `tools/__init__.py` — 2 tool dev cùng cần**

Tách theo thời gian, không tách theo dòng:
- **Đợt 1 (~15:15–15:50):** Tuấn Anh thêm import + entry `TOOL_FUNCTIONS` cho tool A, merge vào `main`.
- **Đợt 2 (từ ~16:05):** Quyền `git pull --rebase origin main` **trước**, rồi mới thêm 3 dòng của tool B/C/D.

Quyền không đụng file này trước khi tool A merge xong.

**3. `REPORT.md` là của Khánh, nhưng nội dung đến từ cả nhóm**

Mỗi người **không** sửa `REPORT.md`. Thay vào đó tự tạo file riêng `artifacts/notes/<ten>.md` (file mới → không bao giờ conflict), Khánh ráp vào report:
- `notes/kyanh.md` — hypothesis từng version, trước/sau
- `notes/hoang.md` — bảng metric, failure analysis
- `notes/tuananh.md`, `notes/quyen.md` — tool làm gì, khi nào agent nên gọi
- `notes/ducanh.md` — URL demo, screenshot UI

Riêng **URL public** của Đức Anh phải tới tay Khánh **trước 16:20** để kịp Phần A.

---

## Chi tiết & Definition of Done

### Kỳ Anh (TL) — Prompt/Routing Owner + Run Captain

Bạn là serial bottleneck có chủ đích: một người giữ cả 2 artifact + chạy mọi eval → `prompt_hash`/`tools_hash` nhất quán, không tốn quota song song, không ai conflict với ai.

- Phát `.env` cho cả nhóm qua kênh riêng. Trước push đầu tiên: `git ls-files | grep -E "\.env|\.venv"` phải rỗng.
- Chạy `scripts/preflight_provider.py` trước khi cả nhóm bắt đầu.
- **v0 baseline** → commit `runs/*_v0.json` → báo Hoàng.
- v1, v2, v3: mỗi vòng **sửa đúng một thứ**, dựa trên failure thật trong run JSON trước đó, không phải cảm giác. Ba version phải khác hypothesis — copy-paste 3 run giống nhau là fail yêu cầu README.
  - Hiện `tools.yaml` mô tả rất mơ hồ ("Tìm trên mạng xã hội.", "Tra cứu thông tin trên internet.") → đây là mỏ điểm: nói rõ *khi nào dùng / khi nào không*, convention `topic`/`timeframe`/`search_type`, và confirmation boundary của `send`.
- Nếu đổi tên tool: chạy đủ checklist đồng bộ 8 file trong README. Trong eval cố định **chỉ** đổi field tên, không sửa query/expected.
- Chạy suite group của Khánh ở v3.

**DoD:** 4 run JSON đã commit, mỗi run có `provider_error_cases = 0` và `measured_cases = total_cases`.

### Hoàng — Evidence Analyst

- Sau mỗi run của TL: mở run JSON, lấy `summary.case_accuracy`, `tool_routing_accuracy`, `argument_accuracy`, `multiturn_accuracy` → ghi 1 dòng vào `version_log.csv`:
  ```
  version,author,changed_artifact,artifact_version,prompt_hash,tools_hash,reason,hypothesis,metric_name,metric_before,metric_after,run_file
  ```
  `author` = người đề xuất hypothesis (thường là TL), không phải người ghi file.
- `python scripts/parse_runs.py runs/ --output analysis/base_runs.csv`.
- Đọc `results[*].result.failures` và `observed_mismatch` của case fail, viết failure analysis vào `notes/hoang.md`. Đây là input để TL quyết hypothesis vòng sau → **bạn phải trả kết quả trong ~5 phút sau mỗi run**, đừng để TL chờ.
- Nhắc cả nhóm: PASS ở routing **không** có nghĩa tool chạy đúng — `tool_results` có error vẫn phải review tay.

**DoD:** `version_log.csv` đủ 4 dòng v0–v3, không dòng nào để trống hash.

### Tuấn Anh — Tool Dev A (bắt buộc)

- `tools/<tool_A>/tool.py` + `TOOL.md`, đăng ký vào `TOOL_FUNCTIONS` ở `tools/__init__.py`.
- Smoke-test trực tiếp bằng python trước khi đưa vào eval — đừng để lỗi tool lộ ra lúc chạy version.
- Gửi block YAML declaration cho TL (xem điểm giao nhau #1).
- Chọn tool mà eval case của Khánh chấm được: `compare` (đối chiếu 2 nguồn), `summarize_thread`, `save_note`, `rank_sources`…
- **Deadline 15:50** — đây là tool bắt buộc của nhóm, không được trượt.

**DoD:** tool chạy thật, xuất hiện trong `tools.yaml`, agent gọi được ít nhất 1 lần trong run hoặc transcript.

### Quyền — Tool Dev B (bonus) + Final Gate

- README: bonus cần UI bắt buộc **và** tự viết **hơn 3 tool mới**. Tool A của Tuấn Anh + B/C/D của bạn = 4 tool → vừa đủ. **Thiếu 1 tool là mất trắng bonus**, nên ưu tiên xong đủ 3 tool đơn giản hơn là 1 tool phức tạp. Optional tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tính.
- Rebase trước khi đụng `tools/__init__.py` (điểm giao nhau #2).
- **Final Gate 17:35–17:40** — bạn đọc checklist cuối file này, cái nào thiếu thì hô lên ngay, đừng tự lặng lẽ sửa.

**DoD:** 3 tool có `TOOL.md` + đăng ký + declaration; checklist final gate tick hết.

### Đức Anh — UI & Deploy

- Tạo `app.py`, **tái sử dụng `run_model_tool_loop` trong `chat.py`** — tuyệt đối không viết agent loop thứ hai (README nói rõ).
- UI phải nhìn thấy được: request + response cuối, trace từng tool (tên, args, round/status, result/error), và `transcript / run / artifact_version` đang xem.
- `streamlit>=1.30.0` vào `requirements.txt`. PASS khi mở được `http://localhost:8501`.
- Deploy: `cloudflared tunnel --url http://localhost:8501` → test bằng **điện thoại hoặc máy khác**, không phải máy build. Gửi URL cho Khánh **trước 16:20**.
- Kiểm tra UI public không lộ key, không in `.env` ra màn hình.
- Giữ tunnel sống suốt showdown 16:30–17:15; nếu rớt thì reconnect và gửi URL mới vào nhóm chat ngay.

**DoD:** người ngoài mở được URL và chat được với agent.

### Khánh — Eval Author + Report

- **10 case đúng** vào `data/eval_group.json`: 5 single-turn (`query`) + 5 multi-turn (`turns`, phần tử cuối phải là user turn đang được chấm). Mỗi case đủ `id`, `phase: "B"`, `failure_type`, `expect` (`tool_calls` hoặc `no_tool`), `metadata.what_it_tests`. Schema mẫu: `starter_v0/samples/eval_group.schema.example.json` (không tính vào 10 case).
- Case có giá trị = case bám đúng lỗi thật thấy trong run v0 của TL, không phải case bịa. Phủ trải các `failure_type`: `wrong_tool`, `wrong_arg_value`, `wrong_boundary`, `unnecessary_tool`, `out_of_scope`, `missing_info`.
- **Live chat** `python chat.py --provider openrouter --version v3` — tối thiểu 3 turn: 1 research bình thường, 1 thiếu thông tin rồi bổ sung ở lượt sau, 1 hành động nhạy cảm để test boundary xác nhận. Commit `transcripts/*.transcript.json`.
- **REPORT Phần A — xong trước 16:30**: agent làm gì, bảng tool, câu hỏi mẫu, link dùng thử.
- **REPORT Phần B** sau showdown: ráp từ `artifacts/notes/*.md` + bảng v0–v3 của Hoàng.

**DoD:** đúng 10 case (không 9, không 11), Phần A xong 16:30, Phần B đủ evidence từ log thật.

---

## Timeline

| Giờ | Kỳ Anh (TL) | Hoàng | Tuấn Anh | Quyền | Đức Anh | Khánh |
|---|---|---|---|---|---|---|
| 14:00–14:40 | phát `.env`, preflight | setup | setup | setup | setup | setup |
| 14:40–15:15 | **chạy v0** | đọc trace, note failure | code tool A | code tool B | dựng UI local | phác case từ trace v0 |
| 15:15–15:50 | sửa 1 hypothesis → **v1** | ghi dòng v1 | **xong tool A + `__init__`** | tool B | UI hiện tool trace | 5 case single-turn |
| 15:50–16:05 | nghỉ | | | | | |
| 16:05–16:30 | **v2** (+ paste declaration tool A) | ghi dòng v2, `analysis/` | note tool A | rebase → tool C, D | **deploy + gửi URL 16:20** | 5 multi-turn, **Phần A 16:30** |
| 16:30–17:15 | dẫn showdown | mở sẵn run JSON | demo tool A | demo tool bonus | live demo UI | ghi feedback team khác |
| 17:15–17:35 | áp feedback → **v3** + chạy suite group | ghi dòng v3 | hỗ trợ | **final gate** | giữ tunnel sống | live chat + **Phần B** |
| 17:35–17:40 | | | | **check submit** | | |

---

## Luật git

```bash
git checkout -b feat/<ten>-<viec>     # vd: feat/ducanh-ui-streamlit
git pull --rebase origin main
git push -u origin feat/<ten>-<viec>  # mở PR, TL merge
```

- PR nhỏ, merge mỗi 30–45 phút. Đừng ôm branch 3 tiếng rồi merge một cục lúc 17:30.
- **Không commit:** `.env`, `.venv/`, `__pycache__/`, key trong log/screenshot/poster. Đã có trong `.gitignore` — vẫn check `git status` trước mỗi commit.
- Commit message: `feat|fix|docs|eval: <mô tả>`. Ví dụ `eval: add 5 multi-turn group cases`.
- Cả 6 người phải có commit trên `main` trước 17:40.

## Final Gate checklist (Quyền, 17:35)

- [ ] `artifacts/system_prompt.md` + `artifacts/tools.yaml` khớp nhau và khớp `tools/__init__.py`
- [ ] `artifacts/version_log.csv` đủ `v0`,`v1`,`v2`,`v3` — 3 hypothesis **khác nhau**
- [ ] `data/eval_group.json` đúng 10 case (5 + 5), tất cả `phase: "B"`
- [ ] ≥ 4 tool mới, mỗi tool có `TOOL.md` + entry `TOOL_FUNCTIONS` + declaration trong `tools.yaml`
- [ ] `app.py` chạy được, URL public mở được từ máy khác
- [ ] `artifacts/REPORT.md` đủ Phần A + Phần B
- [ ] `runs/*.json` + `transcripts/*.transcript.json` đã commit
- [ ] `analysis/*.csv` đã commit
- [ ] Không có `.env` / `.venv/` / key trong repo: `git ls-files | grep -E "\.env|\.venv"` rỗng
- [ ] Cả 6 người đều có commit trên `main`
