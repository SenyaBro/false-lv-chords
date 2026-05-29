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
    r"C:\Users\Ars\projects\university\lab_urfu_2026\table_const\data\raw\ИСХОДНЫЕ ДАННЫЕ 66 ЧЕЛОВЕК.xlsx"
)

REPORT_DIR = FINAL_PATH.parent / "merge_reports"


# =========================
# Column settings
# =========================

FINAL_NAME_COL = "subject_full_name"

# Новые имена переменных в стиле snake_case
NEW_REST_COL = "hemo_sbp_rest_mmhg"
NEW_EXERCISE_COL = "hemo_sbp_exercise_mmhg"
NEW_DSWS_COL = "dsws"

# Если эти колонки уже есть в final dataset, они будут заменены
OVERWRITE_EXISTING_COLUMNS = True


# =========================
# Helpers
# =========================

def normalize_header(value) -> str:
    """
    Нормализация заголовков колонок:
    'САД покоя', 'САД ПОКОЯ', ' САД   покоя ' -> 'садпокоя'
    """
    if pd.isna(value):
        return ""

    s = str(value).strip().lower()
    s = s.replace("ё", "е")
    s = re.sub(r"[^a-zа-я0-9]+", "", s)
    return s


def normalize_person_name(value) -> str | None:
    """
    Нормализация ФИО для мэчинга:
    - нижний регистр
    - ё -> е
    - убираем точки, запятые, лишние пробелы
    """
    if pd.isna(value):
        return None

    s = str(value).strip().lower()
    s = s.replace("ё", "е")
    s = re.sub(r"[^a-zа-я\s-]+", " ", s)
    s = re.sub(r"[-]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()

    return s if s else None


def to_number(value):
    """
    Аккуратно переводит значения давления в число.
    Поддерживает варианты типа '120', '120,0', '120 мм рт.ст.'
    """
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


def find_source_sheet_and_columns(path: Path):
    """
    Ищет лист и строку заголовков, где есть:
    - ФИО
    - САД покоя
    - САД НАГР
    """

    required = {
        "fio": ["ФИО", "фио"],
        "sad_rest": ["САД покоя", "сад покоя", "садпокоя"],
        "sad_exercise": ["САД НАГР", "сад нагр", "сад нагрузки", "сад нагрузка", "саднагр"],
    }

    xls = pd.ExcelFile(path)

    for sheet_name in xls.sheet_names:
        raw = pd.read_excel(path, sheet_name=sheet_name, header=None, dtype=object)

        # смотрим первые 50 строк на случай, если таблица начинается не с первой строки
        max_scan_rows = min(50, len(raw))

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
        "Не удалось найти в исходном файле лист с колонками: "
        "ФИО, САД покоя, САД НАГР. Проверь названия колонок."
    )


def make_backup(path: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = path.with_name(f"{path.stem}_backup_before_bp_merge_{timestamp}{path.suffix}")
    shutil.copy2(path, backup_path)
    return backup_path


# =========================
# Main script
# =========================

def main():
    if not FINAL_PATH.exists():
        raise FileNotFoundError(f"Финальный файл не найден: {FINAL_PATH}")

    if not SOURCE_PATH.exists():
        raise FileNotFoundError(f"Исходный файл не найден: {SOURCE_PATH}")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ---------- Read final dataset ----------
    final_xls = pd.ExcelFile(FINAL_PATH)
    final_sheet_name = final_xls.sheet_names[0]

    final_df = pd.read_excel(FINAL_PATH, sheet_name=final_sheet_name, dtype=object)

    if FINAL_NAME_COL not in final_df.columns:
        raise ValueError(
            f"В финальном датасете не найдена колонка '{FINAL_NAME_COL}'. "
            f"Доступные колонки: {list(final_df.columns)}"
        )

    # ---------- Read source dataset ----------
    source_sheet_name, header_row_idx, source_cols = find_source_sheet_and_columns(SOURCE_PATH)

    raw_source = pd.read_excel(SOURCE_PATH, sheet_name=source_sheet_name, header=None, dtype=object)

    source_data = raw_source.iloc[header_row_idx + 1:].copy()
    source_header = raw_source.iloc[header_row_idx].tolist()
    source_data.columns = source_header

    fio_col = source_header[source_cols["fio"]]
    sad_rest_col = source_header[source_cols["sad_rest"]]
    sad_exercise_col = source_header[source_cols["sad_exercise"]]

    source_small = source_data.iloc[
        :,
        [
            source_cols["fio"],
            source_cols["sad_rest"],
            source_cols["sad_exercise"],
        ],
    ].copy()

    source_small.columns = [
        "source_full_name",
        NEW_REST_COL,
        NEW_EXERCISE_COL,
    ]

    # ---------- Normalize and parse ----------
    final_df["_merge_name_key"] = final_df[FINAL_NAME_COL].apply(normalize_person_name)
    source_small["_merge_name_key"] = source_small["source_full_name"].apply(normalize_person_name)

    source_small[NEW_REST_COL] = source_small[NEW_REST_COL].apply(to_number)
    source_small[NEW_EXERCISE_COL] = source_small[NEW_EXERCISE_COL].apply(to_number)

    # dsws = САД нагрузки - САД покоя
    source_small[NEW_DSWS_COL] = source_small[NEW_EXERCISE_COL] - source_small[NEW_REST_COL]

    # убираем пустые ФИО
    source_small = source_small[source_small["_merge_name_key"].notna()].copy()
    final_df = final_df[final_df["_merge_name_key"].notna()].copy()

    # ---------- Check duplicates ----------
    source_duplicates = source_small[
        source_small.duplicated("_merge_name_key", keep=False)
    ].sort_values("_merge_name_key")

    final_duplicates = final_df[
        final_df.duplicated("_merge_name_key", keep=False)
    ].sort_values("_merge_name_key")

    # В source дубли лучше не мержить автоматически
    source_unique = source_small[
        ~source_small.duplicated("_merge_name_key", keep=False)
    ].copy()

    # ---------- Remove existing columns if needed ----------
    new_cols = [NEW_REST_COL, NEW_EXERCISE_COL, NEW_DSWS_COL]

    existing_new_cols = [col for col in new_cols if col in final_df.columns]

    if existing_new_cols and not OVERWRITE_EXISTING_COLUMNS:
        raise ValueError(
            "В финальном датасете уже есть колонки: "
            f"{existing_new_cols}. Если нужно заменить их, поставь "
            "OVERWRITE_EXISTING_COLUMNS = True."
        )

    if existing_new_cols:
        final_df = final_df.drop(columns=existing_new_cols)

    # ---------- Merge ----------
    merge_cols = [
        "_merge_name_key",
        "source_full_name",
        NEW_REST_COL,
        NEW_EXERCISE_COL,
        NEW_DSWS_COL,
    ]

    merged_df = final_df.merge(
        source_unique[merge_cols],
        on="_merge_name_key",
        how="left",
        validate="m:1",
    )

    matched_mask = merged_df[NEW_REST_COL].notna() | merged_df[NEW_EXERCISE_COL].notna()

    matched = merged_df.loc[
        matched_mask,
        [
            FINAL_NAME_COL,
            "source_full_name",
            NEW_REST_COL,
            NEW_EXERCISE_COL,
            NEW_DSWS_COL,
        ],
    ].copy()

    unmatched_final = merged_df.loc[
        ~matched_mask,
        [FINAL_NAME_COL, "_merge_name_key"],
    ].copy()

    used_source_keys = set(merged_df.loc[matched_mask, "_merge_name_key"].dropna())
    unmatched_source = source_unique[
        ~source_unique["_merge_name_key"].isin(used_source_keys)
    ].copy()

    # ---------- Prepare final output ----------
    columns_to_drop = ["_merge_name_key", "source_full_name"]
    merged_df = merged_df.drop(columns=[c for c in columns_to_drop if c in merged_df.columns])

    # ---------- Save report ----------
    report_path = REPORT_DIR / f"bp_merge_report_{timestamp}.xlsx"

    summary = pd.DataFrame(
        {
            "metric": [
                "final_rows",
                "source_rows_after_header",
                "source_unique_names_used_for_merge",
                "matched_final_rows",
                "unmatched_final_rows",
                "unmatched_source_rows",
                "source_duplicate_rows_excluded",
                "final_duplicate_rows",
                "source_sheet",
                "source_header_row_excel_number",
                "source_fio_col",
                "source_sad_rest_col",
                "source_sad_exercise_col",
                "dsws_formula",
            ],
            "value": [
                len(final_df),
                len(source_small),
                len(source_unique),
                len(matched),
                len(unmatched_final),
                len(unmatched_source),
                len(source_duplicates),
                len(final_duplicates),
                source_sheet_name,
                header_row_idx + 1,
                str(fio_col),
                str(sad_rest_col),
                str(sad_exercise_col),
                f"{NEW_DSWS_COL} = {NEW_EXERCISE_COL} - {NEW_REST_COL}",
            ],
        }
    )

    with pd.ExcelWriter(report_path, engine="openpyxl") as writer:
        summary.to_excel(writer, sheet_name="summary", index=False)
        matched.to_excel(writer, sheet_name="matched", index=False)
        unmatched_final.to_excel(writer, sheet_name="unmatched_final", index=False)
        unmatched_source.to_excel(writer, sheet_name="unmatched_source", index=False)
        source_duplicates.to_excel(writer, sheet_name="source_duplicates", index=False)
        final_duplicates.to_excel(writer, sheet_name="final_duplicates", index=False)

    # ---------- Backup and save final file ----------
    backup_path = make_backup(FINAL_PATH)

    with pd.ExcelWriter(
        FINAL_PATH,
        engine="openpyxl",
        mode="a",
        if_sheet_exists="replace",
    ) as writer:
        merged_df.to_excel(writer, sheet_name=final_sheet_name, index=False)

    print("Готово.")
    print(f"Финальный файл обновлён: {FINAL_PATH}")
    print(f"Backup сохранён: {backup_path}")
    print(f"Отчёт по merge сохранён: {report_path}")
    print()
    print("Добавлены переменные:")
    print(f"  - {NEW_REST_COL}")
    print(f"  - {NEW_EXERCISE_COL}")
    print(f"  - {NEW_DSWS_COL}")
    print()
    print(f"Matched rows: {len(matched)}")
    print(f"Unmatched final rows: {len(unmatched_final)}")
    print(f"Source duplicate rows excluded: {len(source_duplicates)}")


if __name__ == "__main__":
    main()