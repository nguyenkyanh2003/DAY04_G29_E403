from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import (
    ARTIFACTS_DIR,
    ROOT,
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


SYSTEM_PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"
TRANSCRIPTS_DIR = ROOT / "transcripts"
PROVIDERS = ("openrouter", "openai", "anthropic", "gemini")


st.set_page_config(
    page_title="Research Agent",
    page_icon="🔎",
    layout="wide",
)


def redact_secrets(value: Any) -> Any:
    """Remove configured secret values before rendering errors or tool results."""
    secret_names = (
        "OPENROUTER_API_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
        "TAVILY_API_KEY",
        "FIRECRAWL_API_KEY",
        "RAPIDAPI_KEY",
        "TELEGRAM_BOT_TOKEN",
    )
    secrets = [os.getenv(name) for name in secret_names if os.getenv(name)]

    if isinstance(value, str):
        redacted = value
        for secret in secrets:
            redacted = redacted.replace(secret, "***REDACTED***")
        return redacted
    if isinstance(value, dict):
        return {key: redact_secrets(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redact_secrets(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_secrets(item) for item in value)
    return value


def new_transcript(
    *,
    provider_name: str,
    model: str | None,
    version_label: str,
    history_window: int,
    max_tool_rounds: int,
) -> tuple[dict[str, Any], Path]:
    artifact_version = build_artifact_version(
        version_label,
        SYSTEM_PROMPT_PATH,
        TOOLS_PATH,
    )
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join(
        [safe_slug(version_label), safe_slug(provider_name), timestamp]
    )
    transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    transcript: dict[str, Any] = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": model,
        "system_prompt": str(SYSTEM_PROMPT_PATH),
        "tools": str(TOOLS_PATH),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    return transcript, transcript_path


def reset_chat() -> None:
    for key in ("history", "turns", "transcript", "transcript_path", "run_id"):
        st.session_state.pop(key, None)


def render_trace(turn: dict[str, Any]) -> None:
    rounds = turn.get("rounds") or []
    if not rounds:
        if turn.get("error"):
            st.error(redact_secrets(turn["error"]))
        else:
            st.caption("Lượt này không có tool trace.")
        return

    for round_record in rounds:
        round_number = round_record.get("round", "?")
        calls = round_record.get("tool_calls") or []
        results = round_record.get("tool_results") or []
        status = "completed" if calls else "answered"
        st.markdown(f"### Round {round_number}")
        st.caption(f"Trạng thái: {status}")

        assistant_text = round_record.get("assistant_text")
        if assistant_text:
            with st.container(border=True):
                st.markdown("#### Phản hồi của model")
                st.markdown(redact_secrets(assistant_text))

        if not calls:
            st.caption("Model trả lời trực tiếp, không gọi tool.")
            continue

        for index, call in enumerate(calls):
            tool_name = call.get("name", "unknown_tool")
            result_event = results[index] if index < len(results) else {}
            result = result_event.get("result")
            has_error = isinstance(result, dict) and bool(result.get("error"))
            call_status = "error" if has_error else "success"

            with st.container(border=True):
                st.markdown(f"`{tool_name}` · **{call_status}**")
                args_col, result_col = st.columns(2)
                with args_col:
                    st.caption("Arguments")
                    st.json(redact_secrets(call.get("args") or {}))
                with result_col:
                    st.caption("Result / Error")
                    st.json(redact_secrets(result))


def initialize_session(
    *,
    provider_name: str,
    model: str | None,
    version_label: str,
    history_window: int,
    max_tool_rounds: int,
) -> None:
    if "history" not in st.session_state:
        st.session_state.history = []
    if "turns" not in st.session_state:
        st.session_state.turns = []
    if "run_id" not in st.session_state:
        st.session_state.run_id = f"ui-{datetime.now().strftime('%Y%m%dT%H%M%S')}"
    if "transcript" not in st.session_state:
        transcript, path = new_transcript(
            provider_name=provider_name,
            model=model,
            version_label=version_label,
            history_window=history_window,
            max_tool_rounds=max_tool_rounds,
        )
        st.session_state.transcript = transcript
        st.session_state.transcript_path = path


st.title("🔎 Research Agent")
st.caption("Chat với agent, theo dõi từng tool call và kiểm tra artifact đang chạy.")

with st.sidebar:
    st.header("Cấu hình")
    provider_name = st.selectbox("Provider", PROVIDERS, index=0)
    version_label = st.text_input("Version", value="v0").strip() or "v0"
    model_input = st.text_input(
        "Model (để trống để dùng mặc định)",
        value="",
    ).strip()
    history_window = st.number_input(
        "Số cặp hội thoại giữ trong context",
        min_value=1,
        max_value=20,
        value=5,
        step=1,
    )
    max_tool_rounds = st.number_input(
        "Số vòng gọi tool tối đa",
        min_value=1,
        max_value=10,
        value=4,
        step=1,
    )
    if st.button("Bắt đầu cuộc chat mới", use_container_width=True):
        reset_chat()
        st.rerun()

model = model_input or None
initialize_session(
    provider_name=provider_name,
    model=model,
    version_label=version_label,
    history_window=int(history_window),
    max_tool_rounds=int(max_tool_rounds),
)

try:
    current_artifact = build_artifact_version(
        version_label,
        SYSTEM_PROMPT_PATH,
        TOOLS_PATH,
    )
except Exception as exc:
    st.error(f"Không thể đọc artifact: {redact_secrets(str(exc))}")
    st.stop()

with st.sidebar:
    st.divider()
    st.subheader("Phiên đang xem")
    st.code(f"run: {st.session_state.run_id}")
    st.code(f"transcript: {st.session_state.transcript['transcript_id']}")
    st.code(f"artifact_version: {current_artifact.artifact_version}")
    st.caption(f"Transcript file: {st.session_state.transcript_path.name}")

for turn_index, turn in enumerate(st.session_state.turns, start=1):
    with st.chat_message("user"):
        st.markdown(turn["user"])
    with st.chat_message("assistant"):
        if turn.get("status") == "provider_error":
            st.error(redact_secrets(turn.get("error", "Provider error")))
        else:
            st.markdown(turn.get("assistant_text") or "_Không có nội dung trả lời._")
        with st.expander(f"Tool trace · lượt {turn_index}"):
            render_trace(turn)

user_text = st.chat_input("Nhập yêu cầu nghiên cứu...")
if user_text:
    with st.chat_message("user"):
        st.markdown(user_text)

    turn_record: dict[str, Any] = {
        "turn_index": len(st.session_state.turns) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    with st.chat_message("assistant"):
        with st.spinner("Agent đang xử lý..."):
            try:
                system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
                declarations = load_tool_declarations(TOOLS_PATH)
                openai_tools = to_openai_tools(declarations)
                provider = make_provider(provider_name)
                selected_model = model or getattr(provider, "default_model", None)
                messages = [
                    {"role": "system", "content": system_prompt},
                    *trim_history(
                        st.session_state.history,
                        int(history_window),
                    ),
                    {"role": "user", "content": user_text},
                ]
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=openai_tools,
                    model=model,
                    max_tool_rounds=int(max_tool_rounds),
                )
                turn_record.update(result)
                assistant_text = result.get("assistant_text") or ""
                st.markdown(assistant_text or "_Không có nội dung trả lời._")
                st.session_state.history.extend(
                    [
                        {"role": "user", "content": user_text},
                        {"role": "assistant", "content": assistant_text},
                    ]
                )
                st.session_state.transcript["model"] = selected_model
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
                turn_record.update(
                    {
                        "status": "provider_error",
                        "error": redact_secrets(error),
                    }
                )
                st.error(redact_secrets(error))

        turn_record["ended_at"] = now_iso()
        st.session_state.turns.append(turn_record)
        st.session_state.transcript["turns"].append(turn_record)
        write_transcript(
            st.session_state.transcript_path,
            st.session_state.transcript,
        )

        with st.expander(
            f"Tool trace · lượt {turn_record['turn_index']}",
            expanded=True,
        ):
            render_trace(turn_record)
