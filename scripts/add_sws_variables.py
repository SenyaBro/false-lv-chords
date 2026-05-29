from pathlib import Path
from datetime import datetime
import re
import shutil

import pandas as pd


# =========================
# Paths
# =========================

FINAL_PATH = Path(
    r"C:\Users\Ars\projects\university\lab_urfu_2026\false-lv-chords\data\final_analysis_dataset_ver2.xlsx"
)

SOURCE_PATH = Path(
    r"C:\Users\Ars\Downloads\final_analysis_dataset ВК 27.05.xlsx"
)

REPORT_DIR = FINAL_PATH.parent / "merge_reports"


# =========================
# Columns
# =========================

FINAL_NAME_COL = "subject_full_name"

# Колонки в исходном файле
SOURCE_SWS_REST_COL_ALIASES = ["SWsrest", "SWSrest", "swsrest"]
SOURCE_SWS_MAX_COL_ALIASES = ["SWSmax", "SWsmax", "swsmax"]
SOURCE_DSWS_COL_ALIASES = ["dSWS", "DSWS", "dsws"]

# Новые имена в финальном датасете
SWS_REST_FINAL_COL = "echo_lv_sws_rest_g_cm2"
SWS_MAX_FINAL_COL = "echo_lv_sws_max_g_cm2"
SWS_DELTA_FINAL_COL = "echo_lv_sws_delta_g_cm2"

OVERWRITE_EXISTING_SWS_COLUMNS = True


# =========================
# Helpers
# =========================

def normalize_header(value) -> str:
    if pd.isna(value):
        return ""

    s = str(value).strip().lower()
    s = s.replace("ё", "е")
    s = re.sub(r"[^a-zа-я0-9]+", "", s)
    return s


def normalize_person_name(value) -> str | None:
    if pd.isna(value):
        return None

    s = str(value).strip().lower()
    s = s.replace("ё", "е")
    s = re.sub(r"[^a-zа-я\s-]+", " ", s)
    s = re.sub(r"[-]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()

    return s if s else None


def extract_surname(value) -> str | None:
    """
    Берём фамилию как первое слово из ФИО.
    Например:
    'Иванов Иван Иванович' -> 'иванов'
    'Иванов' -> 'иванов'
    """
    normalized = normalize_person_name(value)

    if not normalized:
        return None

    parts = normalized.split()
    return parts[0] if parts else None


def to_number(value):
    if pd.isna(value):
        return pd.NA

    if isinstance(value, (int, float)):
        return value

    s = str(value).strip()
    s = s.replace(",", ".")
    s = s.replace("\xa0", " ")

    match = re.search(r"-?\d+(?:\.\d+)?", s)
    if not match:
        return pd.NA

    return float(match.group(0))


def make_backup(path: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = path.with_name(
        f"{path.stem}_backup_before_sws_merge_{timestamp}{path.suffix}"
    )
    shutil.copy2(path, backup_path)
    return backup_path


def find_source_sheet_and_columns(path: Path):
    """
    Ищет лист и строку заголовков, где есть:
    - колонка с фамилией/ФИО
    - SWsrest
    - SWSmax
    - dSWS
    """

    name_aliases = [
        "ФИО",
        "фио",
        "Фамилия",
        "фамилия",
        "subject_full_name",
        "full_name",
        "name",
        "спортсмен",
    ]

    required = {
        "name": name_aliases,
        "sws_rest": SOURCE_SWS_REST_COL_ALIASES,
        "sws_max": SOURCE_SWS_MAX_COL_ALIASES,
        "sws_delta": SOURCE_DSWS_COL_ALIASES,
    }

    xls = pd.ExcelFile(path)

    for sheet_name in xls.sheet_names:
        raw = pd.read_excel(path, sheet_name=sheet_name, header=None, dtype=object)

        max_scan_rows = min(80, len(raw))

        for row_idx in range(max_scan_rows):
            row_values = raw.iloc[row_idx].tolist()
            normalized = [normalize_header(v) for v in row_values]

            found = {}

            for logical_name, variants in required.items():
                variant_norms = [normalize_header(v) for v in variants]

                for col_idx, cell_norm in enumerate(normalized):
                    if not cell_norm:
                        continue

                    if any(v == cell_norm or v in cell_norm for v in variant_norms):
                        found[logical_name] = col_idx
                        break

            if set(found.keys()) == set(required.keys()):
                return sheet_name, row_idx, found

    raise ValueError(
        "Не удалось найти в исходном файле строку заголовков с колонками: "
        "ФИО/Фамилия, SWsrest, SWSmax, dSWS. "
        "Проверь, как точно называется колонка с фамилиями."
    )


def move_cols_after_subject_name(df: pd.DataFrame) -> pd.DataFrame:
    """
    Переставляет новые SWS-колонки сразу после subject_full_name,
    чтобы их было видно в Excel.
    """
    new_cols = [
        SWS_REST_FINAL_COL,
        SWS_MAX_FINAL_COL,
        SWS_DELTA_FINAL_COL,
    ]

    cols = list(df.columns)

    for col in new_cols:
        if col in cols:
            cols.remove(col)

    if FINAL_NAME_COL not in cols:
        return df

    insert_pos = cols.index(FINAL_NAME_COL) + 1

    for col in reversed(new_cols):
        if col in df.columns:
            cols.insert(insert_pos, col)

    return df[cols]


# =========================
# Main
# =========================

def main():
    if not FINAL_PATH.exists():
        raise FileNotFoundError(f"Финальный файл не найден: {FINAL_PATH}")

    if not SOURCE_PATH.exists():
        raise FileNotFoundError(f"Исходный файл не найден: {SOURCE_PATH}")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ---------- Read final ----------
    final_xls = pd.ExcelFile(FINAL_PATH)
    final_sheet_name = final_xls.sheet_names[0]

    final_df = pd.read_excel(FINAL_PATH, sheet_name=final_sheet_name, dtype=object)

    if FINAL_NAME_COL not in final_df.columns:
        raise ValueError(
            f"В финальном датасете нет колонки '{FINAL_NAME_COL}'. "
            f"Доступные колонки: {list(final_df.columns)}"
        )

    # Если SWS-колонки уже есть, решаем, перезаписывать или нет
    sws_final_cols = [
        SWS_REST_FINAL_COL,
        SWS_MAX_FINAL_COL,
        SWS_DELTA_FINAL_COL,
    ]

    existing_sws_cols = [col for col in sws_final_cols if col in final_df.columns]

    if existing_sws_cols and not OVERWRITE_EXISTING_SWS_COLUMNS:
        raise ValueError(
            f"В финальном датасете уже есть колонки {existing_sws_cols}. "
            "Если нужно заменить их, поставь OVERWRITE_EXISTING_SWS_COLUMNS = True."
        )

    if existing_sws_cols:
        final_df = final_df.drop(columns=existing_sws_cols)

    final_df["_surname_key"] = final_df[FINAL_NAME_COL].apply(extract_surname)

    final_duplicate_surnames = final_df[
        final_df.duplicated("_surname_key", keep=False) & final_df["_surname_key"].notna()
    ].sort_values("_surname_key")

    # ---------- Read source ----------
    source_sheet_name, header_row_idx, source_cols = find_source_sheet_and_columns(SOURCE_PATH)

    raw_source = pd.read_excel(
        SOURCE_PATH,
        sheet_name=source_sheet_name,
        header=None,
        dtype=object,
    )

    source_data = raw_source.iloc[header_row_idx + 1:].copy()
    source_header = raw_source.iloc[header_row_idx].tolist()
    source_data.columns = source_header

    name_col = source_header[source_cols["name"]]
    sws_rest_col = source_header[source_cols["sws_rest"]]
    sws_max_col = source_header[source_cols["sws_max"]]
    sws_delta_col = source_header[source_cols["sws_delta"]]

    source_small = source_data.iloc[
        :,
        [
            source_cols["name"],
            source_cols["sws_rest"],
            source_cols["sws_max"],
            source_cols["sws_delta"],
        ],
    ].copy()

    source_small.columns = [
        "source_name",
        SWS_REST_FINAL_COL,
        SWS_MAX_FINAL_COL,
        SWS_DELTA_FINAL_COL,
    ]

    source_small["_surname_key"] = source_small["source_name"].apply(extract_surname)

    for col in sws_final_cols:
        source_small[col] = source_small[col].apply(to_number)

    # Оставляем только строки с фамилией
    source_small = source_small[source_small["_surname_key"].notna()].copy()

    # Оставляем только строки, где есть хотя бы одно значение SWS
    source_small = source_small[
        source_small[SWS_REST_FINAL_COL].notna()
        | source_small[SWS_MAX_FINAL_COL].notna()
        | source_small[SWS_DELTA_FINAL_COL].notna()
    ].copy()

    source_duplicate_surnames = source_small[
        source_small.duplicated("_surname_key", keep=False)
    ].sort_values("_surname_key")

    # Дубли по фамилии из исходника не используем автоматически
    source_unique = source_small[
        ~source_small.duplicated("_surname_key", keep=False)
    ].copy()

    # ---------- Merge ----------
    merged = final_df.merge(
        source_unique[
            [
                "_surname_key",
                "source_name",
                SWS_REST_FINAL_COL,
                SWS_MAX_FINAL_COL,
                SWS_DELTA_FINAL_COL,
            ]
        ],
        on="_surname_key",
        how="left",
        validate="m:1",
    )

    # Если в финальном датасете есть одинаковые фамилии, не заполняем их автоматически
    duplicate_final_keys = set(final_duplicate_surnames["_surname_key"].dropna())

    can_fill_mask = (
        merged["source_name"].notna()
        & ~merged["_surname_key"].isin(duplicate_final_keys)
    )

    # ---------- Report masks ----------
    filled_mask = (
        can_fill_mask
        & (
            merged[SWS_REST_FINAL_COL].notna()
            | merged[SWS_MAX_FINAL_COL].notna()
            | merged[SWS_DELTA_FINAL_COL].notna()
        )
    )

    filled_rows = merged.loc[
        filled_mask,
        [
            FINAL_NAME_COL,
            "source_name",
            SWS_REST_FINAL_COL,
            SWS_MAX_FINAL_COL,
            SWS_DELTA_FINAL_COL,
        ],
    ].copy()

    unmatched_final = merged.loc[
        merged["source_name"].isna(),
        [
            FINAL_NAME_COL,
            "_surname_key",
        ],
    ].copy()

    skipped_final_duplicate_surnames = merged.loc[
        merged["_surname_key"].isin(duplicate_final_keys),
        [
            FINAL_NAME_COL,
            "_surname_key",
            "source_name",
            SWS_REST_FINAL_COL,
            SWS_MAX_FINAL_COL,
            SWS_DELTA_FINAL_COL,
        ],
    ].copy()

    used_source_keys = set(merged.loc[merged["source_name"].notna(), "_surname_key"].dropna())

    unmatched_source = source_unique[
        ~source_unique["_surname_key"].isin(used_source_keys)
    ].copy()

    # ---------- Clean final ----------
    merged = merged.drop(columns=["_surname_key", "source_name"])

    merged = move_cols_after_subject_name(merged)

    # ---------- Report ----------
    summary = pd.DataFrame(
        {
            "metric": [
                "final_rows",
                "source_rows_with_sws",
                "source_unique_surnames_used_for_merge",
                "filled_final_rows",
                "unmatched_final_rows",
                "unmatched_source_rows",
                "source_duplicate_surname_rows_excluded",
                "final_duplicate_surname_rows_skipped",
                "source_sheet",
                "source_header_row_excel_number",
                "source_name_col",
                "source_sws_rest_col",
                "source_sws_max_col",
                "source_sws_delta_col",
                "final_sws_rest_col",
                "final_sws_max_col",
                "final_sws_delta_col",
            ],
            "value": [
                len(final_df),
                len(source_small),
                len(source_unique),
                len(filled_rows),
                len(unmatched_final),
                len(unmatched_source),
                len(source_duplicate_surnames),
                len(skipped_final_duplicate_surnames),
                source_sheet_name,
                header_row_idx + 1,
                str(name_col),
                str(sws_rest_col),
                str(sws_max_col),
                str(sws_delta_col),
                SWS_REST_FINAL_COL,
                SWS_MAX_FINAL_COL,
                SWS_DELTA_FINAL_COL,
            ],
        }
    )

    report_path = REPORT_DIR / f"sws_merge_report_{timestamp}.xlsx"

    with pd.ExcelWriter(report_path, engine="openpyxl") as writer:
        summary.to_excel(writer, sheet_name="summary", index=False)
        filled_rows.to_excel(writer, sheet_name="filled_rows", index=False)
        unmatched_final.to_excel(writer, sheet_name="unmatched_final", index=False)
        unmatched_source.to_excel(writer, sheet_name="unmatched_source", index=False)
        source_duplicate_surnames.to_excel(writer, sheet_name="source_duplicate_surnames", index=False)
        final_duplicate_surnames.to_excel(writer, sheet_name="final_duplicate_surnames", index=False)
        skipped_final_duplicate_surnames.to_excel(writer, sheet_name="skipped_final_duplicates", index=False)

    # ---------- Backup and save ----------
    backup_path = make_backup(FINAL_PATH)

    with pd.ExcelWriter(
        FINAL_PATH,
        engine="openpyxl",
        mode="a",
        if_sheet_exists="replace",
    ) as writer:
        merged.to_excel(writer, sheet_name=final_sheet_name, index=False)

    print("Готово.")
    print(f"Финальный файл обновлён: {FINAL_PATH}")
    print(f"Backup сохранён: {backup_path}")
    print(f"Отчёт сохранён: {report_path}")
    print()
    print("Добавлены колонки:")
    print(f"  - {SWS_REST_FINAL_COL}")
    print(f"  - {SWS_MAX_FINAL_COL}")
    print(f"  - {SWS_DELTA_FINAL_COL}")
    print()
    print(f"Строк заполнено: {len(filled_rows)}")
    print(f"Не найдено в source: {len(unmatched_final)}")
    print(f"Дубли фамилий в source исключены: {len(source_duplicate_surnames)}")
    print(f"Дубли фамилий в final пропущены: {len(skipped_final_duplicate_surnames)}")


if __name__ == "__main__":
    main()