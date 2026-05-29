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
    r"C:\Users\Ars\projects\university\lab_urfu_2026\table_const\data\raw\набор данных для докторской диссертации 23_03_20.xls"
)

REPORT_DIR = FINAL_PATH.parent / "merge_reports"


# =========================
# Columns
# =========================

FINAL_NAME_COL = "subject_full_name"

REST_COL = "hemo_sbp_rest_mmhg"
EXERCISE_COL = "hemo_sbp_exercise_mmhg"
DSWS_COL = "dsws"


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


def is_missing(value) -> bool:
    return pd.isna(value) or str(value).strip() == ""


def make_backup(path: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = path.with_name(
        f"{path.stem}_backup_before_doctoral_bp_fill_{timestamp}{path.suffix}"
    )
    shutil.copy2(path, backup_path)
    return backup_path


def find_source_sheet_and_columns(path: Path):
    """
    Ищет лист и строку заголовков, где есть:
    - ФИО
    - САД покоя
    - САД КОНЕЦ ТЕСТА
    """

    required = {
        "fio": [
            "ФИО",
            "фио",
        ],
        "sad_rest": [
            "САД покоя",
            "сад покоя",
            "садпокоя",
        ],
        "sad_end_test": [
            "САД КОНЕЦ ТЕСТА",
            "сад конец теста",
            "сад конец",
            "садконецтеста",
        ],
    }

    xls = pd.ExcelFile(path, engine="xlrd")

    for sheet_name in xls.sheet_names:
        raw = pd.read_excel(
            path,
            sheet_name=sheet_name,
            header=None,
            dtype=object,
            engine="xlrd",
        )

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
        "Не удалось найти в source-файле колонки: "
        "ФИО, САД покоя, САД КОНЕЦ ТЕСТА. "
        "Проверь названия колонок или строку заголовков."
    )


def move_cols_after_subject_name(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ставит новые колонки рядом с subject_full_name, чтобы их было видно в Excel.
    """
    new_cols = [REST_COL, EXERCISE_COL, DSWS_COL]

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
        raise FileNotFoundError(f"Source-файл не найден: {SOURCE_PATH}")

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

    # Если колонок ещё нет, создаём
    for col in [REST_COL, EXERCISE_COL, DSWS_COL]:
        if col not in final_df.columns:
            final_df[col] = pd.NA

    # Считаем состояние ДО
    before_counts = {
        REST_COL: final_df[REST_COL].notna().sum(),
        EXERCISE_COL: final_df[EXERCISE_COL].notna().sum(),
        DSWS_COL: final_df[DSWS_COL].notna().sum(),
    }

    final_df["_merge_name_key"] = final_df[FINAL_NAME_COL].apply(normalize_person_name)

    # ---------- Read source ----------
    source_sheet_name, header_row_idx, source_cols = find_source_sheet_and_columns(SOURCE_PATH)

    raw_source = pd.read_excel(
        SOURCE_PATH,
        sheet_name=source_sheet_name,
        header=None,
        dtype=object,
        engine="xlrd",
    )

    source_data = raw_source.iloc[header_row_idx + 1:].copy()
    source_header = raw_source.iloc[header_row_idx].tolist()
    source_data.columns = source_header

    source_small = source_data.iloc[
        :,
        [
            source_cols["fio"],
            source_cols["sad_rest"],
            source_cols["sad_end_test"],
        ],
    ].copy()

    source_small.columns = [
        "source_full_name",
        "source_sbp_rest",
        "source_sbp_end_test",
    ]

    source_small["_merge_name_key"] = source_small["source_full_name"].apply(normalize_person_name)
    source_small["source_sbp_rest"] = source_small["source_sbp_rest"].apply(to_number)
    source_small["source_sbp_end_test"] = source_small["source_sbp_end_test"].apply(to_number)

    source_small["source_dsws"] = (
        source_small["source_sbp_end_test"] - source_small["source_sbp_rest"]
    )

    # Оставляем только строки с ФИО
    source_small = source_small[source_small["_merge_name_key"].notna()].copy()

    # Оставляем только строки, где есть хотя бы одно давление
    source_small = source_small[
        source_small["source_sbp_rest"].notna()
        | source_small["source_sbp_end_test"].notna()
    ].copy()

    # Дубли по ФИО не мержим автоматически
    source_duplicates = source_small[
        source_small.duplicated("_merge_name_key", keep=False)
    ].sort_values("_merge_name_key")

    source_unique = source_small[
        ~source_small.duplicated("_merge_name_key", keep=False)
    ].copy()

    # ---------- Merge ----------
    merged = final_df.merge(
        source_unique[
            [
                "_merge_name_key",
                "source_full_name",
                "source_sbp_rest",
                "source_sbp_end_test",
                "source_dsws",
            ]
        ],
        on="_merge_name_key",
        how="left",
        validate="m:1",
    )

    has_source_match = merged["source_full_name"].notna()

    # ---------- Fill only missing values ----------
    rest_missing = merged[REST_COL].apply(is_missing)
    exercise_missing = merged[EXERCISE_COL].apply(is_missing)
    dsws_missing = merged[DSWS_COL].apply(is_missing)

    fill_rest_mask = rest_missing & merged["source_sbp_rest"].notna()
    fill_exercise_mask = exercise_missing & merged["source_sbp_end_test"].notna()

    merged.loc[fill_rest_mask, REST_COL] = merged.loc[fill_rest_mask, "source_sbp_rest"]
    merged.loc[fill_exercise_mask, EXERCISE_COL] = merged.loc[
        fill_exercise_mask,
        "source_sbp_end_test",
    ]

    # dsws пересчитываем только там, где dsws пустой,
    # но уже есть оба значения давления в финальной таблице
    rest_num = pd.to_numeric(merged[REST_COL], errors="coerce")
    exercise_num = pd.to_numeric(merged[EXERCISE_COL], errors="coerce")

    fill_dsws_mask = (
        dsws_missing
        & rest_num.notna()
        & exercise_num.notna()
    )

    merged.loc[fill_dsws_mask, DSWS_COL] = (
        exercise_num.loc[fill_dsws_mask] - rest_num.loc[fill_dsws_mask]
    )

    # ---------- Reports ----------
    after_counts = {
        REST_COL: merged[REST_COL].notna().sum(),
        EXERCISE_COL: merged[EXERCISE_COL].notna().sum(),
        DSWS_COL: merged[DSWS_COL].notna().sum(),
    }

    filled_rows = merged[
        fill_rest_mask | fill_exercise_mask | fill_dsws_mask
    ][
        [
            FINAL_NAME_COL,
            "source_full_name",
            REST_COL,
            EXERCISE_COL,
            DSWS_COL,
            "source_sbp_rest",
            "source_sbp_end_test",
            "source_dsws",
        ]
    ].copy()

    matched_but_not_filled = merged[
        has_source_match
        & ~(fill_rest_mask | fill_exercise_mask | fill_dsws_mask)
    ][
        [
            FINAL_NAME_COL,
            "source_full_name",
            REST_COL,
            EXERCISE_COL,
            DSWS_COL,
            "source_sbp_rest",
            "source_sbp_end_test",
            "source_dsws",
        ]
    ].copy()

    still_missing_final = merged[
        merged[REST_COL].apply(is_missing)
        | merged[EXERCISE_COL].apply(is_missing)
        | merged[DSWS_COL].apply(is_missing)
    ][
        [
            FINAL_NAME_COL,
            REST_COL,
            EXERCISE_COL,
            DSWS_COL,
        ]
    ].copy()

    source_not_used = source_unique[
        ~source_unique["_merge_name_key"].isin(set(merged.loc[has_source_match, "_merge_name_key"]))
    ].copy()

    summary = pd.DataFrame(
        {
            "metric": [
                "final_rows",
                "source_rows_with_name_and_bp",
                "source_unique_names_used_for_merge",
                "source_duplicate_rows_excluded",
                "source_sheet",
                "source_header_row_excel_number",
                f"{REST_COL}_non_missing_before",
                f"{REST_COL}_non_missing_after",
                f"{EXERCISE_COL}_non_missing_before",
                f"{EXERCISE_COL}_non_missing_after",
                f"{DSWS_COL}_non_missing_before",
                f"{DSWS_COL}_non_missing_after",
                "filled_rest_cells",
                "filled_exercise_cells",
                "filled_dsws_cells",
                "rows_with_any_value_filled",
                "still_missing_any_of_3_cols",
                "dsws_formula",
            ],
            "value": [
                len(final_df),
                len(source_small),
                len(source_unique),
                len(source_duplicates),
                source_sheet_name,
                header_row_idx + 1,
                before_counts[REST_COL],
                after_counts[REST_COL],
                before_counts[EXERCISE_COL],
                after_counts[EXERCISE_COL],
                before_counts[DSWS_COL],
                after_counts[DSWS_COL],
                int(fill_rest_mask.sum()),
                int(fill_exercise_mask.sum()),
                int(fill_dsws_mask.sum()),
                len(filled_rows),
                len(still_missing_final),
                f"{DSWS_COL} = {EXERCISE_COL} - {REST_COL}",
            ],
        }
    )

    report_path = REPORT_DIR / f"bp_fill_from_doctoral_dataset_report_{timestamp}.xlsx"

    with pd.ExcelWriter(report_path, engine="openpyxl") as writer:
        summary.to_excel(writer, sheet_name="summary", index=False)
        filled_rows.to_excel(writer, sheet_name="filled_rows", index=False)
        matched_but_not_filled.to_excel(writer, sheet_name="matched_but_not_filled", index=False)
        still_missing_final.to_excel(writer, sheet_name="still_missing_final", index=False)
        source_not_used.to_excel(writer, sheet_name="source_not_used", index=False)
        source_duplicates.to_excel(writer, sheet_name="source_duplicates", index=False)

    # ---------- Clean and save ----------
    drop_cols = [
        "_merge_name_key",
        "source_full_name",
        "source_sbp_rest",
        "source_sbp_end_test",
        "source_dsws",
    ]

    merged = merged.drop(columns=[c for c in drop_cols if c in merged.columns])

    # Чтобы колонки было видно сразу рядом с ФИО
    merged = move_cols_after_subject_name(merged)

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
    print("Заполнено ячеек:")
    print(f"  {REST_COL}: {int(fill_rest_mask.sum())}")
    print(f"  {EXERCISE_COL}: {int(fill_exercise_mask.sum())}")
    print(f"  {DSWS_COL}: {int(fill_dsws_mask.sum())}")
    print()
    print("Непустые значения ДО:")
    print(before_counts)
    print()
    print("Непустые значения ПОСЛЕ:")
    print(after_counts)


if __name__ == "__main__":
    main()