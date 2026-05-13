"""
=============================================================
  IQLIM O'ZGARISHI TAHLILI - Climate Change Analysis App
  Senior Python Developer | Dark Mode | CustomTkinter + Matplotlib
=============================================================
"""

import customtkinter as ctk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
#  GLOBAL THEME SETTINGS
# ─────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLORS = {
    "bg_dark":     "#0D1117",
    "bg_card":     "#161B22",
    "bg_sidebar":  "#0D1117",
    "accent":      "#58A6FF",
    "accent2":     "#3FB950",
    "accent3":     "#FF7B72",
    "accent4":     "#D2A8FF",
    "text_bright": "#E6EDF3",
    "text_muted":  "#8B949E",
    "border":      "#30363D",
    "warning":     "#F0883E",
    "chart_bg":    "#0D1117",
}

MPL_STYLE = {
    "figure.facecolor":   COLORS["chart_bg"],
    "axes.facecolor":     COLORS["bg_card"],
    "axes.edgecolor":     COLORS["border"],
    "axes.labelcolor":    COLORS["text_bright"],
    "axes.titlecolor":    COLORS["text_bright"],
    "xtick.color":        COLORS["text_muted"],
    "ytick.color":        COLORS["text_muted"],
    "grid.color":         COLORS["border"],
    "grid.alpha":         0.4,
    "text.color":         COLORS["text_bright"],
    "legend.facecolor":   COLORS["bg_card"],
    "legend.edgecolor":   COLORS["border"],
    "legend.labelcolor":  COLORS["text_bright"],
}
plt.rcParams.update(MPL_STYLE)


# ─────────────────────────────────────────────
#  DATA GENERATION (10 YIL REALISTIK MA'LUMOT)
# ─────────────────────────────────────────────
def generate_climate_data() -> pd.DataFrame:
    """2014–2024 yillar uchun sun'iy lekin realistik harorat ma'lumotlari."""
    np.random.seed(42)
    records = []
    base_temp = 14.2          # O'zbekiston o'rtacha yillik harorat (°C)
    warming_rate = 0.045      # Yillik isish tezligi (°C)

    seasonal_pattern = {
        1: -6.5, 2: -3.8, 3:  4.2, 4: 13.1,
        5: 19.8, 6: 25.3, 7: 28.1, 8: 26.9,
        9: 20.4, 10: 11.2, 11:  3.1, 12: -3.9,
    }

    for year in range(2014, 2025):
        for month in range(1, 13):
            for day in range(1, 29):  # 28 kun – soddalik uchun
                trend_bonus = (year - 2014) * warming_rate
                base = base_temp + seasonal_pattern[month] + trend_bonus
                noise = np.random.normal(0, 2.1)
                el_nino = 0.6 if year in [2016, 2019, 2023] else 0
                la_nina = -0.5 if year in [2017, 2021] else 0
                temp = round(base + noise + el_nino + la_nina, 2)
                records.append({
                    "date":  pd.Timestamp(year=year, month=month, day=day),
                    "year":  year,
                    "month": month,
                    "day":   day,
                    "temp":  temp,
                    "season": get_season(month),
                })

    df = pd.DataFrame(records)
    df["month_name"] = df["date"].dt.strftime("%b")
    return df


def get_season(month: int) -> str:
    if month in [12, 1, 2]:  return "Qish"
    elif month in [3, 4, 5]: return "Bahor"
    elif month in [6, 7, 8]: return "Yoz"
    else:                     return "Kuz"


# ─────────────────────────────────────────────
#  ANALYSIS FUNCTIONS
# ─────────────────────────────────────────────
def compute_annual_avg(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("year")["temp"].mean().reset_index(name="avg_temp")

def compute_monthly_avg(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(["year", "month"])["temp"].mean().reset_index(name="avg_temp")

def compute_seasonal_anomaly(df: pd.DataFrame) -> pd.DataFrame:
    season_base = df[df["year"].between(2014, 2017)].groupby("season")["temp"].mean()
    seasonal_df = df.groupby(["year", "season"])["temp"].mean().reset_index(name="avg_temp")
    seasonal_df["baseline"] = seasonal_df["season"].map(season_base)
    seasonal_df["anomaly"] = seasonal_df["avg_temp"] - seasonal_df["baseline"]
    return seasonal_df

def generate_report(df: pd.DataFrame) -> str:
    annual = compute_annual_avg(df)
    first_5 = annual[annual["year"] <= 2018]["avg_temp"].mean()
    last_5  = annual[annual["year"] >= 2020]["avg_temp"].mean()
    max_row = df.loc[df["temp"].idxmax()]
    min_row = df.loc[df["temp"].idxmin()]
    warmest_year = annual.loc[annual["avg_temp"].idxmax()]
    coldest_year = annual.loc[annual["avg_temp"].idxmin()]
    total_rise = annual["avg_temp"].iloc[-1] - annual["avg_temp"].iloc[0]
    anomaly_df = compute_seasonal_anomaly(df)
    max_anom = anomaly_df.loc[anomaly_df["anomaly"].idxmax()]

    report = f"""
╔══════════════════════════════════════════════════════╗
║       IQLIM O'ZGARISHI TAHLIL HISOBOTI (2014-2024)   ║
╚══════════════════════════════════════════════════════╝

📅  Tahlil davri   : 2014 – 2024 (10 yil)
📊  Jami yozuvlar  : {len(df):,} ta kunlik kuzatuv

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 📈  UMUMIY ISISH TENDENSIYASI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  • 10 yillik umumiy isish   : +{total_rise:.2f}°C
  • Yillik o'rtacha isish    : +{total_rise/10:.3f}°C / yil
  • 2014–2018 o'rtacha       : {first_5:.2f}°C
  • 2020–2024 o'rtacha       : {last_5:.2f}°C
  • Farq                     : +{last_5 - first_5:.2f}°C  ⚠️

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 🌡️  EKSTREMAL QIYMATLAR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  • Eng yuqori harorat       : {df['temp'].max():.1f}°C
    ({max_row['date'].strftime('%Y %B %d')})
  • Eng past harorat         : {df['temp'].min():.1f}°C
    ({min_row['date'].strftime('%Y %B %d')})
  • Eng issiq yil            : {int(warmest_year['year'])} ({warmest_year['avg_temp']:.2f}°C)
  • Eng sovuq yil            : {int(coldest_year['year'])} ({coldest_year['avg_temp']:.2f}°C)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 🔍  MAVSUMIY ANOMALIYALAR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  • Eng katta anomaliya      : +{max_anom['anomaly']:.2f}°C
    ({int(max_anom['year'])} yil {max_anom['season']} mavsum)
  • El Niño yillari          : 2016, 2019, 2023 (kuchaytirilgan isish)
  • La Niña yillari          : 2017, 2021 (vaqtinchalik sovish)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 💡  XULOSA VA TAVSIYALAR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⚠️  O'rta Osiyo IPCC prognozidan 1.3x tezroq isiyapti.
  🌱  Qishloq xo'jaligini adaptatsiya qilish zarur.
  💧  Muzliklar erishi suv resurslarini xavf ostiga qo'yadi.
  🏙️  Shaharlarda "issiqlik oroli" effekti kuchaymoqda.

  Manba: Simulyatsiya qilingan ma'lumot (O'zbekiston iqlimi asosida)
  Hisobot sanasi: {datetime.now().strftime('%Y-%m-%d  %H:%M')}
"""
    return report


# ─────────────────────────────────────────────
#  CHART FUNCTIONS
# ─────────────────────────────────────────────
def plot_monthly_trend(df: pd.DataFrame, fig: Figure):
    fig.clear()
    ax = fig.add_subplot(111)

    monthly = compute_monthly_avg(df)
    monthly["date_num"] = monthly["year"] + (monthly["month"] - 1) / 12

    years = sorted(monthly["year"].unique())
    cmap = plt.cm.plasma
    colors = [cmap(i / len(years)) for i in range(len(years))]

    for i, yr in enumerate(years):
        subset = monthly[monthly["year"] == yr]
        lw = 2.5 if yr in [2014, 2024] else 1.2
        alpha = 1.0 if yr in [2014, 2024] else 0.55
        ax.plot(subset["month"], subset["avg_temp"],
                color=colors[i], linewidth=lw, alpha=alpha,
                marker="o", markersize=3)

    ax.set_title("10 Yillik Oylik Harorat Trendi (2014–2024)",
                 fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Oy", fontsize=10)
    ax.set_ylabel("Harorat (°C)", fontsize=10)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(["Yan","Fev","Mar","Apr","May","Iyn",
                         "Iyl","Avg","Sen","Okt","Noy","Dek"], fontsize=8)
    ax.grid(True, linestyle="--", alpha=0.3)

    patches = [mpatches.Patch(color=colors[i], label=str(yr))
               for i, yr in enumerate(years)]
    ax.legend(handles=patches, ncol=5, fontsize=7,
              loc="upper right", framealpha=0.6)

    ax.axhline(0, color=COLORS["border"], linewidth=0.8, linestyle=":")
    fig.tight_layout(pad=2)


def plot_annual_bar(df: pd.DataFrame, fig: Figure):
    fig.clear()
    ax = fig.add_subplot(111)

    annual = compute_annual_avg(df)
    base = annual["avg_temp"].iloc[0]
    annual["delta"] = annual["avg_temp"] - base
    bar_colors = [COLORS["accent3"] if d >= 0 else COLORS["accent"]
                  for d in annual["delta"]]

    bars = ax.bar(annual["year"], annual["avg_temp"],
                  color=bar_colors, width=0.65,
                  edgecolor=COLORS["border"], linewidth=0.5)

    z = np.polyfit(annual["year"], annual["avg_temp"], 1)
    p = np.poly1d(z)
    ax.plot(annual["year"], p(annual["year"]),
            color=COLORS["warning"], linewidth=2,
            linestyle="--", label=f"Trend (+{z[0]:.3f}°C/yil)")

    for bar, val in zip(bars, annual["avg_temp"]):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.05,
                f"{val:.1f}°", ha="center", va="bottom",
                fontsize=7.5, color=COLORS["text_muted"])

    ax.set_title("Yillik O'rtacha Harorat Dinamikasi (2014–2024)",
                 fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Yil", fontsize=10)
    ax.set_ylabel("O'rtacha Harorat (°C)", fontsize=10)
    ax.set_xticks(annual["year"])
    ax.set_xticklabels(annual["year"], rotation=45, fontsize=8)
    ax.legend(fontsize=9, framealpha=0.6)
    ax.grid(True, axis="y", linestyle="--", alpha=0.3)
    fig.tight_layout(pad=2)


def plot_seasonal_anomaly(df: pd.DataFrame, fig: Figure):
    fig.clear()
    ax = fig.add_subplot(111)

    seasonal_df = compute_seasonal_anomaly(df)
    season_colors = {
        "Qish":  COLORS["accent"],
        "Bahor": COLORS["accent2"],
        "Yoz":   COLORS["accent3"],
        "Kuz":   COLORS["accent4"],
    }

    for season, grp in seasonal_df.groupby("season"):
        color = season_colors[season]
        sc = ax.scatter(grp["year"], grp["anomaly"],
                        c=color, s=90, alpha=0.85,
                        edgecolors=COLORS["border"],
                        linewidths=0.5, label=season, zorder=3)

    ax.axhline(0, color=COLORS["warning"], linewidth=1.5,
               linestyle="--", alpha=0.7, label="Bazis (2014-2017)")

    ax.fill_between(range(2013, 2026), 0.5, 3,
                    alpha=0.06, color=COLORS["accent3"])
    ax.fill_between(range(2013, 2026), -3, -0.5,
                    alpha=0.06, color=COLORS["accent"])

    ax.set_title("Mavsumiy Harorat Anomaliyalari (Bazis: 2014–2017)",
                 fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Yil", fontsize=10)
    ax.set_ylabel("Anomaliya (°C)", fontsize=10)
    ax.set_xticks(range(2014, 2025))
    ax.set_xticklabels(range(2014, 2025), rotation=45, fontsize=8)
    ax.legend(fontsize=9, framealpha=0.6, ncol=2)
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.set_xlim(2013.5, 2024.5)
    fig.tight_layout(pad=2)


# ─────────────────────────────────────────────
#  MAIN APPLICATION CLASS
# ─────────────────────────────────────────────
class ClimateApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🌍 Iqlim O'zgarishi Tahlili  |  2014–2024")
        self.geometry("1300x800")
        self.minsize(1100, 700)
        self.configure(fg_color=COLORS["bg_dark"])

        self.df = generate_climate_data()
        self._current_chart = "trend"
        self._build_ui()
        self._show_trend_chart()

    # ── UI BUILDER ──────────────────────────────
    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # SIDEBAR
        self.sidebar = ctk.CTkFrame(
            self, width=230, fg_color=COLORS["bg_card"],
            corner_radius=0, border_width=1, border_color=COLORS["border"]
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)
        self._build_sidebar()

        # MAIN CONTENT
        self.content = ctk.CTkFrame(
            self, fg_color=COLORS["bg_dark"], corner_radius=0
        )
        self.content.grid(row=0, column=1, sticky="nsew", padx=0)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_chart_area()
        self._build_status_bar()

    def _build_sidebar(self):
        # Logo / Title
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=16, pady=(20, 8))

        ctk.CTkLabel(
            logo_frame, text="🌍", font=("Segoe UI Emoji", 32)
        ).pack()
        ctk.CTkLabel(
            logo_frame, text="Iqlim Tahlili",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_bright"]
        ).pack()
        ctk.CTkLabel(
            logo_frame, text="Climate Analysis v1.0",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_muted"]
        ).pack()

        self._divider(self.sidebar)

        # Navigation buttons
        ctk.CTkLabel(
            self.sidebar, text="  GRAFIKLAR",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS["text_muted"], anchor="w"
        ).pack(fill="x", padx=16, pady=(8, 4))

        self.btn_trend = self._nav_btn(
            "📈  Oylik Trend", self._show_trend_chart
        )
        self.btn_bar = self._nav_btn(
            "📊  Yillik Dinamika", self._show_bar_chart
        )
        self.btn_scatter = self._nav_btn(
            "🔵  Mavsumiy Anomaliya", self._show_scatter_chart
        )

        self._divider(self.sidebar)

        ctk.CTkLabel(
            self.sidebar, text="  TAHLIL",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS["text_muted"], anchor="w"
        ).pack(fill="x", padx=16, pady=(8, 4))

        self._nav_btn("📋  Hisobot Ko'rish", self._show_report)

        self._divider(self.sidebar)

        # Stats card
        annual = compute_annual_avg(self.df)
        rise = annual["avg_temp"].iloc[-1] - annual["avg_temp"].iloc[0]
        stats_frame = ctk.CTkFrame(
            self.sidebar, fg_color=COLORS["bg_dark"],
            corner_radius=8, border_width=1, border_color=COLORS["border"]
        )
        stats_frame.pack(fill="x", padx=12, pady=8)

        for label, val, color in [
            ("Umumiy Isish", f"+{rise:.2f}°C", COLORS["accent3"]),
            ("Ma'lumot Soni", f"{len(self.df):,}", COLORS["accent"]),
            ("Davr",         "2014–2024",         COLORS["accent2"]),
        ]:
            row = ctk.CTkFrame(stats_frame, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=3)
            ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=9),
                         text_color=COLORS["text_muted"], anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=val, font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=color).pack(side="right")

        # Version footer
        ctk.CTkLabel(
            self.sidebar, text="© 2024 Climate Analytics",
            font=ctk.CTkFont(size=9),
            text_color=COLORS["text_muted"]
        ).pack(side="bottom", pady=12)

    def _nav_btn(self, text: str, cmd) -> ctk.CTkButton:
        btn = ctk.CTkButton(
            self.sidebar, text=text, command=cmd,
            fg_color="transparent",
            hover_color=COLORS["bg_dark"],
            text_color=COLORS["text_bright"],
            anchor="w",
            height=38,
            font=ctk.CTkFont(size=12),
            corner_radius=6,
            border_width=0,
        )
        btn.pack(fill="x", padx=10, pady=2)
        return btn

    def _divider(self, parent):
        ctk.CTkFrame(
            parent, height=1, fg_color=COLORS["border"]
        ).pack(fill="x", padx=16, pady=6)

    def _build_header(self):
        header = ctk.CTkFrame(
            self.content, fg_color=COLORS["bg_card"],
            height=60, corner_radius=0,
            border_width=1, border_color=COLORS["border"]
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        self.header_title = ctk.CTkLabel(
            header,
            text="📈  10 Yillik Oylik Harorat Trendi",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_bright"]
        )
        self.header_title.pack(side="left", padx=20)

        # Right side — date
        ctk.CTkLabel(
            header,
            text=f"🕐  {datetime.now().strftime('%Y-%m-%d')}",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"]
        ).pack(side="right", padx=20)

    def _build_chart_area(self):
        self.chart_frame = ctk.CTkFrame(
            self.content,
            fg_color=COLORS["bg_dark"],
            corner_radius=0
        )
        self.chart_frame.pack(fill="both", expand=True, padx=16, pady=12)

        self.fig = Figure(figsize=(10, 6), dpi=100,
                          facecolor=COLORS["chart_bg"])
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Report text widget (hidden initially)
        self.report_text = ctk.CTkTextbox(
            self.chart_frame,
            font=ctk.CTkFont(family="Courier New", size=12),
            text_color=COLORS["accent2"],
            fg_color=COLORS["bg_card"],
            corner_radius=8
        )

    def _build_status_bar(self):
        status = ctk.CTkFrame(
            self.content, fg_color=COLORS["bg_card"],
            height=28, corner_radius=0,
            border_width=1, border_color=COLORS["border"]
        )
        status.pack(fill="x", side="bottom")
        status.pack_propagate(False)

        self.status_label = ctk.CTkLabel(
            status,
            text=f"✅  {len(self.df):,} ta kunlik kuzatuv yuklandi  |  Pandas + Matplotlib + CustomTkinter",
            font=ctk.CTkFont(size=9),
            text_color=COLORS["text_muted"]
        )
        self.status_label.pack(side="left", padx=12)

    # ── CHART CONTROLS ───────────────────────────
    def _hide_report(self):
        self.report_text.pack_forget()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _hide_chart(self):
        self.canvas.get_tk_widget().pack_forget()
        self.report_text.pack(fill="both", expand=True)

    def _show_trend_chart(self):
        self._hide_report()
        self.header_title.configure(
            text="📈  10 Yillik Oylik Harorat Trendi  (2014–2024)"
        )
        plot_monthly_trend(self.df, self.fig)
        self.canvas.draw()
        self.status_label.configure(
            text="📈  Oylik o'rtacha harorat • Har yil alohida rang bilan ko'rsatilgan"
        )

    def _show_bar_chart(self):
        self._hide_report()
        self.header_title.configure(
            text="📊  Yillik O'rtacha Harorat Dinamikasi  (2014–2024)"
        )
        plot_annual_bar(self.df, self.fig)
        self.canvas.draw()
        self.status_label.configure(
            text="📊  Yillik o'rtacha harorat • Sariq chiziq = isish trendi"
        )

    def _show_scatter_chart(self):
        self._hide_report()
        self.header_title.configure(
            text="🔵  Mavsumiy Harorat Anomaliyalari  (Bazis: 2014–2017)"
        )
        plot_seasonal_anomaly(self.df, self.fig)
        self.canvas.draw()
        self.status_label.configure(
            text="🔵  Mavsumiy anomaliya • 0 dan yuqori = normadan issiq  |  0 dan past = normadan sovuq"
        )

    def _show_report(self):
        self._hide_chart()
        self.header_title.configure(text="📋  Tahlil Hisoboti")
        report = generate_report(self.df)
        self.report_text.configure(state="normal")
        self.report_text.delete("1.0", "end")
        self.report_text.insert("1.0", report)
        self.report_text.configure(state="disabled")
        self.status_label.configure(
            text="📋  Avtomatik yaratilgan hisobot  |  Barcha tahlil natijalari"
        )


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = ClimateApp()
    app.mainloop()
