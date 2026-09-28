from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from threading import Thread
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from src.aggregator import summarize
from src.archive_indexer import ArchiveCatalog, carrier_file_counts, discover_archive, select_forms
from src.excel_reporter import write_report
from src.form_reader import read_form
from src.models import AssetType, UnreadableFile, ValidityRecord
from src.question_catalog import default_catalog

ARCHIVE_HELP = (
    "1. Arşiv klasörünü seçin veya örnek yapıyı oluşturun.  "
    "2. Excel kontrol formlarını Nakliyeci/Kontrol Formları içine koyun.  "
    "3. Yıl, ay, gün ve nakliyeci filtresini seçip Analizi Listele'ye basın."
)


@dataclass(frozen=True)
class Selection:
    years: set[int]
    months: set[str]
    days: set[int]
    carrier: str | None


def build_selection(years: set[str], months: set[str], days: set[str], carrier_label: str) -> Selection:
    carrier = carrier_label.rsplit(" (", 1)[0] if carrier_label and carrier_label != "Tümü" else None
    return Selection({int(item) for item in years}, {item.upper() for item in months}, {int(item) for item in days}, carrier)


def choose_carrier(values: set[str]) -> str:
    if not values:
        return "Tümü"
    if len(values) != 1:
        raise ValueError("Tek seferde yalnız bir nakliyeci seçilebilir.")
    return next(iter(values))


def expected_archive_path(root: Path, year: int, month: str, day: int, carrier: str) -> Path:
    return root / str(year) / month.upper() / str(day) / carrier / "Kontrol Formları"


def analyze_archive(root: Path, selection: Selection) -> tuple[list[ValidityRecord], list[UnreadableFile], list]:
    catalog = discover_archive(root)
    files = select_forms(catalog, selection.years, selection.months, selection.days, selection.carrier)
    records: list[ValidityRecord] = []
    unreadable: list[UnreadableFile] = []
    for archive_file in files:
        parsed, errors = read_form(archive_file, default_catalog())
        records.extend(parsed)
        unreadable.extend(errors)
    return records, unreadable, files


class ArchiveAnalysisApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SEYMEN | Kontrol Formu Arşiv Analizi")
        self.geometry("1280x780")
        self.minsize(1050, 650)
        self.root_path: Path | None = None
        self.catalog = ArchiveCatalog(Path("."), ())
        self.last_result = None
        self.last_unreadable: list[UnreadableFile] = []
        self._build()

    def _build(self):
        header = tk.Frame(self, bg="#153f69", pady=18)
        header.pack(fill="x")
        tk.Label(header, text="SEYMEN", bg="#ffcc18", fg="#12395e", font=("Arial", 22, "bold"), padx=20, pady=9).pack(side="left", padx=24)
        tk.Label(header, text="KONTROL FORMU ARŞİV ANALİZİ", bg="#153f69", fg="white", font=("Arial", 20, "bold")).pack(side="left")
        controls = ttk.Frame(self, padding=(12, 12, 12, 6))
        controls.pack(fill="x")
        ttk.Button(controls, text="Arşiv Klasörünü Seç", command=self.select_root).pack(side="left", padx=(0, 8))
        ttk.Button(controls, text="Örnek Arşiv Yapısı Oluştur", command=self.create_archive_template).pack(side="left", padx=8)
        self.open_root_button = ttk.Button(controls, text="Seçilen Klasörü Aç", command=self.open_root, state="disabled")
        self.open_root_button.pack(side="left", padx=8)
        self.analyze_button = ttk.Button(controls, text="Analizi Listele", command=self.start_analysis, state="disabled")
        self.analyze_button.pack(side="left", padx=8)
        self.export_button = ttk.Button(controls, text="Excel'e Aktar", command=self.export_report, state="disabled")
        self.export_button.pack(side="left", padx=8)
        self.status = tk.StringVar(value="Başlamak için arşiv klasörünü seçin.")
        info = ttk.LabelFrame(self, text="Kullanım", padding=(12, 7))
        info.pack(fill="x", padx=12, pady=(0, 8))
        ttk.Label(info, text=ARCHIVE_HELP, wraplength=1200, justify="left").pack(anchor="w")
        self.root_display = tk.StringVar(value="Seçilen arşiv klasörü: —")
        ttk.Label(info, textvariable=self.root_display, foreground="#153f69").pack(anchor="w", pady=(5, 0))
        ttk.Label(controls, textvariable=self.status).pack(side="left", padx=16)
        filters = ttk.Frame(self, padding=(12, 0, 12, 8))
        filters.pack(fill="x")
        self.years = self._list_filter(filters, "Yıl", 0)
        self.months = self._list_filter(filters, "Ay (çoklu seçim)", 1)
        self.days = self._list_filter(filters, "Gün (çoklu seçim)", 2)
        self.carriers = self._list_filter(filters, "Nakliyeci", 3, multiple=False)
        table_frame = ttk.Frame(self, padding=12)
        table_frame.pack(fill="both", expand=True)
        columns = ("nakliyeci", "plaka", "son_tarih", "gelis", "evrak", "tarih", "durum")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        labels = ("Nakliyeci", "Çekici Plakası", "En Son Geliş", "Geliş Sayısı", "Evrak", "Geçerlilik", "Durum")
        for key, label in zip(columns, labels):
            self.tree.heading(key, text=label)
            self.tree.column(key, width=170 if key in {"nakliyeci", "evrak"} else 120, anchor="w")
        self.tree.tag_configure("expired", background="#ffb3b3")
        self.tree.tag_configure("warning", background="#ffd59a")
        yscroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        yscroll.pack(side="right", fill="y")

    def _list_filter(self, parent, label: str, column: int, multiple: bool = True) -> tk.Listbox:
        group = ttk.LabelFrame(parent, text=label, padding=5)
        group.grid(row=0, column=column, padx=5, sticky="nsew")
        parent.grid_columnconfigure(column, weight=1)
        box = tk.Listbox(group, height=6, exportselection=False, selectmode="extended" if multiple else "browse")
        box.pack(fill="both", expand=True)
        return box

    @staticmethod
    def _selected(box: tk.Listbox) -> set[str]:
        return {box.get(index) for index in box.curselection()}

    def select_root(self):
        chosen = filedialog.askdirectory(title="Kontrol formu arşiv ana klasörünü seçin")
        if not chosen:
            return
        self.root_path = Path(chosen)
        self.catalog = discover_archive(self.root_path)
        self.root_display.set(f"Seçilen arşiv klasörü: {self.root_path}")
        self.open_root_button.configure(state="normal")
        for box in (self.years, self.months, self.days, self.carriers):
            box.delete(0, "end")
        for value in self.catalog.years:
            self.years.insert("end", str(value))
        for value in self.catalog.months:
            self.months.insert("end", value)
        for value in sorted({item.day for item in self.catalog.files}):
            self.days.insert("end", str(value))
        counts = carrier_file_counts(list(self.catalog.files))
        self.carriers.insert("end", "Tümü")
        for carrier, count in counts.items():
            self.carriers.insert("end", f"{carrier} ({count} form)")
        if not self.catalog.files:
            self.status.set(
                "Kontrol formu bulunamadı. Excel dosyalarını Yıl/Ay/Gün/Nakliyeci/Kontrol Formları klasörüne koyun."
            )
            self.analyze_button.configure(state="disabled")
            return
        for box in (self.years, self.months, self.days):
            box.selection_set(0, "end")
        self.carriers.selection_set(0)
        self.status.set(f"{len(self.catalog.files)} kontrol formu bulundu. Tüm filtreler seçildi; isterseniz daraltın.")
        self.analyze_button.configure(state="normal")

    def create_archive_template(self):
        chosen = filedialog.askdirectory(title="Arşiv ana klasörünün oluşturulacağı yeri seçin")
        if not chosen:
            return
        root = Path(chosen) / "SEYMEN_Kontrol_Formu_Arsivi"
        target = expected_archive_path(root, date.today().year, "EYLÜL", date.today().day, "NAKLIYECI_ADI")
        target.mkdir(parents=True, exist_ok=True)
        messagebox.showinfo(
            "SEYMEN",
            "Örnek arşiv yapısı oluşturuldu. Excel kontrol formlarını aşağıdaki klasöre koyun:\n\n"
            f"{target}\n\nSonra 'Arşiv Klasörünü Seç' ile SEYMEN_Kontrol_Formu_Arsivi klasörünü seçin.",
        )

    def open_root(self):
        if not self.root_path:
            return
        try:
            import os
            import subprocess
            import sys

            if sys.platform == "darwin":
                subprocess.run(["open", str(self.root_path)], check=False)
            elif os.name == "nt":
                os.startfile(self.root_path)  # type: ignore[attr-defined]
            else:
                subprocess.run(["xdg-open", str(self.root_path)], check=False)
        except OSError:
            messagebox.showwarning("SEYMEN", f"Klasör açılamadı:\n{self.root_path}")

    def _selection(self) -> Selection:
        return build_selection(self._selected(self.years), self._selected(self.months), self._selected(self.days), choose_carrier(self._selected(self.carriers)))

    def start_analysis(self):
        if not self.root_path:
            return
        self.analyze_button.configure(state="disabled")
        self.status.set("Arşiv formları arka planda okunuyor...")
        Thread(target=self._analysis_worker, args=(self._selection(),), daemon=True).start()

    def _analysis_worker(self, selection: Selection):
        records, unreadable, files = analyze_archive(self.root_path, selection)
        result = summarize(records, date.today())
        self.after(0, lambda: self._show_result(result, unreadable, len(files)))

    def _show_result(self, result, unreadable, file_count: int):
        self.last_result, self.last_unreadable = result, unreadable
        self.tree.delete(*self.tree.get_children())
        for summary in result.by_type[AssetType.TRACTOR]:
            for name, validity in sorted(summary.document_dates.items()):
                remaining = (validity - date.today()).days
                status = "Geçmiş" if remaining < 0 else "Yaklaşıyor" if remaining <= 20 else "Geçerli"
                tag = "expired" if status == "Geçmiş" else "warning" if status == "Yaklaşıyor" else ""
                self.tree.insert("", "end", values=(summary.carrier, summary.asset_id, summary.latest_control_date, summary.arrival_count, name, validity, status), tags=(tag,))
        self.status.set(f"{file_count} form okundu; {len(unreadable)} dosya okunamadı; {len(result.critical)} kritik tarih bulundu.")
        self.analyze_button.configure(state="normal")
        self.export_button.configure(state="normal")

    def export_report(self):
        if not self.last_result:
            messagebox.showwarning("SEYMEN", "Önce arşiv analizi yapın.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")], initialfile="Kontrol_Formu_Arsiv_Raporu.xlsx")
        if not path:
            return
        write_report(self.last_result, self.last_unreadable, Path(path), date.today())
        messagebox.showinfo("SEYMEN", "Excel raporu oluşturuldu.")


if __name__ == "__main__":
    ArchiveAnalysisApp().mainloop()
