import io
import os
import re
from multiprocessing import Process, Queue
from pathlib import Path
from typing import List

from docx import Document
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw_data"
OUT_DIR = DATA_DIR / "process_data"


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _strip_html(text: str) -> str:
    text = re.sub(r"<script.*?>.*?</script>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<style.*?>.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return _normalize_text(text)


def _extract_pdf_pages(data: bytes) -> List[str]:
    pages = []
    for page_layout in extract_pages(io.BytesIO(data)):
        texts = []
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                texts.append(element.get_text())
        page_text = _normalize_text(" ".join(texts))
        if page_text:
            pages.append(page_text)
    return pages


def _extract_docx_text(data: bytes) -> str:
    doc = Document(io.BytesIO(data))
    texts = [para.text for para in doc.paragraphs if para.text.strip()]
    return _normalize_text(" ".join(texts))


def _extract_pdf_pages_with_timeout(data: bytes, seconds: int) -> List[str]:
    if seconds <= 0:
        return _extract_pdf_pages(data)

    queue: Queue = Queue()

    def _worker(payload: bytes, result_queue: Queue) -> None:
        try:
            result_queue.put(("ok", _extract_pdf_pages(payload)))
        except Exception as exc:
            result_queue.put(("err", str(exc)))

    proc = Process(target=_worker, args=(data, queue))
    proc.start()
    proc.join(seconds)
    if proc.is_alive():
        proc.terminate()
        proc.join()
        raise TimeoutError(f"Timed out after {seconds}s")

    if queue.empty():
        raise RuntimeError("PDF extraction failed without output")

    status, payload = queue.get()
    if status == "ok":
        return payload
    raise RuntimeError(payload)


def _gemini_ocr_pptx(path: Path, api_key: str, model_name: str) -> str:
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    file_ref = genai.upload_file(path)
    try:
        prompt = (
            "Extract all text from this PowerPoint file. "
            "Use OCR for any text embedded in images. "
            "Return plain text only, ordered by slide. "
            "Start each slide with 'Slide N:' on its own line."
        )
        response = model.generate_content([prompt, file_ref])
        return (response.text or "").strip()
    finally:
        try:
            genai.delete_file(file_ref.name)
        except Exception:
            pass


def main() -> None:
    if not RAW_DIR.exists():
        print(f"Missing raw data directory: {RAW_DIR}")
        return

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    pdf_timeout = int(os.getenv("PDF_TIMEOUT_SECONDS", "60"))

    processed = 0
    skipped = 0
    for path in sorted(RAW_DIR.iterdir()):
        if not path.is_file():
            continue
        output_path = OUT_DIR / f"{path.stem}.txt"
        if output_path.exists():
            skipped += 1
            continue

        ext = path.suffix.lower()
        print(f"Processing {path.name}...")
        data = path.read_bytes()
        text = ""

        try:
            if ext == ".pptx":
                if not api_key:
                    print(f"Skipping {path.name}: GEMINI_API_KEY not set")
                    skipped += 1
                    continue
                text = _gemini_ocr_pptx(path, api_key, model_name)
            elif ext == ".pdf":
                pages = _extract_pdf_pages_with_timeout(data, pdf_timeout)
                text = "\n\n".join(pages)
            elif ext == ".docx":
                text = _extract_docx_text(data)
            elif ext in {".html", ".htm"}:
                text = _strip_html(data.decode("utf-8", errors="ignore"))
            elif ext == ".txt":
                text = _normalize_text(data.decode("utf-8", errors="ignore"))
            else:
                skipped += 1
                continue
        except Exception as exc:
            print(f"Skipping {path.name}: {exc}")
            skipped += 1
            continue

        if text:
            output_path.write_text(text, encoding="utf-8")
            processed += 1
        else:
            skipped += 1

    print(f"Processed {processed} files into {OUT_DIR} (skipped {skipped}).")


if __name__ == "__main__":
    main()
